# Tenable Interview 2

This project limits requests from each client.

## Rule

A client can make 5 requests in 5 seconds.

- Request 1 starts the client's 5-second window.
- Requests 1 through 5 return `True`.
- Request 6 returns `False`.
- After 5 seconds, the next request starts a new window.
- Each client has its own limit.

The client ID is in the URL as a query parameter:

```text
/get?client_id=client-123
```

## Use it

```python
from rate_limiter import should_process_req

if should_process_req("/get?client_id=client-123"):
    process_request()
```

The function uses a dictionary to store each client's count and a lock to make updates safe when several threads call it at the same time. It works inside one Python process. If the app uses several processes, the dictionary must be replaced with shared storage such as Redis.

## Tests

Tests are in `tests/test_rate_limiter.py`. Run them with:

```bash
python -m unittest discover -s tests -v
```
