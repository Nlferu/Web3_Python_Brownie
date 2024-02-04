from brownie import network, AdvancedCollectible
from scripts.helpful_scripts import OPENSEA_URL, get_breed, get_account

dogs_metadata_dictionary = {
    "PUG": "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json",
    "SHIBA_INU": "https://ipfs.io/ipfs/QmdryoExpgEQQQgJPoruwGJyZmz6SqV4FRTX1i73CT3iXn?filename=1-SHIBA_INU.json",
    "ST_BERNARD": "https://ipfs.io/ipfs/QmPrfxtkzcEQza8L8kksAZUsdneb4esAzEr2sWiBkYpdMt?filename=2-ST_BERNARD.json"
}


def main():
    print(f'Working on {network.show_active()}')
    advanced_collectible = AdvancedCollectible[-1]
    number_of_collectibles = advanced_collectible.tokenCounter()
    print(f"You have {number_of_collectibles} tokenId's")
    for token_id in range(number_of_collectibles):
        breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
        # If our tokenURI doesn't start with "https://" that mean we know it hasn't been set ("startswith" function is boolean)
        if not advanced_collectible.tokenURI(token_id).startswith("https://"):
            print(f"Setting tokenURI of {token_id}")
            set_tokenURI(token_id, advanced_collectible, dogs_metadata_dictionary[breed])


# Function below is going to call "_setTokenURI" function from ERC721 contract
def set_tokenURI(token_id, nft_contract, tokenURI):
    account = get_account()
    # setTokenURI is function from AdvancedCollectible.sol contract
    tx = nft_contract.setTokenURI(token_id, tokenURI, {"from": account})
    tx.wait(1)
    print(f'You can view your NFT at {OPENSEA_URL.format(nft_contract.address, token_id)}')
    print("Please wait up to 20min's and hit the refresh metadata button!")
