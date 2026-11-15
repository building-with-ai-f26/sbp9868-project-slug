"""CyberEye backend tests. Run: python3 -m unittest discover -s tests -v"""
import json
import os
import sys
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

    def test_missing_api_key_is_not_mocked_as_ai(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            with self.assertRaises(server.AnalysisError) as caught:
                server.analyze_message("Verify my account now")
        self.assertEqual(caught.exception.status, 503)

    def test_prompt_injection_is_not_a_system_instruction(self):
        self.assertIn("UNTRUSTED DATA", server.SYSTEM_PROMPT)
        self.assertIn("Do not open links", server.SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
