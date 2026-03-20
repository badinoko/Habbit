"""Capture README screenshots against a running HabitFlow instance.

Registers a fresh user, creates demo themes / tasks / habits, toggles some completions
so statistics look alive, then saves PNGs under assets/.

Themes are created via the HTML form; tasks use form POST and habits use JSON POST on the
same Playwright browser context so cookies and CSRF stay in sync (task/habit forms omit
user themes when the template context loses auth — API routes still enforce ownership).

Requires: poetry run playwright install chromium

Usage:
  SCREENSHOT_BASE_URL=http://127.0.0.1:8000 poetry run python scripts/capture_readme_screenshots.py
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

from playwright.async_api import BrowserContext, Page, async_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets"

DEMO_QUOTE_INNER_HTML = (
    '<blockquote class="quote-card-text">'
    "Маленькие ежедневные улучшения лучше, чем одна грандиозная попытка раз в год."
    '</blockquote><p class="quote-card-author">— Джеймс Клир</p>'
)


async def _goto(page: Page, url: str) -> None:
    await page.goto(url, wait_until="networkidle", timeout=60_000)


async def register_or_login(page: Page, base: str, email: str, password: str) -> None:
    await _goto(page, f"{base}/auth/login")
    await page.locator("#email").fill(email)
    await page.locator("#password").fill(password)
    async with page.expect_navigation(wait_until="networkidle", timeout=60_000):
        await page.locator('form[action="/auth/login"] button[type="submit"]').click()

    if "/auth/login" in page.url:
        await _goto(page, f"{base}/auth/register")
        await page.locator("#email").fill(email)
        await page.locator("#password").fill(password)
        async with page.expect_navigation(wait_until="networkidle", timeout=60_000):
            await page.locator(
                'form[action="/auth/register"] button[type="submit"]'
            ).click()

    if "/auth/register" in page.url or "/auth/login" in page.url:
        body = await page.locator("main").inner_text()
        raise RuntimeError(
            "Не удалось войти или зарегистрироваться. "
            "Проверьте SCREENSHOT_EMAIL / SCREENSHOT_PASSWORD или лимиты на /auth/*. "
            f"Ответ страницы: {body[:500]}",
        )


async def submit_current_form(page: Page) -> None:
    await page.locator("form.item-form button[type='submit']").click()
    await page.wait_for_load_state("networkidle")


async def create_theme(page: Page, base: str, name: str, color_hex: str) -> None:
    await _goto(page, f"{base}/themes/new")
    await page.locator("#name").fill(name)
    await page.evaluate(
        """(hex) => {
            const pick =
                document.querySelector(`input[name="color"][value="${hex}"]`)
                || document.querySelector('input[name="color"][value="randoms"]');
            if (!pick) return;
            pick.checked = true;
            pick.dispatchEvent(new Event("input", { bubbles: true }));
            pick.dispatchEvent(new Event("change", { bubbles: true }));
        }""",
        color_hex,
    )
    await submit_current_form(page)


async def fetch_csrf_token(page: Page, base: str) -> str:
    await _goto(page, f"{base}/")
    token = await page.locator('meta[name="csrf-token"]').get_attribute("content")
    if not token:
        raise RuntimeError("CSRF token meta tag is missing")
    return token


async def scrape_theme_ids(page: Page, base: str) -> dict[str, str]:
    await _goto(page, f"{base}/themes")
    cards = page.locator(".theme-card[data-theme-name]")
    n = await cards.count()
    out: dict[str, str] = {}
    for i in range(n):
        card = cards.nth(i)
        name = await card.get_attribute("data-theme-name")
        tid = await card.get_attribute("data-theme-id")
        if name and tid:
            out[name] = tid
    if len(out) < 1:
        raise RuntimeError(f"No theme cards found on /themes (parsed {out!r})")
    return out


async def api_create_task(
    context: BrowserContext,
    base: str,
    csrf: str,
    *,
    name: str,
    description: str,
    theme_id: str,
    priority: str,
) -> None:
    resp = await context.request.post(
        f"{base}/tasks",
        form={
            "csrf_token": csrf,
            "name": name,
            "description": description,
            "theme_id": theme_id,
            "priority": priority,
        },
    )
    if resp.status >= 400:
        body = await resp.text()
        raise RuntimeError(f"Create task {name!r}: HTTP {resp.status} {body[:600]}")


async def api_create_habit(
    context: BrowserContext,
    base: str,
    csrf: str,
    payload: dict[str, object],
) -> None:
    resp = await context.request.post(
        f"{base}/habits/",
        headers={
            "Content-Type": "application/json",
            "X-CSRFToken": csrf,
        },
        data=json.dumps(payload, default=str),
    )
    if resp.status >= 400:
        body = await resp.text()
        raise RuntimeError(
            f"Create habit {payload.get('name')!r}: HTTP {resp.status} {body[:600]}",
        )


async def ensure_demo_quote(page: Page) -> None:
    if await page.locator(".quote-card-empty").count():
        await page.evaluate(
            """(html) => {
                const el = document.querySelector(".quote-card");
                if (el) el.innerHTML = html;
            }""",
            DEMO_QUOTE_INNER_HTML,
        )


async def complete_first_n_tasks(page: Page, base: str, n: int) -> None:
    await _goto(page, f"{base}/tasks")
    boxes = page.locator(".task-checkbox input[type='checkbox']")
    count = min(n, await boxes.count())
    for i in range(count):
        cb = boxes.nth(i)
        if await cb.is_checked():
            continue
        await cb.click()
        await asyncio.sleep(0.4)


async def seed_demo_data(page: Page, context: BrowserContext, base: str) -> None:
    today = date.today()
    period_start = today - timedelta(days=18)
    period_end = today + timedelta(days=45)

    await create_theme(page, base, "Работа", "#3498DB")
    await create_theme(page, base, "Здоровье", "#2ECC71")
    await create_theme(page, base, "Обучение", "#9B59B6")

    theme_ids = await scrape_theme_ids(page, base)
    csrf = await fetch_csrf_token(page, base)

    def tid(name: str) -> str:
        if name not in theme_ids:
            raise KeyError(f"Theme {name!r} not in {sorted(theme_ids)!r}")
        return theme_ids[name]

    for spec in (
        (
            "Спланировать спринт",
            "Разбить эпики, оценить риски, согласовать с командой.",
            "Работа",
            "high",
        ),
        (
            "Code review отчёта",
            "Проверить PR по статистике и edge cases.",
            "Работа",
            "medium",
        ),
        (
            "Прогулка 30 минут",
            "После обеда, без телефона.",
            "Здоровье",
            "low",
        ),
        (
            "Модуль FastAPI: тесты",
            "Покрыть сервисный слой и редиректы.",
            "Обучение",
            "medium",
        ),
        (
            "Подготовить демо для README",
            "Скриншоты, демо-данные, актуальная статистика.",
            "Обучение",
            "high",
        ),
    ):
        name, desc, theme_name, prio = spec
        await api_create_task(
            context,
            base,
            csrf,
            name=name,
            description=desc,
            theme_id=tid(theme_name),
            priority=prio,
        )

    await api_create_habit(
        context,
        base,
        csrf,
        {
            "name": "Утренняя зарядка",
            "description": "10 минут разминки до завтрака.",
            "theme_id": tid("Здоровье"),
            "schedule_type": "daily",
            "schedule_config": {},
            "starts_on": period_start.isoformat(),
            "ends_on": period_end.isoformat(),
        },
    )
    await api_create_habit(
        context,
        base,
        csrf,
        {
            "name": "Медитация",
            "description": "Дыхание 10 минут.",
            "theme_id": None,
            "schedule_type": "daily",
            "schedule_config": {},
            "starts_on": period_start.isoformat(),
            "ends_on": period_end.isoformat(),
        },
    )
    await api_create_habit(
        context,
        base,
        csrf,
        {
            "name": "Техдолг по пятницам",
            "description": "Мелкий рефакторинг и чистка зависимостей.",
            "theme_id": tid("Работа"),
            "schedule_type": "weekly_days",
            "schedule_config": {"days": ["mon", "tue", "wed", "thu", "fri"]},
            "starts_on": period_start.isoformat(),
            "ends_on": period_end.isoformat(),
        },
    )


async def main() -> int:
    base = os.environ.get("SCREENSHOT_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
    email = os.environ.get(
        "SCREENSHOT_EMAIL",
        f"readme.{uuid4().hex[:16]}@example.com",
    )
    password = os.environ.get("SCREENSHOT_PASSWORD", "ReadmeDemo1!")

    ASSETS.mkdir(parents=True, exist_ok=True)

    shot_specs: list[tuple[str, Path]] = [
        (f"{base}/stats?range=30d", ASSETS / "stats_page.png"),
        (f"{base}/", ASSETS / "main_page.png"),
        (f"{base}/tasks", ASSETS / "tasks_list.png"),
        (f"{base}/habits?status=active", ASSETS / "habits_list.png"),
        (f"{base}/themes", ASSETS / "themes_list.png"),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 900},
            device_scale_factor=1,
            extra_http_headers={"Cache-Control": "no-cache"},
        )
        page = await context.new_page()

        await register_or_login(page, base, email, password)
        await seed_demo_data(page, context, base)
        await complete_first_n_tasks(page, base, 2)

        await _goto(page, f"{base}/")
        await ensure_demo_quote(page)
        await page.screenshot(path=str(ASSETS / "main_page.png"), full_page=True)

        for url, path in shot_specs:
            if path.name == "main_page.png":
                continue
            await _goto(page, url)
            await page.screenshot(path=str(path), full_page=True)

        await browser.close()

    print(f"Wrote {len(shot_specs)} screenshots to {ASSETS} (user {email})")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
