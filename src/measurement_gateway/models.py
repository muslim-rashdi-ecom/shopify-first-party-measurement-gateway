"""Validated, provider-neutral event contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


STANDARD_EVENTS = frozenset(
    {
        "page_view",
        "view_item",
        "add_to_cart",
        "begin_checkout",
        "add_payment_info",
        "purchase",
    }
)


class EventValidationError(ValueError):
    """Raised when a payload does not meet the public event contract."""


@dataclass(frozen=True)
class ConsentState:
    """The minimum consent state needed to make forwarding decisions."""

    analytics_storage: bool = False
    ad_storage: bool = False
    ad_user_data: bool = False
    ad_personalization: bool = False

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "ConsentState":
        value = value or {}
        return cls(
            analytics_storage=bool(value.get("analytics_storage", False)),
            ad_storage=bool(value.get("ad_storage", False)),
            ad_user_data=bool(value.get("ad_user_data", False)),
            ad_personalization=bool(value.get("ad_personalization", False)),
        )


@dataclass(frozen=True)
class MeasurementEvent:
    """A normalized event safe to pass to provider payload builders."""

    name: str
    event_id: str
    client_id: str
    source: str
    occurred_at: datetime
    properties: Mapping[str, Any] = field(default_factory=dict)
    consent: ConsentState = field(default_factory=ConsentState)

    def __post_init__(self) -> None:
        if self.name not in STANDARD_EVENTS:
            raise EventValidationError(f"Unsupported event name: {self.name}")
        if not self.event_id.strip():
            raise EventValidationError("event_id is required")
        if not self.client_id.strip():
            raise EventValidationError("client_id is required")
        if not self.source.strip():
            raise EventValidationError("source is required")
        if self.occurred_at.tzinfo is None:
            raise EventValidationError("occurred_at must include a timezone")
        forbidden = {"email", "phone", "phone_number"}.intersection(self.properties)
        if forbidden:
            names = ", ".join(sorted(forbidden))
            raise EventValidationError(f"Raw PII fields are not accepted: {names}")


def _parse_timestamp(value: Any) -> datetime:
    if value in (None, ""):
        return datetime.now(timezone.utc)
    if not isinstance(value, str):
        raise EventValidationError("occurred_at must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventValidationError("occurred_at must be an ISO-8601 string") from exc
    if parsed.tzinfo is None:
        raise EventValidationError("occurred_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def normalize_event(payload: Mapping[str, Any]) -> MeasurementEvent:
    """Validate and normalize a JSON-like mapping into an event."""

    if not isinstance(payload, Mapping):
        raise EventValidationError("Event payload must be an object")
    properties = payload.get("properties", {})
    if not isinstance(properties, Mapping):
        raise EventValidationError("properties must be an object")
    return MeasurementEvent(
        name=str(payload.get("name", "")),
        event_id=str(payload.get("event_id", "")),
        client_id=str(payload.get("client_id", "")),
        source=str(payload.get("source", "")),
        occurred_at=_parse_timestamp(payload.get("occurred_at")),
        properties=dict(properties),
        consent=ConsentState.from_mapping(payload.get("consent")),
    )
