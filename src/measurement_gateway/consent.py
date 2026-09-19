"""Consent-to-channel policy used before payload generation."""

from __future__ import annotations

from .models import ConsentState, MeasurementEvent


def allowed_channels(event: MeasurementEvent) -> tuple[str, ...]:
    """Return channels allowed by the event's consent state.

    GA4 requires analytics consent. Advertising destinations require ad storage
    and ad-user-data consent in this conservative demo policy.
    """

    channels: list[str] = []
    if event.consent.analytics_storage:
        channels.append("ga4")
    if event.consent.ad_storage and event.consent.ad_user_data:
        channels.extend(("meta", "tiktok", "google_ads"))
    return tuple(channels)


def consent_summary(consent: ConsentState) -> dict[str, bool]:
    """Return a serializable consent summary for logs and reports."""

    return {
        "analytics_storage": consent.analytics_storage,
        "ad_storage": consent.ad_storage,
        "ad_user_data": consent.ad_user_data,
        "ad_personalization": consent.ad_personalization,
    }
