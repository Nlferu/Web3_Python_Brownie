from brownie import network, config, accounts, MockV3Aggregator, MockWETH, MockDAI, Contract, interface

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev", "mainnet-fork-lottery"]

DECIMALS = 18
# Below is equal to $2,000
INITIAL_PRICE_FEED_VALUE = 2000000000000000000000


def get_account(index = None, id = None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if(network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "weth_token": MockWETH,
    "fau_token": MockDAI
}


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


def deploy_mocks(decimals = DECIMALS, initial_value = INITIAL_PRICE_FEED_VALUE):
    account = get_account()
    print(f'The active network is {network.show_active()}')
    print("Deploying Mocks...")
    print("Deploying Mock Price Feed...")
    price_feed = MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    print(f'Mock PriceFeed deployed to {price_feed.address}')
    print("Deploying Mock WETH...")
    weth_token = MockWETH.deploy({"from": account})
    print(f'Mock WETH deployed to {weth_token.address}')
    print("Deploying Mock DAI...")
    dai_token = MockDAI.deploy({"from": account})
    print(f'Mock DAI deployed to {dai_token.address}')
    print("Mocks Deployed!")


def fund_with_link(contract_address, account = None, link_token = None, link_amount = 10 ** 17):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, link_amount, {"from": account})
    tx.wait(1)
    print("Contract Has Been Funded!")
    return tx
