# Codex Workflow

## Purpose

Keep HabitFlow work reproducible across chat windows and avoid mixing three different states:

1. local ZIP snapshot without git;
2. real checkout linked to the original upstream;
3. personal lab repository used for independent development.

## Bootstrap Rules

1. If `.git` is missing, say so explicitly.
2. Do not pretend the folder is already synchronized with GitHub.
3. Prefer creating a fresh git checkout with history before serious implementation work.
4. Intended remote layout:
   - `upstream` = original author repository
   - `origin` = user's private/public lab repository

## Documentation Rules

1. `docs/project/overview.md` holds task statuses.
2. `docs/project/progress.md` is append-only.
3. `docs/project/startup.md` is the first file to read in a new session.
4. `README.md` and `docs/*.mdc` describe the actual product and technical contracts.

## New Chat Handoff

When preparing a new chat window, provide:

```md
[CODEX.md](CODEX.md) [AGENTS.md](AGENTS.md)

Минимальный bundle:
- [startup.md](docs/project/startup.md)
- [overview.md](docs/project/overview.md)
- [progress.md](docs/project/progress.md)
- [README.md](README.md)
- [frontend-redesign-contracts.md](frontend-redesign-contracts.md)
- [besedka_design_kit README.md](docs/imports/besedka_design_kit_2026-03/README.md)
```

Then add:

- current checkpoint;
- git/snapshot state;
- what is blocked;
- the next recommended execution mode.
