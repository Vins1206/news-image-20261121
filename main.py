"""THE WORLD TODAY - Saturday 21 November 2026.

Pure-stdlib Python program that draws a one-page newspaper front
page summing up the world news of Saturday 21 November 2026 and
writes a deterministic 1024x1024 PNG to /output/entry.png.

No network, no third-party code, no timestamps in the output: every
run writes the same bytes. The picture is drawn pixel by pixel with
a small 5x7 bitmap font, so it needs nothing but the standard library.

Stories on the page (all first reported on Saturday 21 November
2026, or the day's lead stories that morning):
  * Russian missiles come down in Poland; NATO calls it a grave
    violation of its airspace
  * Wall Street slumps: S&P 500 and Dow enter correction as AI
    shares sell off, Nasdaq down over 5%
  * Trump, Xi and Putin leave their first trilateral summit with
    few concrete results
  * Myanmar calls the World Court genocide ruling "unfair";
    Malaysia to resettle 10,000 Rohingya in Turkiye
  * A pill hailed as a breakthrough for pancreatic cancer
  * Cyclone Akvan: the aftermath on India's Odisha coast
  * UK and EU sign deals on food, carbon markets, youth mobility
  * Indonesia fires: losses could reach $30 billion
  * Iran war: Trump says he is not rushing any decision
  * Sport: Jaiswal and Rahul put on India's first century opening
    stand in New Zealand this century
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (250, 246, 236)
INK = (18, 18, 18)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
GREY = (112, 110, 102)
GOLD = (186, 146, 38)
LIGHT = (233, 227, 214)


# ---------------------------------------------------------------- PNG ---

def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------------- canvas ---

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, t=1):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                for k in range(t):
                    self.set(px + k, py, c)
                    self.set(px, py + k, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts

        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(ay, cy + 1):
            if y < by:
                xa = edge_x(ax, ay, bx, by, y)
                xb = edge_x(ax, ay, cx, cy, y)
            else:
                xa = edge_x(bx, by, cx, cy, y)
                xb = edge_x(ax, ay, cx, cy, y)
            lo, hi = sorted((int(round(xa)), int(round(xb))))
            for x in range(lo, hi + 1):
                self.set(x, y, c)


# ----------------------------------------------------------- bitmap font ---
# 5x7 glyphs, each row a 5-bit int, top row first.

FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    "-": (0, 0, 0, 31, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "$": (4, 15, 20, 14, 5, 30, 4),
    '"': (10, 10, 10, 0, 0, 0, 0),
    "*": (0, 4, 21, 14, 21, 4, 0),
    "_": (0, 0, 0, 0, 0, 0, 31),
}


# ------------------------------------------------------------ text drawing ---

def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale
    return cx - x - scale


def draw_center(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_w, scale):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(cv, x, y, s, scale, color, max_w, leading=None):
    lh = leading if leading is not None else 10 * scale
    for line in wrap(s, max_w, scale):
        draw_text(cv, x, y, line, scale, color)
        y += lh
    return y


def headline(cv, x, y, lines, scale, color=INK, leading=None):
    lh = leading if leading is not None else 10 * scale
    for line in lines:
        draw_text(cv, x, y, line, scale, color)
        y += lh
    return y


# -------------------------------------------------------------- pictograms ---

def draw_map_europe(cv, x, y, w, h, color):
    # Stylised map outline: Poland marked with a star, a missile arc.
    cv.rect(x, y, w, h, color, 2)
    cv.fill_rect(x + 6, y + 6, w - 12, h - 12, LIGHT)
    # Rough landmass: a low coastline band across the panel.
    cv.fill_rect(x + 20, y + h - 44, w - 40, 22, color)
    cv.line(x + 20, y + h - 44, x + w - 20, y + 22, color)
    # Star over Poland (upper right of the panel)
    sx, sy = x + w - 70, y + 34
    cv.disc(sx, sy, 5, RED)
    for dx, dy in ((-14, 0), (14, 0), (0, -14), (0, 14)):
        cv.line(sx, sy, sx + dx, sy + dy, RED)
    draw_text(cv, x + 12, y + 8, "POLAND", 2, RED)
    draw_text(cv, x + w - 118, y + 8, "NATO", 2, BLUE)


def draw_chart(cv, x, y, w, h, color):
    # Falling market chart: axes, steep red line, -5% tag.
    cv.rect(x, y, w, h, color, 2)
    cv.fill_rect(x + 6, y + 6, w - 12, h - 12, LIGHT)
    cv.line(x + 14, y + h - 18, x + w - 14, y + h - 18, GREY)
    cv.line(x + 14, y + 14, x + 14, y + h - 18, GREY)
    pts = [(x + 22, y + 22), (x + 60, y + 30), (x + 100, y + 28),
           (x + 140, y + 52), (x + 180, y + 66), (x + 220, y + 92),
           (x + w - 24, y + h - 30)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, RED)
        cv.line(ax, ay + 1, bx, by + 1, RED)
    draw_text(cv, x + w - 78, y + 12, "-5.0%", 2, RED)


def draw_scales(cv, x, y, s, color):
    top = y
    cv.vline(x + s // 2, top, s, color, 2)
    cv.hline(x + 4, top + 6, s - 8, color, 2)
    cv.disc(x + s // 2, top + 2, 3, color)
    for side in (0, 1):
        px = x + 6 + side * (s - 12)
        cv.line(px, top + 6, px - 9, top + s // 2, color)
        cv.line(px, top + 6, px + 9, top + s // 2, color)
        cv.hline(px - 10, top + s // 2, 21, color, 2)
        cv.fill_rect(px - 8, top + s // 2, 17, 3, color)
    cv.hline(x + 2, top + s - 2, s - 4, color, 3)


def draw_pill(cv, cx, cy, color):
    # Capsule, half red half white, with a small cross.
    cv.disc(cx - 18, cy, 12, RED)
    cv.disc(cx + 18, cy, 12, (255, 255, 255))
    cv.fill_rect(cx - 18, cy - 12, 36, 24, RED)
    cv.fill_rect(cx, cy - 12, 18, 24, (255, 255, 255))
    cv.circle(cx - 18, cy, 12, color, 1)
    cv.circle(cx + 18, cy, 12, color, 1)
    cv.fill_rect(cx - 2, cy - 12, 4, 24, color)
    cv.disc(cx, cy - 26, 3, GOLD)
    cv.disc(cx - 34, cy + 20, 3, GOLD)
    cv.disc(cx + 34, cy + 18, 3, GOLD)


def draw_cyclone(cv, cx, cy, color):
    for ring in range(4):
        r = 8 + ring * 7
        steps = 26 - ring * 4
        for i in range(steps):
            a = 2 * math.pi * i / 26 + ring * 0.9
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a))
            cv.set(x, y, color)
            cv.set(x + 1, y, color)
    cv.disc(cx, cy, 3, PAPER)
    cv.circle(cx, cy, 3, color, 1)


# ------------------------------------------------------------------ page ---

def draw_page():
    cv = Canvas(W, H, PAPER)
    cv.rect(14, 14, W - 28, H - 28, INK, 2)

    # ---- masthead ------------------------------------------------------
    cv.hline(30, 30, W - 60, RED, 4)
    draw_center(cv, W // 2, 44, "THE WORLD TODAY", 7, INK)
    draw_center(cv, W // 2, 106, "SATURDAY, 21 NOVEMBER 2026", 3, RED)
    draw_text(cv, 34, 108, "NO. 325", 2, GREY)
    draw_text(cv, W - 34 - text_w("ONE DAY, ONE PAGE", 2), 108,
              "ONE DAY, ONE PAGE", 2, GREY)
    cv.hline(30, 134, W - 60, INK, 3)
    cv.hline(30, 140, W - 60, INK, 1)

    # ---- lead story: missiles in Poland --------------------------------
    draw_center(cv, W // 2, 156, "MISSILES HIT POLAND", 2, RED)
    draw_center(cv, W // 2, 182, "NATO: A GRAVE", 4, INK)
    draw_center(cv, W // 2, 216, "VIOLATION", 4, INK)
    paragraph(cv, 34, 258,
              "Two Russian missiles and a suspected drone come down in "
              "Poland. Warsaw calls it a deliberate provocation; NATO "
              "calls it a grave violation of its airspace.",
              2, INK, 600, leading=20)
    draw_map_europe(cv, 660, 244, 330, 82, BLUE)
    cv.hline(30, 340, W - 60, INK, 2)

    # ---- row two: Wall Street / trilateral summit -----------------------
    draw_text(cv, 34, 358, "NEW YORK", 2, RED)
    headline(cv, 34, 382, ["WALL STREET", "IN CORRECTION"], 3, INK)
    paragraph(cv, 34, 450,
              "The S&P 500 falls 3.7% and the Dow follows it into "
              "correction as AI shares sell off. The Nasdaq loses over "
              "5% and erases its 2026 gains.",
              2, INK, 452, leading=20)
    draw_chart(cv, 34, 540, 452, 92, BLUE)
    draw_text(cv, 532, 358, "SHENZHEN", 2, RED)
    headline(cv, 532, 382, ["SUMMIT ENDS", "WITH LITTLE DONE"], 3, INK)
    paragraph(cv, 532, 450,
              "Trump, Xi and Putin leave their first three-way summit "
              "with few concrete results: a joint declaration on "
              "nuclear war, oil and UN reform.",
              2, INK, 452, leading=20)
    draw_text(cv, 532, 556, "ALSO: NVIDIA FACES A PROBE", 2, GREY)
    draw_text(cv, 532, 580, "AS SHARES SINK; ANTHROPIC SLIDES.", 2, GREY)
    draw_text(cv, 532, 606, "CYCLONE AKVAN: RESCUE UNDER WAY", 2, GREY)
    draw_text(cv, 532, 628, "IN ODISHA; 300,000 EVACUATED.", 2, GREY)
    cv.vline(512, 358, 274, GREY, 1)
    cv.hline(30, 646, W - 60, INK, 2)

    # ---- row three: World Court / cancer pill ----------------------------
    draw_text(cv, 34, 664, "THE HAGUE", 2, RED)
    headline(cv, 34, 688, ["MYANMAR CALLS", "RULING UNFAIR"], 3, INK)
    paragraph(cv, 34, 756,
              "A day after the World Court found Myanmar committed "
              "genocide against the Rohingya, Myanmar rejects the "
              "ruling. Malaysia will resettle 10,000 Rohingya.",
              2, INK, 452, leading=19)
    draw_scales(cv, 34, 852, 32, BLUE)
    draw_text(cv, 532, 664, "MEDICINE", 2, RED)
    headline(cv, 532, 688, ["PILL HAILED AS", "CANCER BREAKTHROUGH"], 3, INK)
    paragraph(cv, 532, 756,
              "Trial pill daraxonrasib stops pancreatic tumours "
              "growing in nearly all patients; cancer becomes "
              "undetectable in one in 12.",
              2, INK, 360, leading=19)
    draw_pill(cv, 920, 866, BLUE)
    cv.vline(512, 664, 226, GREY, 1)
    cv.hline(30, 890, W - 60, INK, 2)

    # ---- bottom band: three short stories --------------------------------
    draw_text(cv, 34, 906, "BRUSSELS", 2, RED)
    paragraph(cv, 34, 928,
              "UK AND EU SIGN FOOD, CARBON, YOUTH DEALS.",
              2, INK, 300, leading=17)
    cv.vline(352, 906, 52, GREY, 1)
    draw_text(cv, 372, 906, "ASIA", 2, RED)
    paragraph(cv, 372, 928,
              "INDONESIA FIRES: LOSSES MAY HIT $30BN.",
              2, INK, 300, leading=17)
    cv.vline(690, 906, 52, GREY, 1)
    draw_text(cv, 710, 906, "IRAN", 2, RED)
    paragraph(cv, 710, 928,
              "TRUMP: NO RUSH ON IRAN; DECISION IN 2027.",
              2, INK, 280, leading=17)

    # ---- footer ----------------------------------------------------------
    cv.hline(30, 968, W - 60, INK, 2)
    draw_center(cv, W // 2, 980,
                "SPORT - CRICKET: JAISWAL AND RAHUL, INDIA'S FIRST "
                "CENTURY OPENING STAND IN NZ", 2, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    page = draw_page()
    size = write_png(path, W, H, page.px)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
