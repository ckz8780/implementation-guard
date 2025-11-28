#!/usr/bin/env python3
import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.default_account = w3.eth.accounts[0]

def load_contract_artifact(contract_name):
    artifact_path = f"artifacts/contracts/{contract_name}.sol/{contract_name}.json"
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
    return artifact["abi"], artifact["bytecode"]

def deploy_contract(contract_name, *constructor_args):
    abi, bytecode = load_contract_artifact(contract_name)
    factory = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    print(f"Deploying {contract_name}...")
    tx_hash = factory.constructor(*constructor_args).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt["contractAddress"]
    print(f"SUCCESS: {contract_name} deployed to: {contract_address}")
    print(f"Gas used: {tx_receipt['gasUsed']}\n")
    
    return w3.eth.contract(address=contract_address, abi=abi)

# Deploy ImplementationGuard
initial_owner = w3.eth.default_account
guard = deploy_contract("ImplementationGuard", initial_owner)

print("=== DEPLOYMENT SUMMARY ===")
print(f"ImplementationGuard: {guard.address}")
print(f"Owner: {initial_owner}")