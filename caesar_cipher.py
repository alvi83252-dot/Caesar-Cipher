"""
Caesar Cipher console tool.

This program encrypts and decrypts text with a Caesar cipher.
Each letter moves a fixed number of places in the alphabet.
Spaces, numbers, and punctuation stay exactly as they are.
Uppercase letters stay uppercase, and lowercase letters stay lowercase.
"""

# English alphabet length. A shift of 26 lands on the same letter.
ALPHABET_SIZE = 26


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


def main():
    """Keep showing the menu until the user chooses Exit."""
    print("Welcome. Letters are shifted. Everything else stays the same.")

    while True:
        show_menu()
        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            run_cipher("encrypt")
        elif choice == "2":
            run_cipher("decrypt")
        elif choice == "3":
            print("\nGoodbye.")
            break
        else:
            # Covers letters, symbols, blank input, and numbers outside 1-3.
            print("Invalid choice. Please enter 1, 2, or 3.\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or a closed input stream should not print a traceback.
        print("\n\nProgram stopped. Goodbye.")
