"""Crop an approved transparent frame and build nine contiguous PNG slices."""
import argparse
import json
from pathlib import Path
import re

from PIL import Image


def prepare(source, assets, variant, cw, ch):
    if not re.fullmatch(r"[a-z][a-z0-9-]*", variant):
        raise ValueError("Invalid theme ID")
    with Image.open(source) as image:
        panel = image.convert("RGBA")
    alpha = panel.getchannel("A")
    w, h = panel.size
    corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
    if any(alpha.getpixel(pt) != 0 for pt in corners):
        raise ValueError("Opaque or matted exterior. Remove the background first; cropping cannot create alpha.")
    if alpha.getpixel((w // 2, h // 2)) < 128:
        raise ValueError("Expected a filled panel center")
    bounds = alpha.point(lambda value: 255 if value >= 128 else 0).getbbox()
    if bounds is None:
        raise ValueError("No visible frame")
    left, top, right, bottom = bounds
    # Leave two pixels for the contour antialiasing around the solid frame.
    crop = (max(0, left-2), max(0, top-2), min(w, right+2), min(h, bottom+2))
    cropped = panel.crop(crop)
    w, h = cropped.size
    if not (0 < 2*cw < w and 0 < 2*ch < h):
        raise ValueError("Corner cut lines must leave a positive center area")
    alpha = cropped.getchannel("A")
    if any(alpha.getpixel(pt) >= 128 for pt in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))):
        raise ValueError("Frame has a solid rectangular exterior after trim. Recheck the cutout.")

    xs, ys = [0, cw, w-cw, w], [0, ch, h-ch, h]
    pieces = []
    manifest = assets / "nine-slice.json"
    existing = json.loads(manifest.read_text(encoding="utf-8-sig")) if manifest.exists() else {}
    target = assets / f"{variant}-panel.png"
    if source.resolve() == target.resolve():
        raise ValueError("Keep the source in a separate location")
    assets.mkdir(parents=True, exist_ok=True)
    cropped.save(target)
    for row in range(3):
        for col in range(3):
            box = [xs[col], ys[row], xs[col+1], ys[row+1]]
            file = f"{variant}-slice-{row}{col}.png"
            cropped.crop(box).save(assets / file)
            pieces.append(dict(row=row, col=col, box=box, file=file))
    existing[variant] = dict(sourceSize=[w, h], sourceCorner=[cw, ch], pieces=pieces)
    manifest.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(variant=variant, crop=crop, size=[w, h], corner=[cw, ch])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("assets", type=Path)
    parser.add_argument("variant")
    parser.add_argument("corner_width", type=int)
    parser.add_argument("corner_height", type=int)
    args = parser.parse_args()
    try:
        prepare(args.source, args.assets, args.variant, args.corner_width, args.corner_height)
    except ValueError as error:
        parser.exit(1, f"{error}\n")
