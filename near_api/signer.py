import json
from typing import Union

import base58
import ed25519


class KeyPair(object):

    def __init__(self, secret_key: Union[str, bytes] = None):
        """
        If no secret_key, a new one is created.
        secret_key must be a base58-encoded string or
        the byte object returned as "secret_key" property of a KeyPair object."""
        if not secret_key:
            self._secret_key, self._public_key = ed25519.keys.create_keypair()
            raise Exception("No secret_key")
        if isinstance(secret_key, bytes):
            self._secret_key = ed25519.keys.SigningKey(secret_key)
        elif isinstance(secret_key, str):
            secret_key = secret_key.split(':')[-1]
            self._secret_key = ed25519.keys.SigningKey(base58.b58decode(secret_key))
        else:
            raise Exception("Unrecognised")
        self._public_key = self._secret_key.get_verifying_key()

    @property
    def public_key(self) -> bytes:
        return self._public_key.to_bytes()

    def encoded_public_key(self) -> str:
        return base58.b58encode(self.public_key).decode('utf-8')

    def sign(self, message: bytes) -> str:
        return self._secret_key.sign(message)

    @property
    def secret_key(self) -> bytes:
        return self._secret_key.to_bytes()

    @property
    def encoded_secret_key(self) -> str:
        return base58.b58encode(self.secret_key).decode('utf-8')

    @property
    def corresponding_account_id(self) -> str:
        return self.public_key.hex()

    @staticmethod
    def encoded_public_key_from_id(account_id) -> str:
        return base58.b58encode(bytes.fromhex(account_id)).decode('utf-8')


class Signer(object):
    def __init__(self, account_id: str, key_pair: 'KeyPair'):
        self._account_id = account_id
        self._key_pair = key_pair

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def key_pair(self) -> 'KeyPair':
        return self._key_pair

    @property
    def public_key(self) -> bytes:
        return self._key_pair.public_key

    def sign(self, message: bytes) -> str:
        return self._key_pair.sign(message)

    @classmethod
    def from_json(cls, j: dict):
        return cls(j['account_id'], KeyPair(j['secret_key']))

    @classmethod
    def from_json_file(cls, json_file: str):
        with open(json_file) as f:
            return cls.from_json(json.loads(f.read()))
