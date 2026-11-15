"""CyberEye backend tests. Run: python3 -m unittest discover -s tests -v"""
import json
import os
import sys
import socket
import ssl
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server


class CyberEyeTests(unittest.TestCase):
    def test_empty_message_rejected(self):
        with self.assertRaises(server.AnalysisError) as caught:
            server.validate_message("   ")
        self.assertEqual(caught.exception.status, 400)

    def test_long_message_rejected(self):
        with self.assertRaises(server.AnalysisError):
            server.validate_message("a" * 5001)

    def test_valid_model_output(self):
        parsed = server.parse_model_response({
            "model": "demo-model",
            "choices": [{"message": {"content": json.dumps({
                "risk_level": "medium",
                "summary": "Requests payment information.",
                "indicators": [{"title": "Urgency", "explanation": "Immediate action requested."}],
                "next_step": "Use the service's official app."
            })}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 40}
        })
        self.assertEqual(parsed["risk_level"], "medium")
        self.assertEqual(parsed["usage"]["prompt_tokens"], 100)

    def test_bad_model_output_fails_closed(self):
        with self.assertRaises(server.AnalysisError) as caught:
            server.parse_model_response({
                "choices": [{"message": {"content": '{"risk_level":"totally safe"}'}}]
            })
        self.assertEqual(caught.exception.status, 502)

    def test_markdown_fenced_json_is_accepted(self):
        content = json.dumps({
            "risk_level": "high",
            "summary": "Urgent message asking for credentials.",
            "indicators": [{"title": "Urgency", "explanation": "It threatens cancellation."}],
            "next_step": "Verify directly in the official app."
        })
        response = {
            "choices": [{"finish_reason": "stop", "message": {"content": "```json\n" + content + "\n```"}}]
        }
        self.assertEqual(server.parse_model_response(response)["risk_level"], "high")

    def test_text_content_parts_are_accepted(self):
        content = json.dumps({
            "risk_level": "unclear", "summary": "Insufficient information.",
            "indicators": [], "next_step": "Verify through an independent channel."
        })
        response = {"choices": [{"message": {"content": [{"type": "text", "text": content}]}}]}
        self.assertEqual(server.parse_model_response(response)["risk_level"], "unclear")

    def test_output_limit_explained(self):
        with self.assertRaises(server.AnalysisError) as caught:
            server.parse_model_response({
                "choices": [{"finish_reason": "length", "message": {"content": ""}}]
            })
        self.assertIn("tokens", caught.exception.message)

    def test_empty_output_explained(self):
        with self.assertRaises(server.AnalysisError) as caught:
            server.parse_model_response({"choices": [{"message": {"content": ""}}]})
        self.assertIn("empty", caught.exception.message)

    def test_invalid_json_is_not_presented_as_safe(self):
        with self.assertRaises(server.AnalysisError) as caught:
            server.parse_model_response({"choices": [{"message": {"content": "Looks safe!"}}]})
        self.assertIn("not valid JSON", caught.exception.message)

    def test_missing_api_key_is_not_mocked_as_ai(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            with self.assertRaises(server.AnalysisError) as caught:
                server.analyze_message("Verify my account now")
        self.assertEqual(caught.exception.status, 503)

    def test_ssl_error_identified(self):
        err = server.classify_connection_error(ssl.SSLCertVerificationError("certificate verify failed"))
        self.assertEqual(err.status, 502)
        self.assertIn("certificate", err.message.lower())

    def test_dns_error_identified(self):
        err = server.classify_connection_error(socket.gaierror("nodename nor servname provided"))
        self.assertIn("DNS", err.message)

    def test_timeout_error_identified(self):
        err = server.classify_connection_error(TimeoutError("timed out"))
        self.assertEqual(err.status, 504)

    def test_default_free_model(self):
        self.assertEqual(server.DEFAULT_MODEL, "openrouter/free")

    def test_timeout_configuration(self):
        self.assertGreaterEqual(server.OPENROUTER_TIMEOUT_SECONDS, 60)

    def test_prompt_injection_is_not_a_system_instruction(self):
        self.assertIn("UNTRUSTED DATA", server.SYSTEM_PROMPT)
        self.assertIn("Do not open links", server.SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
