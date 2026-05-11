from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import Any

from .context import current_stage_stack, current_story


@dataclass
class StageRecord:
    name: str
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None
    duration_seconds: float | None = None
    completed: bool = False
    failed: bool = False


class stage:
    def __init__(self, name: str):
        self.name = name
        self.record = StageRecord(name=name)

    def _bind_to_story(self) -> Any:
        story_runtime = current_story.get()
        if story_runtime is None:
            raise RuntimeError("stage() must run inside an active story() context")

        story_runtime.register_stage(self.record)
        stack = list(current_stage_stack.get())
        stack.append(self.record)
        current_stage_stack.set(stack)
        return story_runtime

    def _finalize_timestamps_and_stack(self, exc_type: type[BaseException] | None) -> tuple[Any | None, bool]:
        """Pop stack, set failed/completed flags. Returns (story_runtime, emit_stage_completed)."""
        ended_at = datetime.now()
        self.record.ended_at = ended_at
        self.record.duration_seconds = (ended_at - self.record.started_at).total_seconds()

        story_runtime = current_story.get()
        if story_runtime is not None and exc_type is not None:
            story_runtime.failed_stage_name = self.record.name

        stack = list(current_stage_stack.get())
        if stack:
            stack.pop()
        current_stage_stack.set(stack)

        if story_runtime is None:
            return None, False

        if exc_type is None:
            self.record.completed = True
            return story_runtime, True

        self.record.failed = True
        return story_runtime, False

    def __enter__(self) -> StageRecord:
        story_runtime = self._bind_to_story()
        story_runtime.on_stage_started(self.record)
        return self.record

    async def __aenter__(self) -> StageRecord:
        story_runtime = self._bind_to_story()
        await story_runtime.on_stage_started_async(self.record)
        return self.record

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> bool:
        story_runtime, emit_completed = self._finalize_timestamps_and_stack(exc_type)
        if story_runtime is not None and emit_completed:
            await story_runtime.on_stage_completed_async(self.record)
        return False

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> bool:
        story_runtime, emit_completed = self._finalize_timestamps_and_stack(exc_type)
        if story_runtime is not None and emit_completed:
            story_runtime.on_stage_completed(self.record)
        return False
