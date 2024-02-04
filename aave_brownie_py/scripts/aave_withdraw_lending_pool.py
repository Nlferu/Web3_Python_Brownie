from brownie import config, network
from scripts.aave_borrow import get_lending_pool, get_account, get_borrowable_data, get_weth, approve_erc20
from web3 import Web3

amount = Web3.toWei(0.1, "ether")
# uint(-1) in solidity is the same as (2 ** 256) - 1 in python.
max_amount = 2 ** 256 - 1


def main():
    account = get_account()
    lending_pool = get_lending_pool()
    
    """ Uncomment lines below, to use on local testnet """
    # erc20_address = config["networks"][network.show_active()]["weth_token"]
    # if network.show_active() in ["mainnet-fork-dev"]:
    #     get_weth()
    # approve_erc20(amount, lending_pool.address, erc20_address, account)
    # print("Depositing Collateral...")
    # tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    # tx.wait(1)
    # print("Collateral Deposited!")
    
    get_borrowable_data(lending_pool, account)
    withdraw_all_collateral(lending_pool, account)
    print("You just withdrew all collateral")
    get_borrowable_data(lending_pool, account)


# From ETH(Supplied) to WETH on AAVE
def withdraw_all_collateral(lending_pool, account):
    print("Withdrawing collateral...")
    tx = lending_pool.withdraw(config["networks"][network.show_active()]["weth_token"], max_amount, account, {"from": account})
    tx.wait(1)
    print("Withdrew!")
    return tx
