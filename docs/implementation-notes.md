# Implementation notes

## Why one event contract

Campaign and analytics systems often disagree because the same commerce action is named, timestamped, or deduplicated differently. A provider-neutral contract makes the decision visible before any payload is sent.

## Test-mode boundary

The repository is useful without platform credentials. Tests verify validation, consent gating, idempotency, and payload shape. A production adapter would add authenticated HTTP delivery, retries, rate limits, secret management, observability, and dead-letter handling.

## Portfolio evidence boundary

This project proves that the author can reason about and implement a measurement architecture. It does not prove access to a production Shopify store or advertising account.
