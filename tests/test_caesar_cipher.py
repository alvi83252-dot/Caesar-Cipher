"""Simple checks for the Caesar cipher helpers. Run: python -m unittest discover"""

import unittest

from caesar_cipher import decrypt, encrypt, normalize_shift


class CaesarCipherTests(unittest.TestCase):
    def test_encrypt_preserves_case_and_symbols(self):
        self.assertEqual(encrypt("Hello, World! 123", 3), "Khoor, Zruog! 123")

    def test_decrypt_reverses_encryption(self):
        original = "Attack at dawn."
        ciphertext = encrypt(original, 5)
        self.assertEqual(ciphertext, "Fyyfhp fy ifbs.")
        self.assertEqual(decrypt(ciphertext, 5), original)

    def test_shift_wraps_past_the_end_of_the_alphabet(self):
        self.assertEqual(encrypt("XYZ xyz!", 1), "YZA yza!")

    def test_full_alphabet_rotation_returns_the_same_text(self):
        self.assertEqual(encrypt("Abc!", 26), "Abc!")
        self.assertEqual(normalize_shift(29), 3)

    def test_negative_shift_moves_backward(self):
        self.assertEqual(encrypt("abc", -1), "zab")
        self.assertEqual(decrypt("abc", -1), "bcd")


if __name__ == "__main__":
    unittest.main()
