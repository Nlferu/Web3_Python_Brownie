from brownie import network, config, accounts, MockV3Aggregator, Contract
from scripts.helpful_scripts import get_account

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

DECIMALS = 8
INITIAL_VALUE = 200000000000

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator
}


def main():
    printer()


def printer():
    # i = get_contract_local("eth_usd_price_feed")
    j = get_contract("eth_usd_price_feed")
    print(j)


# def get_contract_local(contract_name):
#     contract_type = contract_to_mock[contract_name]
#     # Checking below if we are on a local blockchain
#     if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         # Checking if one of above contracts are even deployed (if MockV3Aggregator.length > 0 this mean mockV3 has been deployed and its deploy counter is bigger than 0)
#         if len(contract_type) <= 0:
#             deploy_mocks()
#         # Getting recently deployed mock contract address
#         contract = contract_type[-1]
#     return contract


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    contract_address = config["networks"][network.show_active()][contract_name]
    # We need "address" and "ABI" (We will get "ABI" from MockV3Aggregator)
    # We will be getting Contract from it's ABI from package from brownie called "Contract"
    # MockV3Aggregator got attributes as "name" and "abi"
    contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    # return contract_type.__dir__()
    return contract.__dir__()


def deploy_mocks(decimals = DECIMALS, initial_value = INITIAL_VALUE):
    print(f'The active network is {network.show_active()}')
    print("Deploying Mocks...")
    # This have "decimals" and "initial value" in constructor:
    MockV3Aggregator.deploy(decimals, initial_value, {"from": get_account()})
    print("Mocks Deployed!")
