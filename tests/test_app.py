"""Checks for the Vercel Flask entrypoint. Run: python -m unittest tests.test_app"""

import unittest
from unittest.mock import patch

from app import app
from caesar_cipher import DictionaryError


class CipherApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_encrypt_matches_the_console_program(self):
        response = self.client.post(
            "/api/cipher",
            json={"message": "Hello, World! 123", "shift": 3, "mode": "encrypt"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "original": "Hello, World! 123",
                "shiftEntered": 3,
                "shiftUsed": 3,
                "label": "Encrypted text",
                "result": "Khoor, Zruog! 123",
            },
        )

    def test_decrypt_reverses_a_shift_of_five(self):
        response = self.client.post(
            "/api/cipher",
            json={"message": "Fyyfhp fy ifbs.", "shift": 5, "mode": "decrypt"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["result"], "Attack at dawn.")
        self.assertEqual(body["label"], "Decrypted text")

    def test_negative_shift_wraps(self):
        response = self.client.post(
            "/api/cipher",
            json={"message": "abc", "shift": -1, "mode": "encrypt"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["result"], "zab")
        self.assertEqual(body["shiftUsed"], 25)

    def test_invalid_shift_is_rejected(self):
        response = self.client.post(
            "/api/cipher",
            json={"message": "abc", "shift": "five", "mode": "encrypt"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("whole number", response.get_json()["error"])

    def test_empty_message_is_rejected(self):
        response = self.client.post(
            "/api/cipher",
            json={"message": "", "shift": 3, "mode": "encrypt"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Enter a message.")

    def test_crack_stops_when_the_dictionary_is_ninety_percent_sure(self):
        def is_word(word):
            return word in {"attack", "at", "dawn"}

        with patch("caesar_cipher.lookup_word", side_effect=is_word):
            response = self.client.post(
                "/api/crack",
                json={"message": "Fyyfhp fy ifbs."},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["result"], "Attack at dawn.")
        self.assertEqual(body["shiftUsed"], 5)
        self.assertEqual(body["shiftsTried"], 6)
        self.assertEqual(body["confidence"], 100)
        self.assertTrue(body["confident"])
        self.assertEqual(body["label"], "Cracked text")

    def test_crack_reports_a_dictionary_outage(self):
        def fail(word):
            raise DictionaryError("Could not reach the dictionary API.")

        with patch("caesar_cipher.lookup_word", side_effect=fail):
            response = self.client.post("/api/crack", json={"message": "Fyyfhp fy ifbs."})

        self.assertEqual(response.status_code, 502)
        self.assertIn("dictionary", response.get_json()["error"])
