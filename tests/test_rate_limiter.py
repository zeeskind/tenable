import unittest
from concurrent.futures import ThreadPoolExecutor

from rate_limiter import RateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.current_time = 0.0

    def __call__(self) -> float:
        return self.current_time

    def advance(self, seconds: float) -> None:
        self.current_time += seconds


class RateLimiterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.limiter = RateLimiter(clock=self.clock)

    def test_allows_five_requests_and_rejects_the_sixth(self) -> None:
        url = "/get?client_id=client-1"

        self.assertEqual(
            [self.limiter.should_process_req(url) for _ in range(6)],
            [True, True, True, True, True, False],
        )

    def test_new_request_at_window_boundary_starts_a_new_window(self) -> None:
        url = "/get?client_id=client-1"

        for _ in range(5):
            self.assertTrue(self.limiter.should_process_req(url))
        self.assertFalse(self.limiter.should_process_req(url))

        self.clock.advance(5.0)

        self.assertTrue(self.limiter.should_process_req(url))
        self.assertTrue(
            self.limiter.should_process_req(url.replace("client-1", "client-2"))
        )

    def test_clients_have_independent_windows(self) -> None:
        for _ in range(5):
            self.assertTrue(
                self.limiter.should_process_req("/get?client_id=client-1")
            )

        self.assertFalse(
            self.limiter.should_process_req("/get?client_id=client-1")
        )
        self.assertTrue(
            self.limiter.should_process_req("/get?client_id=client-2")
        )

    def test_invalid_url_is_rejected(self) -> None:
        self.assertFalse(self.limiter.should_process_req("/get"))
        self.assertFalse(self.limiter.should_process_req("/get?client_id="))
        self.assertFalse(self.limiter.should_process_req("not a valid url"))

    def test_concurrent_requests_are_counted_atomically(self) -> None:
        url = "/get?client_id=client-1"

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(
                executor.map(
                    self.limiter.should_process_req,
                    [url] * 100,
                )
            )

        self.assertEqual(results.count(True), 5)
        self.assertEqual(results.count(False), 95)


if __name__ == "__main__":
    unittest.main()
