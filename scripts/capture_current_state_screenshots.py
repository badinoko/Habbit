"""Capture current-state full-page screenshots for key HabitFlow screens.

This script seeds demo data against a running local HabitFlow instance, then
captures desktop and mobile full-page screenshots into docs/screenshots/current_state/.
"""

from __future__ import annotations

import asyncio
import os
from datetime import date
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
    ("13_login", "/auth/login"),
    ("14_register", "/auth/register"),
]

AUTH_SHOTS: list[tuple[str, str]] = [
    ("01_home_dashboard", "/"),
    ("02_tasks_list", "/tasks"),
    ("03_habits_list", "/habits?status=active"),
    ("04_stats_overview", "/stats"),
    ("05_stats_tasks", "/stats#stats-tasks"),
    ("06_stats_habits", "/stats?range=30d#stats-habits"),
    ("07_stats_themes", "/stats#stats-themes"),
    ("08_stats_insights", "/stats#stats-insights"),
    ("09_themes_list", "/themes"),
    ("10_task_form", "/tasks/new"),
    ("11_habit_form", "/habits/new"),
    ("12_theme_form", "/themes/new"),
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


async def seed_capture_account(browser: Browser, base: str) -> tuple[str, str]:
    context = await browser.new_context(
        viewport=DESKTOP_VIEWPORT,
        device_scale_factor=1,
        extra_http_headers={"Cache-Control": "no-cache"},
    )
    page = await context.new_page()
    email = f"currentstate.{uuid4().hex[:16]}@example.com"
    password = "CurrentState1!"

    try:
        await register_or_login(page, base, email, password)
        await seed_demo_data(page, context, base)
        await complete_first_n_tasks(page, base, 2)
        await _goto(page, f"{base}/")
        await ensure_demo_quote(page)
    finally:
        await context.close()

    return email, password


async def open_existing_authenticated_context(
    browser: Browser,
    base: str,
    viewport: dict[str, int],
    *,
    email: str,
    password: str,
) -> tuple[BrowserContext, Page]:
    context = await browser.new_context(
        viewport=viewport,
        device_scale_factor=1,
        extra_http_headers={"Cache-Control": "no-cache"},
    )
    page = await context.new_page()
    await register_or_login(page, base, email, password)
    await _goto(page, f"{base}/")
    await ensure_demo_quote(page)
    return context, page


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
    raise NotImplementedError


async def capture_auth_set_with_account(
    browser: Browser,
    base: str,
    kind: str,
    *,
    email: str,
    password: str,
) -> None:
    viewport = DESKTOP_VIEWPORT if kind == "desktop" else MOBILE_VIEWPORT
    context, page = await open_existing_authenticated_context(
        browser,
        base,
        viewport,
        email=email,
        password=password,
    )
    try:
        for slug, suffix in AUTH_SHOTS:
            await capture_page(page, base, suffix, shot_path(kind, slug))
    finally:
        await context.close()


async def main() -> int:
    base = os.environ.get("SCREENSHOT_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
    captured_on = date.today().isoformat()
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    MOBILE_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            shared_email, shared_password = await seed_capture_account(browser, base)
            await capture_guest_set(browser, base, "desktop")
            await capture_auth_set_with_account(
                browser,
                base,
                "desktop",
                email=shared_email,
                password=shared_password,
            )
            await capture_guest_set(browser, base, "mobile")
            await capture_auth_set_with_account(
                browser,
                base,
                "mobile",
                email=shared_email,
                password=shared_password,
            )
        finally:
            await browser.close()

    readme = OUTPUT_ROOT / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# HabitFlow Current State Screenshots",
                "",
                f"Captured on: {captured_on}",
                f"Base URL: `{base}`",
                "",
                "This folder is the baseline screenshot pack for redesign and frontend audit work.",
                "Use it together with `docs/project/overview.md` and the imported Besedka reference kit.",
                "",
                "Viewports:",
                f"- desktop: `{DESKTOP_VIEWPORT['width']}x{DESKTOP_VIEWPORT['height']}`",
                f"- mobile: `{MOBILE_VIEWPORT['width']}x{MOBILE_VIEWPORT['height']}`",
                "",
                "Screen set:",
                "- 01 home dashboard",
                "- 02 tasks list",
                "- 03 habits list",
                "- 04 stats overview",
                "- 05 stats tasks",
                "- 06 stats habits",
                "- 07 stats themes",
                "- 08 stats insights",
                "- 09 themes list",
                "- 10 task form",
                "- 11 habit form",
                "- 12 theme form",
                "- 13 login",
                "- 14 register",
                "",
                "Seeded users:",
                f"- desktop capture user: `{shared_email}`",
                f"- mobile capture user: `{shared_email}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Saved screenshots to {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
