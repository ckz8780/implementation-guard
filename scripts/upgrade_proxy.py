#!/usr/bin/env python3
import json
import sys
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.default_account = w3.eth.accounts[0]

def load_contract_artifact(contract_name):
    artifact_path = f"artifacts/contracts/{contract_name}.sol/{contract_name}.json"
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
    return artifact["abi"], artifact["bytecode"]

if len(sys.argv) != 3:
    print("Usage: python upgrade.py <proxy_address> <new_logic_address>")
    sys.exit(1)

proxy_address = sys.argv[1]
new_logic_address = sys.argv[2]

# Load the logic ABI to interact with the proxy
logic_abi, _ = load_contract_artifact("SimpleLogic")
proxy = w3.eth.contract(address=proxy_address, abi=logic_abi)

print(f"Upgrading proxy at {proxy_address}")
print(f"New logic: {new_logic_address}\n")

# Call upgradeToAndCall with empty data
tx_hash = proxy.functions.upgradeToAndCall(new_logic_address, b"").transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"SUCCESS: Upgrade complete")
print(f"Gas used: {tx_receipt['gasUsed']}")