from brownie import network, accounts, config, LotteryV2


def main():
    deploy()


def deploy():
    account = accounts.add(config["wallets"]["from_key"])
    lottery = LotteryV2.deploy(config["networks"][network.show_active()]["eth_usd_price_feed"], {"from": account})
    return lottery
