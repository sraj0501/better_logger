# Project memory (runtime-narrative)

Short-lived notes for humans and agents. Prefer **README.MD** for users and **CLAUDE.md** for deep architecture.

## Current state (2026-05)

- **PyPI / package name:** `runtime-narrative` (`runtime_narrative/`). The git checkout directory may be named `better_logger` or similar.
- **Python:** `>=3.9`. Dev workflow: `uv sync --group dev`, `uv run pytest tests/ -v`.
- **`pyproject.toml`:** Must be valid TOML; `[tool.setuptools]` is followed by `[dependency-groups]` with no stray characters between sections.

## Recent changes

### Async stage event dispatch

- **`async with stage(...)`** (under **`async with story(...)`**) emits `StageStarted` / `StageCompleted` via **`StoryRuntime.emit_async()`**, so async `handle()` on renderers is **awaited** for stage boundaries.
- **`with stage(...)`** still uses **`emit()`** (sync path). Middleware examples may use either; use **`async with stage`** when using async renderers and you need stage hooks awaited.

Implementation: `StoryRuntime.on_stage_started_async` / `on_stage_completed_async` in `runtime_narrative/story.py`; `runtime_narrative/stage.py` routes `__aenter__` / `__aexit__` through those methods.

### Packaging

- Removed an invalid stray backtick line in `pyproject.toml` that broke `uv` / TOML parsing.

## Where to look

| Topic | File |
|-------|------|
| User-facing docs | `README.MD` |
| Agent / contributor architecture | `CLAUDE.md` |
| Cursor / agent project defaults | `AGENTS.md` |
