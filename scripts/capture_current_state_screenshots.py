"""Capture current-state full-page screenshots for key HabitFlow screens.

This script seeds demo data against a running local HabitFlow instance, then
captures desktop and mobile full-page screenshots into docs/screenshots/current_state/.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import uuid4

from capture_readme_screenshots import (
    _goto,
    complete_first_n_tasks,
    ensure_demo_quote,
    register_or_login,
    seed_demo_data,
)
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = REPO_ROOT / "docs" / "screenshots" / "current_state"
DESKTOP_DIR = OUTPUT_ROOT / "desktop"
MOBILE_DIR = OUTPUT_ROOT / "mobile"

DESKTOP_VIEWPORT = {"width": 1920, "height": 1080}
MOBILE_VIEWPORT = {"width": 390, "height": 844}

GUEST_SHOTS: list[tuple[str, str]] = [
    ("09_login", "/auth/login"),
    ("10_register", "/auth/register"),
]

AUTH_SHOTS: list[tuple[str, str]] = [
    ("01_home_dashboard", "/"),
    ("02_tasks_list", "/tasks"),
    ("03_habits_list", "/habits?status=active"),
    ("04_stats", "/stats?range=30d"),
    ("05_themes_list", "/themes"),
    ("06_task_form", "/tasks/new"),
    ("07_habit_form", "/habits/new"),
    ("08_theme_form", "/themes/new"),
]


def shot_path(kind: str, slug: str) -> Path:
    if kind == "desktop":
        return DESKTOP_DIR / f"{slug}_desktop.png"
    return MOBILE_DIR / f"{slug}_mobile.png"


async def capture_page(page: Page, base: str, suffix: str, path: Path) -> None:
    await _goto(page, f"{base}{suffix}")
    await page.screenshot(path=str(path), full_page=True)


async def prepare_authenticated_context(
    browser: Browser, base: str, viewport: dict[str, int]
) -> tuple[BrowserContext, Page, str]:
    context = await browser.new_context(
        viewport=viewport,
        device_scale_factor=1,
        extra_http_headers={"Cache-Control": "no-cache"},
    )
    page = await context.new_page()
    email = f"currentstate.{uuid4().hex[:16]}@example.com"
    password = "CurrentState1!"
    await register_or_login(page, base, email, password)
    await seed_demo_data(page, context, base)
    await complete_first_n_tasks(page, base, 2)
    await _goto(page, f"{base}/")
    await ensure_demo_quote(page)
    return context, page, email


async def capture_guest_set(browser: Browser, base: str, kind: str) -> None:
    viewport = DESKTOP_VIEWPORT if kind == "desktop" else MOBILE_VIEWPORT
    context = await browser.new_context(viewport=viewport, device_scale_factor=1)
    page = await context.new_page()
    try:
        for slug, suffix in GUEST_SHOTS:
            await capture_page(page, base, suffix, shot_path(kind, slug))
    finally:
        await context.close()


async def capture_auth_set(browser: Browser, base: str, kind: str) -> str:
    viewport = DESKTOP_VIEWPORT if kind == "desktop" else MOBILE_VIEWPORT
    context, page, email = await prepare_authenticated_context(browser, base, viewport)
    try:
        for slug, suffix in AUTH_SHOTS:
            await capture_page(page, base, suffix, shot_path(kind, slug))
    finally:
        await context.close()
    return email


async def main() -> int:
    base = os.environ.get("SCREENSHOT_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    MOBILE_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            await capture_guest_set(browser, base, "desktop")
            desktop_email = await capture_auth_set(browser, base, "desktop")
            await capture_guest_set(browser, base, "mobile")
            mobile_email = await capture_auth_set(browser, base, "mobile")
        finally:
            await browser.close()

    readme = OUTPUT_ROOT / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# HabitFlow Current State Screenshots",
                "",
                "Captured on: 2026-03-21",
                f"Base URL: `{base}`",
                "",
                "Viewports:",
                f"- desktop: `{DESKTOP_VIEWPORT['width']}x{DESKTOP_VIEWPORT['height']}`",
                f"- mobile: `{MOBILE_VIEWPORT['width']}x{MOBILE_VIEWPORT['height']}`",
                "",
                "Screen set:",
                "- 01 home dashboard",
                "- 02 tasks list",
                "- 03 habits list",
                "- 04 stats",
                "- 05 themes list",
                "- 06 task form",
                "- 07 habit form",
                "- 08 theme form",
                "- 09 login",
                "- 10 register",
                "",
                "Seeded users:",
                f"- desktop capture user: `{desktop_email}`",
                f"- mobile capture user: `{mobile_email}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Saved screenshots to {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
