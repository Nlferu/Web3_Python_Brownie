from brownie import network, AdvancedCollectible
from scripts.helpful_scripts import INVERSE_BREED_MAPPING, get_breed
from metadata.sample_metadata import metadata_template
from pathlib import Path
import requests, json, os

# All URI's will be the same for everyone who upload it to IPFS
# so to avoid re-upload to IPFS we refactor .env and below, so our or someone else's IPFS node do not have to be running 24/7 to get .png and .json
breed_to_image_uri = {
    "PUG": "https://ipfs.io/ipfs/QmSsYRx3LpDAb1GZQm7zZ1AuHZjfbPkD6J7s9r41xu1mf8?filename=pug.png",
    "SHIBA_INU": "https://ipfs.io/ipfs/QmYx6GsYAKnNzZ9A6NvEKV9nf1VaDzJrqDR23Y8YSkebLU?filename=shiba-inu.png",
    "ST_BERNARD": "https://ipfs.io/ipfs/QmUPjADFGEKmfohdTaNcWhp7VGk26h5jXDA7v3VtTnTLcW?filename=st-bernard.png"
}


def main():
    advanced_collectible = AdvancedCollectible[-1]
    number_of_advanced_collectibles = advanced_collectible.tokenCounter()
    print(f'You Have Created {number_of_advanced_collectibles} Collectibles!')
    for token_id in range(number_of_advanced_collectibles):
        breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
        # dog_index = INVERSE_BREED_MAPPING[breed] -> it will always match breed with it's number and name, while swapped with below "token_id"
        metadata_file_name = (f'./metadata/{network.show_active()}/{token_id}-{breed}.json')
        print(f'File Name: {metadata_file_name}')
        collectible_metadata = metadata_template
        if Path(metadata_file_name).exists():
            print(f'{metadata_file_name} already exists! Delete it to overwrite')
        else:
            print(f'Creating Metadata File: {metadata_file_name}')
            collectible_metadata["name"] = breed
            collectible_metadata["description"] = f"An adorable {breed} woof!"
            # We have to first upload our image to IPFS, so we can assign it to our metadata here
            image_path = "./img/" + breed.lower().replace("_", "-") + ".png"
            
            image_uri = None
            # Below is case sensitive
            if os.getenv("UPLOAD_IPFS") == "True":
                image_uri = upload_to_ipfs(image_path)
            # Below we are setting "image_uri" to whatever "image_uri" is, if "image_uri" isn't "None", otherwise take from mapping
            image_uri = image_uri if image_uri else breed_to_image_uri[breed]

            collectible_metadata["image"] = image_uri
            # Below will gonna dump(move) "collectible_metadata" dictionary as json to this "collectible_metadata" file named "metadata_file_name".
            with open(metadata_file_name, "w") as file:
                json.dump(collectible_metadata, file)
            if os.getenv("UPLOAD_IPFS") == "True":
                upload_to_ipfs(metadata_file_name)


def upload_to_ipfs(filepath):
    # Below means that we go to given "filepath", open it in "rb" = binary and that opened file will gonna be named "fp"(filepath)
    with Path(filepath).open("rb") as fp:
        image_binary = fp.read()
        # Upload stuff
        # In console: ipfs daemon 
        # (this will run our own ipfs node, once we turn it off all images uploaded will get lost and we will have to repeat process or just keep node running)
        # If we don't want to run our own node, we should use 3rd party node using "Pinata"
        ipfs_url = "http://127.0.0.1:5001"
        # IPFS command line at: https://docs.ipfs.tech/reference/kubo/rpc/#rpc-commands
        endpoint = "/api/v0/add"
        response = requests.post(ipfs_url + endpoint, files = {"file": image_binary})
        ipfs_hash = response.json()["Hash"]
        # "./img/0-PUG.png" -> "0-PUG.png", actually ".split("/")[-1][0]" gives us 1st char after last "/", so "0"
        # to get "0-PUG.png" we need to use ".split("/")[-1]" or ".split("/")[-1:][0]"
        filename = filepath.split("/")[-1:][0]
        image_uri = f"https://ipfs.io/ipfs/{ipfs_hash}?filename={filename}"
        # our img_uri.png: https://ipfs.io/ipfs/QmUPjADFGEKmfohdTaNcWhp7VGk26h5jXDA7v3VtTnTLcW?filename=st-bernard.png
        # our img_uri.json: https://ipfs.io/ipfs/QmPrfxtkzcEQza8L8kksAZUsdneb4esAzEr2sWiBkYpdMt?filename=2-ST_BERNARD.json
        print(f'IMG URI .png and .json: {image_uri}')
        return image_uri
