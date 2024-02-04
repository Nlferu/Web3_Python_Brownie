
from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for rinkeby test net")
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(180)
    assert lottery.recentWinner() == account
    # Lottery balance is now X as we funded it with "fund_with_link" function, so after picking winner our lottery is transfering him all funds, so that's
    # why we should have 0 after ending lottery on lottery address
    assert lottery.balance() == 0
