"""Utilities for generating a 6-dimension radar-score image with labels and avatar."""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


Point = tuple[int, int]


def interp_point(p0: Point, p1: Point, t: float) -> tuple[float, float]:
    return (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)


def point_for_score(anchor_0_to_10: list[Point], score: float) -> Point:
    """
    Convert one 0~10 score to one pixel point based on 11 anchor points.

    anchor_0_to_10: length=11, where index 0..10 maps to score 0..10
    score: float score in [0, 10] (e.g., 1.5)
    """
    if len(anchor_0_to_10) != 11:
        raise ValueError("Each dimension must provide 11 points for scores 0..10")

    s = float(score)
    if s != s:  # NaN
        s = 0.0
    s = max(0.0, min(10.0, s))

    lo = int(math.floor(s + 1e-9))
    hi = min(lo + 1, 10)
    t = s - lo

    if t <= 1e-9 or lo == hi:
        x, y = anchor_0_to_10[lo]
        return (int(x), int(y))

    x, y = interp_point(anchor_0_to_10[lo], anchor_0_to_10[hi], t)
    return (int(round(x)), int(round(y)))


def _load_font(size: int) -> ImageFont.ImageFont:
    """Try common CJK fonts first, and gracefully fall back."""
    candidates: Iterable[str] = ("msyh.ttc", "Microsoft YaHei.ttf", "simhei.ttf", "arial.ttf")
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_radar_by_anchors(
    img_path: str,
    out_path: str,
    scores_0_to_10: list[float],
    final_score: int,
    anchors: list[list[Point]],
    label_positions: list[Point],
    name_title: list[str],
    title_positions: list[Point],
    fill_rgba: tuple[int, int, int, int] = (255, 140, 0, 110),
    outline_rgba: tuple[int, int, int, int] = (255, 140, 0, 200),
    outline_width: int = 4,
) -> tuple[str, list[Point]]:
    """Draw radar polygon and text labels onto the template image."""
    if len(scores_0_to_10) != 6:
        raise ValueError("scores_0_to_10 must contain exactly 6 values")
    if len(anchors) != 6:
        raise ValueError("anchors must contain exactly 6 dimensions")

    img = Image.open(img_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    points = [point_for_score(anchor, score) for score, anchor in zip(scores_0_to_10, anchors)]

    draw.polygon(points, fill=fill_rgba)
    if outline_width > 0:
        draw.line(points + [points[0]], fill=outline_rgba, width=outline_width)

    out = Image.alpha_composite(img, overlay)
    draw2 = ImageDraw.Draw(out)

    score_font = _load_font(100)
    width, height = out.size

    for (x, y), score in zip(label_positions, scores_0_to_10):
        text = str(score)
        bbox = draw2.textbbox((0, 0), text, font=score_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        x = max(0, min(int(x), width - tw - 8))
        y = max(0, min(int(y), height - th - 8))

        pad = 10
        draw2.rectangle((x - pad, y - pad, x + tw + pad, y + th + pad), fill=(255, 255, 255, 220))
        draw2.text((x, y - 26), text, fill=(0, 0, 0, 255), font=score_font)

    title_font = _load_font(60)
    for (x, y), text in zip(title_positions, name_title):
        draw2.text((x, y), text, fill=(0, 0, 0, 255), font=title_font)

    meta_font = _load_font(50)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw2.text((900, 2692), now, fill=(255, 255, 255, 255), font=meta_font)
    draw2.text((220, 2000), f"总分: {final_score}", fill=(255, 255, 255, 255), font=title_font)

    out.save(out_path)
    return out_path, points


def add_avatar(
    bg_path: str,
    avatar_path: str,
    center: Point,
    size: int = 260,
    radius: int = 40,
    border_width: int = 10,
    border_color: tuple[int, int, int, int] = (255, 80, 0, 255),
) -> str:
    """Paste a rounded avatar with border onto an existing background image."""
    bg = Image.open(bg_path).convert("RGBA")
    avatar = Image.open(avatar_path).convert("RGBA")

    w, h = avatar.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top = (h - min_side) // 2
    avatar = avatar.crop((left, top, left + min_side, top + min_side)).resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    avatar.putalpha(mask)

    border_size = size + border_width * 2
    avatar_with_border = Image.new("RGBA", (border_size, border_size), (0, 0, 0, 0))

    ring_mask = Image.new("L", (border_size, border_size), 0)
    d = ImageDraw.Draw(ring_mask)
    d.rounded_rectangle((0, 0, border_size - 1, border_size - 1), radius=radius + border_width, fill=255)
    d.rounded_rectangle(
        (border_width, border_width, border_size - 1 - border_width, border_size - 1 - border_width),
        radius=radius,
        fill=0,
    )

    border_layer = Image.new("RGBA", (border_size, border_size), border_color)
    border_layer.putalpha(ring_mask)

    avatar_with_border.paste(border_layer, (0, 0), border_layer)
    avatar_with_border.paste(avatar, (border_width, border_width), avatar)

    cx, cy = center
    x = int(cx - border_size / 2)
    y = int(cy - border_size / 2)
    bg.paste(avatar_with_border, (x, y), avatar_with_border)

    bg.save(bg_path)
    return bg_path


def demo() -> None:
    """Demo call with the same sample values from your draft."""
    img_path = "score3.png"
    out_path = "anchors_fixed.png"

    titles = ["聪哥", "重生50", "AI真人剧"]
    scores = [8, 9, 7, 7, 10, 8]
    final_score = 9

    anchors = [
        [(770, 1210), (770, 1167), (770, 1123), (770, 1082), (770, 1040), (770, 1000), (770, 960), (770, 926), (770, 895), (770, 858), (770, 825)],
        [(770, 1210), (815, 1190), (855, 1168), (895, 1148), (935, 1126), (972, 1106), (1010, 1090), (1044, 1072), (1078, 1054), (1112, 1036), (1145, 1020)],
        [(770, 1210), (815, 1236), (855, 1260), (895, 1280), (935, 1298), (972, 1318), (1010, 1336), (1044, 1355), (1078, 1375), (1112, 1390), (1145, 1408)],
        [(770, 1210), (770, 1258), (770, 1305), (770, 1340), (770, 1385), (770, 1426), (770, 1460), (770, 1498), (770, 1530), (770, 1570), (770, 1602)],
        [(770, 1210), (728, 1236), (683, 1260), (645, 1280), (606, 1298), (570, 1318), (532, 1336), (500, 1355), (465, 1375), (430, 1390), (395, 1408)],
        [(770, 1210), (728, 1190), (686, 1168), (645, 1148), (606, 1128), (570, 1110), (532, 1090), (500, 1072), (465, 1054), (430, 1036), (395, 1020)],
    ]

    label_positions = [(858, 745), (1178, 1060), (1178, 1490), (858, 1605), (260, 1490), (260, 1060)]
    title_positions = [(865, 250), (975, 355), (978, 455)]

    saved, points = draw_radar_by_anchors(
        img_path,
        out_path,
        scores,
        final_score,
        anchors,
        label_positions,
        titles,
        title_positions,
    )

    add_avatar(saved, "avatar.png", center=(400, 420), size=290, radius=43)
    print("Saved:", saved)
    print("Points:", points)


if __name__ == "__main__":
    if Path("score3.png").exists() and Path("avatar.png").exists():
        demo()
    else:
        print("Place score3.png and avatar.png in the current directory, then run again.")
