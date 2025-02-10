import base64
import logging
import os
import traceback

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from tournaments_backend.errors.backend import InvalidTokenError

IV_SIZE: int = 16
IV_SIZE_B64: int = 24

JWT_ALGORITHM: str = "EdDSA"

_logger = logging.getLogger(__name__)


class WebTokenService:
    _sign_key: bytes
    _encrypt_key: bytes

    def __init__(self, sign_key: bytes | str, encrypt_key: bytes | str):
        if isinstance(sign_key, str):
            _logger.debug(f"Signing key is string, encoding in bytes")
            self._sign_key = sign_key.encode()
        else:
            self._sign_key = sign_key

        _logger.debug(f"Signing key: {self._sign_key}")

        self._encrypt_key = base64.urlsafe_b64decode(encrypt_key)
        _logger.debug(f"Encrypting key: {self._encrypt_key}")

    async def encrypt(self, data: dict | None = None) -> str:
        if data is None:
            data = {}

        encoded_jwt: str = jwt.encode(data, self._sign_key, algorithm=JWT_ALGORITHM)

        iv: bytes = os.urandom(16)

        cipher = self._generate_cypher(iv)
        encryptor = cipher.encryptor()

        encrypted_jwt: bytes = encryptor.update(encoded_jwt.encode()) + encryptor.finalize()
        tag: bytes = encryptor.tag

        return (base64.urlsafe_b64encode(tag).decode()
                + base64.urlsafe_b64encode(iv).decode()
                + base64.urlsafe_b64encode(encrypted_jwt).decode())

    async def decrypt(self, encrypted_data: str) -> dict:
        if len(encrypted_data) < IV_SIZE_B64:
            raise InvalidTokenError()

        tag: bytes = base64.urlsafe_b64decode(encrypted_data[0:24])
        iv: bytes = base64.urlsafe_b64decode(encrypted_data[24:48])
        ciphertext: bytes = base64.urlsafe_b64decode(encrypted_data[48:])

        cipher = self._generate_cypher(iv)
        decryptor = cipher.decryptor()

        decrypted_jwt: bytes = decryptor.update(ciphertext) + decryptor.finalize_with_tag(tag)

        decoded_jwt = decrypted_jwt.decode()

        try:
            return jwt.decode(decoded_jwt, self._sign_key, algorithms=[JWT_ALGORITHM])
        except Exception as e:
            _logger.error(f"Error verifying token signature: {e}\n{traceback.format_exc()}")
            raise InvalidTokenError()

    def _generate_cypher(self, iv: bytes) -> Cipher:
        return Cipher(
            algorithm=algorithms.AES256(self._encrypt_key),
            mode=modes.GCM(iv),
            backend=default_backend()
        )
