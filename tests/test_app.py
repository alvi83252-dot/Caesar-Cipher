"""Checks for the Vercel Flask entrypoint. Run: python -m unittest tests.test_app"""

import unittest

from app import app


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
