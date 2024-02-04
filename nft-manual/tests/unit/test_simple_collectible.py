from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from scripts.simple_collectible.deploy_and_create import deploy_and_create
import pytest


def test_can_create_simple_collectible():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Act
    simple_collectible = deploy_and_create()
    #Assert
    # Below ".ownerOf()" is a function from ERC-721
    assert simple_collectible.ownerOf(0) == get_account()
