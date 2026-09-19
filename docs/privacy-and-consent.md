# Privacy and consent model

The gateway defaults to deny. An event may be prepared for GA4 only when `analytics_storage` is true. Advertising destinations require both `ad_storage` and `ad_user_data` in the conservative demo policy.

The project rejects raw `email`, `phone`, and `phone_number` fields. It does not attempt to decide legal compliance or invent a merchant's consent policy. A real deployment must document:

1. the consent management platform and regional defaults;
2. the lawful basis and retention period for each destination;
3. hashing and normalization rules for any user-provided data;
4. deletion and access procedures;
5. provider-specific data-processing terms.

The in-memory dedupe ledger stores only event IDs and is intentionally not a production persistence design.
