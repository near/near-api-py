# near-api-py

*Status: super rough, APIs are subject to change*

A Python library for development of applications that are using NEAR platform.

# Installation

```bash
pip install near-api-py
```

# Usage example

## Send money

```python
near_provider = near_api.providers.JsonProvider("https://rpc.testnet.near.org")

sender_key_pair = near_api.signer.KeyPair("ed25519:[SENDER_PRIVATE_KEY]")
sender_signer = near_api.signer.Signer("sender.testnet", sender_key_pair)
sender_account = near_api.account.Account(near_provider, sender_signer)

out = sender_account.send_money("vsab.testnet", 1000)

print(out)
```


## Smart contract call method

```python
contract_id = "contract.testnet"
signer_id = "signer.testnet"
signer_key = "ed25519:[SIGNER_SECRET_KEY]"
args = {"counter": 1, "action": "increase"}

near_provider = near_api.providers.JsonProvider("https://rpc.testnet.near.org")
key_pair = near_api.signer.KeyPair(signer_key)
signer = near_api.signer.Signer(signer_id, key_pair)
account = near_api.account.Account(near_provider, signer)

out = account.function_call(contract_id, "counter_set", args)

print(out)
```


# Contribution

First, install the package in development mode:
```bash
python setup.py develop
```

To run tests, use nose (`pip install nose`):
```bash
nosetests
```

# License

This repository is distributed under the terms of both the MIT license and the Apache License (Version 2.0). See LICENSE and LICENSE-APACHE for details.
