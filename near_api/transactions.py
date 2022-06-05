import hashlib

import near_api
from near_api.serializer import BinarySerializer


class Signature:
    pass


class SignedTransaction:
    pass


class Transaction:
    pass


class PublicKey:
    pass


class AccessKey:
    pass


class AccessKeyPermission:
    pass


class FunctionCallPermission:
    pass


class FullAccessPermission:
    pass


class Action:
    pass


class CreateAccount:
    pass


class DeployContract:
    pass


class FunctionCall:
    pass


class Transfer:
    pass


class Stake:
    pass


class AddKey:
    pass


class DeleteKey:
    pass


class DeleteAccount:
    pass


tx_schema = dict(
    [
        [
            Signature,
            {
                'kind': 'struct',
                'fields': [
                    ['keyType', 'u8'],
                    ['data', [64]],
                ],
            },
        ],
        [
            SignedTransaction,
            {
                'kind': 'struct',
                'fields': [
                    ['transaction', Transaction],
                    ['signature', Signature],
                ],
            },
        ],
        [
            Transaction,
            {
                'kind': 'struct',
                'fields': [
                    ['signerId', 'string'],
                    ['publicKey', PublicKey],
                    ['nonce', 'u64'],
                    ['receiverId', 'string'],
                    ['blockHash', [32]],
                    ['actions', [Action]],
                ],
            },
        ],
        [
            PublicKey,
            {
                'kind': 'struct',
                'fields': [
                    ['keyType', 'u8'],
                    ['data', [32]],
                ],
            },
        ],
        [
            AccessKey,
            {
                'kind': 'struct',
                'fields': [
                    ['nonce', 'u64'],
                    ['permission', AccessKeyPermission],
                ],
            },
        ],
        [
            AccessKeyPermission,
            {
                'kind': 'enum',
                'field': 'enum',
                'values': [
                    ['functionCall', FunctionCallPermission],
                    ['fullAccess', FullAccessPermission],
                ],
            },
        ],
        [
            FunctionCallPermission,
            {
                'kind': 'struct',
                'fields': [
                    ['allowance', {'kind': 'option', type: 'u128'}],
                    ['receiverId', 'string'],
                    ['methodNames', ['string']],
                ],
            },
        ],
        [
            FullAccessPermission,
            {
                'kind': 'struct',
                'fields': []
            },
        ],
        [
            Action,
            {
                'kind': 'enum',
                'field': 'enum',
                'values': [
                    ['createAccount', CreateAccount],
                    ['deployContract', DeployContract],
                    ['functionCall', FunctionCall],
                    ['transfer', Transfer],
                    ['stake', Stake],
                    ['addKey', AddKey],
                    ['deleteKey', DeleteKey],
                    ['deleteAccount', DeleteAccount],
                ],
            },
        ],
        [
            CreateAccount,
            {
                'kind': 'struct',
                'fields': []
            },
        ],
        [
            DeployContract,
            {
                'kind': 'struct',
                'fields': [
                    ['code', ['u8']],
                ],
            },
        ],
        [
            FunctionCall,
            {
                'kind': 'struct',
                'fields': [
                    ['methodName', 'string'],
                    ['args', ['u8']],
                    ['gas', 'u64'],
                    ['deposit', 'u128'],
                ],
            },
        ],
        [
            Transfer,
            {
                'kind': 'struct',
                'fields': [
                    ['deposit', 'u128'],
                ],
            },
        ],
        [
            Stake,
            {
                'kind': 'struct',
                'fields': [
                    ['stake', 'u128'],
                    ['publicKey', PublicKey],
                ],
            },
        ],
        [
            AddKey,
            {
                'kind': 'struct',
                'fields': [
                    ['publicKey', PublicKey],
                    ['accessKey', AccessKey]
                ],
            },
        ],
        [
            DeleteKey,
            {
                'kind': 'struct',
                'fields': [
                    ['publicKey', PublicKey],
                ],
            },
        ],
        [
            DeleteAccount,
            {
                'kind': 'struct',
                'fields': [
                    ['beneficiaryId', 'string'],
                ],
            },
        ],
    ]
)


def sign_and_serialize_transaction(
        receiver_id: str,
        nonce: int,
        actions: list[Action],
        block_hash: bytes,
        signer: 'near_api.signer.Signer'
) -> bytes:
    assert signer.public_key is not None    # TODO: Need to replace to Exception
    assert block_hash is not None    # TODO: Need to replace to Exception
    tx = Transaction()
    tx.signerId = signer.account_id
    tx.publicKey = PublicKey()
    tx.publicKey.keyType = 0
    tx.publicKey.data = signer.public_key
    tx.nonce = nonce
    tx.receiverId = receiver_id
    tx.actions = actions
    tx.blockHash = block_hash

    msg: bytes = BinarySerializer(tx_schema).serialize(tx)
    hash_: bytes = hashlib.sha256(msg).digest()

    signature = Signature()
    signature.keyType = 0
    signature.data = signer.sign(hash_)

    signed_tx = SignedTransaction()
    signed_tx.transaction = tx
    signed_tx.signature = signature

    return BinarySerializer(tx_schema).serialize(signed_tx)


def create_create_account_action() -> 'Action':
    create_account = CreateAccount()
    action = Action()
    action.enum = "createAccount"
    action.createAccount = create_account
    return action


def create_delete_account_action(beneficiary_id: str) -> 'Action':
    delete_account = DeleteAccount()
    delete_account.beneficiaryId = beneficiary_id
    action = Action()
    action.enum = "deleteAccount"
    action.deleteAccount = delete_account
    return action


def create_full_access_key_action(pk: str) -> 'Action':
    permission = AccessKeyPermission()
    permission.enum = "fullAccess"
    permission.fullAccess = FullAccessPermission()
    access_key = AccessKey()
    access_key.nonce = 0
    access_key.permission = permission
    public_key = PublicKey()
    public_key.keyType = 0
    public_key.data = pk
    add_key = AddKey()
    add_key.accessKey = access_key
    add_key.publicKey = public_key
    action = Action()
    action.enum = "addKey"
    action.addKey = add_key
    return action


def create_delete_access_key_action(pk: str) -> 'Action':
    public_key = PublicKey()
    public_key.keyType = 0
    public_key.data = pk
    delete_key = DeleteKey()
    delete_key.publicKey = public_key
    action = Action()
    action.enum = "deleteKey"
    action.deleteKey = delete_key
    return action


def create_transfer_action(amount: int) -> 'Action':
    transfer = Transfer()
    transfer.deposit = amount
    action = Action()
    action.enum = "transfer"
    action.transfer = transfer
    return action


# TODO: deprecate usage of create_payment_action.
create_payment_action = create_transfer_action


def create_staking_action(amount: int, pk: str) -> 'Action':
    stake = Stake()
    stake.stake = amount
    stake.publicKey = PublicKey()
    stake.publicKey.keyType = 0
    stake.publicKey.data = pk
    action = Action()
    action.enum = "stake"
    action.stake = stake
    return action


def create_deploy_contract_action(code: bytes) -> 'Action':
    deploy_contract = DeployContract()
    deploy_contract.code = code
    action = Action()
    action.enum = "deployContract"
    action.deployContract = deploy_contract
    return action


def create_function_call_action(method_name: str, args: bytes, gas: int, deposit: int) -> 'Action':
    function_call = FunctionCall()
    function_call.methodName = method_name
    function_call.args = args
    function_call.gas = gas
    function_call.deposit = deposit
    action = Action()
    action.enum = "functionCall"
    action.functionCall = function_call
    return action


def sign_create_account_tx(
        creator_signer: 'near_api.signer.Signer',
        new_account_id: str,
        nonce: int,
        block_hash: bytes
) -> bytes:
    action = create_create_account_action()
    return sign_and_serialize_transaction(new_account_id, nonce, [action], block_hash, creator_signer)


def sign_create_account_with_full_access_key_and_balance_tx(
        creator_key: 'near_api.signer.Signer',
        new_account_id: str,
        new_key,
        balance: int,
        nonce: int,
        block_hash: bytes
) -> bytes:
    create_account_action = create_create_account_action()
    full_access_key_action = create_full_access_key_action(new_key.decoded_pk())
    payment_action = create_transfer_action(balance)
    actions = [create_account_action, full_access_key_action, payment_action]
    return sign_and_serialize_transaction(new_account_id, nonce, actions, block_hash, creator_key.account_id,
                                          creator_key.decoded_pk(), creator_key.decoded_sk())   # TODO: Last two params is unused


def sign_delete_access_key_tx(
        signer_key: 'near_api.signer.Signer',
        target_account_id: str,
        key_for_deletion,
        nonce: int,
        block_hash: bytes
) -> bytes:
    action = create_delete_access_key_action(key_for_deletion.decoded_pk())
    return sign_and_serialize_transaction(target_account_id, nonce, [action], block_hash, signer_key.account_id,
                                          signer_key.decoded_pk(), signer_key.decoded_sk())   # TODO: Last two params is unused


def sign_payment_tx(
        key: 'near_api.signer.Signer',
        to: str,
        amount: int,
        nonce: int,
        block_hash: bytes
) -> bytes:
    action = create_transfer_action(amount)
    return sign_and_serialize_transaction(to, nonce, [action], block_hash, key.account_id,
                                          key.decoded_pk(), key.decoded_sk())   # TODO: Last two params is unused


def sign_staking_tx(
        signer_key: 'near_api.signer.Signer',
        validator_key,
        amount: int,
        nonce: int,
        block_hash: bytes
) -> bytes:
    action = create_staking_action(amount, validator_key.decoded_pk())
    return sign_and_serialize_transaction(signer_key.account_id, nonce, [action], block_hash, signer_key.account_id,
                                          signer_key.decoded_pk(), signer_key.decoded_sk())   # TODO: Last two params is unused


def sign_deploy_contract_tx(
        signer_key: 'near_api.signer.Signer',
        code: bytes,
        nonce: int,
        block_hash: bytes
) -> bytes:
    action = create_deploy_contract_action(code)
    return sign_and_serialize_transaction(signer_key.account_id, nonce, [action], block_hash, signer_key.account_id,
                                          signer_key.decoded_pk(), signer_key.decoded_sk())   # TODO: Last two params is unused


def sign_function_call_tx(
        signer_key: 'near_api.signer.Signer',
        contract_id: str,
        method_name: str,
        args: bytes,
        gas: int,
        deposit: int,
        nonce: int,
        block_hash: bytes
) -> bytes:
    action = create_function_call_action(method_name, args, gas, deposit)
    return sign_and_serialize_transaction(contract_id, nonce, [action], block_hash, signer_key.account_id,
                                          signer_key.decoded_pk(), signer_key.decoded_sk())   # TODO: Last two params is unused
