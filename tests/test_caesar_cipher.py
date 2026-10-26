"""Simple checks for the Caesar cipher helpers. Run: python -m unittest discover"""

import unittest
import urllib.error
from io import StringIO
from unittest.mock import patch

from caesar_cipher import (
    DictionaryError,
    crack_text,
    decrypt,
    encrypt,
    lookup_word,
    main,
    normalize_shift,
)


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


class AutoCrackTests(unittest.TestCase):
    def test_stops_at_ninety_percent_and_skips_later_shifts(self):
        ciphertext = encrypt("Attack at dawn.", 5)
        seen = []

        def is_word(word):
            seen.append(word)
            return word in {"attack", "at", "dawn"}

        result = crack_text(ciphertext, is_word=is_word)

        self.assertEqual(ciphertext, "Fyyfhp fy ifbs.")
        self.assertTrue(result["confident"])
        self.assertEqual(result["shift"], 5)
        self.assertEqual(result["text"], "Attack at dawn.")
        self.assertEqual(result["matched"], 3)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["shiftsTried"], 6)
        later_word = decrypt(ciphertext, 6).split()[0].lower()
        self.assertNotIn(later_word, seen)

    def test_keeps_searching_when_every_shift_stays_under_ninety_percent(self):
        ciphertext = encrypt("one two three four five", 2)
        shifts_seen = []

        def is_word(word):
            return word in {"one", "two", "three", "four"}

        def on_progress(attempt):
            shifts_seen.append(attempt["shift"])

        result = crack_text(ciphertext, is_word=is_word, on_progress=on_progress)

        self.assertEqual(shifts_seen, list(range(26)))
        self.assertFalse(result["confident"])
        self.assertEqual(result["shift"], 2)
        self.assertEqual(result["matched"], 4)
        self.assertEqual(result["total"], 5)
        self.assertAlmostEqual(result["confidence"], 0.8)

    def test_text_without_letters_is_not_english(self):
        result = crack_text("123 !!!", is_word=lambda word: True)

        self.assertFalse(result["confident"])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["shiftsTried"], 0)
        self.assertEqual(result["text"], "123 !!!")

    def test_nine_of_ten_words_is_confident(self):
        words = "alpha bravo charlie delta echo foxtrot golf hotel india juliet"
        ciphertext = encrypt(words, 4)
        english = set(words.split()) - {"juliet"}

        def is_word(word):
            return word in english

        result = crack_text(ciphertext, is_word=is_word)

        self.assertTrue(result["confident"])
        self.assertEqual(result["shift"], 4)
        self.assertEqual(result["matched"], 9)
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["shiftsTried"], 5)

    @patch("caesar_cipher.urllib.request.urlopen")
    def test_lookup_uses_the_dictionary_api(self, urlopen):
        response = unittest.mock.Mock()
        response.status = 200
        response.__enter__ = lambda self: self
        response.__exit__ = lambda self, *args: False
        urlopen.return_value = response

        self.assertTrue(lookup_word("Dawn"))

        request = urlopen.call_args.args[0]
        self.assertIn("api.dictionaryapi.dev", request.full_url)
        self.assertTrue(request.full_url.endswith("/dawn"))

    @patch("caesar_cipher.urllib.request.urlopen")
    def test_unknown_word_is_a_dictionary_miss(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError(
            "https://api.dictionaryapi.dev/api/v2/entries/en/fyyfhp",
            404,
            "Not Found",
            hdrs=None,
            fp=None,
        )

        self.assertFalse(lookup_word("fyyfhp"))

    @patch("caesar_cipher.time.sleep")
    @patch("caesar_cipher.urllib.request.urlopen")
    def test_repeated_gateway_error_counts_as_not_a_word(self, urlopen, _sleep):
        urlopen.side_effect = urllib.error.HTTPError(
            "https://api.dictionaryapi.dev/api/v2/entries/en/cvvcem",
            502,
            "Bad Gateway",
            hdrs=None,
            fp=None,
        )

        self.assertFalse(lookup_word("cvvcem"))
        self.assertGreater(urlopen.call_count, 1)

    @patch("caesar_cipher.urllib.request.urlopen")
    def test_dictionary_outage_is_reported(self, urlopen):
        urlopen.side_effect = urllib.error.URLError("offline")

        with self.assertRaises(DictionaryError):
            lookup_word("dawn")

    def test_menu_auto_crack_stops_and_can_exit(self):
        def is_word(word):
            return word in {"attack", "at", "dawn"}

        output = StringIO()
        with patch("caesar_cipher.lookup_word", side_effect=is_word):
            with patch("sys.stdin", StringIO("4\nFyyfhp fy ifbs.\n3\n")):
                with patch("sys.stdout", output):
                    main()

        text = output.getvalue()
        self.assertIn("Shift 5: 100% English", text)
        self.assertNotIn("Shift 6:", text)
        self.assertIn("Cracked text", text)
        self.assertIn("Attack at dawn.", text)
        self.assertIn("Goodbye.", text)


if __name__ == "__main__":
    unittest.main()
