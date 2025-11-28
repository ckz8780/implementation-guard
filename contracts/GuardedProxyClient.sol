// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

import "./ImplementationGuard.sol";

interface ISimpleProxy {
    function implementation() external view returns (address);
}

interface ISimpleLogic {
    function setValue(uint256 newValue) external;
    function value() external view returns (uint256);
}

/**
 * @title GuardedProxyClient
 * @notice A contract that safely interacts with an external upgradeable proxy
 * @dev Before calling the external proxy, this contract verifies that its current
 *      implementation is approved in the ImplementationGuard registry.
 */
contract GuardedProxyClient {
    
    ImplementationGuard public immutable guard;
    ISimpleProxy public immutable externalProxy;
    
    event ValueSet(uint256 newValue);
    
    constructor(address guardAddress, address proxyAddress) {
        guard = ImplementationGuard(guardAddress);
        externalProxy = ISimpleProxy(proxyAddress);
    }
    
    /**
     * @notice Verify that the external proxy's current implementation is approved
     * @dev Reverts if the implementation is not approved
     */
    modifier onlyApprovedImplementation() {
        address implementation = externalProxy.implementation();
        require(
            guard.isApproved(address(externalProxy), implementation),
            "Implementation not approved"
        );
        _;
    }
    
    /**
     * @notice Safely call setValue on the external proxy (only if implementation is approved)
     * @param newValue The value to set
     */
    function safeSetValue(uint256 newValue) external onlyApprovedImplementation {
        ISimpleLogic(address(externalProxy)).setValue(newValue);
        emit ValueSet(newValue);
    }
    
    /**
     * @notice Get the current value from the external proxy (only if implementation is approved)
     * @return currentValue The current value
     */
    function safeGetValue() external view onlyApprovedImplementation returns (uint256 currentValue) {
        return ISimpleLogic(address(externalProxy)).value();
    }
}