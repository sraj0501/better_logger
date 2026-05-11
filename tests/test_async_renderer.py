from __future__ import annotations

import asyncio

import pytest

from runtime_narrative import stage, story
from runtime_narrative.events import FailureOccurred, StageCompleted, StageStarted, StoryCompleted, StoryStarted

from tests.conftest import AsyncCapturingRenderer


def test_async_renderer_story_events_are_awaited_without_stages() -> None:
    """Story boundaries and failure path use emit_async so async renderers are awaited."""
    cap = AsyncCapturingRenderer()

    async def run() -> None:
        async with story("NoStages", renderers=[cap]):
            raise ValueError("direct")

    with pytest.raises(ValueError):
        asyncio.run(run())

    kinds = [type(e).__name__ for e in cap.events]
    assert kinds == ["StoryStarted", "FailureOccurred", "StoryCompleted"]
    assert isinstance(cap.events[0], StoryStarted)
    assert isinstance(cap.events[1], FailureOccurred)
    assert isinstance(cap.events[2], StoryCompleted)


def test_async_renderer_stage_events_are_awaited() -> None:
    """async with stage dispatches via emit_async so async renderer handles are awaited."""
    cap = AsyncCapturingRenderer()

    async def run() -> None:
        async with story("WithStages", renderers=[cap]):
            async with stage("A"):
                async with stage("B"):
                    pass

    asyncio.run(run())

    kinds = [type(e).__name__ for e in cap.events]
    assert kinds == [
        "StoryStarted",
        "StageStarted",
        "StageStarted",
        "StageCompleted",
        "StageCompleted",
        "StoryCompleted",
    ]
    assert isinstance(cap.events[1], StageStarted)
    assert cap.events[1].stage_name == "A"
    assert isinstance(cap.events[2], StageStarted)
    assert cap.events[2].stage_name == "B"
    assert isinstance(cap.events[3], StageCompleted)
    assert isinstance(cap.events[4], StageCompleted)
