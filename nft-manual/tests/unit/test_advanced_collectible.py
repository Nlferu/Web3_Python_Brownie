from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
from scripts.advanced_collectible.adv_deploy_and_create import adv_deploy_and_create
import pytest


def test_can_create_advanced_collectible():
    # Deploy The Contract
    # Create An NFT
    # Get A Random Breed Back
    
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Act
    advanced_collectible, creation_transaction = adv_deploy_and_create()
    print(f'Primal tokenCounter: {advanced_collectible.tokenCounter()}')
    # ".events" will call "emit" function from our "AdvancedCollectible" contract, in first [] we pick emit function then in second [] we pick parameter we want to get
    requestId = creation_transaction.events["requestedCollectible"]["requestId"]
    # "callBackWithRandmoness" has constructor of (bytes32 requestId, uint256 randomness, address consumerContract) -> we are picking 2nd parameter by ourselves, so it can be any
    RANDOM_NUMBER = 777
    get_contract("vrf_coordinator").callBackWithRandomness(requestId, RANDOM_NUMBER, advanced_collectible.address, {"from": get_account()})
    print(f'First tokenCounter: {advanced_collectible.tokenCounter()}')
    """
    We would use below right away but it would return us primal version of "tokenCounter", which equals to "0", so we have to call version updated by "fulfillRandomness" function
    
    assert advanced_collectible.tokenCounter() > 0

    As showed above we have to:
    1. Call "requestId" from "emit" function from "AdvancedCollectible" contract.
    2. Call  "callBackWithRandomness" function from VRFCoordinatorMock contract and fill it with above.
    3. It can now callBack our "advanced_collectible.address" and update it with requestId and random_number, so our "advanced_collectible.tokenCounter()" will now return 1.
    """
    # Assert
    assert advanced_collectible.tokenCounter() > 0
    print(f'tokenIdToBreed: {advanced_collectible.tokenIdToBreed(0)}')
    assert advanced_collectible.tokenIdToBreed(0) == RANDOM_NUMBER % 3
    
    # Every time we call below, our "tokenCounter" will increase it's value by 1
    get_contract("vrf_coordinator").callBackWithRandomness(requestId, RANDOM_NUMBER, advanced_collectible.address, {"from": get_account()})
    print(f'Scond tokenCounter: {advanced_collectible.tokenCounter()}')
