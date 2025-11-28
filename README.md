# Implementation Guard Demo

This repository demonstrates a defense mechanism against malicious upgrades in external upgradeable smart contracts. It shows how to use the `ImplementationGuard` registry to verify that external proxies are using approved implementations before interacting with them.

## What This Demonstrates

**The Problem:** When your protocol depends on external upgradeable contracts (via proxies), a malicious upgrade to those external contracts could steal funds or break your protocol's functionality.

**The Solution:** Before calling an external proxy, verify its current implementation address against your own approved list. This gives you control over which versions of external dependencies you trust, even though you don't control the external protocol's upgrade mechanism.

**Key Concepts:**
- UUPS (Universal Upgradeable Proxy Standard) proxies separate storage (proxy) from logic (implementation)
- Upgrades change the implementation while preserving the proxy address and state
- `ImplementationGuard` is a separate registry *you* control to track approved implementations
- `GuardedProxyClient` demonstrates safe interaction patterns with external proxies

## Quickstart
```bash
# Clone and setup
git clone <repository-url>
cd implementation-guard

# Install Python dependencies and activate the venv
pipenv install
pipenv shell

# Install Node dependencies and compile contracts
npm install
make compile # (or npx hardhat compile if you don't have make)

# Terminal 1: Start local blockchain
make hardhat # (or npx hardhat node if you don't have make)

# Terminal 2: Run full demo
python scripts/guard_demo.py
```

## Project Structure
```
contracts/
├── SimpleLogic.sol           # V1 implementation (basic logic)
├── SimpleLogicV2.sol         # V2 implementation (modified behavior)
├── SimpleProxy.sol           # ERC1967 UUPS proxy
├── ImplementationGuard.sol   # Registry for approved implementations
└── GuardedProxyClient.sol    # Safe client that checks implementations

scripts/
├── deploy_v1_logic.py        # Deploy V1 implementation
├── deploy_proxy.py           # Deploy proxy pointing to an implementation
├── call_proxy.py             # Test proxy behavior and show current implementation
├── deploy_v2_logic.py        # Deploy V2 implementation
├── upgrade.py                # Upgrade proxy to new implementation
├── deploy_guard.py           # Deploy ImplementationGuard registry
├── deploy_guarded_client.py  # Deploy GuardedProxyClient
├── approve_implementation.py # Approve an implementation in the guard
├── call_guarded_client.py    # Safely interact with proxy via guarded client
└── guard_demo.py             # Full automated demonstration
```

## Script Descriptions

- **deploy_v1_logic.py** - Deploys the `SimpleLogic` V1 implementation contract.
- **deploy_proxy.py** - Deploys a `SimpleProxy` contract pointing to a specified implementation address.
- **call_proxy.py** - Calls functions on the proxy to demonstrate current behavior and shows the active implementation address.
- **deploy_v2_logic.py** - Deploys the `SimpleLogicV2` implementation with modified behavior.
- **upgrade.py** - Upgrades a proxy to point to a new implementation address.
- **deploy_guard.py** - Deploys the `ImplementationGuard` registry contract.
- **deploy_guarded_client.py** - Deploys a `GuardedProxyClient` that safely interacts with an external proxy.
- **approve_implementation.py** - Approves an implementation address for a proxy in the guard registry.
- **call_guarded_client.py** - Calls functions through the guarded client (reverts if implementation not approved).
- **guard_demo.py** - Runs the complete workflow automatically to demonstrate the full security mechanism.

## Manual Testing Flow

For a hands-on understanding, run the scripts manually (hardhat must be running):
```bash
# 1. Deploy and test basic proxy upgrade
python scripts/deploy_v1_logic.py              # Note V1 address
python scripts/deploy_proxy.py <v1_address>    # Note proxy address
python scripts/call_proxy.py <proxy_address>   # Shows V1 behavior

python scripts/deploy_v2_logic.py              # Note V2 address
python scripts/upgrade.py <proxy_address> <v2_address>
python scripts/call_proxy.py <proxy_address>   # Shows V2 behavior

# 2. Add implementation guard protection
python scripts/deploy_guard.py                 # Note guard address
python scripts/deploy_guarded_client.py <guard_address> <proxy_address>  # Note client address

# 3. Try without approval (fails)
python scripts/call_guarded_client.py <client_address>  # REVERTS

# 4. Approve and try again (succeeds)
python scripts/approve_implementation.py <guard_address> <proxy_address> <v2_address>
python scripts/call_guarded_client.py <client_address>  # SUCCESS
```

## How It Works

1. **`SimpleProxy`** represents an external dependency you don't control
2. **`ImplementationGuard`** is your registry - you control which implementations you trust
3. **`GuardedProxyClient`** is your contract which uses the external `SimpleProxy`, and is at risk of invisible malicious upgrades. It is "guarded" because it checks the `ImplementationGuard` registry before every interaction with the external proxy
4. If the external proxy is upgraded to an unapproved implementation, your client reverts instead of interacting with potentially malicious code

## Key Insight

This protects the **caller** (you) from external protocols, not the external protocol from attackers. External protocols must still protect their own upgrade mechanisms with timelocks, multisigs, or by renouncing upgradeability. The `ImplementationGuard` gives you defense-in-depth: even if an external protocol's upgrade controls fail, you won't interact with unapproved code.

## Version Differences

**V1 Behavior:** `setValue(x)` sets value to `x`  
**V2 Behavior:** `setValue(x)` sets value to `x + 1`

This simple difference makes it easy to verify which implementation is active. Inspect the scripts to expand your understanding.