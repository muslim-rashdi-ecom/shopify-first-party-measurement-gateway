# Provider contract notes

The gateway returns inspectable payloads for four destinations. It does not send them over the network.

| Destination | Demo builder | Key safeguards |
| --- | --- | --- |
| GA4 | `build_ga4_payload` | Requires analytics consent; preserves `event_id` in parameters |
| Meta | `build_meta_payload` | Uses a stable event name and `event_id`; no raw PII |
| TikTok | `build_tiktok_payload` | Keeps event ID and normalized properties together |
| Google Ads | `build_google_ads_payload` | Keeps conversion event, timestamp, value, and currency explicit |

Before a live integration, validate each destination's current API schema, hashing requirements, retention policy, and account permissions. Platform APIs change; this repository intentionally keeps provider calls behind small adapters.
