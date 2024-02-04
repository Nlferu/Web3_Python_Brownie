from scripts.helpful_scripts import get_account
from brownie import config, network, interface


def main():
    get_weth()


# If we run this, our ETH will be taken and exchanged 1 to 1 into WETH token, which is needed to interact with aave application
def get_weth():
    """
    Mints WETH by depositing ETH

    First we want to interact with contract named "Wrapped Ether"

    To do this we will need:
    # ABI
    # Address
    """
    account = get_account()
    # address comes from config "weth_token" and ABI comes from interface "IWeth"
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    # We are calling deposit function from WETH contract
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print(f'Received 0.1 WETH')
    return tx
