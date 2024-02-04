from brownie import network, Contract, config, Box, BoxV2, ProxyAdmin, TransparentUpgradeableProxy
from scripts.helpful_scripts import get_account, encode_function_data, upgrade


def main():
    account = get_account()
    print(f'Deploying to {network.show_active()}')
    box = Box.deploy({"from": account}, publish_source = config["networks"][network.show_active()]["verify"])

    # Optional, deploy the ProxyAdmin and use that as the admin contract
    proxy_admin = ProxyAdmin.deploy({"from": account})
    
    # If we want an intializer function we can add
    # `initializer = box.store, 1`
    # to simulate the initializer being the `store` function
    # with a `newValue` of 1
    box_encoded_initializer_function = encode_function_data()
    # "box.store" is the function to call and "1" is first parameter
    # initializer = box.store, 1
    # box_encoded_initializer_function = encode_function_data(initializer=box.store, 1)

    proxy = TransparentUpgradeableProxy.deploy(box.address, proxy_admin.address, box_encoded_initializer_function, {"from": account, "gas_limit": 1000000})
    print(f'Proxy deployed to {proxy}, you can now upgrade to v2!')
    # Assigning Box ABI to a proxy address   
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    print(f"Here is the initial value in the Box: {proxy_box.retrieve()}")
    tx = proxy_box.store(1, {"from": account})
    tx.wait(1)
    
    # Upgrading from Box to BoxV2
    box_v2 = BoxV2.deploy({"from": account}, publish_source = config["networks"][network.show_active()]["verify"])
    # We do not have "initializer"
    upgrade_transaction = upgrade(account, proxy, box_v2.address, proxy_admin_contract = proxy_admin)
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    tx_inc = proxy_box.increment({"from": account})
    tx_inc.wait(1)
    print(f'TransparentUpgradeableProxy address is: {proxy_box}, Our BoxV2 new value is: {proxy_box.retrieve()}')
