from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_breed
from scripts.advanced_collectible.adv_deploy_and_create import adv_deploy_and_create
from scripts.advanced_collectible.set_token_uri import dogs_metadata_dictionary, set_tokenURI
import pytest, time

# TODO ------------------------------------------------------------------------
# def test_can_set_token_uri(): 
#     # Arrange
#     if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         pytest.skip("Only for integration testing")    
#     breed = get_breed(0)
#     token_id = 0
#     tokenURI = dogs_metadata_dictionary[breed]
#     # Act
#     advanced_collectible, creation_transaction = adv_deploy_and_create()
#     time.sleep(180)
#     our_token = set_tokenURI(token_id, advanced_collectible, tokenURI)
#     check_token = isinstance(our_token, str)
#     print(f'Our TOKEN is: {our_token}')
#     assert str(check_token) == True
