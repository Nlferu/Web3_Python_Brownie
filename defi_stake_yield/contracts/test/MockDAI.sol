// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockDAI is ERC20 {
    constructor() public ERC20("Mock DAI", "DAI"){
        _mint(msg.sender, 15000000000000000000001);
    }
}
