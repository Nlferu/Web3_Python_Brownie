from brownie import AdvancedCollectible, config, network
from scripts.helpful_scripts import get_account, get_contract, fund_with_link, OPENSEA_URL


def main():
    adv_deploy_and_create()


def adv_deploy_and_create():
    account = get_account()
    advanced_collectible = AdvancedCollectible.deploy(
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["keyHash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
        # This could be "publish_source = True", we are reading "verify" from active network and giving it's value, so in our case True for Rinkeby and Goerli
        publish_source = config["networks"][network.show_active()].get("verify", False)
    )
    fund_with_link(advanced_collectible.address)
    creating_tx = advanced_collectible.createCollectible({"from": account})
    creating_tx.wait(1)
    print("New Token Has Been Created!")
    return advanced_collectible, creating_tx
