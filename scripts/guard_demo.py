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
    print(f"  Deployed to: {contract_address}")
    
    return w3.eth.contract(address=contract_address, abi=abi)

print("=" * 80)
print("FULL IMPLEMENTATION GUARD DEMO")
print("=" * 80)

# Step 1: Deploy V1 Logic
print("\n[1] Deploying SimpleLogic V1...")
logic_v1 = deploy_contract("SimpleLogic")

# Step 2: Deploy Proxy
print("\n[2] Deploying SimpleProxy...")
owner = w3.eth.default_account
proxy = deploy_contract("SimpleProxy", logic_v1.address, owner)

# Step 3: Test V1 through proxy
print("\n[3] Testing V1 through proxy...")
logic_abi, _ = load_contract_artifact("SimpleLogic")
proxy_as_logic = w3.eth.contract(address=proxy.address, abi=logic_abi)
version = proxy_as_logic.functions.version().call()
value = proxy_as_logic.functions.value().call()
print(f"  Version: {version}")
print(f"  Value: {value}")

# Step 4: Deploy ImplementationGuard
print("\n[4] Deploying ImplementationGuard...")
guard = deploy_contract("ImplementationGuard", owner)

# Step 5: Deploy GuardedProxyClient
print("\n[5] Deploying GuardedProxyClient...")
client = deploy_contract("GuardedProxyClient", guard.address, proxy.address)

# Step 6: Try to use client WITHOUT approval (should fail)
print("\n[6] Attempting to call GuardedProxyClient WITHOUT approval...")
client_abi, _ = load_contract_artifact("GuardedProxyClient")
guarded_client = w3.eth.contract(address=client.address, abi=client_abi)
try:
    # Build transaction manually to avoid gas estimation issues
    tx = guarded_client.functions.safeSetValue(100).build_transaction({
        'from': w3.eth.default_account,
        'gas': 100000,  # Manual gas limit
        'nonce': w3.eth.get_transaction_count(w3.eth.default_account)
    })
    tx_hash = w3.eth.send_transaction(tx)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("  ERROR: Should have failed!")
except Exception as e:
    print(f"  EXPECTED FAILURE: Transaction reverted (implementation not approved)")

# Step 7: Approve V1 implementation
print("\n[7] Approving V1 implementation in guard...")
tx_hash = guard.functions.approveImplementation(proxy.address, logic_v1.address).transact()
w3.eth.wait_for_transaction_receipt(tx_hash)
print("  Approved!")

# Step 8: Try to use client WITH approval (should succeed)
print("\n[8] Attempting to call GuardedProxyClient WITH approval...")
value = guarded_client.functions.safeGetValue().call()
print(f"  SUCCESS: Value = {value}")

# Step 9: Deploy V2 Logic
print("\n[9] Deploying SimpleLogic V2...")
logic_v2 = deploy_contract("SimpleLogicV2")

# Step 10: Upgrade proxy to V2
print("\n[10] Upgrading proxy to V2...")
tx_hash = proxy_as_logic.functions.upgradeToAndCall(logic_v2.address, b"").transact()
w3.eth.wait_for_transaction_receipt(tx_hash)
print("  Upgraded!")

# Step 11: Verify upgrade worked through direct proxy call
print("\n[11] Testing V2 through direct proxy call...")
version = proxy_as_logic.functions.version().call()
print(f"  Version: {version}")

# Step 12: Try to use client after upgrade WITHOUT approving V2 (should fail)
print("\n[12] Attempting to call GuardedProxyClient after upgrade (V2 not approved)...")
try:
    # Build transaction manually to avoid gas estimation issues
    tx = guarded_client.functions.safeSetValue(100).build_transaction({
        'from': w3.eth.default_account,
        'gas': 100000,  # Manual gas limit
        'nonce': w3.eth.get_transaction_count(w3.eth.default_account)
    })
    tx_hash = w3.eth.send_transaction(tx)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("  ERROR: Should have failed!")
except Exception as e:
    print(f"  EXPECTED FAILURE: Transaction reverted (implementation not approved)")

# Step 13: Approve V2 implementation
print("\n[13] Approving V2 implementation in guard...")
tx_hash = guard.functions.approveImplementation(proxy.address, logic_v2.address).transact()
w3.eth.wait_for_transaction_receipt(tx_hash)
print("  Approved!")

# Step 14: Try to use client WITH V2 approval (should succeed)
print("\n[14] Attempting to call GuardedProxyClient WITH V2 approval...")
value = guarded_client.functions.safeGetValue().call()
print(f"  SUCCESS: Value = {value}")

# Step 15: Test V2 behavior through guarded client
print("\n[15] Testing V2 behavior (setValue adds 1)...")
tx_hash = guarded_client.functions.safeSetValue(100).transact()
w3.eth.wait_for_transaction_receipt(tx_hash)
value = guarded_client.functions.safeGetValue().call()
print(f"  Called safeSetValue(100)")
print(f"  Result: Value = {value} (should be 101)")

print("\n" + "=" * 80)
print("DEMO COMPLETE")
print("=" * 80)
print("\nDeployed Addresses:")
print(f"  Logic V1: {logic_v1.address}")
print(f"  Logic V2: {logic_v2.address}")
print(f"  Proxy: {proxy.address}")
print(f"  Guard: {guard.address}")
print(f"  GuardedProxyClient: {client.address}")