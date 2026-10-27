"""
Caesar Cipher console tool.

This program encrypts and decrypts text with a Caesar cipher.
Each letter moves a fixed number of places in the alphabet.
Spaces, numbers, and punctuation stay exactly as they are.
Uppercase letters stay uppercase, and lowercase letters stay lowercase.

Auto-crack tries every shift, asks a dictionary API whether the words
are English, and stops when it is at least 90% confident.
"""

import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

# English alphabet length. A shift of 26 lands on the same letter.
ALPHABET_SIZE = 26
# Free Dictionary API. A real word returns 200. An unknown word returns 404.
DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
# Stop brute force once this share of the words are in the dictionary.
CONFIDENCE_PERCENT = 90
REQUEST_TIMEOUT_SECONDS = 5


def normalize_shift(shift):
    """
    Wrap a shift into the range 0 to 25.

    A shift of 27 is the same as a shift of 1.
    A negative shift wraps the other way, so -1 is the same as 25.
    """
    return shift % ALPHABET_SIZE


def transform_text(text, shift):
    """
    Shift every letter in text and leave every other character unchanged.

    The shift is applied modulo 26 so very large values still work.
    """
    wrapped_shift = normalize_shift(shift)
    transformed_characters = []

    for character in text:
        if character.isupper():
            # 'A' is the start of the uppercase alphabet.
            alphabet_start = ord("A")
            position = ord(character) - alphabet_start
            new_position = (position + wrapped_shift) % ALPHABET_SIZE
            transformed_characters.append(chr(alphabet_start + new_position))
        elif character.islower():
            # Lowercase uses its own start point so case is preserved.
            alphabet_start = ord("a")
            position = ord(character) - alphabet_start
            new_position = (position + wrapped_shift) % ALPHABET_SIZE
            transformed_characters.append(chr(alphabet_start + new_position))
        else:
            # Digits, spaces, and punctuation are copied unchanged.
            transformed_characters.append(character)

    return "".join(transformed_characters)


def encrypt(text, shift):
    """Encrypt text by moving letters forward by shift places."""
    return transform_text(text, shift)


def decrypt(text, shift):
    """Decrypt text by moving letters backward by shift places."""
    return transform_text(text, -shift)


class DictionaryError(Exception):
    """The dictionary API could not answer a lookup."""


def extract_words(text):
    """Return the letter groups in text. Spaces and punctuation are not words."""
    words = []
    current = []

    for character in text:
        if character.isalpha():
            current.append(character)
        elif current:
            words.append("".join(current))
            current = []

    if current:
        words.append("".join(current))

    return words


def is_confident(matched, total):
    """True when matched words are at least 90% of the words in the text."""
    return total > 0 and matched * 100 >= CONFIDENCE_PERCENT * total


def lookup_word(word):
    """
    Ask the Free Dictionary API whether word is English.

    The console program stays free of extra packages: this uses urllib.
    No API key is required. A 404 means the word is not listed. A repeated
    502 or 503 is also treated as not listed, because that API sometimes
    fails on strings that are not words. Rate limits are retried, then reported.
    """
    quoted = urllib.parse.quote(word.lower())
    url = DICTIONARY_URL.format(word=quoted)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "caesar-cipher-cracker",
        },
    )
    gateway_errors_left = 2
    network_errors_left = 3

    while True:
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                response.read()
                return True
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return False
            if error.code in (502, 503, 504) and gateway_errors_left > 0:
                gateway_errors_left -= 1
                time.sleep(0.4)
                continue
            if error.code in (502, 503, 504):
                return False
            if error.code == 429:
                time.sleep(1)
                gateway_errors_left -= 1
                if gateway_errors_left >= 0:
                    continue
            raise DictionaryError(f"Dictionary API returned {error.code}.") from error
        except urllib.error.URLError as error:
            # The dictionary server often resets the connection on the first try.
            if network_errors_left > 0:
                network_errors_left -= 1
                time.sleep(0.6)
                continue
            raise DictionaryError("Could not reach the dictionary API.") from error


def score_text(text, is_word):
    """
    Return how many words in text the dictionary accepts.

    Once the remaining words cannot lift the score to 90%, the rest of the
    line is not sent to the API.
    """
    words = extract_words(text)
    total = len(words)
    matched = 0

    for index, word in enumerate(words, start=1):
        if is_word(word.lower()):
            matched += 1

        remaining = total - index
        if (matched + remaining) * 100 < CONFIDENCE_PERCENT * total:
            break

    if total == 0:
        confidence = 0.0
    else:
        confidence = matched / total

    return {
        "text": text,
        "confidence": confidence,
        "matched": matched,
        "total": total,
        "confident": is_confident(matched, total),
    }


def crack_text(ciphertext, is_word=None, on_progress=None):
    """
    Try every Caesar shift and stop at the first readable English result.

    Decryption uses shift 0, then 1, and so on up to 25. Each candidate is
    scored with the dictionary. The search returns as soon as confidence
    reaches 90%, so later shifts are not tried. If none reach 90%, the
    best candidate is returned with confident set to False.
    """
    if is_word is None:
        cache = {}

        def is_word(word):
            if word not in cache:
                cache[word] = lookup_word(word)
            return cache[word]

    words = extract_words(ciphertext)
    if not words:
        result = score_text(ciphertext, is_word)
        result["shift"] = 0
        result["shiftsTried"] = 0
        return result

    best = None
    shifts_tried = 0

    for shift in range(ALPHABET_SIZE):
        shifts_tried += 1
        candidate = decrypt(ciphertext, shift)
        result = score_text(candidate, is_word)
        result["shift"] = shift
        result["shiftsTried"] = shifts_tried

        if on_progress is not None:
            on_progress(result)

        if best is None or result["confidence"] > best["confidence"]:
            best = result

        if result["confident"]:
            return result

    return best


class Spinner:
    """A one-line spinner that stays on screen until stop() is called."""

    def __init__(self):
        self.label = "Cracking"
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        """Spin only on a real terminal. Piped output stays line by line."""
        if not getattr(sys.stdout, "isatty", lambda: False)():
            return

        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def _spin(self):
        frames = "|/-\\"
        index = 0

        while not self._stop.wait(0.1):
            frame = frames[index % len(frames)]
            index += 1
            sys.stdout.write(f"\r{self.label} {frame}")
            sys.stdout.flush()

        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()

    def stop(self):
        """Clear the spinner. Calling this is what makes it stop."""
        if self._thread is None:
            return

        self._stop.set()
        self._thread.join()
        self._thread = None


def read_message():
    """
    Read the message from the user.

    An empty message returns None so the caller can go back to the menu.
    Messages that contain only spaces are allowed, because spaces are valid text.
    """
    message = input("Enter the message (press Enter to go back): ")
    if message == "":
        print("Returning to the menu.\n")
        return None
    return message


def read_shift():
    """
    Read a whole-number shift from the user.

    Returns the integer, or None if the user wants to cancel.
    Keeps asking when the value is not a whole number.
    """
    while True:
        raw_value = input("Enter the shift value (whole number, or 'back'): ").strip()

        if raw_value.lower() == "back":
            print("Returning to the menu.\n")
            return None

        try:
            return int(raw_value)
        except ValueError:
            print("Invalid shift. Enter a whole number such as 3 or -1.\n")


def show_menu():
    """Print the main menu."""
    print()
    print("=" * 46)
    print("           CAESAR CIPHER TOOL")
    print("     Cybersecurity Internship Task")
    print("=" * 46)
    print("1. Encrypt Text")
    print("2. Decrypt Text")
    print("3. Exit")
    print("4. Auto-crack")


def run_cipher(mode):
    """
    Collect a message and a shift, then print the result.

    mode is either 'encrypt' or 'decrypt'.
    """
    message = read_message()
    if message is None:
        return

    shift = read_shift()
    if shift is None:
        return

    if mode == "encrypt":
        result = encrypt(message, shift)
        action_label = "Encrypted text"
    else:
        result = decrypt(message, shift)
        action_label = "Decrypted text"

    # Show the wrapped key so a shift of 29 is clearly the same as 3.
    print()
    print(f"Original message : {message}")
    print(f"Shift entered    : {shift}")
    print(f"Shift used       : {normalize_shift(shift)} (wrapped into 0-25)")
    print(f"{action_label:17}: {result}")
    print()


def run_crack():
    """
    Brute-force a ciphertext with the dictionary API.

    The spinner keeps moving through every shift and stops only when the
    text is at least 90% English, or when every shift has been tried.
    """
    message = read_message()
    if message is None:
        return

    print()
    print("Brute-forcing every shift. Each result is checked with the dictionary API.")
    print("The spinner stops when a result is at least 90% English.")
    print()

    spinner = Spinner()
    interactive = getattr(sys.stdout, "isatty", lambda: False)()

    def on_progress(attempt):
        percent = f"{attempt['confidence']:.0%}"
        spinner.label = f"Trying shift {attempt['shift']} ({percent} English)"
        if not interactive:
            print(f"Shift {attempt['shift']}: {percent} English")

    spinner.start()
    try:
        result = crack_text(message, on_progress=on_progress)
    except DictionaryError as error:
        spinner.stop()
        print(f"{error}\n")
        return
    spinner.stop()

    if result["total"] == 0:
        print("No letters to check against the dictionary.\n")
        return

    if result["confident"]:
        print("Stopped at 90% English. Later shifts were not tried.")
        label = "Cracked text"
    else:
        print("No shift reached 90% English. Showing the best result.")
        label = "Best guess"

    percent = f"{result['confidence']:.0%}"
    print()
    print(f"{'Ciphertext':17}: {message}")
    print(f"{'Shift found':17}: {result['shift']}")
    print(f"{'Confidence':17}: {percent} ({result['matched']} of {result['total']} words)")
    print(f"{label:17}: {result['text']}")
    print()


def main():
    """Keep showing the menu until the user chooses Exit."""
    print("Welcome. Letters are shifted. Everything else stays the same.")

    while True:
        show_menu()
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            run_cipher("encrypt")
        elif choice == "2":
            run_cipher("decrypt")
        elif choice == "3":
            print("\nGoodbye.")
            break
        elif choice == "4":
            run_crack()
        else:
            # Covers letters, symbols, blank input, and numbers outside 1-4.
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or a closed input stream should not print a traceback.
        print("\n\nProgram stopped. Goodbye.")
