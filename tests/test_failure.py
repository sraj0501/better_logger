from __future__ import annotations

from runtime_narrative.failure import summarize_exception


def test_summarize_exception_extracts_leaf_frame() -> None:
    def inner() -> None:
        raise KeyError("missing")

    try:
        inner()
    except KeyError as e:
        summary = summarize_exception(type(e), e, e.__traceback__)

    assert summary.error_type == "KeyError"
    assert "missing" in summary.error_message
    assert summary.function == "inner"
    assert "KeyError" in summary.exception_chain
    assert "inner" in summary.traceback_text
