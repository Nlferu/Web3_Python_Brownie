
from brownie import network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract
from web3 import Web3
import pytest

# 50$ / 1673.22$(ETH current price) = 0.029882
# In Wei -> 290000000000000000 (16 x 0)

"""
In order to run this test we need to provide all arguments that constructor in "Lottery.sol" has.
We can get all arguments from constructor as described below:
1. address _priceFeedAddress -> this is mock and we can get this from our "helpful_scripts" from "get_contract()" function.
2. address _vrfCoordinator -> this is mock and go to https://docs.chain.link/docs/vrf-contracts/ and find "Rinkeby" for example then -> "VRF Coordinator" and copy address then add
   it to our "brownie-config.yaml" networks list. To import mocks like "MockV3Aggregator" and "vrf_coordinator"
   go to: https://github.com/smartcontractkit/chainlink-mix/tree/main/contracts/test as we need those source codes to be pasted here in our project in:
   smartcontract-lottery/contracts/test.
   For older mocks versions go to: https://github.com/smartcontractkit/chainlink/tree/develop/contracts/src/v0.6/tests.
3. address _link -> this is another smart contract as vrfCoordinator and it is mock too, so same steps as for above, add it to "brownie-config.yaml" and import it's code into 
   smartcontract-lottery/contracts/test.
4. uint256 _fee -> this is number, we just gonna set default value for this in our "brownie-config.yaml", we can use fee from "rinkeby", so go to
   https://docs.chain.link/docs/vrf-contracts/ and grab "fee", then add it to "brownie-config.yaml" BUT USING WEI, so for 0.1 it will be 100000000000000000 (17 zeros) !!!
5. bytes32 _keyHash -> this is number, we just gonna set default value for this in our "brownie-config.yaml", we can use fee from "rinkeby", so go to
   https://docs.chain.link/docs/vrf-contracts/ and grab "Key Hash", then add it to "brownie-config.yaml" for "development" and "rinkeby" networks.
6. We also have to remember that VRFCoordinator and LinkToken are mocks and we have to add them to our "helpful_scripts.py" "deploy_mocks() function!
"""


def test_get_entrance_fee():
   # We want to run below only for local/development networks
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip("Only for local testing")
   # Arrange
   lottery = deploy_lottery()
   # Act
   # 2000 ETH/USD
   # usdEntryFee is 50$
   # 2000/1 == 50/x == 0.025
   expected_entrance_fee = Web3.toWei(0.025, "ether")
   entrance_fee = lottery.getEntranceFee()
   # Assert
   assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
   # Arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip("Only for local testing")
   # Act / Assert
   lottery = deploy_lottery()
   # Below says if it will throw error that means we could't enter lottery, which is good as we need lottery to be started first
   with pytest.raises(exceptions.VirtualMachineError):
      lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
   # Arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip("Only for local testing")
   lottery = deploy_lottery()
   lottery.startLottery({"from": get_account()})
   # Act
   lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
   # Assert
   # We are checking if we have successfully added player to this lottery, so we check if 1st player account is our account for development network
   assert lottery.players(0) == get_account()


def test_can_end_lottery():
   # Arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip("Only for local testing")
   lottery = deploy_lottery()
   lottery.startLottery({"from": get_account()})
   lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
   fund_with_link(lottery)
   # Act
   lottery.endLottery({"from": get_account()})
   # Assert
   # Lottery state stands as following OPEN = 0, CLOSED = 1, CALCULATING_WINNER = 2
   assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
   # Arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip("Only for local testing")
   lottery = deploy_lottery()
   account = get_account()
   lottery.startLottery({"from": account})
   # Creating 3 players
   lottery.enter({"from": account, "value": lottery.getEntranceFee()})
   lottery.enter({"from": get_account(index = 1), "value": lottery.getEntranceFee()})
   lottery.enter({"from": get_account(index = 2), "value": lottery.getEntranceFee()})
   fund_with_link(lottery)
   transaction = lottery.endLottery({"from": account})
   request_id = transaction.events["RequestedRandmoness"]["requestId"]
   # We are creating random number for testing purposes
   STATIC_RNG = 777
   # Dummying response from chain-link node for RandomNumber and this is how we mock responses in tests
   get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from": account})
   starting_balance_of_account = account.balance()
   balance_of_lottery = lottery.balance()
   # 777 % 3 = 0
   # Assert
   assert lottery.recentWinner() == account
   assert lottery.balance() == 0
   assert account.balance() == starting_balance_of_account + balance_of_lottery
