from __future__ import annotations

import json
from datetime import datetime
from io import StringIO

from runtime_narrative.events import FailureOccurred
from runtime_narrative.renderer.json_renderer import JsonRenderer


def test_json_renderer_failure_includes_diagnostics_fields() -> None:
    buf = StringIO()
    r = JsonRenderer(output=buf)
    event = FailureOccurred(
        story_id="sid",
        story_name="S",
        stage_name="St",
        error_type="ValueError",
        error_message="m",
        filename="f.py",
        lineno=10,
        function="fn",
        source_line="raise ValueError",
        exception_chain="ValueError: m",
        exact_cause="because",
        llm_analysis=None,
        stage_timeline="x",
        progress_percent=0,
        completed_stages=0,
        total_stages=1,
        timestamp=datetime(2020, 1, 1, 12, 0, 0),
        traceback_text="Traceback...",
        diagnostics_mode="rich",
        primary_frame_reason="innermost_app",
        stack_frames=[{"index": 0, "filename": "f.py", "kind": "app", "is_primary": True}],
        source_snippet="> 10 | raise",
        compressed_stack_summary="1 app frame(s), 0 other",
        hidden_frame_count=0,
        traceback_truncated=False,
        locals_by_frame=None,
        redaction_removed_keys=0,
    )
    r.handle(event)
    buf.seek(0)
    data = json.loads(buf.read())
    assert data["event"] == "FailureOccurred"
    assert data["diagnostics_mode"] == "rich"
    assert data["primary_frame_reason"] == "innermost_app"
    assert data["stack_frames"][0]["kind"] == "app"
    assert data["traceback_text"] == "Traceback..."
