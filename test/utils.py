import time

import near_api


def create_account(master_account, amount=10 ** 24):
    account_id = "testtest-%s.test.near" % int(time.time() * 10_000)
    master_account.create_account(account_id, master_account.signer.public_key, amount)
    signer = near_api.signer.Signer(account_id, master_account.signer.key_pair)
    account = near_api.account.Account(master_account.provider, signer)
    return account
