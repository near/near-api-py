import base64
import json
from typing import Union, Tuple, Any

import requests

TimeoutType = Union[float, Tuple[float, float]]
""" The type used as "timeout" argument when sending requests. Quantities are in seconds.
    As a float, it indicates how long to wait for the server to send data,
    As a (connect timeout, read timeout) tuple, it specifically indicates how long to
    wait for the connection to establish and how long to wait for the sever to respond.
    See https://requests.readthedocs.io/en/latest/api/#requests.request"""


class FinalityTypes:
    FINAL = "final"
    OPTIMISTIC = "optimistic"


class JsonProviderError(Exception):
    pass


class JsonProvider(object):
    def __init__(self, rpc_addr, proxies=None):
        if isinstance(rpc_addr, tuple):
            self._rpc_addr = "http://%s:%s" % rpc_addr
        else:
            self._rpc_addr = rpc_addr
        self.proxies = proxies

    def rpc_addr(self) -> str:
        return self._rpc_addr

    def json_rpc(self, method: str, params: Union[dict, list, str], timeout: 'TimeoutType' = 2.0) -> dict:
        j = {
            'method': method,
            'params': params,
            'id': "dontcare",
            'jsonrpc': "2.0"
        }
        r = requests.post(self.rpc_addr(), json=j, timeout=timeout, proxies=self.proxies)
        r.raise_for_status()
        content = json.loads(r.content)
        if "error" in content:
            raise JsonProviderError(content['error'])
        return content['result']

    def send_tx(self, signed_tx: bytes, timeout: 'TimeoutType' = 2.0) -> dict:
        return self.json_rpc("broadcast_tx_async",
                             [base64.b64encode(signed_tx).decode('utf8')], timeout=timeout)

    def send_tx_and_wait(self, signed_tx: bytes, timeout: 'TimeoutType') -> dict:
        return self.json_rpc("broadcast_tx_commit",
                             [base64.b64encode(signed_tx).decode('utf8')],
                             timeout=timeout)

    def get_status(self, timeout: 'TimeoutType' = 2.0) -> dict:
        r = requests.get("%s/status" % self.rpc_addr(), timeout=timeout)
        r.raise_for_status()
        return json.loads(r.content)

    def get_validators(self, timeout: 'TimeoutType' = 2.0) -> dict:
        return self.json_rpc("validators", [None], timeout=timeout)

    def query(self, query_object: str, timeout: 'TimeoutType' = 2.0) -> dict:
        return self.json_rpc("query", query_object, timeout=timeout)

    def get_account(
            self,
            account_id: str,
            finality: str = FinalityTypes.OPTIMISTIC,
            timeout: 'TimeoutType' = 2.0
    ) -> dict:
        return self.json_rpc(
            "query", {
                'request_type': "view_account",
                'account_id': account_id,
                'finality': finality
            }, timeout=timeout)

    def get_access_key_list(
            self,
            account_id: str,
            finality: str = FinalityTypes.OPTIMISTIC,
            timeout: 'TimeoutType' = 2.0
    ) -> dict:
        return self.json_rpc(
            "query", {
                'request_type': "view_access_key_list",
                'account_id': account_id,
                'finality': finality
            }, timeout=timeout)

    def get_access_key(
            self,
            account_id: str,
            public_key: str,
            finality: str = FinalityTypes.OPTIMISTIC,
            timeout: 'TimeoutType' = 2.0
    ) -> dict:
        return self.json_rpc(
            "query", {
                'request_type': "view_access_key",
                'account_id': account_id,
                'public_key': public_key,
                'finality': finality
            }, timeout=timeout)

    def view_call(
            self,
            account_id: str,
            method_name: str,
            args: bytes,
            finality: str = FinalityTypes.OPTIMISTIC,
            timeout: 'TimeoutType' = 2.0
    ) -> dict:
        return self.json_rpc(
            "query", {
                'request_type': "call_function",
                'account_id': account_id,
                'method_name': method_name,
                'args_base64': base64.b64encode(args).decode('utf8'),
                'finality': finality
            }, timeout=timeout)

    def get_block(self, block_id: str, timeout: 'TimeoutType' = 2.0) -> dict:
        return self.json_rpc("block", [block_id], timeout=timeout)

    def get_chunk(self, chunk_id: str, timeout: 'TimeoutType' = 2.0) -> dict:
        return self.json_rpc("chunk", [chunk_id], timeout=timeout)

    def get_tx(self, tx_hash: str, tx_recipient_id: str, timeout: 'TimeoutType' = 2.0) -> dict:
        return self.json_rpc("tx", [tx_hash, tx_recipient_id], timeout=timeout)

    def get_changes_in_block(
            self,
            block_id: Union[str] = None,
            finality: str = None,
            timeout: 'TimeoutType' = 2.0
    ) -> dict:
        """Use either block_id or finality. Choose finality from "finality_types" class."""
        params = {}
        if block_id:
            params['block_id'] = block_id
        if finality:
            params['finality'] = finality
        return self.json_rpc("EXPERIMENTAL_changes_in_block", params, timeout=timeout)

    def get_validators_ordered(self, block_hash: bytes) -> dict:
        return self.json_rpc("EXPERIMENTAL_validators_ordered", [block_hash])

    def get_light_client_proof(
            self,
            outcome_type: str,
            tx_or_receipt_id: str,
            sender_or_receiver_id: str,
            light_client_head: str
    ) -> dict:
        if outcome_type == "receipt":
            params = {
                'type': "receipt",
                'receipt_id': tx_or_receipt_id,
                'receiver_id': sender_or_receiver_id,
                'light_client_head': light_client_head
            }
        else:
            params = {
                'type': "transaction",
                'transaction_hash': tx_or_receipt_id,
                'sender_id': sender_or_receiver_id,
                'light_client_head': light_client_head
            }
        return self.json_rpc("light_client_proof", params)

    def get_next_light_client_block(self, last_block_hash) -> dict:
        return self.json_rpc("next_light_client_block", [last_block_hash])

    def get_receipt(self, receipt_hash, timeout: 'TimeoutType' = 2.0) -> dict:
        return self.json_rpc("EXPERIMENTAL_receipt", [receipt_hash], timeout=timeout)
