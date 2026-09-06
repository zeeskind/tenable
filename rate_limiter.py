"""Simple per-client request limit."""

import threading
import time
from urllib.parse import parse_qs, urlsplit


MAX_REQUESTS = 5
WINDOW_SECONDS = 5

# client_id -> (window start time, number of requests)
_client_windows = {}
_lock = threading.Lock()


def should_process_req(url: str) -> bool:
    """Return True if this client can make another request."""
    client_id = _get_client_id(url)
    if client_id is None:
        return False

    with _lock:
        now = time.monotonic()
        window = _client_windows.get(client_id)

        # No window, or an old window: start a new one.
        if window is None or now - window[0] >= WINDOW_SECONDS:
            _client_windows[client_id] = (now, 1)
            return True

        # The client already used all five requests.
        if window[1] >= MAX_REQUESTS:
            return False

        _client_windows[client_id] = (window[0], window[1] + 1)
        return True


def _get_client_id(url: str):
    """Get the client ID from /get?client_id=123."""
    if not isinstance(url, str):
        return None

    try:
        values = parse_qs(urlsplit(url).query).get("client_id")
    except ValueError:
        return None

    return values[0] if values and values[0] else None
