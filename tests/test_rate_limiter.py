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

    def test_old_requests_leave_the_window(self):
        url = "/get?client_id=client-1"

        with patch("rate_limiter.time.monotonic", return_value=0):
            for _ in range(5):
                self.assertTrue(should_process_req(url))
            self.assertFalse(should_process_req(url))

        with patch("rate_limiter.time.monotonic", return_value=5):
            self.assertTrue(should_process_req(url))

    def test_rejected_requests_are_counted(self):
        url = "/get?client_id=client-1"

        # Five requests spread over four seconds fill the queue.
        for request_time in (0, 1, 2, 3, 4):
            with patch("rate_limiter.time.monotonic", return_value=request_time):
                self.assertTrue(should_process_req(url))

        # This request is rejected, but it is still added to the queue.
        with patch("rate_limiter.time.monotonic", return_value=4.5):
            self.assertFalse(should_process_req(url))

        # The request at time 0 has expired, but the rejected request at 4.5
        # keeps five requests in the last five seconds.
        with patch("rate_limiter.time.monotonic", return_value=5.1):
            self.assertFalse(should_process_req(url))

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
