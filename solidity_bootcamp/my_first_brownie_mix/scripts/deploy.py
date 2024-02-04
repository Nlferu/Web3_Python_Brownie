from brownie import MyFirstContract, ERC20Basic, config, accounts


def deployContract():
    account = accounts.add(config["wallets"]["from_key"])
    MyFirstContract.deploy({'from': account})


def deployERC20():
    account = accounts.add(config["wallets"]["from_key"])
    ERC20Basic.deploy(1000, {"from": account})

def main():
    deployContract()
    deployERC20()
