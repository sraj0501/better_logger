from __future__ import annotations

import asyncio

import pytest

from runtime_narrative import stage, story
from runtime_narrative.events import FailureOccurred, StoryCompleted, StoryStarted

from tests.conftest import AsyncCapturingRenderer, CapturingRenderer


def test_sync_story_success_emits_started_and_completed() -> None:
    cap = CapturingRenderer()
    with story("S", renderers=[cap]):
        pass
    names = [e.__class__.__name__ for e in cap.events]
    assert names == ["StoryStarted", "StoryCompleted"]
    assert cap.events[-1].success is True


def test_sync_story_failure_emits_failure_with_diagnostics() -> None:
    cap = CapturingRenderer()
    with pytest.raises(ValueError):
        with story("S", renderers=[cap], failure_diagnostics="rich", runtime_environment="development"):
            with stage("Step"):
                x = 1
                raise ValueError("bad")

    names = [e.__class__.__name__ for e in cap.events]
    assert "StoryStarted" in names
    assert "FailureOccurred" in names
    assert names[-1] == "StoryCompleted"
    assert cap.events[-1].success is False

    fail = next(e for e in cap.events if isinstance(e, FailureOccurred))
    assert fail.error_type == "ValueError"
    assert fail.stage_name == "Step"
    assert fail.diagnostics_mode == "rich"
    assert fail.locals_by_frame is not None
    assert "frame_0" in fail.locals_by_frame


def test_sync_story_production_forces_lean() -> None:
    cap = CapturingRenderer()
    with pytest.raises(ValueError):
        with story(
            "S",
            renderers=[cap],
            runtime_environment="production",
            failure_diagnostics="rich",
        ):
            with stage("Step"):
                raise ValueError("x")

    fail = next(e for e in cap.events if isinstance(e, FailureOccurred))
    assert fail.diagnostics_mode == "lean"
    assert fail.locals_by_frame is None


def test_async_story_records_all_stage_events() -> None:
    # async with stage uses emit_async; sync CapturingRenderer.handle still receives stage events.
    cap = CapturingRenderer()

    async def run() -> None:
        async with story("A", renderers=[cap]):
            async with stage("S"):
                pass

    asyncio.run(run())
    assert [e.__class__.__name__ for e in cap.events] == [
        "StoryStarted",
        "StageStarted",
        "StageCompleted",
        "StoryCompleted",
    ]


def test_async_story_failure_enriched_async_path() -> None:
    cap = CapturingRenderer()

    async def run() -> None:
        async with story("A", renderers=[cap], failure_diagnostics="lean"):
            async with stage("Do"):
                raise RuntimeError("async err")

    with pytest.raises(RuntimeError):
        asyncio.run(run())

    fail = next(e for e in cap.events if isinstance(e, FailureOccurred))
    assert fail.diagnostics_mode == "lean"
    assert fail.stack_frames
    assert fail.primary_frame_reason in ("innermost_app", "leaf", "innermost_non_stdlib")


def test_background_analysis_emits_llm_ready() -> None:
    class QuickAnalyzer:
        async def analyze_failure_async(self, **kwargs: object) -> str:
            return "hint"

    cap = AsyncCapturingRenderer()

    async def run() -> None:
        with pytest.raises(ValueError):
            async with story(
                "Bg",
                renderers=[cap],
                failure_analyzer=QuickAnalyzer(),
                background_analysis=True,
            ):
                raise ValueError("fail")
        # Same loop: let the background task finish before run() tears down.
        await asyncio.sleep(0.2)

    asyncio.run(run())
    kinds = [type(e).__name__ for e in cap.events]
    assert "FailureOccurred" in kinds
    assert "StoryCompleted" in kinds
    assert "LLMAnalysisReady" in kinds
