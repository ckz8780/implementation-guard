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
    print("Usage: python call_proxy.py <proxy_address>")
    sys.exit(1)

proxy_address = sys.argv[1]

# Load proxy ABI to call implementation()
proxy_abi, _ = load_contract_artifact("SimpleProxy")
proxy = w3.eth.contract(address=proxy_address, abi=proxy_abi)

# Get current implementation
current_implementation = proxy.functions.implementation().call()
print(f"Proxy: {proxy_address}")
print(f"Current implementation: {current_implementation}\n")

# Load logic ABI to interact with proxy as logic
logic_abi, _ = load_contract_artifact("SimpleLogic")
proxy_as_logic = w3.eth.contract(address=proxy_address, abi=logic_abi)

# Check version to determine expected behavior
version = proxy_as_logic.functions.version().call()
print(f"Version: {version}")

# Get current value
current_value = proxy_as_logic.functions.value().call()
print(f"Current value: {current_value}\n")

# Determine expected behavior based on version
test_input = 100
if version == "v1":
    expected_result = test_input
    print(f"Expected behavior (V1): setValue({test_input}) should set value to {expected_result}")
elif version == "v2":
    expected_result = test_input + 1
    print(f"Expected behavior (V2): setValue({test_input}) should set value to {expected_result}")
else:
    print(f"Unknown version: {version}")
    sys.exit(1)

# Execute setValue
print(f"\nCalling setValue({test_input})...")
tx_hash = proxy_as_logic.functions.setValue(test_input).transact()
w3.eth.wait_for_transaction_receipt(tx_hash)

# Get actual result
actual_result = proxy_as_logic.functions.value().call()
print(f"Actual result: value = {actual_result}")

# Verify
if actual_result == expected_result:
    print("SUCCESS: Behavior matches expected version")
else:
    print(f"FAILURE: Expected {expected_result}, got {actual_result}")