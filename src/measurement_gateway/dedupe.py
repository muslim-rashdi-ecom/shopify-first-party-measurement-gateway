"""Small in-memory idempotency ledger for the demo gateway."""

from __future__ import annotations

from collections import OrderedDict


class DedupeLedger:
    """Remember recent event IDs without storing event payloads."""

    def __init__(self, max_entries: int = 5000) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self.max_entries = max_entries
        self._ids: OrderedDict[str, None] = OrderedDict()

    def check_and_remember(self, event_id: str) -> bool:
        """Return True when the ID was already seen; otherwise remember it."""

        if event_id in self._ids:
            self._ids.move_to_end(event_id)
            return True
        self._ids[event_id] = None
        while len(self._ids) > self.max_entries:
            self._ids.popitem(last=False)
        return False

    def __len__(self) -> int:
        return len(self._ids)
