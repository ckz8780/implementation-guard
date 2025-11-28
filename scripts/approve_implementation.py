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

if len(sys.argv) != 4:
    print("Usage: python approve_implementation.py <guard_address> <proxy_address> <implementation_address>")
    sys.exit(1)

guard_address = sys.argv[1]
proxy_address = sys.argv[2]
implementation_address = sys.argv[3]

# Load guard contract
guard_abi, _ = load_contract_artifact("ImplementationGuard")
guard = w3.eth.contract(address=guard_address, abi=guard_abi)

print(f"Approving implementation for proxy {proxy_address}")
print(f"Implementation: {implementation_address}\n")

# Call approveImplementation
tx_hash = guard.functions.approveImplementation(proxy_address, implementation_address).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"SUCCESS: Implementation approved")
print(f"Gas used: {tx_receipt['gasUsed']}")