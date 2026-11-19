#!/usr/bin/env python3
"""Deterministic newspaper front page for Thursday 19 November 2026.

Draws a 1024x1024 PNG front page that sums up the day's world news using
PIL shapes and the DejaVu fonts only.  The layout is fully fixed -- no
randomness, no clocks, no network -- so every run produces byte-identical
output.  Run it once to regenerate tools/../entry.png (or pass an output
path as argv[1]).

Usage:
    python3 tools/generate_image.py [output.png]
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# palette: warm newsprint paper, near-black ink, red and blue accents
# ---------------------------------------------------------------------------
PAPER = (246, 240, 227)     # warm off-white page
INK = (28, 26, 24)          # near-black body ink
RED = (156, 30, 24)         # masthead rule, section labels, ticker "ALSO"
BLUE = (28, 56, 104)        # panel headers (headlines, rules)
HAIR = (205, 195, 175)      # hairline panel frames
TICKBG = (233, 225, 207)    # ticker strip backing

# ---------------------------------------------------------------------------
# fonts
# ---------------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def load_font(size, bold=True):
    """Load a DejaVu face at the given size; fall back to PIL's default."""
    path = FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size)

# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------
SIZE = 1024
MARGIN = 40
CONTENT = SIZE - 2 * MARGIN                 # 944 px usable width
GUTTER = 19
PANEL_W = (CONTENT - 2 * GUTTER) // 3       # 302 px per panel
COLS = [MARGIN + i * (PANEL_W + GUTTER) for i in range(3)]
MASTHEAD_TOP = 40
TICKER_H = 58
ICON_W, ICON_H = 52, 40
TEXT_W = PANEL_W - 78                       # 224 px, panel width minus 78
TEXT_LEFT = 14

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------
def tw(draw, s, font):
    """Ink width of s in the given font."""
    bb = draw.textbbox((0, 0), s, font=font)
    return bb[2] - bb[0]


def fit_headline(draw, s):
    """Largest bold font (26..20px) whose one-line width fits TEXT_W."""
    for size in (26, 24, 22, 20):
        f = load_font(size, bold=True)
        if tw(draw, s, f) <= TEXT_W:
            return f
    raise RuntimeError("headline too wide: %r" % s)


def wrap_lines(draw, s, font, max_w):
    """Greedy word wrap of s into lines no wider than max_w."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if tw(draw, trial, font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------------------
# icon painters: pure PIL shapes in a 52x40 box at (x, y) -- no photos
# ---------------------------------------------------------------------------
def icon_iran(d, x, y):
    """Missile dart + red burst over a blue gulf arc."""
    d.arc([x + 4, y + 26, x + 24, y + 40], 180, 360, fill=BLUE, width=2)
    cx, cy, r = x + 13, y + 14, 11
    for k in range(8):
        a = math.radians(k * 45)
        d.line([cx, cy,
                cx + r * math.cos(a), cy + r * math.sin(a)],
               fill=RED, width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    d.polygon([(x + 22, y + 16), (x + 48, y + 38), (x + 18, y + 34)], fill=INK)


def icon_gta(d, x, y):
    """Dusk sky band, moon, 'VI' and a city skyline."""
    d.rectangle([x, y, x + ICON_W, y + 13], fill=BLUE)
    d.ellipse([x + 5, y + 4, x + 11, y + 10], fill=PAPER)
    d.text((x + 28, y), "VI", font=load_font(16, bold=True), fill=RED)
    for bx, bw, bh in ((2, 10, 11), (13, 11, 18), (25, 11, 13), (37, 15, 21)):
        d.rectangle([x + bx, y + ICON_H - bh, x + bx + bw, y + ICON_H], fill=INK)


def icon_summit(d, x, y):
    """Three flag poles with red, blue and ink flags."""
    for fx, col in ((6, RED), (22, BLUE), (38, INK)):
        d.line([x + fx, y + 12, x + fx, y + ICON_H - 2], fill=INK, width=2)
        d.rectangle([x + fx, y + 4, x + fx + 13, y + 12], fill=col)


def icon_capitol(d, x, y):
    """US Capitol: dome, base and columns."""
    d.arc([x + 15, y + 2, x + 39, y + 26], 180, 360, fill=INK, width=2)
    d.rectangle([x + 8, y + 24, x + 46, y + 38], outline=INK, width=2)
    for cx in (16, 24, 32, 40):
        d.line([x + cx, y + 24, x + cx, y + 38], fill=INK, width=1)


def icon_eu(d, x, y):
    """Twelve-star circle above a red '45bn'; the two never touch."""
    cx, cy, r = x + 26, y + 11, 9
    for k in range(12):
        a = math.radians(k * 30)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=BLUE)
    f = load_font(15, bold=True)
    t = "45bn"
    tb = d.textbbox((0, 0), t, font=f)
    ty = y + 24
    d.text((x + (ICON_W - (tb[2] - tb[0])) // 2 - tb[0], ty), t, font=f, fill=RED)
    if cy + r + 3 >= ty + tb[1]:
        raise RuntimeError("eu icon text overlaps stars")
    if ty + tb[3] > y + ICON_H:
        raise RuntimeError("eu icon text leaves its box")


def icon_chip(d, x, y):
    """Integrated circuit: body, die and pins on four sides."""
    d.rectangle([x + 13, y + 7, x + 39, y + 33], outline=INK, width=2)
    d.rectangle([x + 20, y + 14, x + 32, y + 26], fill=INK)
    for px in (16, 26, 36):
        d.line([x + px, y + 7, x + px, y + 3], fill=INK, width=2)
        d.line([x + px, y + 33, x + px, y + 37], fill=INK, width=2)
    for py in (11, 21, 31):
        d.line([x + 13, y + py, x + 9, y + py], fill=INK, width=2)
        d.line([x + 39, y + py, x + 43, y + py], fill=INK, width=2)


# ---------------------------------------------------------------------------
# large illustration band painters: big PIL-shape drawings filling a box
# (x, y, x + w, y + h) in the lower part of each panel -- no faces, no photos
# ---------------------------------------------------------------------------
def big_iran(d, x, y, w, h):
    """Big red burst and ink missile over a blue gulf arc."""
    d.arc([x + 10, y + h - 70, x + 140, y + h], 180, 360, fill=BLUE, width=4)
    cx, cy, r = x + 78, y + 60, 44
    for k in range(8):
        a = math.radians(k * 45)
        d.line([cx, cy,
                cx + r * math.cos(a), cy + r * math.sin(a)],
               fill=RED, width=6)
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=RED)
    d.polygon([(x + 128, y + 55), (x + w - 18, y + h - 18), (x + 105, y + h - 30)],
              fill=INK)


def big_gta(d, x, y, w, h):
    """Dusk sky band, moon, 'VI' and a tall city skyline."""
    d.rectangle([x, y, x + w, y + 50], fill=BLUE)
    d.ellipse([x + 42, y + 14, x + 66, y + 38], fill=PAPER)
    d.text((x + w - 104, y + 3), "VI", font=load_font(52, bold=True), fill=RED)
    for bx, bh in ((2, 45), (26, 80), (50, 55), (74, 100), (98, 70),
                   (122, 90), (146, 60), (170, 110), (196, 80), (222, 95),
                   (248, 65)):
        d.rectangle([x + bx, y + h - bh, x + bx + 22, y + h], fill=INK)


def big_summit(d, x, y, w, h):
    """Three big flags on poles over a ground line."""
    for p, col in ((55, RED), (137, BLUE), (219, INK)):
        d.rectangle([x + p, y + 10, x + p + 52, y + 42], fill=col)
        d.line([x + p, y + 42, x + p, y + h - 20], fill=INK, width=4)
    d.line([x + 18, y + h - 20, x + w - 18, y + h - 20], fill=INK, width=3)


def big_capitol(d, x, y, w, h):
    """US Capitol: big dome, base, columns and steps."""
    d.arc([x + 92, y + 10, x + 182, y + 98], 180, 360, fill=INK, width=5)
    d.rectangle([x + 48, y + 94, x + 226, y + 160], outline=INK, width=5)
    for c in (70, 94, 118, 142, 166, 190, 208):
        d.line([x + c, y + 94, x + c, y + 160], fill=INK, width=2)
    d.rectangle([x + 32, y + 160, x + 242, y + 174], outline=INK, width=4)
    d.rectangle([x + 20, y + 174, x + 254, y + 188], outline=INK, width=4)


def big_eu(d, x, y, w, h):
    """Big twelve-star circle with a large '45bn' below it."""
    cx, cy, r = x + w // 2, y + 70, 52
    for k in range(12):
        a = math.radians(k * 30)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=BLUE)
    f = load_font(44, bold=True)
    t = "45bn"
    tb = d.textbbox((0, 0), t, font=f)
    ty = y + h - (tb[3] - tb[1]) - 10
    d.text((x + (w - (tb[2] - tb[0])) // 2 - tb[0], ty), t, font=f, fill=RED)
    if cy + r + 6 >= ty + tb[1]:
        raise RuntimeError("big eu text overlaps stars")


def big_chip(d, x, y, w, h):
    """Large integrated circuit with pins on all four sides."""
    d.rectangle([x + 55, y + 30, x + w - 55, y + h - 35], outline=INK, width=6)
    d.rectangle([x + 100, y + 72, x + 180, y + 142], fill=INK)
    for px in (80, 115, 150, 185):
        d.line([x + px, y + 30, x + px, y + 10], fill=INK, width=4)
        d.line([x + px, y + h - 35, x + px, y + h - 8], fill=INK, width=4)
    for py in (55, 90, 125):
        d.line([x + 55, y + py, x + 30, y + py], fill=INK, width=4)
        d.line([x + w - 55, y + py, x + w - 30, y + py], fill=INK, width=4)


# ---------------------------------------------------------------------------
# panel painter: section label, one-line headline, summary, icon -- checked
# ---------------------------------------------------------------------------
def draw_panel(d, x, y, section, headline, summary, icon, big):
    d.rectangle([x, y, x + PANEL_W, y + PANEL_H], outline=HAIR, width=1)
    ix, iy = x + PANEL_W - 8 - ICON_W, y + 8
    icon(d, ix, iy)
    icon_box = (ix, iy, ix + ICON_W, iy + ICON_H)
    spans = []

    fl = load_font(16, bold=True)
    d.text((x + TEXT_LEFT, y + 12), section, font=fl, fill=RED)
    spans.append((section, fl, x + TEXT_LEFT, y + 12))

    fh = fit_headline(d, headline)
    hy = y + 12 + 22
    d.text((x + TEXT_LEFT, hy), headline, font=fh, fill=BLUE)
    spans.append((headline, fh, x + TEXT_LEFT, hy))
    hb = d.textbbox((x + TEXT_LEFT, hy), headline, font=fh)

    rule_y = hb[3] + 5
    d.line([x + TEXT_LEFT, rule_y, hb[2] + 3, rule_y], fill=BLUE, width=2)

    fs = load_font(16, bold=False)
    sy = rule_y + 9
    lines = wrap_lines(d, summary, fs, TEXT_W)
    if len(lines) > 3:
        raise RuntimeError("summary wraps to %d lines: %r" % (len(lines), summary))
    for ln in lines:
        d.text((x + TEXT_LEFT, sy), ln, font=fs, fill=INK)
        spans.append((ln, fs, x + TEXT_LEFT, sy))
        sy += 21

    # large illustration band fills the lower part of the panel
    divider = sy + 6
    band_top = divider + 8
    d.line([x + TEXT_LEFT, divider, x + PANEL_W - TEXT_LEFT, divider],
           fill=HAIR, width=1)
    big(d, x + TEXT_LEFT, band_top, PANEL_W - 2 * TEXT_LEFT,
        y + PANEL_H - 10 - band_top)

    for s, f, tx, ty in spans:
        bb = d.textbbox((tx, ty), s, font=f)
        if bb[2] > x + PANEL_W - 6 or bb[3] > y + PANEL_H - 6:
            raise RuntimeError("text overflows panel: %r" % s)
        if not (bb[2] <= icon_box[0] or bb[0] >= icon_box[2] or
                bb[3] <= icon_box[1] or bb[1] >= icon_box[3]):
            raise RuntimeError("text crosses icon box: %r" % s)


# ---------------------------------------------------------------------------
# masthead and ticker
# ---------------------------------------------------------------------------
def draw_masthead(d):
    f = load_font(78, bold=True)
    s = "THE WORLD TODAY"
    bb = d.textbbox((0, 0), s, font=f)
    mx = (SIZE - (bb[2] - bb[0])) // 2 - bb[0]
    d.text((mx, MASTHEAD_TOP), s, font=f, fill=INK)

    df = load_font(24, bold=False)
    ds = "THURSDAY, 19 NOVEMBER 2026"
    db = d.textbbox((0, 0), ds, font=df)
    dy = MASTHEAD_TOP + bb[3] + 18 - db[1]
    dx = (SIZE - (db[2] - db[0])) // 2 - db[0]
    d.text((dx, dy), ds, font=df, fill=INK)

    r1y = dy + db[3] + 6
    d.rectangle([MARGIN, r1y, SIZE - MARGIN, r1y + 4], fill=RED)
    d.rectangle([MARGIN, r1y + 7, SIZE - MARGIN, r1y + 9], fill=INK)

    m_box = (mx + bb[0], MASTHEAD_TOP + bb[1], mx + bb[2], MASTHEAD_TOP + bb[3])
    d_box = (dx + db[0], dy + db[1], dx + db[2], dy + db[3])
    if m_box[3] >= d_box[1]:
        raise RuntimeError("masthead and dateline overlap")
    if d_box[3] >= r1y:
        raise RuntimeError("dateline and rule overlap")
    return r1y + 9


def draw_ticker(d):
    top = SIZE - MARGIN - TICKER_H
    d.rectangle([MARGIN, top, SIZE - MARGIN, SIZE - MARGIN], fill=TICKBG)
    d.rectangle([MARGIN, top, SIZE - MARGIN, top + 3], fill=RED)
    fb = load_font(15, bold=True)
    f = load_font(15, bold=False)
    sep = "  \u2022  "
    segs = [
        "Voyager 1 reaches one light-day from Earth",
        "Cyclone Akvan nears India's coast between Machilipatnam and Puri",
        "UN's top court rules on Myanmar genocide",
        "Fed minutes: more rate hikes ahead",
    ]
    y0 = top + 3 + 6
    d.text((MARGIN, y0), "ALSO", font=fb, fill=RED)
    x = MARGIN + tw(d, "ALSO", fb) + tw(d, sep, f)
    d.text((x, y0), segs[0] + sep + segs[1], font=f, fill=INK)
    d.text((MARGIN, y0 + 19), segs[2] + sep + segs[3], font=f, fill=INK)

    w1 = tw(d, "ALSO", fb) + tw(d, sep + segs[0] + sep + segs[1], f)
    w2 = tw(d, segs[2] + sep + segs[3], f)
    if w1 > CONTENT or w2 > CONTENT:
        raise RuntimeError("ticker line too wide: %d %d" % (w1, w2))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    global PANEL_H
    im = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(im)
    mast_bottom = draw_masthead(d)
    panel_top = mast_bottom + 22
    PANEL_H = (SIZE - MARGIN - TICKER_H - 18 - GUTTER - panel_top) // 2
    rows = [panel_top, panel_top + PANEL_H + GUTTER]

    panels = [
        ("MIDDLE EAST", "IRAN WAR WIDENS",
         "US strikes Iran's Qeshm Island; Iran hits US bases in Kuwait and Bahrain.",
         icon_iran, big_iran),
        ("GAMES", "GTA VI LAUNCHES",
         "After 13 years, GTA VI launches, set in Vice City; 99 out of 100 on Metacritic.",
         icon_gta, big_gta),
        ("DIPLOMACY", "SHENZHEN SUMMIT",
         "Trump, Xi and Putin met in Shenzhen; Trump and Putin met one-on-one.",
         icon_summit, big_summit),
        ("US POLITICS", "JEFFRIES: SPEAKER",
         "Democrats pick Hakeem Jeffries to be the first African-American Speaker.",
         icon_capitol, big_capitol),
        ("EUROPE", "45BN FOR UKRAINE",
         "EU's 45-billion-euro loan to Ukraine is repaid after Russian reparations.",
         icon_eu, big_eu),
        ("TECH", "NVIDIA: NEW CEO",
         "Jensen Huang resigned; CFO Colette Kress is interim CEO.",
         icon_chip, big_chip),
    ]
    for i, (sec, head, summ, icon, big) in enumerate(panels):
        draw_panel(d, COLS[i % 3], rows[i // 3], sec, head, summ, icon, big)

    draw_ticker(d)

    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "entry.png")
    im.save(out, "PNG")
    print("wrote %s" % out)


if __name__ == "__main__":
    main()