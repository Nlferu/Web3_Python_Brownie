from brownie import NiferuToken
from scripts.helpful_scripts import get_account
from web3 import Web3

initialSupply = Web3.toWei(1000, "ether")


def deploy_token():
    account = get_account()
    token = NiferuToken.deploy(initialSupply, {"from": account})
    print(token.name())
    return token


def main():
    deploy_token()
