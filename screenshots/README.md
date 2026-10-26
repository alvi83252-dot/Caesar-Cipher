# Screenshot guide

The proof images in this folder use the file names below. `06-invalid-shift-rejected.png` is the extra frame taken while the program was still waiting after `five`. `06-invalid-shift.png` is the frame after shift `5` decrypted the message.

Before you start:

1. Open PowerShell.
2. Go to this project folder:

```powershell
cd "C:\Users\faiza\Downloads\Casesar Cipher Task 1"
```

3. Make the window wide enough that each result stays on one line.
4. Leave the `python caesar_cipher.py` command visible at the top of the window.
5. After each step below, pause and take the screenshot before you type the next step.

## 01-menu.png

Start the program:

```powershell
python caesar_cipher.py
```

Type nothing else. Capture the window when the menu is waiting at `Enter your choice (1-4):`.

You should see:

```text
1. Encrypt Text
2. Decrypt Text
3. Exit
4. Auto-crack
```

## 02-encrypt-hello.png

Type these three lines, pressing Enter after each one:

```text
1
Hello, World! 123
3
```

Capture when this line is on screen:

```text
Encrypted text   : Khoor, Zruog! 123
```

## 03-decrypt-hello.png

Stay in the same window. Type:

```text
2
Khoor, Zruog! 123
3
```

Capture when this line is on screen:

```text
Decrypted text   : Hello, World! 123
```

## 04-encrypt-attack.png

Type:

```text
1
Attack at dawn.
5
```

Capture when this line is on screen:

```text
Encrypted text   : Fyyfhp fy ifbs.
```

## 05-invalid-menu.png

Type:

```text
9
```

Capture the error and the menu that appears again:

```text
Invalid choice. Please enter 1, 2, 3, or 4.
```

## 06-invalid-shift.png

Type:

```text
2
Fyyfhp fy ifbs.
five
5
```

`five` is intentional. The program must reject it, then accept `5`.

Capture both of these lines in the same image:

```text
Invalid shift. Enter a whole number such as 3 or -1.
Decrypted text   : Attack at dawn.
```

## 07-exit.png

Type:

```text
3
```

Capture the closing line:

```text
Goodbye.
```

## 09-auto-crack.png

Stay in the same program, or start it again. Type:

```text
4
Fyyfhp fy ifbs.
```

The spinner keeps moving while each shift is checked with the dictionary API. Capture the window when the spinner has stopped and these lines are on screen:

```text
Stopped at 90% English. Later shifts were not tried.
Shift found      : 5
Cracked text     : Attack at dawn.
```

The dictionary check needs the internet. Shift lines before 5 may appear when the output is piped. On a normal terminal the spinner replaces those lines.

## 08-tests.png

Open a new terminal in the same folder and type only this:

```powershell
python -m unittest tests.test_caesar_cipher -v
```

Capture the window when every test says `ok` and the last lines are:

```text
Ran 5 tests in ...

OK
```
