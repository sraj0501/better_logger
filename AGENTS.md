# Agent instructions (runtime-narrative)

This repository implements **Runtime Narrative**: stories and stages with lifecycle events, failure diagnostics, optional LLM analysis, and pluggable renderers.

## Identity

- **Installable name:** `runtime-narrative` (see `pyproject.toml`).
- **Import package:** `runtime_narrative`.
- **Workspace folder** may differ (e.g. `better_logger`); always use paths from the open workspace.

## Commands

```bash
uv sync --group dev
uv run pytest tests/ -v
uv run python examples/basic.py
```

FastAPI demo: `uv run python -m examples.fastapi_app.run` (optional env for LLM: see `README.MD` / `CLAUDE.md`).

## Architecture (concise)

1. **`story(...)`** — `with` / `async with`; sets `current_story`; emits start/complete; on error builds enriched failure and emits `FailureOccurred`.
2. **`stage(...)`** — Must be inside an active story. Sync **`with stage`** → **`emit()`**. **`async with stage`** under **`async with story`** → **`emit_async()`** so async renderers are awaited for stage events.
3. **Context:** `runtime_narrative/context.py` (`ContextVar`s for story and stage stack).
4. **Diagnostics:** `FailureDiagnosticsConfig`, `build_enriched_failure`, env `RUNTIME_NARRATIVE_*` (see README).
5. **Middleware:** `RuntimeNarrativeMiddleware` wraps each request in **`async with story(...)`**; stage dispatch follows the table in point 2 above.

## Documentation map

| Audience | File |
|----------|------|
| End users, env vars, examples | `README.MD` |
| Detailed execution flow, design constraints | `CLAUDE.md` |
| Dated deltas and reminders | `MEMORY.md` |

## When editing

- Match existing style; keep diffs focused.
- Run **`uv run pytest tests/ -v`** after behavior changes.
- Update **README.MD**, **CLAUDE.md**, and **MEMORY.md** when dispatch or public behavior changes.
