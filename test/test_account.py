import unittest

import near_api

from config import NODE_URL


class AccountTest(unittest.TestCase):

    def setUp(self):
        provider = near_api.providers.JsonProvider(NODE_URL)
        signer = near_api.signer.Signer(
            "test.near", near_api.signer.KeyPair("ed25519:2wyRcSwSuHtRVmkMCGjPwnzZmQLeXLzLLyED1NDMt4BjnKgQL6tF85yBx6Jr26D2dUNeC716RBoTxntVHsegogYw"))
        self.master_account = near_api.account.Account(provider, signer, "test.near")

    def test_create_account(self):
        # TODO: write the test
        # self.master_account.create_account("testtest", self.master_account._signer._key_pair.encoded_public_key(), 1)
        pass
