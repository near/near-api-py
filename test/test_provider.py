import unittest

import near_api

from config import NODE_URL


class JsonProviderTest(unittest.TestCase):

    def setUp(self):
        self.provider = near_api.providers.JsonProvider(NODE_URL)

    def test_status(self):
        status = self.provider.get_status()
        self.assertIsNotNone(status["chain_id"])

    def test_get_account(self):
        response = self.provider.get_account("test.near")
        self.assertEqual(response["code_hash"],
                         "11111111111111111111111111111111")
