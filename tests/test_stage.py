from __future__ import annotations

import pytest

from runtime_narrative import stage, story

from tests.conftest import CapturingRenderer


def test_stage_outside_story_raises() -> None:
    with pytest.raises(RuntimeError, match="must run inside an active story"):
        with stage("Orphan"):
            pass


def test_nested_stages() -> None:
    cap = CapturingRenderer()
    with story("S", renderers=[cap]):
        with stage("Outer"):
            with stage("Inner"):
                pass
    names = [e.__class__.__name__ for e in cap.events]
    assert names.count("StageStarted") == 2
    assert names.count("StageCompleted") == 2
