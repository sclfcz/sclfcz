#!/usr/bin/env python3
"""Compare the profile's pinned items with the projects worth pinning.

Target is your own non-fork repository first, then the strongest merged-into projects above the
README's star floor. GitHub has no API for pins (six items, repositories and gists
combined, edited only in the browser), so this prints the order to apply rather than applying it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_merged_prs import collect  # noqa: E402

API = "https://api.github.com/graphql"
SLOTS = 6

# Repositories that exist but should not be promoted on the profile: the pin grid is
# prime real estate, and not every repo is something to lead with.
SKIP_PINS = {"sclfcz/EstateAgents"}
# A grid of nothing but other people's repos hides what you build yourself.
# Two slots because there are two shipped projects worth reading (a desktop app and a
# mini program); raise it again when a third one lands, and drop it back if one goes stale.
OWN_SLOTS = 2

PINS = """
query($login: String!) {
  user(login: $login) {
    pinnedItems(first: 6) {
      nodes { __typename ... on Repository { nameWithOwner } }
    }
  }
}
"""

OWN = """
query($login: String!) {
  user(login: $login) {
    repositories(
      first: 100, ownerAffiliations: OWNER,
      orderBy: {field: STARGAZERS, direction: DESC}
    ) {
      nodes { nameWithOwner stargazerCount pushedAt isFork }
    }
  }
}
"""


def gql(token: str, query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(
        API,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-readme-refresh",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL errors: {json.dumps(payload['errors'])}")
    return payload["data"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=os.environ.get("PROFILE_OWNER", "sxh313"))
    parser.add_argument("--output", type=Path, help="Write the plan here.")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GH_TOKEN / GITHUB_TOKEN.")

    rows, _ = collect(token, f"author:{args.owner} is:pr is:merged")
    # The README lists every project now, so no floor filter here either.
    stars: dict[str, int] = {}
    merges: Counter = Counter()
    for row in rows:
        name = row["repo"]["nameWithOwner"]
        stars.setdefault(name, row["repo"]["stargazerCount"])
        merges[name] += 1
    own = gql(token, OWN, {"login": args.owner})["user"]["repositories"]["nodes"]
    own.sort(key=lambda n: n["pushedAt"] or "", reverse=True)
    own.sort(key=lambda n: -n["stargazerCount"])
    # The profile repo is not "work" — it is already linked at the top of the page.
    profile_repo = f"{args.owner}/{args.owner}"
    # An own repo that also merged one of my PRs is still my work first: keep it in the
    # own group and drop it from the merged group, instead of demoting it.
    own_order = [
        n["nameWithOwner"]
        for n in own
        if not n.get("isFork")
        and n["nameWithOwner"] != profile_repo
        and n["nameWithOwner"] not in SKIP_PINS
    ]
    own_set = set(own_order)
    # Forks are the only way an upstream project can appear in the pin grid, since the
    # picker only offers repositories under my own account.
    fork_by_name = {
        n["nameWithOwner"].split("/", 1)[1]: n["nameWithOwner"] for n in own if n.get("isFork")
    }

    # Merges first, stars second: a project that merged nine of my PRs is stronger
    # evidence of reach than a single merge in a project with more stars.
    merged_order = sorted((n for n in stars if n not in own_set), key=lambda n: (-merges[n], -stars[n], n))

    # GitHub's pin picker only offers repositories you own, so an upstream project can only
    # be pinned through my fork of it. Recommend the fork when it exists and drop the rest,
    # so the plan is always something the browser can actually follow.
    pinned_fork: list[tuple[str, str]] = []  # (fork, upstream project it stands for)
    for name in merged_order:
        fork = fork_by_name.get(name.split("/", 1)[1])
        if fork and all(fork != existing for existing, _ in pinned_fork):
            pinned_fork.append((fork, name))
    upstream_of = dict(pinned_fork)
    merged_order = [fork for fork, _ in pinned_fork]

    nodes = gql(token, PINS, {"login": args.owner})["user"]["pinnedItems"]["nodes"]
    current = [n["nameWithOwner"] for n in nodes if n and n["__typename"] == "Repository"]
    gists = sum(1 for n in nodes if n and n["__typename"] != "Repository")

    # Own work leads the grid: the merged projects prove reach, this proves authorship.
    target = own_order[:OWN_SLOTS] + merged_order[:SLOTS - OWN_SLOTS]
    if len(target) < SLOTS:
        # Personal picks keep their place; a gist costs a slot, so count it.
        room = SLOTS - gists
        for name in current:
            if len(target) >= room:
                break
            if name not in target:
                target.append(name)
        target = target[:room]

    to_add = [n for n in target if n not in current]
    to_drop = [n for n in current if n not in target]

    lines = [f"Pin these {len(target)}, in this order:"]
    for pos, name in enumerate(target, 1):
        # Own work is tagged by authorship, not by merge count: a self-merge is not
        # an upstream contribution.
        if name in own_set:
            tag = "personal"
        else:
            # A pinned fork reports the upstream project's merge count, not the fork's.
            upstream = upstream_of.get(name, name)
            tag = f"merged x{merges[upstream]}" if upstream in merges else "personal"
        lines.append(f"  {pos}. {name:<34} {tag}")
    if to_add:
        lines.append("Add:    " + ", ".join(to_add))
    if to_drop:
        lines.append("Remove: " + ", ".join(to_drop))
    if gists:
        lines.append(f"{gists} gist(s) pinned, so {SLOTS - gists} repository slots remain.")
    if not to_add and not to_drop:
        lines.insert(1, "Already in sync.")

    plan = "\n".join(lines)
    print(plan)
    if to_add or to_drop:
        # A log line GitHub renders as an annotation on the run page.
        print(f"::warning::profile pins drift: add [{', '.join(to_add)}] remove [{', '.join(to_drop)}]")
    if args.output:
        args.output.write_text(plan + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
