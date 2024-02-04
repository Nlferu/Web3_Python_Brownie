//SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
// 20. Import VRF
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

// 18. Assigning ownership for the contract by importing openzeppelin contract (mind the dependencies and remappings)
// 21. Inherit VRFConsumerBase contract
contract LotteryV2 is VRFConsumerBase, Ownable {
    // 2. Create an array of participants (payable, because they will need to transact with our contract)
    address payable[] public players;
    // 30. recentWinner is being paid, so it has to be payable variable.
    address payable public recentWinner;
    // 23. Adding a fee and keyhash variable and passing this variable as parameterized in the constructor (fees can change from blockchain to blockchain)
    uint256 public fee;
    bytes32 public keyhash;

    // 6. We want to store entrance fee in smth, let's create a variable (constructor)
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    // 14. enum as an array of possible lottery states (list options)
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    event RequestedRandomness(bytes32 requestID);

    // 22. Adding variables from VRF's constructor and passing these to imported contract (at point 20.)
    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        // 7. Basic math + V3 priceFeed aggregator - create a dependencies and a solc compiler in the config brownie-config.yaml
        // 8. Check if it compiles, cmd: brownie compile
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        usdEntryFee = 50 * (10**18);
        // 15. When we initialize a lottry, its state has to be closed
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    // 1. In order to participate in a lottery, a participant will need to contribute with $
    function enter() public payable {
        // 4. We want to set a minimum value of a transaction to participate in a lottery - need to work on entranceFee function
        uint256 minimumValue = 50 * 10**18;
        // 16. We can only enter a lottery, when it's open
        require(lottery_state == LOTTERY_STATE.OPEN);
        // 13. After successful testing: brownie test --network mainnet-fork, adding a requirement for transacting.
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        // 3. Anytime someone will want to participate
        players.push(msg.sender);
    }

    // 5. We want to return a value of entrance fee, hence it's uint256
    function getEntranceFee() public view returns (uint256) {
        // 9. Take this from AggregatorV3 latestRoundData
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        // 10. adjustedPrice has to be expressed with 18 decimals. From Chainlink pricefeed, we know ETH/USD has 8 decimals, so we need to multiply by 10^10
        uint256 adjustedPrice = uint256(price) * 10**10;
        // 11. We cannot return decimals, hence we need to express 50$ with 50 * 10*18 / 2000 (adjusted price of ETH)
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        // !!! DON'T FORGET abt SAFEMATH !!!
        // 12. Testing - check Readme file. Create a test_lottery.py file! Setup mainnet-fork, check ON for guidance.
        return costToEnter;
    }

    function startLottery() public {
        // 17. Same as 16.
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public {
        // // 19. Applying randomness:
        // //  1. Casting everything into uint256, to indicate an index of a winner within an array.
        // //  2. Using hashing algorythm keccak256 that hashes bunch of variables together. But it will always be the same.
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce, // nonce is predictable (a.k.a. transaction number)
        //             msg.sender, // msg.sender is predictable
        //             block.difficulty, // can be manipulated by the miners!
        //             block.timestamp // timestamp is predictable
        //         )
        //     )
        // ) % players.lenght;
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // 24. Passing 2 calculated parameters to the function requesting random number - returns request ID
        bytes32 requestID = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestID);
    }

    // 25. Calling this function to fulfill randomness.
    // We want this to be called solely by the chainlink node by VRF Coordinator function hence it has to be an internal fuction.
    // Override means that we are overriding the original declaration of function
    function fulfillRandomness(bytes32 requestID, uint256 randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet!"
        );
        require(_randomness > 0, "random-not-found");
        // 26. Index in the array of the winner will be a modulo of random number and players array lenght
        uint256 indexOfWinner = _randomness % players.length;
        // 27. Pick the winner
        recentWinner = players[indexOfWinner];
        // 28. Pay the winner
        recentWinner.transfer(address(this).balance);
        // 29. Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }
    // modifier onlyOwner() {
    //     require(msg.sender == s_owner);
    //     _;
    // }
}
