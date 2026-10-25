# Caesar Cipher

Console program for a cybersecurity internship task. It encrypts and decrypts text with a Caesar cipher. You run it in a terminal. There is no web page or graphical interface.

A Caesar cipher shifts every letter by a fixed number of places in the alphabet. The number is the key. A shift of 3 turns `A` into `D` and `a` into `d`. To decrypt, shift the same number of places in the opposite direction.

Characters that are not letters are left alone. That includes spaces, digits, and punctuation. Uppercase and lowercase are shifted separately, so case is preserved.

## Features

- Menu with Encrypt, Decrypt, and Exit
- Any message and any whole-number shift
- Uppercase and lowercase letters
- Spaces, numbers, and punctuation stay unchanged
- Shifts wrap with modulo 26 (`27` is the same as `1`, `-1` is the same as `25`)
- Invalid menu choices and non-numeric shifts are rejected with a short message
- Empty message or the word `back` returns to the menu
- Ctrl+C ends the program without a traceback

## Requirements

- Python 3.8 or newer
- No third-party packages

## Folder structure

```text
Caesar-Cipher/
├── caesar_cipher.py          # Main console program
├── requirements.txt          # Notes that no extra packages are needed
├── README.md
├── .gitignore
├── examples/
│   ├── sample_input.txt      # Input you can pipe into the program
│   └── sample_session.txt    # Expected interactive session
└── tests/
    └── test_caesar_cipher.py # Checks for encrypt and decrypt
```

## How to run

From this folder:

```bash
python caesar_cipher.py
```

You will see this menu:

```text
1. Encrypt Text
2. Decrypt Text
3. Exit
```

Choose `1` or `2`, type a message, then type a shift. Choose `3` to leave.

Replay the saved sample input:

```bash
python caesar_cipher.py < examples/sample_input.txt
```

On Windows PowerShell:

```powershell
Get-Content -Raw examples\sample_input.txt | python caesar_cipher.py
```

Run the checks:

```bash
python -m unittest tests.test_caesar_cipher -v
```

## Example session

What you type is shown after each prompt.

```text
Welcome. Letters are shifted. Everything else stays the same.

==============================================
           CAESAR CIPHER TOOL
     Cybersecurity Internship Task
==============================================
1. Encrypt Text
2. Decrypt Text
3. Exit
Enter your choice (1-3): 1
Enter the message (press Enter to go back): Hello, World! 123
Enter the shift value (whole number, or 'back'): 3

Original message : Hello, World! 123
Shift entered    : 3
Shift used       : 3 (wrapped into 0-25)
Encrypted text   : Khoor, Zruog! 123

==============================================
           CAESAR CIPHER TOOL
     Cybersecurity Internship Task
==============================================
1. Encrypt Text
2. Decrypt Text
3. Exit
Enter your choice (1-3): 2
Enter the message (press Enter to go back): Khoor, Zruog! 123
Enter the shift value (whole number, or 'back'): 3

Original message : Khoor, Zruog! 123
Shift entered    : 3
Shift used       : 3 (wrapped into 0-25)
Decrypted text   : Hello, World! 123

==============================================
           CAESAR CIPHER TOOL
     Cybersecurity Internship Task
==============================================
1. Encrypt Text
2. Decrypt Text
3. Exit
Enter your choice (1-3): 1
Enter the message (press Enter to go back): Attack at dawn.
Enter the shift value (whole number, or 'back'): 5

Original message : Attack at dawn.
Shift entered    : 5
Shift used       : 5 (wrapped into 0-25)
Encrypted text   : Fyyfhp fy ifbs.

==============================================
           CAESAR CIPHER TOOL
     Cybersecurity Internship Task
==============================================
1. Encrypt Text
2. Decrypt Text
3. Exit
Enter your choice (1-3): 9
Invalid choice. Please enter 1, 2, or 3.

==============================================
           CAESAR CIPHER TOOL
     Cybersecurity Internship Task
==============================================
1. Encrypt Text
2. Decrypt Text
3. Exit
Enter your choice (1-3): 2
Enter the message (press Enter to go back): Fyyfhp fy ifbs.
Enter the shift value (whole number, or 'back'): five
Invalid shift. Enter a whole number such as 3 or -1.

Enter the shift value (whole number, or 'back'): 5

Original message : Fyyfhp fy ifbs.
Shift entered    : 5
Shift used       : 5 (wrapped into 0-25)
Decrypted text   : Attack at dawn.

==============================================
           CAESAR CIPHER TOOL
     Cybersecurity Internship Task
==============================================
1. Encrypt Text
2. Decrypt Text
3. Exit
Enter your choice (1-3): 3

Goodbye.
```

## More test cases

| Action | Message | Shift | Result |
| --- | --- | --- | --- |
| Encrypt | `Hello, World! 123` | `3` | `Khoor, Zruog! 123` |
| Decrypt | `Khoor, Zruog! 123` | `3` | `Hello, World! 123` |
| Encrypt | `Attack at dawn.` | `5` | `Fyyfhp fy ifbs.` |
| Encrypt | `XYZ xyz!` | `1` | `YZA yza!` |
| Encrypt | `Abc!` | `26` | `Abc!` |
| Encrypt | `abc` | `-1` | `zab` |

## How the cipher works

1. Read the message and the shift.
2. For each character, check whether it is a letter.
3. If it is uppercase, count from `A`. If it is lowercase, count from `a`.
4. Add the shift, then wrap with `% 26` so the result stays inside the alphabet.
5. If the character is not a letter, copy it unchanged.
6. Decryption uses the same steps with the shift reversed.

## Security note

This cipher is a teaching example. It is not a secure way to protect real data. There are only 25 useful keys, so every key can be tried quickly. Letter frequency in normal English also gives the key away. Modern confidentiality needs a standard algorithm such as AES, with a proper key and a safe mode of operation.

## Screenshots to capture

Take these from a real terminal after you run `python caesar_cipher.py`. Keep the full window visible, including the command you used to start the program.

1. The main menu, before any choice is entered.
2. Encrypt `Hello, World! 123` with shift `3`, showing `Khoor, Zruog! 123`.
3. Decrypt `Khoor, Zruog! 123` with shift `3`, showing the original message.
4. Encrypt `Attack at dawn.` with shift `5`, showing `Fyyfhp fy ifbs.`.
5. An invalid menu choice such as `9`, showing the error and the menu again.
6. An invalid shift such as `five`, then a corrected shift, showing the error text.
7. Option `3`, showing `Goodbye.`
8. Optional: `python -m unittest tests.test_caesar_cipher -v` with all tests `OK`.

Save the images as `screenshots/01-menu.png` through `screenshots/08-tests.png` if your submission asks for image proof.

## Internship submission checklist

- [ ] Source code runs with `python caesar_cipher.py` and has no extra installs
- [ ] Menu offers Encrypt, Decrypt, and Exit
- [ ] Encryption and decryption are demonstrated with the same message and shift
- [ ] Sample output shows spaces, numbers, punctuation, and both letter cases
- [ ] Invalid menu input and invalid shift input are shown
- [ ] Code comments explain the shift, the wrap, and why non-letters are unchanged
- [ ] README states the goal, how to run the program, and example output
- [ ] Screenshots listed above are attached or placed in `screenshots/`
- [ ] Repository contains only this project (no secrets, virtual environments, or unrelated files)
- [ ] Short note explains that a Caesar cipher is historical and not suitable for real secrecy
