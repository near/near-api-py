import base58
import json
import itertools

from near_api import transactions


# Amount of gas attached by default 1e14.
DEFAULT_ATTACHED_GAS = 100000000000000


class TransactionError(Exception):
    pass


class ViewFunctionError(Exception):
    pass


class Account(object):

    def __init__(self, provider, signer, account_id):
        self._provider = provider
        self._signer = signer
        self._account_id = account_id
        self._account = provider.get_account(account_id)
        self._access_key = provider.get_access_key(account_id, signer._key_pair.encoded_public_key())
        print(account_id, self._account, self._access_key)

    def _sign_and_submit_tx(self, receiver_id, actions):
        self._access_key["nonce"] += 1
        block_hash = self._provider.get_status()['sync_info']['latest_block_hash']
        block_hash = base58.b58decode(block_hash.encode('utf8'))
        serialzed_tx = transactions.sign_and_serialize_transaction(
            receiver_id, self._access_key["nonce"], actions, block_hash, self._signer)
        result = self._provider.send_tx_and_wait(serialzed_tx, 10)
        for outcome in itertools.chain([result['transaction_outcome']], result['receipts_outcome']):
            for log in outcome['outcome']['logs']:
                print("Log:", log)
        if 'Failure' in result['status']:
            raise TransactionError(result['status']['Failure'])
        return result

    @property
    def account_id(self):
        return self._account_id

    @property
    def signer(self):
        return self._signer

    @property
    def provider(self):
        return self._provider

    @property
    def access_key(self):
        return self._access_key

    @property
    def state(self):
        return self._account

    def fetch_state(self):
        """Fetch state for given account."""
        self._account = self.provider.get_account(self.account_id)

    def send_money(self, account_id, amount):
        """Sends funds to given account_id given amount."""
        return self._sign_and_submit_tx(account_id, [transactions.create_transfer_action(amount)])

    def function_call(self, contract_id, method_name, args, gas=DEFAULT_ATTACHED_GAS, amount=0):
        args = json.dumps(args).encode('utf8')
        return self._sign_and_submit_tx(contract_id, [transactions.create_function_call_action(method_name, args, gas, amount)])

    def create_account(self, account_id, public_key, initial_balance):
        actions = [
            transactions.create_create_account_action(),
            transactions.create_full_access_key_action(public_key),
            transactions.create_transfer_action(initial_balance)]
        return self._sign_and_submit_tx(account_id, actions)

    def deploy_contract(self, contract_code):
        return self._sign_and_submit_tx(self._account_id, [transactions.create_deploy_contract_action(contract_code)])

    def stake(self, public_key, amount):
        return self._sign_and_submit_tx(self._account_id, [transactions.create_staking_action(public_key, amount)])

    def create_and_deploy_contract(self, contract_id, public_key, contract_code, initial_balance):
        actions = [
            transactions.create_create_account_action(),
            transactions.create_transfer_action(initial_balance),
            transactions.create_deploy_contract_action(contract_code)] + \
                  ([transactions.create_full_access_key_action(public_key)] if public_key is not None else [])
        return self._sign_and_submit_tx(contract_id, actions)

    def create_deploy_and_init_contract(self, contract_id, public_key, contract_code, initial_balance, args,
                                        gas=DEFAULT_ATTACHED_GAS, init_method_name="new"):
        args = json.dumps(args).encode('utf8')
        actions = [
          transactions.create_create_account_action(),
          transactions.create_transfer_action(initial_balance),
          transactions.create_deploy_contract_action(contract_code),
          transactions.create_function_call_action(init_method_name, args, gas, 0)] + \
                  ([transactions.create_full_access_key_action(public_key)] if public_key is not None else [])
        return self._sign_and_submit_tx(contract_id, actions)

    def view_function(self, contract_id, method_name, args):
        result = self._provider.view_call(contract_id, method_name, json.dumps(args).encode('utf8'))
        if "error" in result:
            raise ViewFunctionError(result["error"])
        result["result"] = json.loads(''.join([chr(x) for x in result["result"]]))
        return result
