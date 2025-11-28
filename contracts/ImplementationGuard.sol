// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ImplementationGuard
 * @notice A registry for tracking approved implementation addresses of external protocols
 * @dev This contract helps protect against malicious upgrades in external dependencies.
 *      It maintains a registry of approved implementations that YOU control.
 *      Before interacting with an upgradeable external contract, verify its current 
 *      implementation is in your approved list.
 * 
 * SECURITY MODEL:
 * - This registry is controlled by YOUR keys (owner), not the external protocol's keys
 * - Non-upgradeable to ensure it remains a trusted source of truth
 * - Reusable across multiple protocols you depend on
 * 
 * CRITICAL: This protects the CALLER (you) from external protocols, not the external
 * protocol from attackers. External protocols must protect their own upgrade mechanism
 * with timelocks, multisig, or by renouncing upgradeability.
 */
contract ImplementationGuard is Ownable {
    
    // Mapping: proxy address => implementation address => approved status
    mapping(address => mapping(address => bool)) private approvedImplementations;
    
    // Events
    event ImplementationApproved(address indexed proxyAddress, address indexed implementation);
    event ImplementationRevoked(address indexed proxyAddress, address indexed implementation);
    
    constructor(address initialOwner) Ownable(initialOwner) {}
    
    /**
     * @notice Approve an implementation address for a specific proxy
     * @dev Only the owner can approve implementations
     * @param proxyAddress The address of the proxy contract
     * @param implementation The implementation address to approve
     */
    function approveImplementation(address proxyAddress, address implementation) external onlyOwner {
        require(proxyAddress != address(0), "Invalid proxy address");
        require(implementation != address(0), "Invalid implementation address");
        require(!approvedImplementations[proxyAddress][implementation], "Already approved");
        
        approvedImplementations[proxyAddress][implementation] = true;
        
        emit ImplementationApproved(proxyAddress, implementation);
    }
    
    /**
     * @notice Revoke approval for an implementation address
     * @dev Only the owner can revoke implementations
     * @param proxyAddress The address of the proxy contract
     * @param implementation The implementation address to revoke
     */
    function revokeImplementation(address proxyAddress, address implementation) external onlyOwner {
        require(approvedImplementations[proxyAddress][implementation], "Not approved");
        
        approvedImplementations[proxyAddress][implementation] = false;
        
        emit ImplementationRevoked(proxyAddress, implementation);
    }
    
    /**
     * @notice Check if an implementation is approved for a proxy
     * @param proxyAddress The address of the proxy contract
     * @param implementation The implementation address to check
     * @return bool True if the implementation is approved
     */
    function isApproved(address proxyAddress, address implementation) external view returns (bool) {
        return approvedImplementations[proxyAddress][implementation];
    }
}