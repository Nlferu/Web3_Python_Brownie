from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.advanced_collectible.adv_deploy_and_create import adv_deploy_and_create
import pytest
import time


def test_can_create_advanced_collectible_integration():    
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration testing")
    # Act
    advanced_collectible, creation_transaction = adv_deploy_and_create()
    time.sleep(180)
    # Assert
    assert advanced_collectible.tokenCounter() > 0
