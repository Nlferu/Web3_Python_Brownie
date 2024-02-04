from brownie import ERC20Basic, config, accounts


def deployContract():
    account = accounts.add(config["wallets"]["from_key"])
    ERC20Basic.deploy(1000, {'from': account})


def view_supply():
    erc20 = ERC20Basic[-1]
    print("Total Supply is", erc20.totalSupply())


def main():
    deployContract()
    view_supply()
