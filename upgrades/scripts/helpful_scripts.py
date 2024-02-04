from brownie import network, config, accounts
import eth_utils

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev", "mainnet-fork-lottery"]


def get_account(number=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if number:
        return accounts[number]
    if network.show_active() in config["networks"]:
        account = accounts.add(config["wallets"]["from_key"])
        return account
    return None


# We are encoding following to bytes, so our smart contract know what function to call: initializer = box.store, 1 "*args" it will always match amount of args
def encode_function_data(initializer = None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    # "if len(args) == 0:" equals to "if not len(args):" 
    if len(args) == 0: # "or not initializer" this is useless as initializers don't need any args.
        args = b''
    """
    No need to call:
        eth_utils.to_bytes(hexstr="0x")
    because it just equals b''
    """
    #     return eth_utils.to_bytes(hexstr = "0x")
    """ encode_input
    It is a brownie function for ContractTx, it returns a hexstring of ABI calldata that can be used to call the method with the given arguments
    that is why we have to match "*args" for any function from base Contract that we call.
    """
    if initializer:
        return initializer.encode_input(*args)
    return b''


def upgrade(account, proxy, new_implementation_address, proxy_admin_contract = None, initializer = None, *args):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            # "upgradeAndCall" is function from ProxyAdmin
            transaction = proxy_admin_contract.upgradeAndCall(proxy.address, new_implementation_address, encode_function_call, {"from": account})
        else:
            # "upgrade" is function from ProxyAdmin
            transaction = proxy_admin_contract.upgrade(proxy.address, new_implementation_address, {"from": account})
    else:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            # "upgradeToAndCall" is function from TransparentUpgradeableProxy
            transaction = proxy.upgradeToAndCall(new_implementation_address, encode_function_call, {"from": account})
        else:
            # "upgradeTo" is function from TransparentUpgradeableProxy
            transaction = proxy.upgradeTo(new_implementation_address, {"from": account})
    return transaction
