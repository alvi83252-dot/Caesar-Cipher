"""
Web entrypoint for Vercel.

Vercel loads the Flask instance named app from this file.
Encrypt and decrypt still come from caesar_cipher.py.
Static pages live in public/ and are served by Vercel's CDN.
"""

import os
import re
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from caesar_cipher import decrypt, encrypt, normalize_shift

app = Flask(__name__)
PUBLIC_DIR = Path(__file__).resolve().parent / "public"
# Same whole numbers the console tool accepts with int(), including +3 and -1.
SHIFT_PATTERN = re.compile(r"[+-]?\d+")


def parse_shift(value):
    """
    Return a shift as an int, or None when the value is not a whole number.

    Booleans are rejected on purpose: in Python, True is a subclass of int.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and SHIFT_PATTERN.fullmatch(value.strip()):
        return int(value.strip())
    return None


@app.post("/api/cipher")
def cipher():
    """Encrypt or decrypt one message and return the same details as the console tool."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Send a JSON object with message, shift, and mode."), 400

    message = payload.get("message")
    mode = payload.get("mode")
    shift = parse_shift(payload.get("shift"))

    if not isinstance(message, str) or message == "":
        return jsonify(error="Enter a message."), 400
    if mode not in ("encrypt", "decrypt"):
        return jsonify(error="Choose encrypt or decrypt."), 400
    if shift is None:
        return jsonify(error="Invalid shift. Enter a whole number such as 3 or -1."), 400

    if mode == "encrypt":
        result = encrypt(message, shift)
        label = "Encrypted text"
    else:
        result = decrypt(message, shift)
        label = "Decrypted text"

    return jsonify(
        original=message,
        shiftEntered=shift,
        shiftUsed=normalize_shift(shift),
        label=label,
        result=result,
    )


def register_local_pages():
    """
    Serve public/ during local runs of python app.py.

    On Vercel the CDN serves that folder, so these routes stay unregistered.
    """

    @app.get("/")
    def index():
        return send_from_directory(PUBLIC_DIR, "index.html")

    @app.get("/<path:asset_path>")
    def public_asset(asset_path):
        return send_from_directory(PUBLIC_DIR, asset_path)


if os.environ.get("VERCEL") != "1":
    register_local_pages()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
