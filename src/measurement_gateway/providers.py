"""Provider payload builders.

These functions do not make network calls. They create inspectable payloads so
the contract can be tested before a merchant supplies credentials and endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .models import MeasurementEvent


META_EVENT_NAMES = {
    "page_view": "PageView",
    "view_item": "ViewContent",
    "add_to_cart": "AddToCart",
    "begin_checkout": "InitiateCheckout",
    "add_payment_info": "AddPaymentInfo",
    "purchase": "Purchase",
}


def _unix_seconds(value: datetime) -> int:
    return int(value.timestamp())


def build_ga4_payload(event: MeasurementEvent) -> dict[str, Any]:
    return {
        "client_id": event.client_id,
        "events": [{"name": event.name, "params": {**event.properties, "event_id": event.event_id}}],
    }


def build_meta_payload(event: MeasurementEvent) -> dict[str, Any]:
    return {
        "data": [
            {
                "event_name": META_EVENT_NAMES[event.name],
                "event_time": _unix_seconds(event.occurred_at),
                "event_id": event.event_id,
                "action_source": "website",
                "user_data": {"external_id": event.client_id},
                "custom_data": dict(event.properties),
            }
        ]
    }


def build_tiktok_payload(event: MeasurementEvent) -> dict[str, Any]:
    return {
        "event": event.name,
        "event_id": event.event_id,
        "timestamp": event.occurred_at.isoformat(),
        "context": {"user": {"external_id": event.client_id}},
        "properties": dict(event.properties),
    }


def build_google_ads_payload(event: MeasurementEvent) -> dict[str, Any]:
    return {
        "conversion_event": event.name,
        "event_id": event.event_id,
        "timestamp": event.occurred_at.isoformat(),
        "user_provided_data": {"external_id": event.client_id},
        "value": event.properties.get("value"),
        "currency": event.properties.get("currency"),
    }


BUILDERS = {
    "ga4": build_ga4_payload,
    "meta": build_meta_payload,
    "tiktok": build_tiktok_payload,
    "google_ads": build_google_ads_payload,
}
