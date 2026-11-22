"""Exercise the HTTP handler without network access or a provider key."""
from io import BytesIO
from unittest import TestCase
from unittest.mock import Mock, patch

import server


class LoopbackStream:
    def __init__(self):
        self.response = bytearray()

    def makefile(self, *args):
        return BytesIO(b"POST /api/analyze HTTP/1.0\r\nContent-Type: application/json\r\n"
                       b"Content-Length: 2\r\n\r\n{}")

    def sendall(self, data):
        self.response.extend(data)


class RateLimitTest(TestCase):
    @patch.object(server.CyberEyeHandler, "log_message")
    def test_thirty_requests_and_recovery(self, _log):
        with patch.object(server, "recent_requests", server.deque()), patch.object(server, "monotonic") as clock:
            clock.return_value = 100
            for index in range(30):
                stream = LoopbackStream()
                server.CyberEyeHandler(stream, ("127.0.0.1", 5555), Mock())
                self.assertIn(b"400 Bad Request" if index < 5 else b"429 Too Many Requests",
                              stream.response.splitlines()[0])
            self.assertTrue(server.allow_analysis("different visitor"))
            clock.return_value += server.WINDOW_SECONDS
            self.assertTrue(server.allow_analysis("127.0.0.1"))
