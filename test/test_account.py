import time

import unittest

import near_api

from config import NODE_URL


def create_account(master_account, amount=10**24):
    account_id = "testtest-%s" % int(time.time() * 10000)
    master_account.create_account(account_id, master_account.signer.public_key, amount)
    signer = near_api.signer.Signer(account_id, master_account.signer.key_pair)
    account = near_api.account.Account(
        master_account.provider, signer, account_id)
    return account


class AccountTest(unittest.TestCase):

    def setUp(self):
        self.provider = near_api.providers.JsonProvider(NODE_URL)
        self.signer = near_api.signer.Signer(
            "test.near", near_api.signer.KeyPair("ed25519:2wyRcSwSuHtRVmkMCGjPwnzZmQLeXLzLLyED1NDMt4BjnKgQL6tF85yBx6Jr26D2dUNeC716RBoTxntVHsegogYw"))
        self.master_account = near_api.account.Account(self.provider, self.signer, "test.near")

    def test_create_account(self):
        amount = 10**24
        account = create_account(self.master_account, amount)
        self.assertEqual(int(account.state["amount"]), amount)

    def test_send_money(self):
        sender = create_account(self.master_account)
        receiver = create_account(self.master_account)
        sender.send_money(receiver.account_id, 1000)
        receiver.fetch_state()
        self.assertEqual(int(receiver.state["amount"]), 10**24 + 1000)
