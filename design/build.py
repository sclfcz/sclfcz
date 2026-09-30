#!/usr/bin/env python3
"""Generate the profile artwork in assets/.

    python3 design/build.py

The hero shows an edge dislocation gliding through a crystal one lattice step at a
time: the way metals deform, and the idea behind "Small steps every day."
Everything is outlined (no font requests) and animated with SMIL, which GitHub's
image proxy leaves intact. Each figure also gets a *-still.svg that the README's
<picture> serves under prefers-reduced-motion.

Fonts (OFL, from github.com/google/fonts, saved into design/fonts/, not committed):
  Archivo.ttf  <- ofl/archivo/Archivo[wdth,wght].ttf
  Plex.ttf     <- ofl/ibmplexsans/IBMPlexSans[wdth,wght].ttf
  NotoSC.ttf   <- ofl/notosanssc/NotoSansSC[wght].ttf
Requires: pip install uharfbuzz fonttools
"""

from __future__ import annotations

import math
from pathlib import Path

import svgtext as ST

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Temper colours: the oxide tints steel takes on as it heats, straw to blue.
PALETTES = {
    "dark": {
        "ground": "#14202E",
        "plane": "#2E4054",
        "atom": "#5D7189",
        "text": "#E8ECF0",
        "muted": "#93A3B5",
        "straw": "#E3B75E",
        "bronze": "#C8783E",
        "purple": "#9366C4",
        "blue": "#5A8BE0",
        "glow": 0.55,
    },
    "light": {
        "ground": "#E9EDF1",
        "plane": "#BCC7D3",
        "atom": "#7F8FA1",
        "text": "#17222E",
        "muted": "#52606F",
        "straw": "#A67A12",
        "bronze": "#A45220",
        "purple": "#6E44A0",
        "blue": "#2D5FB8",
        "glow": 0.34,
    },
}


def fmt(v: float) -> str:
    s = f"{v:.1f}"
    return "0" if s in ("-0.0", "0.0") else s.rstrip("0").rstrip(".")


def pts_d(points) -> str:
    return "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in points)


# --------------------------------------------------------------------------- hero
#
# Square lattice, spacing A, slip plane at SVG y = YS. An infinite row of edge
# dislocations with period P = N*A: displacement u_x = b/2pi * arg sin(pi z / P),
# the periodic sum of the textbook theta term, plus a small ln|sin| term for u_y.
# The core hops one lattice step every STEP seconds. Because the field is
# periodic, the state one cycle later is the same picture with the top half slipped
# by exactly one lattice vector, so the loop is seamless.

W, H = 1280, 440
A = 40.0  # lattice spacing (= Burgers vector b)
N = 15  # columns per period
P = N * A
STEP = 1.0  # seconds per lattice step
T = N * STEP
DWELL = 0.58  # share of each step spent at rest
YS = 214.0  # slip plane
ROWS = 4  # rows on each side of the slip plane
KAPPA = 0.26  # u_y strength (textbook ~0.14, boosted to read at small size)
WIN = (676.0, 1240.0)  # visible lattice window
X0 = 716.0  # reference column / core start

# Keyframe times within one step: rest, end of rest, then samples of the hop.


_Q = [i / 6 for i in range(1, 6)]


def ease(q: float) -> float:
    return q * q * q * (q * (6 * q - 15) + 10)  # smootherstep: a snap, then a settle


def _stops():
    out = []  # (phase seconds, lattice steps travelled)
    for k in range(N):
        t0 = k * STEP
        out.append((t0, float(k)))
        out.append((t0 + DWELL * STEP, float(k)))
        for q in _Q:
            out.append((t0 + (DWELL + (1 - DWELL) * q) * STEP, k + ease(q)))
    out.append((T, float(N)))
    return out


STOPS = _stops()


def _wrap(v: float) -> float:
    return (v + math.pi) % (2 * math.pi) - math.pi


def field(xi: float, ym: float) -> tuple[float, float]:
    """(u_x, u_y) in math coordinates for an atom at offset xi from the core, height ym.

    theta is the continuous branch of arg sin(pi (xi + i ym) / P): it tends to
    pi/2 - a above the plane and a - pi/2 below, plus a bounded periodic part.
    """
    a, bb = math.pi * xi / P, math.pi * ym / P
    re, im = math.sin(a) * math.cosh(bb), math.cos(a) * math.sinh(bb)
    lin = (math.pi / 2 - a) if ym > 0 else (a - math.pi / 2)
    theta = lin + _wrap(math.atan2(im, re) - lin)
    far = math.log(math.cosh(bb) ** 2)
    ux = A / (2 * math.pi) * theta
    uy = -A / (2 * math.pi) * KAPPA * (math.log(re * re + im * im) - far)
    return ux, uy


def row_y(side: int, k: int) -> float:
    """Math y (up) of row k on side +1 (above) / -1 (below) the slip plane."""
    return side * (k + 0.5) * A


def drift(side: int) -> float:
    """Rigid slide per step that makes every track close after one cycle."""
    return -side * A / (2 * N)


def track(side: int, k: int, s: float, j: int = 0) -> tuple[float, float]:
    """SVG position of the atom in column j, row k, when the core has moved s steps."""
    ym = row_y(side, k)
    ux, uy = field((j - s) * A, ym)
    return X0 + j * A + ux + drift(side) * s, YS - (ym + uy)


def offset(side: int, j: int) -> float:
    """Column j replays column 0's track j steps late, shifted by this much."""
    return j * (A + drift(side))


# How the lattice is animated without one animation per atom:
#
# The picture after one step equals the picture before it, shifted right by
# (A + drift) with every column index moved by one. So each half of the crystal is
# one path per row (atoms drawn as markers on its vertices) plus one path holding
# every column. `d` animates through a single step and repeats; a discrete
# translate adds one shift per step and resets after N steps, where the loop
# closes exactly (see drift()).

J = range(-17, 16)  # enough columns to cover the window across all N shifts
SIGMAS = [0.0, DWELL] + [DWELL + (1 - DWELL) * q for q in _Q] + [1.0]
SIGMA_S = [0.0, 0.0] + [ease(q) for q in _Q] + [1.0]


def row_d(side, k, s):
    return pts_d([track(side, k, s, j) for j in J])


def cols_d(side, s):
    parts = []
    for j in J:
        pts = [track(side, k, s, j) for k in range(ROWS)]
        parts.append(pts_d(pts))
    return " ".join(parts)


def anim_d(fn, still: bool) -> str:
    """A path whose d runs through one step. fn(s) -> d."""
    if still:
        return f'<path d="{fn(0.0)}"/>'
    values = ";".join(fn(s) for s in SIGMA_S)
    times = ";".join(fmt(t / 1) if t in (0, 1) else f"{t:.3f}" for t in SIGMAS)
    return (
        f'<path d="{fn(0.0)}"><animate attributeName="d" dur="{fmt(STEP)}s" '
        f'repeatCount="indefinite" calcMode="linear" keyTimes="{times}" values="{values}"/></path>'
    )


def shifter(side: int, still: bool) -> str:
    if still:
        return ""
    step = A + drift(side)
    vals = ";".join(f"{fmt(i * step)} 0" for i in range(N))
    times = ";".join(f"{i / N:.4f}" for i in range(N))
    return (
        f'<animateTransform attributeName="transform" type="translate" dur="{fmt(T)}s" '
        f'repeatCount="indefinite" calcMode="discrete" keyTimes="{times}" values="{vals}"/>'
    )


def lattice(still: bool) -> tuple[str, str]:
    """(rows group, columns group) for both halves."""
    rows, cols = [], []
    s0 = STILL_AT if still else 0.0
    for side in (1, -1):
        r = "".join(anim_d(lambda s, k=k: row_d(side, k, s + s0), still) for k in range(ROWS))
        c = anim_d(lambda s: cols_d(side, s + s0), still)
        rows.append(f"<g>{shifter(side, still)}{r}</g>")
        cols.append(f"<g>{shifter(side, still)}{c}</g>")
    return "".join(rows), "".join(cols)


STILL_AT = 7.0  # reduced-motion frame: the core sits mid-window


def core_motion(still: bool) -> str:
    if still:
        return ""
    vals = ";".join(f"{fmt(s * A)} 0" for _, s in STOPS)
    times = ";".join(f"{t / T:.4f}" for t, _ in STOPS)
    return (
        f'<animateTransform attributeName="transform" type="translate" dur="{fmt(T)}s" '
        f'repeatCount="indefinite" calcMode="linear" keyTimes="{times}" values="{vals}"/>'
    )


TX = 72  # left text margin


def core_glyph(c) -> str:
    """The edge-dislocation symbol, drawn at the origin."""
    return (
        f'<circle r="15" fill="{c["bronze"]}" opacity="{c["glow"] * 0.45}" filter="url(#soft)"/>'
        f'<path d="M-11 9 H11 M0 9 V-11" stroke="{c["bronze"]}" stroke-width="4" '
        'stroke-linecap="round" fill="none"/>'
    )


def hero(mode: str, still: bool) -> str:
    c = PALETTES[mode]
    rows, cols = lattice(still)
    wx0, wx1 = WIN
    top, bot = YS - ROWS * A - 6, YS + ROWS * A + 6

    name = ST.path("IronMurphy", TX - 4, 194, 94, "archivo", {"wght": 820, "wdth": 108}, tracking=-2.5)
    role = ST.path("AI agent and full-stack engineer", TX, 246, 26, "plex", {"wght": 420, "wdth": 100})
    motto = ST.path("Small steps every day.", TX, 318, 26, "plex", {"wght": 560, "wdth": 100})
    cap = "An edge dislocation: metal bends one row of atoms at a time."
    capd = ST.path(cap, (wx0 + wx1) / 2, bot + 40, 20, "plex", {"wght": 400}, anchor="middle")

    heat = "".join(
        f'<g transform="translate({fmt(X0 + off + (STILL_AT * A if still else 0))} {fmt(YS)})"><g>{core_motion(still)}'
        f'<ellipse rx="{fmt(1.25 * A)}" ry="{fmt(2.9 * A)}" cy="-{fmt(2.1 * A)}" fill="url(#hg)"/></g></g>'
        for off in (0.0, -P)
    )
    cores = "".join(
        f'<g transform="translate({fmt(X0 + off + (STILL_AT * A if still else 0))} {fmt(YS)})"><g>{core_motion(still)}{core_glyph(c)}</g></g>'
        for off in (0.0, -P)
    )
    stops = (
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="0.14" stop-color="#fff"/><stop offset="0.86" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
    )
    # Temper colours as a thin rule under the name: straw -> bronze -> purple -> blue.
    temper = "".join(
        f'<rect x="{fmt(TX + i * 38)}" y="344" width="36" height="6" rx="1" fill="{c[k]}"/>'
        for i, k in enumerate(("straw", "bronze", "purple", "blue"))
    )
    title = "IronMurphy. AI agent and full-stack engineer. Small steps every day."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>
<filter id="soft" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="5"/></filter>
<linearGradient id="fade" x1="{wx0}" x2="{wx1}" gradientUnits="userSpaceOnUse">{stops}</linearGradient>
<mask id="win" maskUnits="userSpaceOnUse"><rect x="{wx0}" y="{top}" width="{wx1 - wx0}" height="{bot - top}" fill="url(#fade)"/></mask>
<radialGradient id="hg"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="heat" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">{heat}</mask>
<marker id="atom" viewBox="-6 -6 12 12" markerWidth="12" markerHeight="12" markerUnits="userSpaceOnUse">
<circle r="4.6" fill="{c["atom"]}"/></marker>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="{c["ground"]}"/>
<g mask="url(#win)">
<g fill="none" stroke="{c["plane"]}" stroke-width="1.6" stroke-linejoin="round">{cols}</g>
<g mask="url(#heat)" fill="none" stroke="{c["bronze"]}" stroke-width="2.4" stroke-linejoin="round">{cols}</g>
<g fill="none" stroke="{c["plane"]}" stroke-width="1.6" stroke-linejoin="round" marker-start="url(#atom)" marker-mid="url(#atom)" marker-end="url(#atom)">{rows}</g>
<path d="M{wx0} {YS} H{wx1}" stroke="{c["straw"]}" stroke-width="1.6" stroke-dasharray="2 6" stroke-linecap="round"/>
{cores}
</g>
<g fill="{c["text"]}"><path d="{name}"/></g>
<g fill="{c["muted"]}"><path d="{role}"/></g>
<g fill="{c["text"]}"><path d="{motto}"/></g>
<g fill="{c["muted"]}"><path d="{capd}"/></g>
{temper}
</svg>
"""


# ------------------------------------------------------------------ project figures


def disc(attr: str, loop: float, initial: str, changes: list[tuple[float, str]]) -> str:
    """A discrete SMIL timeline: `initial` at t=0, then each (t, value) in turn."""
    times = "0;" + ";".join(f"{t / loop:.4f}" for t, _ in changes)
    values = ";".join([initial] + [v for _, v in changes])
    return (
        f'<animate attributeName="{attr}" dur="{fmt(loop)}s" repeatCount="indefinite" '
        f'calcMode="discrete" keyTimes="{times}" values="{values}"/>'
    )


def travel(path_id: str, loop: float, t0: float, t1: float) -> str:
    """Move along #path_id between t0 and t1 of each loop, resting at the ends."""
    k = f"0;{t0 / loop:.4f};{t1 / loop:.4f};1"
    return (
        f'<animateMotion dur="{fmt(loop)}s" repeatCount="indefinite" calcMode="linear" '
        f'keyTimes="{k}" keyPoints="0;0;1;1"><mpath href="#{path_id}"/></animateMotion>'
    )


def frame(w, h, c, title, body) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{title}"><title>{title}</title>'
        f'<rect width="{w}" height="{h}" rx="14" fill="{c["ground"]}"/>{body}</svg>\n'
    )


CHANNELS = ["Browser", "Feishu", "Telegram", "QQ", "DingTalk", "WeChat", "Discord", "WhatsApp"]


def fig_commerce(mode: str, still: bool) -> str:
    c = PALETTES[mode]
    w, h = 900, 300
    D = 1.5  # seconds per message
    loop = D * len(CHANNELS)
    box = (380, 112, 250, 76)
    bx, by, bw, bh = box
    cy = by + bh / 2
    outs = [("host", cy - 44), ("Docker sandbox", cy + 44)]
    ox = 730

    parts = []
    for i, ch in enumerate(CHANNELS):
        y = 38 + i * 32
        d = f"M200 {y} C300 {y} 290 {cy} {bx} {cy}"
        parts.append(f'<path id="in{i}" d="{d}" fill="none" stroke="{c["plane"]}" stroke-width="1.5"/>')
        glyph = ST.path(ch, 184, y + 6, 17, "plex", {"wght": 450}, anchor="end")
        t0 = i * D
        anim = "" if still else disc("fill", loop, c["muted"], [(t0, c["straw"]), (t0 + D, c["muted"])][: 2 if i < len(CHANNELS) - 1 else 1])
        parts.append(f'<path fill="{c["muted"]}" d="{glyph}">{anim}</path>')
    for j, (label, y) in enumerate(outs):
        d = f"M{bx + bw} {cy} C{bx + bw + 50} {cy} {ox - 50} {y} {ox} {y}"
        parts.append(f'<path id="out{j}" d="{d}" fill="none" stroke="{c["plane"]}" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{ox}" cy="{fmt(y)}" r="4" fill="{c["atom"]}"/>')
        parts.append(f'<path fill="{c["text"]}" d="{ST.path(label, ox + 16, y + 6, 17, "plex", {"wght": 450})}"/>')

    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="{c["ground"]}" '
        f'stroke="{c["straw"]}" stroke-width="1.6"/>'
    )
    parts.append(f'<path fill="{c["text"]}" d="{ST.path("CommerceAgent", bx + bw / 2, cy - 2, 23, "archivo", {"wght": 700, "wdth": 104}, anchor="middle")}"/>')
    parts.append(f'<path fill="{c["muted"]}" d="{ST.path("one agent, one workspace", bx + bw / 2, cy + 22, 14.5, "plex", {"wght": 400}, anchor="middle")}"/>')

    if not still:
        for i in range(len(CHANNELS)):
            t0 = i * D
            j = i % 2
            dot = f'<circle r="5" fill="{c["straw"]}" opacity="0">'
            show = disc("opacity", loop, "0", [(t0 + 0.05, "1"), (t0 + 0.75, "0")])
            parts.append(f"{dot}{show}{travel(f'in{i}', loop, t0 + 0.05, t0 + 0.75)}</circle>")
            dot = f'<circle r="5" fill="{c["blue"]}" opacity="0">'
            show = disc("opacity", loop, "0", [(t0 + 0.8, "1"), (t0 + 1.35, "0")])
            parts.append(f"{dot}{show}{travel(f'out{j}', loop, t0 + 0.8, t0 + 1.35)}</circle>")

    title = "CommerceAgent: one agent reached from the browser and seven messaging channels, running on the host or in a Docker sandbox."
    return frame(w, h, c, title, "".join(parts))


DOSES = [  # (day, time, taken?)
    ("Mon", "08:00", True), ("Mon", "13:00", True), ("Mon", "20:00", False),
    ("Tue", "08:00", True), ("Tue", "13:00", False), ("Tue", "20:00", False),
    ("Wed", "08:00", False), ("Wed", "13:00", True), ("Wed", "20:00", True),
]


def fig_care(mode: str, still: bool) -> str:
    c = PALETTES[mode]
    w, h = 900, 300
    x0, gap, y = 118, 84, 168
    per, hold = 1.0, 3.0
    loop = per * len(DOSES) + hold
    reset = loop - 0.4
    xs = [x0 + i * gap for i in range(len(DOSES))]
    parts = []

    # day rules and labels
    for d in range(3):
        a, b = xs[d * 3] - 30, xs[d * 3 + 2] + 30
        parts.append(f'<path d="M{a} 222 H{b}" stroke="{c["plane"]}" stroke-width="1.5"/>')
        parts.append(f'<path fill="{c["text"]}" d="{ST.path(DOSES[d * 3][0], (a + b) / 2, 252, 17, "plex", {"wght": 560}, anchor="middle")}"/>')
    parts.append(f'<path d="M{xs[0] - 40} {y} H{xs[-1] + 40}" stroke="{c["plane"]}" stroke-width="1.5"/>')

    streak_done = None
    streak = 0
    for i, (x, (_, tm, ok)) in enumerate(zip(xs, DOSES)):
        t = i * per + 0.5
        parts.append(f'<path fill="{c["muted"]}" d="{ST.path(tm, x, 212, 13.5, "plex", {"wght": 400}, anchor="middle")}"/>')
        fill = c["blue"] if ok else c["ground"]
        stroke = c["blue"] if ok else c["bronze"]
        idle = (c["ground"], c["plane"])
        if still:
            a1 = a2 = ""
            f0, s0 = fill, stroke
        else:
            f0, s0 = idle
            a1 = disc("fill", loop, idle[0], [(t, fill), (reset, idle[0])])
            a2 = disc("stroke", loop, idle[1], [(t, stroke), (reset, idle[1])])
        parts.append(f'<circle cx="{x}" cy="{y}" r="11" fill="{f0}" stroke="{s0}" stroke-width="2.4">{a1}{a2}</circle>')
        streak = 0 if ok else streak + 1
        if streak == 3 and streak_done is None:
            streak_done = (i, t)

    # the alert: a bracket over the three misses and a line to the family
    i, t = streak_done
    a, b = xs[i - 2] - 20, xs[i] + 20
    alert = [
        f'<path d="M{a} 138 V126 H{b} V138" fill="none" stroke="{c["bronze"]}" stroke-width="2" stroke-linejoin="round"/>',
        f'<path fill="{c["bronze"]}" d="{ST.path("Third miss in a row: family notified", (a + b) / 2, 108, 16, "plex", {"wght": 560}, anchor="middle")}"/>',
    ]
    op = "1" if still else "0"
    anim = "" if still else disc("opacity", loop, "0", [(t + 0.15, "1"), (reset, "0")])
    parts.append(f'<g opacity="{op}">{anim}{"".join(alert)}</g>')

    # the scheduled pass sweeping the day, one dose per tick
    if not still:
        k = f"0;{(per * len(DOSES)) / loop:.4f};1"
        sweep = (
            f'<animateTransform attributeName="transform" type="translate" dur="{fmt(loop)}s" '
            f'repeatCount="indefinite" keyTimes="{k}" values="0 0;{fmt(len(DOSES) * gap)} 0;{fmt(len(DOSES) * gap)} 0"/>'
        )
        fade = disc("opacity", loop, "1", [(per * len(DOSES), "0")])
        parts.append(
            f'<g><path d="M{x0 - gap / 2} 148 V188" stroke="{c["straw"]}" stroke-width="2.4" stroke-linecap="round">{fade}</path>{sweep}</g>'
        )

    legend = [(c["blue"], c["blue"], "taken"), (c["ground"], c["bronze"], "missed, recorded automatically")]
    lx = 64
    for f, s, label in legend:
        parts.append(f'<circle cx="{lx}" cy="46" r="7" fill="{f}" stroke="{s}" stroke-width="2"/>')
        parts.append(f'<path fill="{c["muted"]}" d="{ST.path(label, lx + 16, 51, 15, "plex", {"wght": 400})}"/>')
        lx += 32 + ST.measure(label, 15, "plex", {"wght": 400}) + 18
    parts.append(f'<path fill="{c["text"]}" d="{ST.path("康养日记", w - 64, 52, 22, "plex", {"wght": 600}, anchor="end")}"/>')

    title = "康养日记: nine scheduled doses over three days; the third missed dose in a row notifies the family."
    return frame(w, h, c, title, "".join(parts))


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    jobs = {"hero": hero, "commerceagent": fig_commerce, "health": fig_care}
    for name, fn in jobs.items():
        for mode in PALETTES:
            for still in (False, True):
                out = ASSETS / f"{name}-{mode}{'-still' if still else ''}.svg"
                out.write_text(fn(mode, still), encoding="utf-8")
                print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
