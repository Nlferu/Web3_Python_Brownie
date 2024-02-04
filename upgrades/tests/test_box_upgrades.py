from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import Contract, exceptions, Box, BoxV2, ProxyAdmin, TransparentUpgradeableProxy
import pytest


def test_proxy_upgrades():
    # Arrange
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(box.address, proxy_admin.address, box_encoded_initializer_function, {"from": account, "gas_limit": 1000000})

    box_v2 = BoxV2.deploy({"from": account})
    
    # Act
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    # Calling "increment" function before using "upgrade" function should throw "VirtualMachineError" error, so if it does test pass first step
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})
    upgrade(account, proxy, box_v2.address, proxy_admin_contract = proxy_admin)
    # Assert
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1
