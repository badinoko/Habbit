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

1. `docs/README.md` is the map of the documentation tree.
2. `docs/project/overview.md` holds task statuses only.
3. `docs/project/progress.md` is append-only.
4. `docs/project/startup.md` is the first session-handoff file to read in a new chat.
5. `docs/overview.mdc` holds product and architecture context, not task statuses.
6. `README.md` and the contract files in `docs/*.mdc` describe the actual product and technical behavior.

## New Chat Handoff

When preparing a new chat window, provide:

```md
[CODEX.md](CODEX.md) [AGENTS.md](AGENTS.md)

Минимальный bundle:
- [startup.md](docs/project/startup.md)
- [overview.md](docs/project/overview.md)
- [progress.md](docs/project/progress.md)
- [docs README.md](docs/README.md)
- [README.md](README.md)
- [frontend-redesign-contracts.md](frontend-redesign-contracts.md)
```

Then add:

- current checkpoint;
- git/snapshot state;
- what is blocked;
- the next recommended execution mode.
