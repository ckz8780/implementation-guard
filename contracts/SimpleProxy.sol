// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

contract SimpleProxy is ERC1967Proxy {
    
    constructor(
        address implementation_,
        address initialOwner
    ) ERC1967Proxy(
        implementation_,
        abi.encodeWithSignature(
            "initialize(address)",
            initialOwner
        )
    ) {}
    
    function implementation() public view returns (address) {
        return _implementation();
    }

    receive() external payable {} 
}