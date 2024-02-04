
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    # In console: brownie accounts list -> pick one of added accounts
    # account = get_account(id = "ferum-account") or
    account = get_account()
    # We have performed network checking in FundMe.sol project using development networks or deploying mocks, we change it here a bit (read function info in "helpful_scripts")
    """
    If we will be on local test network below will deploy mock which provide us price feed, and if we will be on forked network it will provide price feed from
    given address saved in brownie-config.yaml

    .address -> it is optional to use, but it is always good to have it just to clarity what this will be and that if it will be contract as below we want only it's address
    """
    ### from given address in .yaml
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        # If we want to publish this use below. ".get("verify", False)" stands for: get that verify key, but if there is no verify key just default "False", previously we have
        # added "False" in our "brownie-config.yaml" in development network, but have to add "True" in "rinkeby" network, so we can verify it on rinkeby chain.
        publish_source = config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed Lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_transaction = lottery.startLottery({"from": account})
    starting_transaction.wait(1)
    print("The Lottery Has Started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # Just to make sure fee will be covered, add some Wei to it: 100000000
    entry_fee = lottery.getEntranceFee() + 10 ** 8
    starting_tx = lottery.enter({"from": account, "value": entry_fee})
    starting_tx.wait(1)
    print("You Have Successfully Entered The Lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    """
    As "endLottery()" function calls "requestRandomness(keyHash, fee)", we will first need to fund our contract with some "LINK" tokens, then we can end lottery
    Funding contract with LINK Tokens will be common function that we use, so we will code it in "helpful_scripts.py"
    
    We just need address to call "fund_with_link" as parameter for below function, because rest will be set as default as we coded that function this way -> 
    look "helpful_scripts.py -> fund_with_link()" function for more comments and clarification!
    """
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    # When we call "endLottery()" function we actually have to wait for called chainlink node to finish from "Lottery.sol" -> "fulfillRandomness()" function
    # Usually chainlink node callback is finished within few blocks, so typically it takes around 180 seconds to respond, we can use "sleep" function to wait
    # that long as showed below
    ending_transaction.wait(1)
    time.sleep(180) # Put seconds in ()
    print("Lottery Has Been Finished!")
    print(f'{lottery.recentWinner()} is the new winner!')


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
