# HabitFlow Frontend Redesign Brief

## Product Overview

HabitFlow is a personal productivity web app for managing themes, tasks, and habits. It is designed around everyday planning and habit tracking rather than team collaboration.

The product is personal and owner-scoped:

- each user sees only their own data
- guests can open public pages but cannot manage personal content
- authenticated users can create, update, complete, and delete their own themes, tasks, and habits

Primary goals:

- organize work into themes
- track active and completed tasks
- create recurring habits with flexible schedules
- mark progress daily and monitor streaks
- quickly scan summary stats from the dashboard/sidebar

## Primary User Types

### Guest

- can view public pages like home, lists, login, and register
- cannot manage data
- personal data views effectively appear empty or unavailable

### Authenticated User

- can manage their own themes, tasks, and habits
- can log in, log out, and optionally use Google sign-in

## Core Data Structures

### User

- `id: UUID`
- `email: string`
- `is_active: boolean`
- `created_at: datetime`
- `updated_at: datetime`

### Theme

- `id: UUID`
- `owner_id: UUID`
- `name: string`
- `color: string` in `#RRGGBB`
- `created_at: datetime`
- `updated_at: datetime`

Rules:

- real theme names are unique per user
- reserved title `"Все темы"` is not allowed for real themes
- a theme color must be unique per user

UI concepts related to themes:

- `All themes` filter option exists in the sidebar
- `No theme` option exists when assigning a task or habit

### Priority

- `id: UUID`
- `name: string`
- `weight: integer`
- `color: string | null`

Supported task priority aliases:

- `low`
- `medium`
- `high`

### Task

- `id: UUID`
- `owner_id: UUID`
- `name: string`
- `description: string | null`
- `theme_id: UUID | null`
- `priority_id: UUID`
- `completed_at: datetime | null`
- `created_at: datetime`
- `updated_at: datetime`

Task view data used by the UI:

- `priority: "low" | "medium" | "high"`
- `theme_name: string | null`
- `theme_color: string | null`

Important product note:

- tasks do not currently have due dates in the backend contract

### Habit

- `id: UUID`
- `owner_id: UUID`
- `name: string`
- `description: string | null`
- `theme_id: UUID | null`
- `schedule_type: "daily" | "weekly_days" | "monthly_day" | "yearly_date" | "interval_cycle"`
- `schedule_config: object`
- `starts_on: date | null`
- `ends_on: date | null`
- `is_archived: boolean`
- `created_at: datetime`
- `updated_at: datetime`

Habit schedule shapes:

- `daily` -> `{}`
- `weekly_days` -> `{ days: ("mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun")[] }`
- `monthly_day` -> `{ day: number }`
- `yearly_date` -> `{ month: number, day: number }`
- `interval_cycle` -> `{ active_days: number, break_days: number }`

Habit view data used by the UI:

- `theme_name: string | null`
- `theme_color: string | null`
- `current_streak: number`
- `completed_today: boolean`
- `due_today: boolean`
- `progress_percent: number`

### HabitCompletion

- `id: UUID`
- `habit_id: UUID`
- `completed_on: date`
- `note: string | null`
- `created_at: datetime`
- `updated_at: datetime`

### SidebarStats

- `total_tasks: number`
- `active_tasks: number`
- `total_habits: number`
- `active_habits: number`
- `due_habits_today: number`
- `completed_habits_today: number`
- `success_rate: number`

### UI Session State

Used by the current product behavior:

- `selected_theme: string | null`
- `current_user: User | null`
- `google_oauth_enabled: boolean`

## Key User Actions

### Authentication

- register with email and password
- log in with email and password
- log out
- start Google sign-in when enabled

### Theme Management

- view theme list
- create theme
- edit theme
- delete theme
- choose a theme as the active app-wide filter
- reset the filter to `All themes`

### Task Management

- view task list
- create task
- edit task
- delete task
- mark task complete
- mark completed task incomplete
- assign task to a theme or leave it without a theme
- set task priority
- filter tasks by status
- sort tasks by date created, date updated, name, or priority
- paginate through tasks

### Habit Management

- view habit list
- create habit
- edit habit
- delete habit
- assign habit to a theme or leave it without a theme
- choose a schedule type
- configure a schedule
- define an optional start and end period
- mark habit completed for today
- view current streak and daily completion state
- filter habits by status
- filter habits by schedule type
- sort habits by date created, date updated, name, or streak
- paginate through habits

### Dashboard Actions

- review recent active tasks
- review due-today habits
- jump to create task
- jump to create habit
- jump to list pages

## Screens To Redesign

### Home Dashboard

Contains:

- welcome section
- recent active tasks
- due-today habits
- quick actions
- sidebar theme filter
- sidebar stats

Current content limits:

- up to 5 active tasks
- up to 4 due-today habits

### Authentication

- login page
- register page

### Themes

- themes list / manager
- create theme form
- edit theme form

### Tasks

- tasks list
- create task form
- edit task form

### Habits

- habits list
- create habit form
- edit habit form

### System / Feedback Screens

- generic message / error page
- Google OAuth error state
- placeholder statistics page

## Critical UI States

### Collection States

- default populated state
- empty state
- filtered empty state
- paginated state

### Request States

- loading
- success feedback
- inline or page-level error
- validation error

### Auth States

- guest navigation
- authenticated navigation
- already authenticated redirect behavior

### Item States

- task active
- task completed
- habit active
- habit completed today
- habit not due today
- habit archived
- active selected theme

### Disabled States

- completion button disabled for archived habits
- completion button disabled for already completed-today habits
- completion button disabled for habits not due today
- pagination boundary buttons disabled

## Functional Constraints For Design

### Product Scope

- this is a personal app, not a team product
- there are no admins, team roles, members, or workspaces
- there is no real statistics page yet; only a placeholder exists

### Content Rules

- users only manage their own content
- deleting a theme removes the theme assignment from related tasks and habits
- tasks and habits can exist without a theme
- tasks currently support priority, not due dates
- habits support recurring schedules and optional time-bounded periods

### Filtering, Sorting, Pagination

- theme filter persists across task, habit, and dashboard views
- task filters:
  - `status = active | completed`
  - `sort = created_at | updated_at | name | priority`
  - `order = asc | desc`
- habit filters:
  - `status = todays | active | completed | archived`
  - `schedule_type = all | daily | weekly_days | monthly_day | yearly_date | interval_cycle`
  - `sort = created_at | updated_at | name | streak`
  - `order = asc | desc`
- list pages use pagination with `page` and `per_page`

### Validation Constraints

- theme name max length: `24`
- theme color: valid hex color
- task name max length: `46`
- habit name max length: `46`
- habit description max length: `200`
- password length: `8..256`
- habit end date cannot be earlier than start date
- weekly habits require at least one weekday
- monthly day must be `1..31`
- yearly month must be `1..12`
- yearly day must be valid for the chosen month
- interval-cycle values must be positive integers

### Localization

- current UI copy is Russian
- redesign should assume Russian-first content unless intentionally redefining product language

## Backend-Relevant Constraints That Affect Design

These are important enough to preserve in the redesign brief:

- the app is still web-first, not a full standalone SPA product
- task creation is a real supported flow
- habit creation/editing depends on schedule configuration UI
- dashboard stats are lightweight summaries, not deep analytics
- theme selection is a major cross-screen navigation/filter pattern

## Do Not Invent

Avoid introducing these as existing product features unless the product is intentionally expanded:

- task due dates
- subtasks
- reminders or notifications
- collaboration features
- teams or shared spaces
- admin dashboards
- advanced reporting or charts
- recurring tasks separate from habits
