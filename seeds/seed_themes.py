# ruff: noqa: E402
import argparse
import asyncio
import colorsys
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import AsyncSessionLocal as async_session_maker
from src.database.models import Theme

DEFAULT_COUNT = 100
GOLDEN_RATIO_CONJUGATE = 0.618033988749895


def generate_hex_color(index: int) -> str:
    hue = (index * GOLDEN_RATIO_CONJUGATE) % 1.0
    saturation = 0.62
    value = 0.92
    red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
    return f"#{int(red * 255):02X}{int(green * 255):02X}{int(blue * 255):02X}"


async def load_existing_theme_data(session: AsyncSession) -> tuple[set[str], set[str]]:
    rows = (await session.execute(select(Theme.name, Theme.color))).all()
    names = {name for name, _ in rows}
    colors = {color for _, color in rows}
    return names, colors


def build_themes_to_insert(
    count: int, existing_names: set[str], existing_colors: set[str]
) -> list[Theme]:
    themes: list[Theme] = []
    name_index = 1
    color_index = 0

    while len(themes) < count:
        name = f"Theme {name_index:03d}"
        name_index += 1

        if name in existing_names:
            continue

        color = generate_hex_color(color_index)
        color_index += 1
        while color in existing_colors:
            color = generate_hex_color(color_index)
            color_index += 1

        themes.append(Theme(name=name, color=color))
        existing_names.add(name)
        existing_colors.add(color)

    return themes


async def seed_themes(count: int) -> int:
    async with async_session_maker() as session:
        existing_names, existing_colors = await load_existing_theme_data(session)
        themes = build_themes_to_insert(count, existing_names, existing_colors)
        session.add_all(themes)
        await session.commit()
        return len(themes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert generated themes into DB")
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"How many themes to insert (default: {DEFAULT_COUNT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count <= 0:
        raise SystemExit("--count must be greater than 0")

    inserted = asyncio.run(seed_themes(args.count))
    print(f"Inserted {inserted} themes")


if __name__ == "__main__":
    main()
