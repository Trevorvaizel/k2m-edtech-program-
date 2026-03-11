# Discord Health Check Hardening

`check_discord_health.py` now retries transient Discord API failures so temporary network instability does not fail the full check immediately.

## Defaults

- Retries: `2` (3 total attempts)
- Backoff: exponential from `1.5s` (`1.5s`, `3.0s`, ...)
- Request timeout: `20s` per Discord API call

## CLI usage

```bash
python check_discord_health.py --json --retries 3 --retry-backoff-seconds 1.5 --timeout-seconds 25
```

## Environment variable overrides

- `DISCORD_HEALTH_RETRIES`
- `DISCORD_HEALTH_RETRY_BACKOFF_SECONDS`
- `DISCORD_HEALTH_TIMEOUT_SECONDS`

## Retry scope

The script retries only transient errors, including:

- HTTP: `429`, `500`, `502`, `503`, `504`
- Transport/timeouts: timeout/read timeout, temporary failures, connection resets/refused, and similar network interruptions

Non-transient failures (for example `403 Missing Access` or bad configuration) fail fast without retry.
