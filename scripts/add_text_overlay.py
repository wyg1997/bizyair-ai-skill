#!/usr/bin/env python3
"""add_text_overlay.py -- add centered Chinese text to the bottom of an image.

Usage:
  python3 scripts/add_text_overlay.py <input_image> <output_image> [--text "欢迎来参加"] [--font-size 72] [--color "255,255,255"] [--y-offset 0.10]

Requires Pillow (PIL). Install: uv pip install --python <venv> Pillow
Font: WenQuanYi Zen Hei (wqy-zenhei.ttc) — supports CJK.
"""
import sys
from pathlib import Path


def main():
    import argparse
    from PIL import Image, ImageDraw, ImageFont

    parser = argparse.ArgumentParser(description="Add text overlay to image bottom")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--text", default="欢迎来参加我妹妹的百日宴", help="Text to overlay")
    parser.add_argument("--font-size", type=int, default=0, help="Font size (0=auto from width)")
    parser.add_argument("--color", default="255,255,255", help="Text color R,G,B")
    parser.add_argument("--shadow", default="180,100,120", help="Shadow color R,G,B")
    parser.add_argument("--y-offset", type=float, default=0.10, help="Bottom margin as fraction of height")
    parser.add_argument("--hearts", action="store_true", default=True, help="Add heart decorations")
    args = parser.parse_args()

    font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

    img = Image.open(args.input).convert("RGBA")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    fs = args.font_size or max(40, W // 14)
    font = ImageFont.truetype(font_path, fs)
    heart_font = ImageFont.truetype(font_path, max(28, W // 22))

    bbox = draw.textbbox((0, 0), args.text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) // 2
    y = H - int(H * args.y_offset) - th // 2

    sc = tuple(int(v) for v in args.shadow.split(","))
    tc = tuple(int(v) for v in args.color.split(","))

    # Shadow + text
    draw.text((x + 3, y + 3), args.text, font=font, fill=sc + (150,))
    draw.text((x, y), args.text, font=font, fill=tc + (255,))

    # Hearts on sides
    if args.hearts:
        for dx in [tw // 2 + 40, -tw // 2 - 45]:
            cx = W // 2 + dx
            draw.text((cx, y + th // 2 - 16), "♥", font=heart_font, fill=(255, 160, 170, 220))

    img.convert("RGB").save(args.output, "PNG", quality=95)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
