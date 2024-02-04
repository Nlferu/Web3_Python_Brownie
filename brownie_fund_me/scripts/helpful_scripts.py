
from brownie import network, config, accounts, MockV3Aggregator
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]

DECIMALS = 8
STARTING_PRICE = 200000000000
# Old starting_price = 2000, which means 2000 usd per eth probably

def get_account():
    # Shows networks in "development" tab or named "ganache-local"
    if(network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    else:
        # Adds account saved in our config.yaml based on it's private key as it is giving you account number
        return accounts.add(config["wallets"]["from_key"])

def deploy_mocks():
    print(f'The active network is {network.show_active()}')
    print("Deploying Mocks...")
    # If Mock was not called yet then deploy it
    if len(MockV3Aggregator) <= 0:
        # MockV3Aggregator.deploy(DECIMALS, Web3.toWei(starting_price, "ether"), {"from": get_account()})
        MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": get_account()})
    print("Mocks Deployed!")
