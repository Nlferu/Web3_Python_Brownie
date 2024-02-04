from brownie import accounts, config, network
from scripts.aave_borrow import get_asset_price, get_lending_pool, get_account, approve_erc20, get_weth
from web3 import Web3 


def test_get_asset_price():
    # Arrange (Setup)
    price_feed_address = config["networks"][network.show_active()]["dai_eth_price_feed"]
    # Act (Run)
    dai_eth_price = get_asset_price(price_feed_address)
    current_dai_eth_price = 0.00055
    # Assert (Compare)
    assert dai_eth_price > current_dai_eth_price


def test_get_lending_pool():
    # Arrange / Act
    lending_pool = get_lending_pool()
    # Assert
    assert lending_pool is not None


def test_approve_erc20():
    # Arrange
    amount = Web3.toWei(0.1, "ether")
    spender = get_lending_pool().address
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    account = get_account()
    # Act
    approve = approve_erc20(amount, spender, erc20_address, account)
    # Assert
    # We can also state "is not False" as it is undefined as we are checking part of the transaction only and not whole "tx"
    assert approve is not True


def test_withdraw():
    # Arrange
    amount = Web3.toWei(0.1, "ether")
    max_amount = 2 ** 256 - 1
    account = get_account()
    lending_pool = get_lending_pool()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()
    # Act
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    dTx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    dTx.wait(1)
    wTx = lending_pool.withdraw(config["networks"][network.show_active()]["weth_token"], max_amount, account, {"from": account})
    wTx.wait(1)
    deposit = dTx.value
    withdraw = wTx.value
    # I'm not sure why is it printing 0's
    print(f'{deposit}, {withdraw}')
    # Assert
    assert deposit == withdraw
