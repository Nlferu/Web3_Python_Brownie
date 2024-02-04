
from brownie import network, config, accounts, Contract

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev", "mainnet-fork-lottery"]

DECIMALS = 8
INITIAL_VALUE = 200000000000


def get_account(index = None, id = None):
    # If index was passed we do below
    if index:
        return accounts[index]
    # If id was passed we do below
    if id:
        return accounts.load(id)
    # Shows networks in "development" tab or named "ganache-local"
    if(network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    # Below will be our default, so if above won't be picked we will get below
    return accounts.add(config["wallets"]["from_key"])
