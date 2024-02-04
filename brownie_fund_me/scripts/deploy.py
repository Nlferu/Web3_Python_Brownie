
from brownie import FundMe, MockV3Aggregator, network, config
from scripts.helpful_scripts import get_account, deploy_mocks, LOCAL_BLOCKCHAIN_ENVIRONMENTS


def deploy_fund_me():
    account = get_account()
    # Live Chain, which saves deployed contracts on left in VScode in "build" -> "deployments"
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
    else:
        # If network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS then call below:
        # Development Chain
        deploy_mocks()
        # [-1] Means to use most recently deployed MockV3Aggregator, which provides fake prices of USD/ETH
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(price_feed_address, {"from": account}, publish_source = config["networks"][network.show_active()].get("verify"))
    print(f'Contract deployed to {fund_me.address}')
    # print(fund_me) -> it is same as above it's address
    return fund_me


def main():
    deploy_fund_me()
