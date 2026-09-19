"""Consent-aware e-commerce event gateway."""

from .gateway import GatewayDecision, MeasurementGateway
from .models import ConsentState, EventValidationError, MeasurementEvent, normalize_event

__all__ = [
    "ConsentState",
    "EventValidationError",
    "GatewayDecision",
    "MeasurementEvent",
    "MeasurementGateway",
    "normalize_event",
]
