import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

class Encryption:
    def __init__(self, key_phrase : str):
        self.key_phrase = key_phrase
        
    def _key(self, salt : bytes) -> bytes:
        kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
        return kdf.derive(self.key_phrase.encode())

    def encrypt(self, text : str) -> str:
        salt, nonce = os.urandom(16), os.urandom(12)
        ct = AESGCM(self._key(salt)).encrypt(nonce, text.encode(), None)
        return base64.urlsafe_b64encode(salt + nonce + ct).decode()

    def decrypt(self, token : str) -> str:
        raw = base64.urlsafe_b64decode(token)
        salt, nonce, ct = raw[:16], raw[16:28], raw[28:]
        return AESGCM(self._key(salt)).decrypt(nonce, ct, None).decode()