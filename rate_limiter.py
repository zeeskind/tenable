"""Simple per-client request limit."""

import threading
import time
from urllib.parse import parse_qs, urlsplit


MAX_REQUESTS = 5
WINDOW_SECONDS = 5


class ClientState:
    """The data that belongs to one client."""

    def __init__(self):
        self.window_start = None
        self.request_count = 0
        self.lock = threading.Lock()


# Each client ID points to its own state object.
_clients = {}
_new_client_lock = threading.Lock()


def should_process_req(url: str) -> bool:
    """Return True if this client can make another request."""
    client_id = _get_client_id(url)
    if client_id is None:
        return False

    client = _get_client(client_id)

    # Different clients use different locks, so they do not block each other.
    with client.lock:
        now = time.monotonic()

        if (
            client.window_start is None
            or now - client.window_start >= WINDOW_SECONDS
        ):
            client.window_start = now
            client.request_count = 1
            return True

        if client.request_count >= MAX_REQUESTS:
            return False

        client.request_count += 1
        return True


def _get_client(client_id: str) -> ClientState:
    """Get an existing client, or create it once."""
    client = _clients.get(client_id)
    if client is not None:
        return client

    # This lock is only needed while adding a new client to the dictionary.
    # Requests for clients that already exist do not wait for this lock.
    with _new_client_lock:
        client = _clients.get(client_id)
        if client is None:
            client = ClientState()
            _clients[client_id] = client
        return client


def _get_client_id(url: str):
    """Get the client ID from /get?client_id=123."""
    if not isinstance(url, str):
        return None

    try:
        values = parse_qs(urlsplit(url).query).get("client_id")
    except ValueError:
        return None

    return values[0] if values and values[0] else None
