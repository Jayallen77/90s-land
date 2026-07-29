#!/usr/bin/env python3
"""Create deterministic local image derivatives and enrich static HTML images."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "assets" / "generated"

RESPONSIVE_IMAGES = {
    "family-pc": ROOT / "assets/media/tech-toys/family-pc-rotterdam-1999.jpg",
    "hubble-launch": ROOT / "assets/media/timeline-1990/hubble-launch.jpg",
    "imac-bondi": ROOT / "assets/media/transparent-tech/imac-g3-bondi-blue.png",
}


def image_dimensions(src: str) -> tuple[int, int] | None:
    if not src.startswith("/"):
        return None
    path = ROOT / src.lstrip("/")
    if not path.is_file():
        return None
    try:
        with Image.open(path) as image:
            return image.size
    except OSError:
        return None


def enrich_tag(tag: str, *, eager: bool) -> str:
    match = re.search(r'\bsrc=(["\'])(.*?)\1', tag)
    if not match:
        return tag
    dimensions = image_dimensions(match.group(2))
    if dimensions and not re.search(r"\bwidth=", tag):
        tag = tag[:-2] + f' width="{dimensions[0]}" height="{dimensions[1]}" />'
    if not re.search(r"\bloading=", tag):
        loading = "eager" if eager else "lazy"
        tag = tag[:-2] + f' loading="{loading}" />'
    if eager and not re.search(r"\bfetchpriority=", tag):
        tag = tag[:-2] + ' fetchpriority="high" />'
    if not re.search(r"\bdecoding=", tag):
        tag = tag[:-2] + ' decoding="async" />'
    return tag


def enrich_html(source: str, path: Path) -> str:
    first_image = True

    def replace(match: re.Match[str]) -> str:
        nonlocal first_image
        tag = match.group(0)
        eager = (
            path == ROOT / "index.html"
            and first_image
            and "family-pc-rotterdam-1999.jpg" in tag
        )
        first_image = False
        return enrich_tag(tag, eager=eager)

    return re.sub(r"<img\b[^>]*?/>", replace, source)


def save_responsive(name: str, source: Path) -> None:
    with Image.open(source) as original:
        original.load()
        width, height = original.size
        for target_width in (480, 960, 1440):
            if target_width > width:
                continue
            target_height = round(height * target_width / width)
            resized = original.resize(
                (target_width, target_height), Image.Resampling.LANCZOS
            )
            if resized.mode not in ("RGB", "RGBA"):
                resized = resized.convert("RGBA")
            webp = GENERATED / f"{name}-{target_width}.webp"
            avif = GENERATED / f"{name}-{target_width}.avif"
            resized.save(webp, "WEBP", quality=78, method=6)
            resized.save(avif, "AVIF", quality=64, speed=6)


def save_animated_imac() -> None:
    source = ROOT / "assets/media/transparent-tech/imac-g3-color-carousel.gif"
    destination = GENERATED / "imac-g3-carousel-480.webp"
    still_destination = GENERATED / "imac-g3-carousel-still-480.webp"
    with Image.open(source) as animated:
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(animated):
            rgba = frame.convert("RGBA")
            height = round(rgba.height * 480 / rgba.width)
            frames.append(rgba.resize((480, height), Image.Resampling.LANCZOS))
            durations.append(frame.info.get("duration", animated.info.get("duration", 100)))
        frames[0].save(
            destination,
            "WEBP",
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            quality=74,
            method=6,
        )
        frames[0].save(still_destination, "WEBP", quality=78, method=6)


def font(size: int):
    candidates = (
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/SFNSMono.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def save_icons() -> None:
    icons = ROOT / "assets/icons"
    icons.mkdir(parents=True, exist_ok=True)
    for size, name in ((32, "favicon-32.png"), (192, "icon-192.png"), (512, "icon-512.png")):
        image = Image.new("RGB", (size, size), "#070018")
        draw = ImageDraw.Draw(image)
        border = max(2, size // 24)
        shadow = max(2, size // 18)
        draw.rectangle(
            (border + shadow, border + shadow, size - border, size - border),
            fill="#ff4fd8",
        )
        draw.rectangle(
            (border, border, size - border - shadow, size - border - shadow),
            fill="#fff35c",
            outline="#f8f2ff",
            width=border,
        )
        label_font = font(max(10, round(size * .25)))
        text = "90s"
        bounds = draw.textbbox((0, 0), text, font=label_font)
        x = (size - shadow - (bounds[2] - bounds[0])) / 2
        y = (size - shadow - (bounds[3] - bounds[1])) / 2 - bounds[1]
        draw.text((x, y), text, font=label_font, fill="#050017")
        image.save(icons / name, "PNG", optimize=True)


def expected_outputs() -> list[Path]:
    outputs = [
        ROOT / "assets/icons/favicon-32.png",
        ROOT / "assets/icons/icon-192.png",
        ROOT / "assets/icons/icon-512.png",
        GENERATED / "imac-g3-carousel-480.webp",
        GENERATED / "imac-g3-carousel-still-480.webp",
    ]
    for name, source in RESPONSIVE_IMAGES.items():
        with Image.open(source) as image:
            for width in (480, 960, 1440):
                if width <= image.width:
                    outputs.extend(
                        [
                            GENERATED / f"{name}-{width}.webp",
                            GENERATED / f"{name}-{width}.avif",
                        ]
                    )
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="fail if derivatives or HTML drift"
    )
    args = parser.parse_args()
    GENERATED.mkdir(parents=True, exist_ok=True)

    drift = []
    if args.check:
        drift.extend(path for path in expected_outputs() if not path.is_file())
    else:
        for name, source in RESPONSIVE_IMAGES.items():
            save_responsive(name, source)
        save_animated_imac()
        save_icons()

    for path in sorted(ROOT.rglob("*.html")):
        original = path.read_text()
        updated = enrich_html(original, path)
        if original == updated:
            continue
        if args.check:
            drift.append(path)
        else:
            path.write_text(updated)

    if drift:
        print("media drift:")
        for path in drift:
            print(path.relative_to(ROOT))
        return 1
    print("media files and intrinsic dimensions are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
