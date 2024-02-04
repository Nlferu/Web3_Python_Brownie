from brownie import MockERC20, MockDAI
from scripts.helpful_scripts import get_account
import pytest
from web3 import Web3


@pytest.fixture
def amount_staked():
    return Web3.toWei(1, "ether")


@pytest.fixture
def random_erc20():
    account = get_account()
    erc20 = MockERC20.deploy({"from": account})
    return erc20


@pytest.fixture
def dai_token():
    account = get_account()
    erc20 = MockDAI.deploy({"from": account})
    return erc20
