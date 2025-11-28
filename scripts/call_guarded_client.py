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

if len(sys.argv) != 2:
    print("Usage: python call_guarded_client.py <client_address>")
    sys.exit(1)

client_address = sys.argv[1]

# Load GuardedProxyClient contract
client_abi, _ = load_contract_artifact("GuardedProxyClient")
client = w3.eth.contract(address=client_address, abi=client_abi)

print(f"Calling GuardedProxyClient at {client_address}\n")

try:
    # Try to get the current value
    print("Calling safeGetValue()...")
    current_value = client.functions.safeGetValue().call()
    print(f"Current value: {current_value}")
    
    # Try to set a new value
    test_value = 200
    print(f"\nCalling safeSetValue({test_value})...")
    tx_hash = client.functions.safeSetValue(test_value).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"SUCCESS: Value set")
    print(f"Gas used: {tx_receipt['gasUsed']}")
    
    # Get the new value
    print("\nCalling safeGetValue() again...")
    new_value = client.functions.safeGetValue().call()
    print(f"New value: {new_value}")
    
except Exception as e:
    print(f"FAILED: {e}")
    print("\nThis is expected if the current implementation is not approved in the guard.")