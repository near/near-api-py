import unittest

import near_api
from config import NODE_URL, TEST_ACCOUNT, TEST_KEY_PAIR
from utils import create_account


class AccountTest(unittest.TestCase):
    def setUp(self):
        self.provider = near_api.providers.JsonProvider(NODE_URL)
        self.signer = near_api.signer.Signer(
            TEST_ACCOUNT,
            near_api.signer.KeyPair(TEST_KEY_PAIR)
        )
        self.master_account = near_api.account.Account(self.provider, self.signer)

    def test_create_account(self):
        amount = 10 ** 24
        account = create_account(self.master_account, amount)
        self.assertEqual(int(account.state["amount"]), amount)

    def test_send_money(self):
        sender = create_account(self.master_account)
        receiver = create_account(self.master_account)
        sender.send_money(receiver.account_id, 1000)
        receiver.fetch_state()
        self.assertEqual(int(receiver.state["amount"]), 10 ** 24 + 1000)
