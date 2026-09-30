"""Shape text with HarfBuzz and emit outlined SVG paths.

GitHub serves README images through a proxy that blocks web fonts, so every
glyph in the generated SVGs is converted to a <path>. Fonts live in
design/fonts/ and are not committed.
"""

from __future__ import annotations

from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONTS = {
    "archivo": FONT_DIR / "Archivo.ttf",
    "plex": FONT_DIR / "Plex.ttf",
    "sc": FONT_DIR / "NotoSC.ttf",
}
_cache: dict = {}


def _font(key: str, axes: dict):
    k = (key, tuple(sorted(axes.items())))
    if k not in _cache:
        face = hb.Face(hb.Blob.from_file_path(str(FONTS[key])))
        font = hb.Font(face)
        if axes:
            font.set_variations(axes)
        _cache[k] = (font, face.upem)
    return _cache[k]


def _runs(text: str, key: str):
    """Split text into runs; CJK characters fall back to Noto Sans SC."""
    out: list[list] = []
    for ch in text:
        k = "sc" if ord(ch) > 0x2E7F else key
        if out and out[-1][0] == k:
            out[-1][1] += ch
        else:
            out.append([k, ch])
    return out


def _layout(text, size, key, axes, tracking):
    glyphs, x = [], 0.0
    for k, chunk in _runs(text, key):
        ax = axes if k == key else {"wght": axes.get("wght", 400)}
        font, upem = _font(k, ax)
        buf = hb.Buffer()
        buf.add_str(chunk)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True})
        scale = size / upem
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            glyphs.append((font, info.codepoint, x + pos.x_offset * scale, pos.y_offset * scale, scale))
            x += pos.x_advance * scale + tracking
    return glyphs, x - (tracking if glyphs else 0)


def measure(text, size, key="plex", axes=None, tracking=0.0) -> float:
    return _layout(text, size, key, axes or {}, tracking)[1]


def path(text, x, y, size, key="plex", axes=None, tracking=0.0, anchor="start") -> str:
    """Return the `d` attribute for `text` with its baseline at (x, y)."""
    glyphs, width = _layout(text, size, key, axes or {}, tracking)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    pen = SVGPathPen(None, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    for font, gid, gx, gy, s in glyphs:
        font.draw_glyph_with_pen(gid, TransformPen(pen, (s, 0, 0, -s, x + gx, y - gy)))
    return pen.getCommands()
