import requests
import base64
import json


class JsonProviderError(Exception):
    pass


class JsonProvider(object):
    def __init__(self, rpc_addr):
        if isinstance(rpc_addr, tuple):
            self._rpc_addr = "http://%s:%s" % rpc_addr
        else:
            self._rpc_addr = rpc_addr

    def rpc_addr(self) -> str:
        return self._rpc_addr

    def json_rpc(self, method: str, params, timeout=2) -> dict:
        j = {
            'method': method,
            'params': params,
            'id': 'dontcare',
            'jsonrpc': '2.0'
        }
        r = requests.post(self.rpc_addr(), json=j, timeout=timeout)
        r.raise_for_status()
        content = json.loads(r.content)
        if "error" in content:
            raise JsonProviderError(content["error"])
        return content["result"]

    def send_tx(self, signed_tx: bytes) -> dict:
        return self.json_rpc('broadcast_tx_async',
                             [base64.b64encode(signed_tx).decode('utf8')])

    def send_tx_and_wait(self, signed_tx: bytes, timeout: int) -> dict:
        return self.json_rpc('broadcast_tx_commit',
                             [base64.b64encode(signed_tx).decode('utf8')],
                             timeout=timeout)

    def get_status(self) -> dict:
        r = requests.get("%s/status" % self.rpc_addr(), timeout=2)
        r.raise_for_status()
        return json.loads(r.content)

    def get_validators(self) -> dict:
        return self.json_rpc('validators', [None])

    def query(self, query_object) -> dict:
        return self.json_rpc('query', query_object)

    def get_account(self, account_id: str, finality='optimistic') -> dict:
        return self.json_rpc(
            'query', {
                "request_type": "view_account",
                "account_id": account_id,
                "finality": finality
            })

    def get_access_key_list(self, account_id: str, finality='optimistic') -> dict:
        return self.json_rpc(
            'query', {
                "request_type": "view_access_key_list",
                "account_id": account_id,
                "finality": finality
            })

    def get_access_key(self, account_id: str, public_key: str, finality='optimistic') -> dict:
        return self.json_rpc(
            'query', {
                "request_type": "view_access_key",
                "account_id": account_id,
                "public_key": public_key,
                "finality": finality
            })

    def view_call(self, account_id: str, method_name: str, args: bytes, finality='optimistic'):
        return self.json_rpc(
            'query', {
                "request_type": "call_function",
                "account_id": account_id,
                "method_name": method_name,
                "args_base64": base64.b64encode(args).decode('utf8'),
                "finality": finality
            })

    def get_block(self, block_id) -> dict:
        return self.json_rpc('block', [block_id])

    def get_chunk(self, chunk_id) -> dict:
        return self.json_rpc('chunk', [chunk_id])

    def get_tx(self, tx_hash, tx_recipient_id) -> dict:
        return self.json_rpc('tx', [tx_hash, tx_recipient_id])

    def get_changes_in_block(self, changes_in_block_request) -> dict:
        return self.json_rpc('EXPERIMENTAL_changes_in_block',
                             changes_in_block_request)

    def get_validators_ordered(self, block_hash) -> dict:
        return self.json_rpc('EXPERIMENTAL_validators_ordered', [block_hash])

    def get_light_client_proof(self, outcome_type, tx_or_receipt_id,
                               sender_or_receiver_id, light_client_head) -> dict:
        if outcome_type == "receipt":
            params = {
                "type": "receipt",
                "receipt_id": tx_or_receipt_id,
                "receiver_id": sender_or_receiver_id,
                "light_client_head": light_client_head
            }
        else:
            params = {
                "type": "transaction",
                "transaction_hash": tx_or_receipt_id,
                "sender_id": sender_or_receiver_id,
                "light_client_head": light_client_head
            }
        return self.json_rpc('light_client_proof', params)

    def get_next_light_client_block(self, last_block_hash) -> dict:
        return self.json_rpc('next_light_client_block', [last_block_hash])
