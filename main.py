#!/usr/bin/env python3
"""THE WORLD TODAY — a one-page newspaper front page for Saturday 21 Nov 2026.

Pure-stdlib Python. Draws a 1024x1024 PNG with its own tiny rasteriser
(rectangles, lines, discs, polygons, starbursts) and its own 5x7 bitmap
letterforms, then encodes the PNG by hand (zlib + CRC, no Pillow).

Stories on the page, all reported on 21 November 2026:
  1. Russian missiles and a drone came down inside Poland during a huge
     overnight attack on Ukraine; Warsaw called it a deliberate
     provocation and NATO called it a grave violation of allied airspace.
  2. Britain and the EU signed their biggest post-Brexit deal: food
     checks scrapped, carbon markets linked, 100,000 youth visas each
     way, Britain back in Erasmus.
  3. A magnitude 6.8 earthquake struck Junin in central Peru; tremors
     were felt 320 km away in Lima. No casualties were reported.
  4. The International Court of Justice ruled Myanmar's forces committed
     state-sponsored genocide against the Rohingya.
  Plus a markets strip: US stocks fell about 3.7% and the S&P 500 entered
  correction territory, and COP31 climate talks entered their final stage.

Deterministic: fixed text, fixed geometry, fixed zlib level, no clock,
no randomness, no network. Two runs write identical bytes.
"""

import binascii
import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)   # warm newsprint cream
INK = (24, 24, 22)        # near-black print ink
NAVY = (20, 38, 74)       # masthead band
NAVY_DEEP = (12, 24, 52)
NAVY_MID = (30, 54, 96)
GOLD = (198, 158, 62)
RED = (178, 32, 44)       # kickers and alert accents
RED_DARK = (140, 20, 30)
GREY = (105, 100, 88)
LIGHT_GREY = (214, 208, 192)
SKY_TOP = (16, 30, 64)
SKY_LOW = (52, 84, 138)
HILL = (38, 74, 52)
HILL_DARK = (28, 56, 40)
WHITE = (245, 244, 238)
CREAM = (238, 228, 200)
ORANGE = (232, 116, 30)
YELLOW = (244, 196, 66)
FLAME = (214, 64, 28)
BLUE_FLAG = (28, 56, 140)
GREEN_LINE = (46, 120, 70)

# ------------------------------------------------------------- 5x7 letters
# Each glyph is seven rows of five bits, "1" = ink. Drawn from scratch
# in this file; every letter is hand-plotted, not copied from a font.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    # Em dash and bullet are written out as their own glyphs.
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}


def glyph_of(ch):
    """Return the 5x7 bitmap for one character (upper-cased first)."""
    return GLYPHS.get(ch.upper(), GLYPHS[" "])


def text_width(text, scale):
    """Pixel width of text at a given scale (6 px advance per glyph)."""
    return len(text) * 6 * scale


# ------------------------------------------------------------------- canvas
class Canvas:
    """A plain RGB raster: one bytearray, origin top-left."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def put(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = col[0]
            self.px[i + 1] = col[1]
            self.px[i + 2] = col[2]

    def fill_rect(self, x, y, w, h, col):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = col
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            span = (x1 - x0) * 3
            self.px[base:base + span] = bytes((r, g, b)) * (x1 - x0)

    def rect(self, x, y, w, h, col, t=1):
        self.fill_rect(x, y, w, t, col)
        self.fill_rect(x, y + h - t, w, t, col)
        self.fill_rect(x, y, t, h, col)
        self.fill_rect(x + w - t, y, t, h, col)

    def hline(self, x, y, length, col, t=1):
        self.fill_rect(x, y, length, t, col)

    def vline(self, x, y, length, col, t=1):
        self.fill_rect(x, y, t, length, col)

    def line(self, x0, y0, x1, y1, col, t=1):
        """Bresenham line; thick lines are stamped as small discs."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            if t <= 1:
                self.put(x, y, col)
            else:
                self.disc(x, y, t // 2 + 1, col)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, col):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cy + dy, dx * 2 + 1, col)

    def ring(self, cx, cy, r, col, t=2):
        for k in range(t):
            rr = r - k
            if rr <= 0:
                break
            for ang in range(0, 360):
                rad = math.radians(ang)
                self.put(cx + int(rr * math.cos(rad)),
                         cy + int(rr * math.sin(rad)), col)

    def poly(self, pts, col):
        """Scanline-filled polygon from a list of (x, y) vertices."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa = int(math.ceil(xs[k]))
                xb = int(math.floor(xs[k + 1]))
                if xb >= xa:
                    self.hline(xa, y, xb - xa + 1, col)

    def starburst(self, cx, cy, r_out, r_in, spikes, col):
        """A spiky explosion shape: alternating long and short points."""
        pts = []
        total = spikes * 2
        for i in range(total):
            ang = math.pi * i / spikes - math.pi / 2
            r = r_out if i % 2 == 0 else r_in
            pts.append((cx + int(r * math.cos(ang)),
                        cy + int(r * math.sin(ang))))
        self.poly(pts, col)

    # ------------------------------------------------------------ text
    def glyph(self, x, y, ch, scale, col):
        rows = glyph_of(ch)
        for ry in range(7):
            row = rows[ry]
            for rx in range(5):
                if row[rx] == "1":
                    self.fill_rect(x + rx * scale, y + ry * scale,
                                   scale, scale, col)

    def text(self, x, y, s, scale, col):
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, col)
            cx += 6 * scale
        return cx

    def centred(self, cx, y, s, scale, col):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, col)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns a list of lines fitting max_w."""
        lines = []
        for raw in s.split("\n"):
            words = raw.split(" ")
            cur = ""
            for word in words:
                trial = word if not cur else cur + " " + word
                if text_width(trial, scale) <= max_w or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
        return lines

    def para(self, x, y, s, scale, max_w, col, leading=None):
        """Draw a wrapped paragraph; returns the y just below it."""
        if leading is None:
            leading = 7 * scale + 3
        yy = y
        for line in self.wrap(s, scale, max_w):
            self.text(x, yy, line, scale, col)
            yy += leading
        return yy


# -------------------------------------------------------------- illustration
def draw_lead_art(cv, x, y, w, h):
    """Night sky over rolling hills: two missile bursts and their arcs.

    A framed panel. The sky is banded navy, the ground is two overlapping
    hills, and each burst is a layered starburst (red, orange, yellow)
    with a dotted arc tracing the missile's path in from the panel edge.
    """
    cv.rect(x, y, w, h, INK, 3)
    # Banded night sky.
    bands = [(SKY_TOP, 0.0), (NAVY_DEEP, 0.35), (NAVY_MID, 0.7),
             (SKY_LOW, 1.0)]
    for i in range(h):
        f = i / max(1, h - 1)
        top = bands[0][0]
        for j in range(len(bands) - 1):
            if bands[j][1] <= f <= bands[j + 1][1]:
                a = bands[j][0]
                b = bands[j + 1][0]
                t = (f - bands[j][1]) / max(0.001, bands[j + 1][1] - bands[j][1])
                top = tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))
                break
        cv.hline(x + 3, y + 3 + i, w - 6, top)
    # Stars: fixed positions, fixed sizes.
    stars = [(0.08, 0.10, 2), (0.22, 0.06, 1), (0.36, 0.14, 2),
             (0.55, 0.08, 1), (0.70, 0.16, 2), (0.86, 0.07, 1),
             (0.93, 0.22, 2), (0.15, 0.26, 1), (0.47, 0.24, 1),
             (0.64, 0.30, 1), (0.30, 0.34, 1), (0.80, 0.38, 1)]
    for fx, fy, r in stars:
        cv.disc(x + int(fx * w), y + int(fy * h), r, WHITE)
    # Pale moon, upper right.
    cv.disc(x + int(0.84 * w), y + int(0.16 * h), 16, CREAM)
    cv.disc(x + int(0.84 * w) + 6, y + int(0.16 * h) - 4, 13, SKY_LOW)
    # Rolling hills along the bottom.
    ground_y = y + int(0.72 * h)
    cv.poly([(x + 3, y + h - 3), (x + 3, ground_y + 18),
             (x + int(0.30 * w), ground_y - 6),
             (x + int(0.62 * w), ground_y + 14),
             (x + w - 3, ground_y - 2), (x + w - 3, y + h - 3)], HILL_DARK)
    cv.poly([(x + 3, y + h - 3), (x + 3, ground_y + 34),
             (x + int(0.28 * w), ground_y + 10),
             (x + int(0.60 * w), ground_y + 30),
             (x + w - 3, ground_y + 16), (x + w - 3, y + h - 3)], HILL)
    # Missile arcs: dotted quadratic curves ending at each burst.
    def arc(x0, y0, cx, cy, x1, y1, col):
        for k in range(0, 41):
            t = k / 40.0
            px = int((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1)
            py = int((1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1)
            if k % 2 == 0:
                cv.disc(px, py, 2, col)
    bx1 = x + int(0.34 * w)
    by1 = y + int(0.52 * h)
    bx2 = x + int(0.72 * w)
    by2 = y + int(0.44 * h)
    arc(x + 6, y + int(0.30 * h), x + int(0.18 * w), y + int(0.10 * h),
        bx1, by1, WHITE)
    arc(x + w - 6, y + int(0.24 * h), x + int(0.88 * w), y + int(0.08 * h),
        bx2, by2, WHITE)
    # Bursts: layered starbursts, red outside, yellow core.
    for cx, cy, r in ((bx1, by1, 46), (bx2, by2, 38)):
        cv.starburst(cx, cy, r, r // 2, 12, FLAME)
        cv.starburst(cx, cy, int(r * 0.68), int(r * 0.34), 10, ORANGE)
        cv.starburst(cx, cy, int(r * 0.42), int(r * 0.22), 8, YELLOW)
        cv.disc(cx, cy, 7, WHITE)
    # Labels on the sky, with a dark chip behind each so they stay legible.
    def chip(tx, ty, s, scale):
        tw = text_width(s, scale)
        cv.fill_rect(tx - 4, ty - 3, tw + 8, 7 * scale + 6, NAVY_DEEP)
        cv.text(tx, ty, s, scale, WHITE)
    chip(x + 16, y + 14, "POLAND", 2)
    chip(x + int(0.55 * w), y + int(0.60 * h), "UKRAINE", 2)
    # Caption strip pinned to the panel's foot.
    cv.fill_rect(x + 3, y + h - 34, w - 6, 31, NAVY_DEEP)
    cv.text(x + 12, y + h - 26, "MISSILES CROSSED INTO POLAND",
            2, WHITE)


def draw_flags(cv, x, y, w, h):
    """Two small flags side by side: Union Jack (simplified) and EU stars."""
    half = w // 2 - 6
    # Union Jack, simplified: blue field, white diagonals, red cross.
    fx, fy = x, y
    cv.fill_rect(fx, fy, half, h, BLUE_FLAG)
    cv.line(fx, fy, fx + half, fy + h, WHITE, 5)
    cv.line(fx + half, fy, fx, fy + h, WHITE, 5)
    cv.line(fx, fy, fx + half, fy + h, RED, 2)
    cv.line(fx + half, fy, fx, fy + h, RED, 2)
    cv.fill_rect(fx + half // 2 - 5, fy, 10, h, WHITE)
    cv.fill_rect(fx, fy + h // 2 - 5, half, 10, WHITE)
    cv.fill_rect(fx + half // 2 - 3, fy, 6, h, RED)
    cv.fill_rect(fx, fy + h // 2 - 3, half, 6, RED)
    cv.rect(fx, fy, half, h, INK, 2)
    # EU flag: blue field, ring of twelve gold dots.
    ex = x + half + 12
    cv.fill_rect(ex, fy, half, h, BLUE_FLAG)
    ccx, ccy = ex + half // 2, fy + h // 2
    rr = min(half, h) // 2 - 10
    for k in range(12):
        ang = 2 * math.pi * k / 12 - math.pi / 2
        cv.disc(ccx + int(rr * math.cos(ang)),
                ccy + int(rr * math.sin(ang)), 3, YELLOW)
    cv.rect(ex, fy, half, h, INK, 2)


def draw_quake(cv, x, y, w, h):
    """A seismograph trace on graph paper: calm line, then a violent spike."""
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    for gx in range(x + 14, x + w, 16):
        cv.vline(gx, y + 3, h - 6, LIGHT_GREY)
    for gy in range(y + 12, y + h, 16):
        cv.hline(x + 3, gy, w - 6, LIGHT_GREY)
    mid = y + h // 2
    pts = []
    n = 26
    for i in range(n + 1):
        px = x + 6 + int(i * (w - 12) / n)
        if i < 8:
            py = mid + (6 if i % 2 else -6)
        elif i < 15:
            py = mid + (-34 if i % 2 else 36)
        elif i < 20:
            py = mid + (26 if i % 2 else -26)
        else:
            py = mid + (5 if i % 2 else -5)
        pts.append((px, py))
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED_DARK, 3)
    cv.text(x + 8, y + 6, "6.8", 2, RED_DARK)


def draw_market_chart(cv, x, y, w, h):
    """A falling market line: small steps down, then a sharp drop."""
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    pts = [(x + 6, y + 10), (x + int(w * 0.25), y + 16),
           (x + int(w * 0.45), y + 14), (x + int(w * 0.60), y + 30),
           (x + int(w * 0.78), y + 44), (x + w - 8, y + h - 10)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED_DARK, 3)
    for px, py in pts:
        cv.disc(px, py, 3, RED_DARK)
    cv.line(x + 6, y + h - 8, x + w - 6, y + h - 8, GREY, 1)


# -------------------------------------------------------------- page layout
def build():
    cv = Canvas(W, H, PAPER)
    # Double outer frame, the way a broadsheet frames its page.
    cv.rect(14, 14, W - 28, H - 28, INK, 3)
    cv.rect(22, 22, W - 44, H - 44, INK, 1)

    # ---- masthead: navy band, gold rule, cream title -------------------
    cv.fill_rect(28, 28, W - 56, 104, NAVY)
    cv.centred(W // 2, 46, "THE WORLD TODAY", 8, WHITE)
    cv.hline(68, 110, W - 136, GOLD, 3)
    cv.centred(W // 2, 118, "ONE DAY  •  ONE PAGE  •  THE WHOLE WORLD",
               1, GOLD)

    # ---- date line ------------------------------------------------------
    cv.hline(28, 146, 200, INK, 2)
    cv.hline(W - 228, 146, 200, INK, 2)
    cv.centred(W // 2, 138, "SATURDAY 21 NOVEMBER 2026", 3, INK)

    # ---- lead story: text left, picture right ---------------------------
    lead_y = 176
    lead_x = 28
    lead_w = 562
    cv.text(lead_x, lead_y, "WAR IN EUROPE", 2, RED)
    cv.hline(lead_x, lead_y + 22, 190, RED, 3)
    yy = lead_y + 30
    for line in ("RUSSIAN", "MISSILES LAND", "IN POLAND"):
        cv.text(lead_x, yy, line, 5, INK)
        yy += 40
    yy += 4
    yy = cv.para(lead_x, yy,
                 "WARSAW CALLS THE INCURSION DELIBERATE AS NATO "
                 "CONDEMNS A GRAVE VIOLATION OF ITS AIRSPACE",
                 2, lead_w, INK, leading=18)
    yy += 6
    cv.hline(lead_x, yy, lead_w, LIGHT_GREY, 1)
    yy += 8
    yy = cv.para(lead_x, yy,
                 "TWO RUSSIAN MISSILES AND A SUSPECTED DRONE CAME DOWN "
                 "INSIDE POLAND DURING AN OVERNIGHT ATTACK ON UKRAINE, "
                 "WARSAW SAID. DONALD TUSK CALLED IT DELIBERATE, AND "
                 "NATO CALLED IT A GRAVE VIOLATION OF ALLIED AIRSPACE.",
                 2, lead_w, INK, leading=18)
    yy += 8
    cv.fill_rect(lead_x, yy, lead_w, 30, NAVY)
    cv.text(lead_x + 12, yy + 8, "400+ DRONES  •  110 MISSILES  •  8 KILLED",
            2, WHITE)

    draw_lead_art(cv, 606, lead_y, 390, 324)

    # ---- rule under the lead --------------------------------------------
    cv.hline(28, 516, W - 56, INK, 3)
    cv.hline(28, 521, W - 56, INK, 1)

    # ---- middle row: two stories side by side ---------------------------
    mid_y = 534
    col_w = 472
    # Left: UK-EU reset.
    draw_flags(cv, 28, mid_y, col_w, 78)
    yy = mid_y + 90
    cv.text(28, yy, "BRITAIN  •  EUROPE", 2, RED)
    yy += 20
    cv.text(28, yy, "UK AND EU SIGN", 3, INK)
    yy += 27
    cv.text(28, yy, "POST-BREXIT RESET", 3, INK)
    yy += 32
    cv.para(28, yy,
            "BRITAIN AND THE EU SIGNED A LANDMARK POST-BREXIT DEAL. "
            "FOOD CHECKS SCRAPPED, 100,000 YOUTH VISAS EACH WAY, "
            "BRITAIN BACK IN ERASMUS.",
            2, col_w, INK, leading=19)
    # Right: Peru quake.
    draw_quake(cv, 524, mid_y, col_w, 78)
    yy = mid_y + 90
    cv.text(524, yy, "NATURAL DISASTER", 2, RED)
    yy += 20
    cv.text(524, yy, "6.8 QUAKE", 3, INK)
    yy += 27
    cv.text(524, yy, "SHAKES PERU", 3, INK)
    yy += 32
    cv.para(524, yy,
            "A 6.8 EARTHQUAKE STRUCK JUNIN IN THE CENTRAL ANDES. "
            "TREMORS WERE FELT 320 KM AWAY IN LIMA. NO CASUALTIES "
            "REPORTED.",
            2, col_w, INK, leading=19)
    # Vertical divider between the two middle columns.
    cv.vline(510, mid_y, 236, LIGHT_GREY, 1)

    # ---- rule above the bottom strip ------------------------------------
    cv.hline(28, 782, W - 56, INK, 3)
    cv.hline(28, 787, W - 56, INK, 1)

    # ---- bottom strip: world court left, markets right ------------------
    bot_y = 800
    cv.text(28, bot_y, "JUSTICE  •  THE HAGUE", 2, RED)
    yy = bot_y + 20
    cv.text(28, yy, "COURT: MYANMAR COMMITTED", 3, INK)
    yy += 27
    cv.text(28, yy, "GENOCIDE", 3, INK)
    yy += 32
    yy = cv.para(28, yy,
                 "THE WORLD COURT RULED MYANMAR'S FORCES COMMITTED "
                 "STATE-SPONSORED GENOCIDE AGAINST THE ROHINGYA. "
                 "MYANMAR CALLED THE RULING UNFAIR.",
                 2, 612, INK, leading=19)
    yy += 6
    cv.text(28, yy, "ALSO: COP31 TALKS IN ANTALYA ENTER FINAL STAGE",
            2, RED)
    # Markets box.
    cv.fill_rect(656, bot_y - 6, 340, 148, WHITE)
    cv.rect(656, bot_y - 6, 340, 148, INK, 2)
    cv.text(670, bot_y + 4, "MARKETS", 2, RED)
    cv.text(670, bot_y + 24, "STOCKS SLIDE", 3, INK)
    draw_market_chart(cv, 670, bot_y + 52, 120, 56)
    cv.para(802, bot_y + 52,
            "US STOCKS FELL 3.7% AS AI SHARES SOLD OFF. S&P 500 IN "
            "CORRECTION.",
            2, 180, INK, leading=17)

    # ---- footer ----------------------------------------------------------
    cv.hline(28, 962, W - 56, INK, 1)
    cv.centred(W // 2, 972,
               "THE WORLD TODAY  —  SATURDAY 21 NOVEMBER 2026  —  DRAWN "
               "FROM THE DAY'S REPORTING",
               2, GREY)
    return cv


# --------------------------------------------------------------- PNG encode
def png_bytes(cv):
    """Encode the canvas as a standard 8-bit RGB PNG (filter 0 rows)."""
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(cv.px[y * W * 3:(y + 1) * W * 3])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", compressed) + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print(f"wrote {path}: {len(data)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
