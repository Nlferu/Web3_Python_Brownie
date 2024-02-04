from brownie import config, accounts, network, Contract, VRFCoordinatorMock, LinkToken
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local", "mainnet-fork-dev"]
# In order to see our image on OpenSea site
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"

BREED_MAPPING = {0: "PUG", 1: "SHIBA_INU", 2: "ST_BERNARD"}
INVERSE_BREED_MAPPING = {"PUG": 0, "SHIBA_INU": 1, "ST_BERNARD": 2}

contract_to_mock = {
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}


def get_breed(breed_number):
    return BREED_MAPPING[breed_number]


def get_account(index = None, id = None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract


def deploy_mocks():
    print(f'The active network is {network.show_active()}')
    print("Deploying Mocks...")
    print("Deploying Link Token Mock...")
    link_token = LinkToken.deploy({"from": get_account()})
    print(f'Link Token Mock deployed to {link_token.address}')
    print("Deploying VRF Coordinator Mock...")
    vrf_coordinator = VRFCoordinatorMock.deploy(link_token.address, {"from": get_account()})
    print(f'VRF Coordinator Mock deployed to {vrf_coordinator.address}')
    print("Mocks Deployed!")


def fund_with_link(contract_address, account = None, link_token = None, link_amount = Web3.toWei(0.3, "ether")):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(contract_address, link_amount, {"from": account})
    funding_tx.wait(1)
    print(f'Contract {contract_address} Has Been Funded!')
    return funding_tx
