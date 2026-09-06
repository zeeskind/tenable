"""Simple per-client request limit."""

from collections import deque
import threading
import time
from urllib.parse import parse_qs, urlsplit


MAX_REQUESTS = 5
WINDOW_SECONDS = 5


class ClientState:
    """The request times for one client."""

    def __init__(self):
        self.request_times = deque(maxlen=MAX_REQUESTS)
        self.lock = threading.Lock()


# Each client ID points to its own state object.
_clients = {}
_new_client_lock = threading.Lock()


def should_process_req(url: str) -> bool:
    """Return True if this request is allowed."""
    client_id = _get_client_id(url)
    if client_id is None:
        return False

    client = _get_client(client_id)

    # Different clients use different locks, so they do not block each other.
    with client.lock:
        now = time.monotonic()

        # Remove requests that are no longer in the last five seconds.
        while (
            client.request_times
            and now - client.request_times[0] >= WINDOW_SECONDS
        ):
            client.request_times.popleft()

        allowed = len(client.request_times) < MAX_REQUESTS

        # Store every request, including rejected requests.
        client.request_times.append(now)
        return allowed


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
