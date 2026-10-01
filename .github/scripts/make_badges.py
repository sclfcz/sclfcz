#!/usr/bin/env python3
"""Render the profile's *moving* numbers as local SVG badges.

Why this exists: the three metric badges and the header chip used to be
img.shields.io images. A badge whose URL changes (12 -> 13 merged PRs) has to be
re-fetched by GitHub's image proxy on every refresh, and when that fetch fails the
badge renders as a broken image - which is what happened on the profile page.
Badges with immutable URLs stay in the proxy cache and keep working, so the static
Featured/Tech badges stay on shields.io and only the values that move come here.

Palette follows design/build.py (tempered steel: straw, bronze, purple, blue) so
the strip sits with the hero and the project figures. Text is plain <text> with a
system font stack - no external font request, nothing to fail at load time.
"""

from __future__ import annotations

import argparse
from pathlib import Path

FONT = "Verdana,DejaVu Sans,Geneva,sans-serif"

TALL_H = 28  # the centered metrics strip
FLAT_H = 20  # the header chip

LABEL_BG = "#3C4A5A"  # a palate-neutral slate, readable on light and dark pages


def _width(text: str, size: float) -> float:
    return len(text) * size * 0.62


def _badge(label: str, value: str, color: str, *, height: int, uppercase: bool, x: float) -> tuple[str, float]:
    size = 12.0 if height == TALL_H else 11.0
    label_text = label.upper() if uppercase else label
    pad = 11.0 if height == TALL_H else 10.0

    label_w = _width(label_text, size) + pad * 2
    value_w = _width(value, size) + pad * 2
    baseline = height / 2 + size * 0.35

    svg = f'''  <g transform="translate({x:.1f},0)">
    <rect width="{label_w:.1f}" height="{height}" rx="3" fill="{LABEL_BG}" />
    <rect x="{label_w - 3:.1f}" width="{value_w + 3:.1f}" height="{height}" rx="3" fill="{color}" />
    <rect x="{label_w - 3:.1f}" y="0" width="6" height="{height}" fill="{color}" />
    <text x="{label_w / 2:.1f}" y="{baseline:.1f}" fill="#FFFFFF" font-family="{FONT}" font-size="{size}" font-weight="700" text-anchor="middle">{label_text}</text>
    <text x="{label_w + value_w / 2:.1f}" y="{baseline:.1f}" fill="#FFFFFF" font-family="{FONT}" font-size="{size}" font-weight="700" text-anchor="middle">{value}</text>
  </g>'''
    return svg, label_w + value_w


def _write(path: Path, items: list[tuple[str, str, str]], *, height: int, uppercase: bool, gap: float) -> None:
    fragments: list[str] = []
    x = 0.0
    for label, value, color in items:
        fragment, width = _badge(label, value, color, height=height, uppercase=uppercase, x=x)
        fragments.append(fragment)
        x += width + gap
    total = x - gap if fragments else 0.0
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total:.1f}" height="{height}" '
        f'viewBox="0 0 {total:.1f} {height}" role="img">\n' + "\n".join(fragments) + "\n</svg>\n",
        encoding="utf-8",
    )


def write_badges(out: Path, merged: int, projects: int, stars: str) -> None:
    """Called by render_merged_prs.py so the badges and the README cannot disagree."""
    out.mkdir(parents=True, exist_ok=True)

    # Tempered-steel accents, matching design/build.py's palettes.
    _write(
        out / "stats.svg",
        [
            ("Merged PRs", str(merged), "#9366C4"),
            ("Projects", str(projects), "#5A8BE0"),
            ("Upstream stars", stars, "#C8783E"),
        ],
        height=TALL_H,
        uppercase=True,
        gap=8.0,
    )
    _write(
        out / "header-merged.svg",
        [("Upstream merged PRs", str(merged), "#9366C4")],
        height=FLAT_H,
        uppercase=False,
        gap=0.0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merged", type=int, required=True)
    parser.add_argument("--projects", type=int, required=True)
    parser.add_argument("--stars", type=str, required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "assets")
    args = parser.parse_args()

    write_badges(args.out, args.merged, args.projects, args.stars)
    print(f"wrote {args.out}/stats.svg and {args.out}/header-merged.svg ({args.merged} merged)")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
