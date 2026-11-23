from pathlib import Path
import json
import sys

from PIL import Image, ImageChops


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rgba(path):
    with Image.open(path) as image:
        return image.convert("RGBA")


def corners_have_alpha(image):
    width, height = image.size
    size = max(1, min(width, height) // 50)
    alpha = image.getchannel("A")
    return all(
        alpha.crop((x, y, x + size, y + size)).getextrema()[0] < 128
        for x in (0, width - size)
        for y in (0, height - size)
    )


def transparent_perimeter(alpha):
    width, height = alpha.size
    edges = (
        (0, 0, width, 1), (0, height - 1, width, height),
        (0, 0, 1, height), (width - 1, 0, width, height),
    )
    return all(alpha.crop(edge).getextrema()[1] == 0 for edge in edges)


def audit(project):
    config = read_json(project / "project.json")
    themes = read_json(project / config["theme"])["themes"]
    slices = read_json(project / config["slices"])
    aliases = read_json(project / config["story"]).get("itemAliases", {})
    sprites = {aliases.get(sprite, sprite) for game in config["gameplay"] for sprite in game["sprites"]}
    assets = project / "assets"
    issues = []

    for theme in themes:
        variant = theme["id"]
        with Image.open(assets / theme["scene"]) as scene:
            width, height = scene.size
            if abs((width / height) / (9 / 16) - 1) > 0.03:
                issues.append(f"{theme['scene']}: expected portrait 9:16 scene, got {width}x{height}")
        panel = rgba(assets / theme["panel"])
        if not corners_have_alpha(panel):
            issues.append(f"{theme['panel']}: panel exterior lacks transparent corners")
        if panel.getchannel("A").getpixel((panel.width // 2, panel.height // 2)) < 128:
            issues.append(f"{theme['panel']}: panel center is missing or too transparent")
        for piece in slices[variant]["pieces"]:
            expected = panel.crop(tuple(piece["box"]))
            actual = rgba(assets / piece["file"])
            if actual.size != expected.size or any(
                channel.getbbox() for channel in ImageChops.difference(actual, expected).split()
            ):
                issues.append(f"{piece['file']}: pixels do not match the declared crop")
        for sprite in sorted(sprites):
            filename = f"{variant}-{sprite}.png"
            image = rgba(assets / filename)
            alpha = image.getchannel("A")
            if not transparent_perimeter(alpha) or alpha.getextrema()[1] < 128:
                issues.append(f"{filename}: expected a visible cutout with alpha 0 along all four outer edges")
    return issues


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python audit-art-alpha.py <project-directory> (requires Pillow)")
    failures = audit(Path(sys.argv[1]))
    if failures:
        sys.exit("\n".join(failures))
    print("Scene aspect ratio, panel alpha, slice pixels and sprite cutouts passed.")
