#!/usr/bin/env python3
"""Finish the single generated social-card background with verified local type."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/generated/og-card-source.png"
OUTPUT = ROOT / "assets/generated/og-card.png"


def loaded_font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(ROOT / "assets/fonts" / filename, size)


image = Image.open(SOURCE).convert("RGB")
image = ImageOps.fit(
    image,
    (1200, 630),
    method=Image.Resampling.LANCZOS,
    centering=(.5, .5),
)
draw = ImageDraw.Draw(image, "RGBA")

# Reinforce the text-safe half while keeping the generated museum atmosphere.
for x in range(700):
    alpha = round(80 * (1 - x / 700))
    draw.line((x, 0, x, 630), fill=(7, 0, 24, alpha))

pixel = loaded_font("press-start-2p-regular.ttf", 23)
headline = loaded_font("space-mono-bold.ttf", 58)
body = loaded_font("space-mono-regular.ttf", 25)

# Original deterministic logo lockup.
draw.rectangle((56, 46, 159, 108), fill="#ff4fd8")
draw.rectangle((50, 40, 153, 102), fill="#fff35c", outline="#f8f2ff", width=4)
draw.text((64, 60), "90s", font=pixel, fill="#050017")
draw.text((154, 55), ".land", font=pixel, fill="#f8f2ff")

headline_text = "A playable\nmuseum of\nthe 1990s."
headline_xy = (52, 158)
draw.multiline_text(
    (headline_xy[0] + 5, headline_xy[1] + 5),
    headline_text,
    font=headline,
    fill="#ff4fd8",
    spacing=-1,
)
draw.multiline_text(
    headline_xy,
    headline_text,
    font=headline,
    fill="#f8f2ff",
    spacing=-1,
)

draw.line((54, 492, 554, 492), fill="#39fff2", width=4)
draw.multiline_text(
    (54, 516),
    "Browse the decade. Open its objects.\nGet lost on purpose.",
    font=body,
    fill="#f8f2ff",
    spacing=8,
)

image.save(OUTPUT, "PNG", optimize=True)
print(f"saved {OUTPUT} ({image.width}x{image.height})")
