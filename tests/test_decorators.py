from __future__ import annotations

import asyncio

import pytest

from runtime_narrative import runtime_narrative_story
from runtime_narrative.events import FailureOccurred

from tests.conftest import CapturingRenderer


def test_runtime_narrative_story_forwards_failure_diagnostics() -> None:
    cap = CapturingRenderer()

    @runtime_narrative_story("Decorated", renderers=[cap], failure_diagnostics="rich")
    def boom() -> None:
        raise RuntimeError("decorated")

    with pytest.raises(RuntimeError):
        boom()

    fail = next(e for e in cap.events if isinstance(e, FailureOccurred))
    assert fail.diagnostics_mode == "rich"
    assert fail.locals_by_frame is not None


def test_runtime_narrative_story_async() -> None:
    cap = CapturingRenderer()

    @runtime_narrative_story("AsyncDeco", renderers=[cap])
    async def ok() -> int:
        return 42

    assert asyncio.run(ok()) == 42
