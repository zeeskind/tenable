# Tenable Interview 2

A simple, thread-safe fixed-window rate limiter for client requests.

## Requirement

Each client may send at most **5 requests during a 5-second window**.

- The first request starts a client's window.
- Requests 2 through 5 in that window are accepted.
- The sixth and later requests are rejected with `False`.
- Once 5 seconds have elapsed, the next request starts a new window.
- Clients have independent windows.

The client ID is expected in the URL's `client_id` query parameter:

```text
/get?client_id=client-123
```

## Usage

```python
from rate_limiter import should_process_req

if should_process_req("/get?client_id=client-123"):
    process_request()
else:
    reject_request()
```

For tests or applications that need an isolated limiter, use `RateLimiter` directly:

```python
from rate_limiter import RateLimiter

limiter = RateLimiter()
limiter.should_process_req("/get?client_id=client-123")
```

## Implementation

`RateLimiter` stores one small counter and start time per client. A lock protects the read-and-update operation, so concurrent requests cannot both observe the same counter and exceed the limit. The operation is constant time, and the in-memory state is suitable for the approximately 5,000 clients in this exercise.

The implementation uses `time.monotonic()` so system clock changes do not affect window durations.

This implementation is safe for multiple threads in one Python process. Separate Python processes do not share the in-memory dictionary; a multi-process deployment would need one shared atomic store, such as Redis or a database, or would need to route a client's requests consistently to the same process.

## Running tests

No third-party dependencies are required:

```bash
python -m unittest discover -s tests -v
```
