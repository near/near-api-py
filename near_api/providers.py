import requests
import base64
import json

class FinalityTypes():
    FINAL = 'final'
    OPTIMISTIC = 'optimistic'

class JsonProviderError(Exception):
    pass


class JsonProvider(object):

    def __init__(self, rpc_addr):
        if isinstance(rpc_addr, tuple):
            self._rpc_addr = "http://%s:%s" % rpc_addr
        else:
            self._rpc_addr = rpc_addr

    def rpc_addr(self):
        return self._rpc_addr

    def json_rpc(self, method, params, timeout=2):
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

    def send_tx(self, signed_tx, timeout:int=2):
        return self.json_rpc('broadcast_tx_async', [base64.b64encode(signed_tx).decode('utf8')], timeout=timeout)

    def send_tx_and_wait(self, signed_tx, timeout:int=2):
        return self.json_rpc('broadcast_tx_commit', [base64.b64encode(signed_tx).decode('utf8')], timeout=timeout)

    def get_status(self, timeout:int=2):
        r = requests.get("%s/status" % self.rpc_addr(), timeout=timeout)
        r.raise_for_status()
        return json.loads(r.content)

    def get_validators(self, timeout:int=2):
        return self.json_rpc('validators', [None], timeout=timeout)

    def query(self, query_object, timeout:int=2):
        return self.json_rpc('query', query_object, timeout=timeout)

    def get_account(self, account_id, finality=FinalityTypes.OPTIMISTIC, timeout:int=2):
        return self.json_rpc('query', {"request_type": "view_account", "account_id": account_id, "finality": finality}, timeout=timeout)

    def get_access_key_list(self, account_id, finality=FinalityTypes.OPTIMISTIC, timeout:int=2):
        return self.json_rpc('query', {"request_type": "view_access_key_list", "account_id": account_id, "finality": finality}, timeout=timeout)

    def get_access_key(self, account_id, public_key, finality=FinalityTypes.OPTIMISTIC, timeout:int=2):
        return self.json_rpc('query', {"request_type": "view_access_key", "account_id": account_id,
                                       "public_key": public_key, "finality": finality}, timeout=timeout)

    def view_call(self, account_id, method_name, args, finality=FinalityTypes.OPTIMISTIC, timeout:int=2):
        return self.json_rpc('query', {"request_type": "call_function", "account_id": account_id,
                                       "method_name": method_name, "args_base64": base64.b64encode(args).decode('utf8'), "finality": finality}, timeout=timeout)

    def get_block(self, block_id, timeout:int=2):
        return self.json_rpc('block', [block_id], timeout=timeout)

    def get_chunk(self, chunk_id, timeout:int=2):
        return self.json_rpc('chunk', [chunk_id], timeout=timeout)

    def get_tx(self, tx_hash, tx_recipient_id, timeout:int=2):
        return self.json_rpc('tx', [tx_hash, tx_recipient_id], timeout=timeout)

    def get_changes_in_block(self, block_id=None, finality:str=None, timeout:int=2):
        '''Use either block_id or finality. Choose finality from "finality_types" class'''
        params = {}
        if block_id:
            params['block_id'] = block_id
        if finality:
            params['finality'] = finality
        return self.json_rpc('EXPERIMENTAL_changes_in_block', params, timeout=timeout)

    def get_receipt(self, receipt_hash, timeout:int=2):
        return self.json_rpc('EXPERIMENTAL_receipt', [receipt_hash], timeout=timeout)