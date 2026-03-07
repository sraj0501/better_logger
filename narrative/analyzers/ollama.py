from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..failure import FailureSummary


@dataclass
class OllamaFailureAnalyzer:
    model: str = "qwen2.5-coder:7b"
    endpoint: str = "http://127.0.0.1:11434/api/generate"
    timeout_seconds: float = 12.0
    include_traceback_lines: int = 30

    def analyze_failure(
        self,
        *,
        story_name: str,
        stage_name: str,
        failure: FailureSummary,
        stage_timeline: str,
        progress_percent: int,
    ) -> Optional[str]:
        prompt = self._build_prompt(
            story_name=story_name,
            stage_name=stage_name,
            failure=failure,
            stage_timeline=stage_timeline,
            progress_percent=progress_percent,
        )
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except URLError:
            return None
        except TimeoutError:
            return None
        except Exception:
            return None

        try:
            parsed = json.loads(body)
            text = parsed.get("response", "").strip()
        except Exception:
            return None

        if not text:
            return None
        return text

    def _build_prompt(
        self,
        *,
        story_name: str,
        stage_name: str,
        failure: FailureSummary,
        stage_timeline: str,
        progress_percent: int,
    ) -> str:
        traceback_lines = failure.traceback_text.strip().splitlines()
        traceback_excerpt = "\n".join(traceback_lines[-self.include_traceback_lines :])
        return (
            "You are debugging a Python runtime stage failure.\n"
            "Return concise markdown with exactly four sections:\n"
            "1) Exact Why\n"
            "2) Evidence\n"
            "3) Targeted Fix\n\n"
            "4) Code Changes\n\n"
            "Constraints:\n"
            "- Do not be generic.\n"
            "- Point to the exact failing statement and mechanism.\n"
            "- Mention assumptions only if uncertain.\n\n"
            "Code Changes format:\n"
            "- Provide minimal edit-ready snippets.\n"
            "- Include file path, old line, and new line when possible.\n"
            "- Prefer small targeted diffs over full-file rewrites.\n\n"
            f"Story: {story_name}\n"
            f"Stage: {stage_name}\n"
            f"Error Type: {failure.error_type}\n"
            f"Error Message: {failure.error_message}\n"
            f"Location: {failure.filename}:{failure.lineno} ({failure.function})\n"
            f"Failing Code: {failure.source_line}\n"
            f"Exception Chain: {failure.exception_chain}\n"
            f"Progress: {progress_percent}%\n"
            f"Recent Stages: {stage_timeline}\n\n"
            "Traceback Excerpt:\n"
            f"{traceback_excerpt}\n"
        )
