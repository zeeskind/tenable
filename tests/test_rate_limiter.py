import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import rate_limiter
from rate_limiter import should_process_req


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        rate_limiter._clients.clear()

    def test_allows_five_and_rejects_sixth_request(self):
        url = "/get?client_id=client-1"

        with patch("rate_limiter.time.monotonic", return_value=0):
            results = [should_process_req(url) for _ in range(6)]

        self.assertEqual(results, [True, True, True, True, True, False])

    def test_starts_new_window_after_five_seconds(self):
        url = "/get?client_id=client-1"

        with patch("rate_limiter.time.monotonic", return_value=0):
            for _ in range(5):
                self.assertTrue(should_process_req(url))
            self.assertFalse(should_process_req(url))

        with patch("rate_limiter.time.monotonic", return_value=5):
            self.assertTrue(should_process_req(url))

    def test_clients_have_separate_limits(self):
        with patch("rate_limiter.time.monotonic", return_value=0):
            for _ in range(5):
                self.assertTrue(should_process_req("/get?client_id=client-1"))

            self.assertFalse(should_process_req("/get?client_id=client-1"))
            self.assertTrue(should_process_req("/get?client_id=client-2"))

    def test_missing_client_id_is_rejected(self):
        self.assertFalse(should_process_req("/get"))
        self.assertFalse(should_process_req("/get?client_id="))

    def test_concurrent_requests_are_counted_safely(self):
        url = "/get?client_id=client-1"

        with patch("rate_limiter.time.monotonic", return_value=0):
            with ThreadPoolExecutor(max_workers=20) as executor:
                results = list(executor.map(should_process_req, [url] * 100))

        self.assertEqual(results.count(True), 5)
        self.assertEqual(results.count(False), 95)

    def test_only_one_state_object_is_created_for_a_client(self):
        url = "/get?client_id=client-1"

        with patch("rate_limiter.time.monotonic", return_value=0):
            with ThreadPoolExecutor(max_workers=20) as executor:
                list(executor.map(should_process_req, [url] * 100))

        self.assertEqual(len(rate_limiter._clients), 1)


if __name__ == "__main__":
    unittest.main()
