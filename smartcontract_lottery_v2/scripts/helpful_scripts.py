
from brownie import network, config, accounts, MockV3Aggregator, VRFCoordinatorMock, LinkToken, Contract, interface

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

# To get Mocks go to: https://github.com/smartcontractkit/chainlink-mix/tree/main/contracts/test or
# https://github.com/smartcontractkit/chainlink/tree/develop/contracts/src/v0.6/tests for older mocks versions.

# We have to map contract type
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}


def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie config if defined, otherwise, it will deploy a mock version of that contract, and return that mock contract.

        Args:
            contract_name (string)
        
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract.
            for example -> MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    # Checking below if we are on a local blockchain
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # Checking if one of above contracts are even deployed (if MockV3Aggregator.length > 0 this mean mockV3 has been deployed)
        if len(contract_type) <= 0:
            deploy_mocks()
        # Getting recently deployed mock
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # We need "address" and "ABI" (We will get "ABI" from MockV3Aggregator)
        # We will be getting Contract from it's abi from package from brownie called "Contract"
        # MockV3Aggregator got attributes as "name" and "abi"
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract


def deploy_mocks(decimals = DECIMALS, initial_value = INITIAL_VALUE):
    print(f'The active network is {network.show_active()}')
    print("Deploying Mocks...")
    # This have "decimals" and "initial value" in constructor:
    MockV3Aggregator.deploy(decimals, initial_value, {"from": get_account()})
    # This doesn't have constructor so we can have it blank:
    link_token = LinkToken.deploy({"from": get_account()})
    # This have only LinkToken address in constructor:
    VRFCoordinatorMock.deploy(link_token.address, {"from": get_account()})
    print("Mocks Deployed!")


# This "contract_address" is to be funded, we are setting default "account" as None, but if you want you can pass specific one, same with "link_token"
# default amount of links set to 10 ** 17, which is 0.1 LINK
def fund_with_link(contract_address, account = None, link_token = None, link_amount = 10 ** 17):
    # We are saying below: "account" that we use is gonna be "account = None" if this "account != None" (exists), so someone have passed specific account,
    # otherwise (else) call "get_account()" function
    account = account if account else get_account()
    # We are doing the same thing with link_token
    """
    We can use LINK token contract, which is from "LinkToken.sol" mock we have taken as external package and placed in "smartcontract-lottery/contracts/test"
    or we can use interfaces from chainlink mix https://github.com/smartcontractkit/chainlink-mix/blob/main/interfaces/LinkTokenInterface.sol in order to
    install it to our project just copy code and add it to "smartcontract-lottery/interfaces" then import "interface" from brownie
    
    First add "dotenv: .env" in "brownie-config.yaml" so it can read "rinkeby" address on infura then:
    
    link_token = config["networks"]["rinkeby"]["link_token"]
    link_token_contract = interface.LinkTokenInterface(link_token)
    tx = link_token_contract.transfer(contract_address, link_amount, {"from": account}) -> using LinkTokenInterface.sol

    below we are using LinkToken.sol contract mock and not interface of LinkTokenInterface.sol
    """
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, link_amount, {"from": account}) # -> using LinkToken.sol mock contained in "get_contract()" function

    tx.wait(1)
    print("Contract Has Been Funded!")
    return tx
