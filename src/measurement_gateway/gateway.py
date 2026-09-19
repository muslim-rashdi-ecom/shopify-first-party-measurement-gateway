"""Core ingestion and forwarding decision logic."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .consent import allowed_channels, consent_summary
from .dedupe import DedupeLedger
from .models import MeasurementEvent, normalize_event
from .providers import BUILDERS


@dataclass(frozen=True)
class GatewayDecision:
    status: str
    event_id: str
    reason: str
    channels: tuple[str, ...] = ()
    payloads: Mapping[str, Mapping[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MeasurementGateway:
    """Validate events, apply consent, deduplicate, and build payloads."""

    def __init__(self, ledger: DedupeLedger | None = None) -> None:
        self.ledger = ledger or DedupeLedger()

    def ingest(self, payload: Mapping[str, Any]) -> GatewayDecision:
        event: MeasurementEvent = normalize_event(payload)
        if self.ledger.check_and_remember(event.event_id):
            return GatewayDecision("duplicate", event.event_id, "event_id already processed")

        channels = allowed_channels(event)
        if not channels:
            return GatewayDecision(
                "blocked",
                event.event_id,
                "consent does not authorize an analytics or advertising destination",
            )

        payloads = {channel: BUILDERS[channel](event) for channel in channels}
        return GatewayDecision(
            "accepted",
            event.event_id,
            "event validated and prepared for test-mode forwarding",
            channels=channels,
            payloads=payloads,
        )

    @staticmethod
    def inspect_consent(payload: Mapping[str, Any]) -> dict[str, bool]:
        event = normalize_event(payload)
        return consent_summary(event.consent)
