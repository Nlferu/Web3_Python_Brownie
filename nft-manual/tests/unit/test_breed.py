from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_breed
import pytest


def test_get_breed():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")    
    # Act
    breed = get_breed(0)
    # Assert
    assert breed == "PUG"
