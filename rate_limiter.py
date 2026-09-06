"""A small, thread-safe fixed-window request limiter."""

from dataclasses import dataclass
import time
from threading import Lock
from typing import Callable, Optional
from urllib.parse import parse_qs, urlsplit


MAX_REQUESTS = 5
WINDOW_SECONDS = 5.0
CLIENT_ID_PARAMETER = "client_id"


@dataclass
class _ClientWindow:
    started_at: float
    request_count: int


class RateLimiter:
    """Allow at most five requests per client in each five-second window.

    The limiter is safe to use from multiple threads in one Python process.
    ``clock`` is injectable so the time-window behavior can be tested without
    waiting in real time.
    """

    def __init__(
        self,
        max_requests: int = MAX_REQUESTS,
        window_seconds: float = WINDOW_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._clock = clock
        self._client_windows: dict[str, _ClientWindow] = {}
        self._lock = Lock()

    def should_process_req(self, url: str) -> bool:
        """Return whether the request in ``url`` is within its client's limit.

        The client ID is expected in the URL's ``client_id`` query parameter,
        for example: ``/get?client_id=client-123``. Invalid URLs or URLs
        without a client ID are rejected.
        """

        client_id = _get_client_id(url)
        if client_id is None:
            return False

        now = self._clock()

        # The complete read/update operation must be atomic. Otherwise two
        # simultaneous requests could both observe the same request count and
        # allow more than the configured limit.
        with self._lock:
            client_window = self._client_windows.get(client_id)

            if (
                client_window is None
                or now - client_window.started_at >= self._window_seconds
            ):
                self._client_windows[client_id] = _ClientWindow(
                    started_at=now,
                    request_count=1,
                )
                return True

            if client_window.request_count >= self._max_requests:
                return False

            client_window.request_count += 1
            return True


def _get_client_id(url: str) -> Optional[str]:
    """Extract a non-empty client ID from a URL."""

    if not isinstance(url, str):
        return None

    try:
        query = parse_qs(urlsplit(url).query)
    except ValueError:
        return None

    client_ids = query.get(CLIENT_ID_PARAMETER)
    if not client_ids or not client_ids[0]:
        return None

    return client_ids[0]


# This is the application-wide limiter for callers that only need the
# requested function. A RateLimiter instance can be used directly in tests or
# when an application needs separate limits.
_default_rate_limiter = RateLimiter()


def should_process_req(url: str) -> bool:
    """Return whether a request should be processed by the default limiter."""

    return _default_rate_limiter.should_process_req(url)
