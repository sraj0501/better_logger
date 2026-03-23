from __future__ import annotations

from typing import Any


class CapturingRenderer:
    """Collects all events passed to ``handle`` for assertions."""

    def __init__(self) -> None:
        self.events: list[Any] = []

    def handle(self, event: object) -> None:
        self.events.append(event)


class AsyncCapturingRenderer:
    """Async renderer that records events (for ``emit_async`` paths)."""

    def __init__(self) -> None:
        self.events: list[Any] = []

    async def handle(self, event: object) -> None:
        self.events.append(event)
