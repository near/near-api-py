import json
from typing import Union

import base58
from nacl import signing, encoding


class KeyPair(object):

    def __init__(self, secret_key: Union[str, bytes, None] = None):
        """
        If no secret_key, a new one is created.
        secret_key must be a base58-encoded string or
        the byte object returned as "secret_key" property of a KeyPair object."""
        if not secret_key:
            self._secret_key = signing.SigningKey.generate()
        if isinstance(secret_key, bytes):
            self._secret_key = signing.SigningKey(secret_key, encoder=encoding.RawEncoder)
        elif isinstance(secret_key, str):
            secret_key = secret_key.split(':')[-1]
            self._secret_key = signing.SigningKey(base58.b58decode(secret_key)[:32], encoder=encoding.RawEncoder)
        else:
            raise Exception("Unrecognised")
        self._public_key = self._secret_key.verify_key

    @property
    def public_key(self) -> bytes:
        return self._public_key.encode()

    def encoded_public_key(self) -> str:
        return base58.b58encode(self.public_key).decode('utf-8')

    def sign(self, message: bytes) -> bytes:
        return self._secret_key.sign(message).signature

    @property
    def secret_key(self) -> bytes:
        return self._secret_key.encode()

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

    def sign(self, message: bytes) -> bytes:
        return self._key_pair.sign(message)

    @classmethod
    def from_json(cls, j: dict):
        return cls(j['account_id'], KeyPair(j['secret_key']))

    @classmethod
    def from_json_file(cls, json_file: str):
        with open(json_file) as f:
            return cls.from_json(json.loads(f.read()))
