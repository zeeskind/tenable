# Tenable Interview 2

This project limits requests from each client.

## Rule

A client can make 5 requests in any rolling 5-second period.

- Requests 1 through 5 return `True`.
- Request 6 returns `False`.
- A rejected request is still counted.
- Old requests leave the queue after 5 seconds.
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

Each `ClientState` has:

- A queue of up to 5 request times
- Its own lock

When a request arrives, old times are removed from the queue. The new request time is then added, whether the request is accepted or rejected.

Different clients use different locks, so they do not wait for each other. Requests from the same client use the same lock.

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
