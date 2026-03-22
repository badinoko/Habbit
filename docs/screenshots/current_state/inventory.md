# HabitFlow UI Inventory

This file tracks the current unique UI states that matter for screenshot coverage and review.

## Route Layouts

| ID | Route / State | Notes | Current screenshot |
|---|---|---|---|
| UI-01 | `/` dashboard | Main signed-in home screen with sidebar and summary cards | `01_home_dashboard_*` |
| UI-02 | `/tasks` list | Filters, list layout, pagination shell | `02_tasks_list_*` |
| UI-03 | `/habits?status=active` list | Filters plus due/completion cards | `03_habits_list_*` |
| UI-04 | `/themes` list | Theme cards, add-tile, empty/populated state shell | `09_themes_list_*` |
| UI-05 | `/tasks/new` form | Shared form header + task-specific controls | `10_task_form_*` |
| UI-06 | `/habits/new` form | Shared form header + habit schedule controls | `11_habit_form_*` |
| UI-07 | `/themes/new` form | Shared form header + theme creation controls | `12_theme_form_*` |
| UI-08 | `/auth/login` | Guest auth screen | `13_login_*` |
| UI-09 | `/auth/register` | Guest auth screen | `14_register_*` |

## Stats States

These are one route, but they are separate review states because the sticky toolbar changes the visible panel.

| ID | Route / State | Notes | Current screenshot |
|---|---|---|---|
| ST-01 | `/stats` overview | KPI row and default overview panel | `04_stats_overview_*` |
| ST-02 | `/stats#stats-tasks` | Task pulse, summary grid, priority/theme breakdown | `05_stats_tasks_*` |
| ST-03 | `/stats?range=30d#stats-habits` | Habit focus, trend chart, streak/theme breakdown | `06_stats_habits_*` |
| ST-04 | `/stats#stats-themes` | Busiest theme plus top theme lists | `07_stats_themes_*` |
| ST-05 | `/stats#stats-insights` | Auto-generated insight cards | `08_stats_insights_*` |

## Coverage Rule

- Treat stats tabs as distinct UI states even though they share one route.
- Edit forms are not duplicated in this inventory because create/edit share the same layout shell.
- If a future redesign adds a materially new empty state, modal, or mobile-only navigation pattern, add it here before refreshing the screenshot pack.
