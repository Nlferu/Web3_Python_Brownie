from brownie import config, network, interface
from scripts.aave_borrow import get_lending_pool, get_account, get_borrowable_data, get_weth, approve_erc20
from web3 import Web3

amount = Web3.toWei(0.01, "ether")
max_amount = 2 ** 256 - 1


def main():
    account = get_account()
    lending_pool = get_lending_pool()
    
    """ Using Interface Works Only On Mainnet """  
    
    get_borrowable_data(lending_pool, account)
    withdraw_weth()
    get_borrowable_data(lending_pool, account)


# From WETH to ETH on AAVE
def withdraw_weth():
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    print("Withdrawing collateral...")
    tx = weth.withdraw(amount, {"from": account})
    tx.wait(1)
    print("Withdrew!")
    return tx
