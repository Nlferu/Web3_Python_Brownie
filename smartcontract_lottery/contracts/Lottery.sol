// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";
import "@openzeppelin/contracts/access/Ownable.sol"; // Adds OnlyOwner modifier that allows only admin to run functions with this mod
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {

    address payable[] public players;
    address payable public recentWinner;
    uint256 public randomness;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    
    // Enums -> user-defined type in Solidity
    // Below means that we have new type with 3 states, those states are going to be represented by numbers accordingly OPEN = 0, CLOSED = 1, CALCULATING_WINNER = 2
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;

    uint256 public fee;
    bytes32 public keyHash;

    event RequestedRandmoness(bytes32 requestId);

    // Adding additional external constructor from VRFConsumerBase
    // Below "_vrfCoordinator" and "_link" are from below VRFConsumerBase link to documentation
    // https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.6/VRFConsumerBase.sol
    // We will also need "keyHash" and "fee" -> look above
    constructor(address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyHash) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10 ** 18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        // lottery_state = 1; 
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    using SafeMathChainlink for uint256;

    function enter() public payable {
        // 50$ minimum
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), "Not Enough ETH!!!");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10 ** 10; // 18 decimals 10 + 8 from ETH/USD
        // 50$, price feed -> 2000$ / ETH
        // 50/2000 -> this doesnt work in Solidity as Solidity doesnt work with decimals
        // 50 * 100000 / 2000
        uint256 constToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
        return constToEnter;
    }

    function startLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can't Start A New Lottery Yet!");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // Below will return bytes32 called "requestId" from VRFConsumerBase documentation
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandmoness(requestId);
    }

    // We are picking our winner here by getting our random number via VRF V2
    // We are also overriding function from VRFConsumerBase
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "You Aren't There Yet!");
        require(_randomness > 0, "Random Not Found");
        uint256 indexOfWinner = _randomness % players.length;

        // Example:
        // We have 7 players signed up
        // Our random number "_randomness" = X
        // We want to get one of these random 7 players
        // So we do: X % 7 = -> this gives us posibilities of getting indexOfWinner = {0, 1, 2, 3, 4, 5, 6} total 7 posibilities each for 1 player

        recentWinner = players[indexOfWinner];
        // Transfering winner all money from this address as w reward
        recentWinner.transfer(address(this).balance);
        // Reset Lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
