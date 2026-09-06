# Tenable Interview 2

This project limits requests from each client.

## Rule

A client can make 5 requests in 5 seconds.

- Requests 1 through 5 return `True`.
- Request 6 returns `False`.
- After 5 seconds, the next request starts a new window.
- Each client has its own limit.

The client ID is in the URL:

```text
/get?client_id=client-123
```

## Simple design

The code keeps a dictionary of clients:

```text
client ID -> ClientState object
```

Each `ClientState` object stores the request count, window start time, and its own lock.

- Different clients use different locks, so they do not wait for each other.
- Requests from the same client use the same lock, so their count stays correct.
- A short separate lock is used only when a new client is added to the dictionary.

## Use it

```python
from rate_limiter import should_process_req

if should_process_req("/get?client_id=client-123"):
    process_request()
```

## Tests

Tests are separate in `tests/test_rate_limiter.py`:

```bash
python -m unittest discover -s tests -v
```
