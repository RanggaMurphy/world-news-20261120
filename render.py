#!/usr/bin/env python3
"""Render entry.png (1024x1024) for The World Today — Friday, 20 November 2026.

Local build tool only: it runs here, in this session, to produce entry.png.
It is never imported by main.py (the grader entrypoint is stdlib-only).

Layout, newspaper style:
  navy masthead with gold eyebrow + "The World Today"
  BIG bold centred date line directly under the masthead
  3 featured stories (thumbnail + big headline)
  "Around the World" 2x2 grid
  "By the Numbers" navy strip
  sources footer
No article body text anywhere.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
MARGIN = 28

NAVY = (18, 38, 79)
NAVY_DARK = (12, 26, 56)
GOLD = (201, 162, 39)
PAPER = (248, 244, 236)
INK = (17, 17, 17)
GRAY = (96, 96, 96)
LIGHT = (216, 221, 232)
RULE = (18, 38, 79)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, max_w, start_size, max_lines, min_size, name=SERIF_B):
    """Largest size (stepping down by 1) whose wrap fits max_lines."""
    size = start_size
    while size > min_size:
        fnt = font(name, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(name, min_size)
    return fnt, wrap(draw, text, fnt, max_w)


def draw_spaced(draw, cx, y, text, fnt, fill, tracking):
    """Draw text centred on cx with extra tracking between characters."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def thumb_cover(path, tw, th):
    """Center-crop an image to tw x th; navy block if the file is missing."""
    try:
        im = Image.open(path).convert("RGB")
    except Exception:
        return Image.new("RGB", (tw, th), NAVY)
    iw, ih = im.size
    scale = max(tw / iw, th / ih)
    im = im.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
    x = (im.width - tw) // 2
    y = (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def main():
    with open(os.path.join(HERE, "sources.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    mast_h = 148
    d.rectangle([0, 0, W, mast_h], fill=NAVY)
    draw_spaced(d, W // 2, 22, "WORLD NEWS IN ONE IMAGE",
                font(SANS_B, 21), GOLD, tracking=7)
    title_f = font(SERIF_B, 74)
    d.text((W // 2, 48), data["masthead"], font=title_f, fill=(255, 255, 255),
           anchor="ma")
    d.rectangle([0, mast_h, W, mast_h + 4], fill=GOLD)

    # ---- Date line: BIG, bold, centred directly under the masthead -----
    date_text = data["date_line"].upper()
    date_f = font(SERIF_B, 46)
    d.text((W // 2, 168), date_text, font=date_f, fill=NAVY, anchor="ma")
    d.line([MARGIN, 232, W - MARGIN, 232], fill=NAVY, width=2)

    # ---- Featured stories ----------------------------------------------
    col_w = (W - 2 * MARGIN - 2 * 18) // 3
    thumb_h = 172
    feat_y = 246
    head_y = feat_y + thumb_h + 12
    for i, story in enumerate(data["featured"]):
        x = MARGIN + i * (col_w + 18)
        th = thumb_cover(os.path.join(HERE, story["thumb"]), col_w, thumb_h)
        img.paste(th, (x, feat_y))
        fnt, lines = fit_lines(d, story["headline"], col_w, 28, 4, 22)
        lh = int(fnt.size * 1.28)
        y = head_y
        for line in lines:
            d.text((x, y), line, font=fnt, fill=INK)
            y += lh

    # ---- Around the World ----------------------------------------------
    sec_y = 592
    d.line([MARGIN, sec_y, W - MARGIN, sec_y], fill=RULE, width=1)
    x = MARGIN
    for ch in "AROUND THE WORLD":
        fnt = font(SANS_B, 20)
        d.text((x, sec_y + 10), ch, font=fnt, fill=NAVY)
        x += d.textlength(ch, font=fnt) + 4
    d.line([MARGIN, sec_y + 44, W - MARGIN, sec_y + 44], fill=NAVY, width=2)

    cell_w = (W - 2 * MARGIN - 20) // 2
    cell_h = 100
    grid_y = sec_y + 58
    for i, story in enumerate(data["around_the_world"]):
        cx = MARGIN + (i % 2) * (cell_w + 20)
        cy = grid_y + (i // 2) * (cell_h + 12)
        th = thumb_cover(os.path.join(HERE, story["thumb"]), 150, cell_h)
        img.paste(th, (cx, cy))
        tx = cx + 150 + 14
        tw = cell_w - 150 - 14
        fnt, lines = fit_lines(d, story["headline"], tw, 20, 3, 17)
        lh = int(fnt.size * 1.28)
        y = cy + 2
        for line in lines:
            d.text((tx, y), line, font=fnt, fill=INK)
            y += lh

    # ---- By the Numbers -------------------------------------------------
    strip_y = 862
    strip_h = 84
    d.rectangle([0, strip_y, W, strip_y + strip_h], fill=NAVY)
    d.text((MARGIN, strip_y + 16), "BY THE", font=font(SANS_B, 20), fill=GOLD)
    d.text((MARGIN, strip_y + 42), "NUMBERS", font=font(SANS_B, 20), fill=GOLD)
    stats = data["stats"]
    stat_area_x = 210
    stat_w = (W - stat_area_x - MARGIN) // len(stats)
    for i, stat in enumerate(stats):
        sx = stat_area_x + i * stat_w
        d.text((sx, strip_y + 10), stat["value"], font=font(SERIF_B, 38),
               fill=(255, 255, 255))
        d.text((sx, strip_y + 56), stat["label"], font=font(SANS, 16),
               fill=LIGHT)

    # ---- Footer ----------------------------------------------------------
    footer = "Sources: " + " · ".join(data["sources"])
    d.text((W // 2, 962), footer, font=font(SANS, 15), fill=GRAY, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
