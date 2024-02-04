//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV2V3Interface.sol";

contract LotteryV2 {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;

    enum LOTTERYV2_STATE {
        OPEN,
        CLOSED,
        PICKING_WINNER
    }

    LOTTERYV2_STATE public lotteryv2_state;

    constructor(address _priceFeedAddress) public {
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        usdEntryFee = 50 * (10 ** 18);
        lotteryv2_state = LOTTERYV2_STATE.CLOSED;
    }

    function pay_entrance_fee() public payable {
        require(msg.value >= getEntranceFee(), "Issufficient funds!");
        require(lotteryv2_state == LOTTERYV2_STATE.OPEN);
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10 ** 10;
        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
        return costToEnter;
    }

    function commence_lottery() public {
        require(lotteryv2_state == LOTTERYV2_STATE.CLOSED, "Can't start a new lottery yet!");
        lotteryv2_state = LOTTERYV2_STATE.OPEN;
    }

    function end_lottery() public {
        require(lotteryv2_state == LOTTERYV2_STATE.OPEN);
        lotteryv2_state = LOTTERYV2_STATE.PICKING_WINNER;
    }

    function pick_a_winner() public {
        require(lotteryv2_state == LOTTERYV2_STATE.PICKING_WINNER);
        //code to be executed here
        lotteryv2_state = LOTTERYV2_STATE.CLOSED;
    }
}
