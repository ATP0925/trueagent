"""
TOTP Helper for WebPilot: Pure Python RFC 6238 2FA code generator.
Zero third-party dependencies.
"""

import hmac
import hashlib
import time
import struct
import base64


def generate_totp(secret: str, interval: int = 30, digits: int = 6) -> str:
    """Generates standard RFC 6238 TOTP token from a base32 secret."""
    clean_secret = secret.strip().replace(" ", "").upper()
    # Pad base32 string to multiple of 8 if needed
    missing_padding = len(clean_secret) % 8
    if missing_padding:
        clean_secret += "=" * (8 - missing_padding)

    key = base64.b32decode(clean_secret, casefold=True)
    counter = int(time.time() // interval)
    msg = struct.pack(">Q", counter)

    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[19] & 0x0F
    code = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    token = str(code % (10 ** digits)).zfill(digits)
    return token

