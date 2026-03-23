from __future__ import annotations

import pytest

pytest.importorskip("starlette")

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from runtime_narrative import RuntimeNarrativeMiddleware, stage
from runtime_narrative.events import FailureOccurred

from tests.conftest import CapturingRenderer


def test_middleware_wraps_request_in_story_and_stages() -> None:
    cap = CapturingRenderer()

    async def boom(_request):
        with stage("Handle"):
            raise RuntimeError("mw boom")

    app = Starlette(
        routes=[Route("/x", endpoint=boom, methods=["GET"])],
        middleware=[
            Middleware(RuntimeNarrativeMiddleware, renderers=[cap], failure_diagnostics="lean"),
        ],
    )

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/x")
    assert r.status_code == 500

    kinds = [type(e).__name__ for e in cap.events]
    assert "StoryStarted" in kinds
    assert "StageStarted" in kinds
    assert "FailureOccurred" in kinds
    assert "StoryCompleted" in kinds

    fail = next(e for e in cap.events if isinstance(e, FailureOccurred))
    assert "GET /x" in fail.story_name or fail.story_name.endswith("/x")
    assert fail.stage_name == "Handle"


def test_middleware_success_emits_story_completed() -> None:
    # Stages use sync emit(); CapturingRenderer records the full sequence.
    cap = CapturingRenderer()

    async def ok(_request):
        with stage("Done"):
            return PlainTextResponse("ok")

    app = Starlette(
        routes=[Route("/ok", endpoint=ok, methods=["GET"])],
        middleware=[Middleware(RuntimeNarrativeMiddleware, renderers=[cap])],
    )

    client = TestClient(app)
    r = client.get("/ok")
    assert r.status_code == 200
    assert [type(e).__name__ for e in cap.events][-1] == "StoryCompleted"
