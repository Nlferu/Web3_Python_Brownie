
from brownie import SimpleStorage, accounts
from eth_account import Account

def test_deploy():
    # Arrange (Setup)
    account = accounts[0]

    # Act
    simple_storage = SimpleStorage.deploy({"from": account})
    starting_value = simple_storage.retrieve()
    expected = 0

    # Assert
    assert starting_value == expected

# Testing updated store function
def test_updating_storage():
    # Arrange
    account = accounts[0]
    simple_storage = SimpleStorage.deploy({"from": account})
    
    # Act
    expected = 77
    simple_storage.store(expected, {"from": account})
    
    # Assert
    assert simple_storage.retrieve() == expected
