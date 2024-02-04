from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_breed
from scripts.advanced_collectible.create_metadata import upload_to_ipfs
import pytest

# To run below we have to be running our own node -> "IPFS DAEMON" 
def test_can_ipfs_upload():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    breed = get_breed(0)
    image_path = "./img/" + breed.lower().replace("_", "-") + ".png"
    # Act
    img_uri = upload_to_ipfs(image_path)
    # Assert
    assert img_uri == "https://ipfs.io/ipfs/QmSsYRx3LpDAb1GZQm7zZ1AuHZjfbPkD6J7s9r41xu1mf8?filename=pug.png"
