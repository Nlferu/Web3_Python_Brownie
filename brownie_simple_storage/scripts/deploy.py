
from brownie import accounts, config, SimpleStorage, network
import os

def deploy_simple_storage():
    account = get_account()
    # Deploying Contract:
    simple_storage = SimpleStorage.deploy({"from": account})
    # Working with store function:
    stored_value = simple_storage.retrieve()
    print(stored_value)
    # Updating value in store function:
    transaction = simple_storage.store(77, {"from": account})
    # Wait for 1 block:
    transaction.wait(1)
    output = transaction.return_value
    print(f'Output: {output}')
    updated_stored_value = simple_storage.retrieve()
    print(updated_stored_value)

def get_account():
    if(network.show_active() == "development"):
        return accounts[0]
    else:
        # Adds account saved in our config.yaml based on it's private key as it is giving you account number
        return accounts.add(config["wallets"]["from_key"])

def main():
    deploy_simple_storage()
