# Archive Index

This folder stores frozen snapshots of large working documents after they are replaced with lighter active versions.

## Purpose

Archives exist to:

- preserve full historical context without loss;
- keep active handoff documents readable;
- avoid thousand-line working files becoming the default surface for every new session.

## Archive Rules

### When to archive

Archive a working document when it grows to roughly `1000+` lines or becomes clearly unwieldy for normal session use.

Primary candidates:

- `docs/project/progress.md`
- `docs/project/overview.md`

Secondary candidates:

- long-lived review notes in `docs/reviews/`
- other operational docs that become too large for routine reading

### How to archive

1. Copy the current file into this tree as-is, without rewriting history.
2. Use a dated filename.
3. Replace the active file with a lighter continuation document.
4. Add links both ways:
   - from the new active file to the archive snapshot;
   - from this index to the archived snapshot.

### Naming

Recommended naming:

- `docs/archive/project/progress-YYYY-MM-DD.md`
- `docs/archive/project/overview-YYYY-MM-DD.md`
- `docs/archive/reviews/<name>-YYYY-MM-DD.md`

### What the new active file must keep

For `progress.md`:

- short summary of prior phases;
- links to archived snapshots;
- append-only continuation from the new starting point.

For `overview.md`:

- the current task dashboard;
- only still-relevant open or recently important items;
- links to archived overview snapshots that preserve older states.

### What must never happen

- do not delete the old content without archiving it first;
- do not silently compress history into vague prose;
- do not mark tasks `DONE` just because an overview was rebuilt;
- do not rewrite archived snapshots after freezing them, unless the user explicitly asks for a repair.

## Current State

No archived snapshots have been created yet in this repository.
