// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract SimpleLogicV2 is Initializable, OwnableUpgradeable, UUPSUpgradeable {
    uint256 public value;
    
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
    
    function initialize(address initialOwner) public initializer {
        __Ownable_init(initialOwner);
        __UUPSUpgradeable_init();
        value = 42;
    }
    
    function setValue(uint256 newValue) public {
        value = newValue + 1;
    }
    
    function version() public pure returns (string memory) {
        return "v2";
    }
    
    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}