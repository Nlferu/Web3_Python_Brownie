// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    // mapping token address -> staker address -> amount
    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    mapping(address => address) public tokenPriceFeedMapping;
    
    address[] public allowedTokens;
    address[] public stakers;

    IERC20 public dappToken;
    
    constructor(address _dappTokenAddress) public {
        dappToken = IERC20(_dappTokenAddress);
    }

    function setPriceFeedContract(address _token, address _priceFeed) public onlyOwner {
        tokenPriceFeedMapping[_token] = _priceFeed;
    }

    function issueTokens() public onlyOwner {
        // Issue tokens to all stakers
        for(uint256 stakersIndex = 0; stakersIndex < stakers.length; stakersIndex++){
            address recipient = stakers[stakersIndex];
            uint256 userTotalValue = getUserTotalValue(recipient);
            // Giving only 10% of staked tokens
            uint256 userTotalVal = userTotalValue / 10;
            // Now we have to send and calculate amount of token reward based on value user locked
            dappToken.transfer(recipient, userTotalVal);
        }
    }

    function getUserTotalValue(address _user) public view returns(uint256) {
        uint256 totalValue = 0;
        require(uniqueTokensStaked[_user] > 0, "No Tokens Staked!");
        for(uint256 allowedTokensIndex = 0; allowedTokensIndex < allowedTokens.length; allowedTokensIndex++){
            totalValue += getUserSingleTokenValue(_user, allowedTokens[allowedTokensIndex]);
        }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token) public view returns(uint256) {
        // 1 ETH -> 2000$ => 2000 | 200 DAI -> 200$ => 200
        if(uniqueTokensStaked[_user] <= 0){
            return 0;
        }
        // Price of the token * stakingBalance[_token][_user]
        (uint256 price, uint256 decimals) = getTokenValue(_token);
        return (stakingBalance[_token][_user] * price / (10 ** decimals));
    }

    function getTokenValue(address _token) public view returns(uint256, uint256) {
        // PriceFeedAddress
        address priceFeedAddress = tokenPriceFeedMapping[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (, int256 price, , ,) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals);
    }

    // We can stake some amount of some token
    function stakeTokens(uint256 _amount, address _token) public {
        require(_amount > 0, "Amount must be greater than 0!");
        require(tokenIsAllowed(_token), "Token is currently not allowed!");
        /*
            We are taking transfer functions from ERC20 contract:
            1. transfer -> this can be called only by wallet, which is owner of particular token
            2. transferFrom -> this can be called by whatever wallet but needs approve first
        */
        // Getting ABI (via import at top) from IERC20 interface
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        // Function figuring out how many different tokens does user has
        updateUniqueTokensStaked(msg.sender, _token);
        stakingBalance[_token][msg.sender] += _amount;
        if(uniqueTokensStaked[msg.sender] == 1){
            stakers.push(msg.sender);
        }
    }

    function unStakeTokens(address _token) public {
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "There is nothing to UnStake!");
        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] -= 1;
        // The code below fixes a problem, where stakers could appear twice in the stakers array, receiving twice the reward.
        if (uniqueTokensStaked[msg.sender] == 0) {
            for (uint256 stakersIndex = 0; stakersIndex < stakers.length; stakersIndex++) {
                if (stakers[stakersIndex] == msg.sender) {
                    stakers[stakersIndex] = stakers[stakers.length - 1];
                    // Below deletes last item in array
                    stakers.pop();
                }
            }
        }
    }

    // Internal = only this contract can call function below
    // Function below will let us know how many different tokens user has
    function updateUniqueTokensStaked(address _user, address _token) internal {
        if (stakingBalance[_token][_user] <= 0){
            uniqueTokensStaked[_user] += 1;
        }
    }

    function addAllowedTokens(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    function tokenIsAllowed(address _token) public view returns (bool){
        for (uint256 allowedTokensIndex = 0; allowedTokensIndex < allowedTokens.length; allowedTokensIndex++){
            if(allowedTokens[allowedTokensIndex] == _token){
                return true;
            }
        }
        return false;
    }

    function arrayLengthGetter() public view returns (uint, uint) {
        uint first_array = stakers.length;
        uint second_array = allowedTokens.length;
        return (first_array, second_array);
    }
}
