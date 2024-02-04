
from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

install_solc("0.6.0")
# Function below looks for .env file and import it into our file
load_dotenv()

# We want to read our Solidity file
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    #print(simple_storage_file)

# Compile Our Solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}}},
    },
    solc_version = "0.6.0",
)

# print(compiled_sol)

# Saving our output in file
with open("compiled_code.json", "w") as file:
    # Instead of file.write
    json.dump(compiled_sol, file)

# Get bytecode in order to deploy contract
# This shows path in our compiled_code.json file so: contracts -> SimpleStorage.sol -> etc...
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# Get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

#print(abi)

# How to deploy it if we do not have account and virtual machine like on Remix?
# We can you Ganache it is fake/simulated blockchain environment to test things fast like on Remix VM (not MetaMask) 
# To connect to our fake blockchain in Ganache we need HTTP:// url
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
# Picking up one of the fake accounts
my_address = "0x319CF4413a944DF14888D7a89BC539ec6a397E09"
# Once we copy it from Ganache we have to add "0x" at start of it
private_key = os.getenv("PRIVATE_KEY_ENV")
print(f'Our Private Key: {private_key}')

# Create the contract in python
SimpleStorage = w3.eth.contract(abi = abi, bytecode = bytecode)
# print(SimpleStorage)

# "Nonce" -> coined for or used on one occassion, nonce is an arbitrary number that can be used just once in cryptographic communication
# To get "Nonce" we can just simply take our transaction count as this is the way of creation of nonce number on eth blockchain 
# (you can check our transactions nonce number (transaction count) we made on VM by Remix)
nonce = w3.eth.getTransactionCount(my_address)
print(f'Number of transactions made: {nonce} this is our nonce')

# To finally deploy our contract we need to:
# 1. Build the Contract Deploy Transaction -> Build Transaction
# 2. Sign the Transaction with our private key
# 3. Send the Transaction
transaction = SimpleStorage.constructor().buildTransaction({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": my_address, "nonce": nonce})

# Signing Our Transaction
# Never hard code your private key, you should set it as environment variable in windows
# To set env variable: "winKey+R" -> type: sysdm.cpl -> advanced -> Env Variables -> new -> restart VS code
# Another way is to create .env file -> to not push your private key into source from .env -> create .gitignore file and write .env there
signed_txn = w3.eth.account.sign_transaction(transaction, private_key = private_key)

# print(transaction)
# print(signed_txn)

# Sending The Signed Transaction to blockchain, so it can actually deploy
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Whenever we are sending transaction we wait for some block confirmations to happen, this will stop our code run for a bit just to wait for this trade go through
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract Deployed!")

# Working with the contract, we will always need:
# Contract Address
# Contract ABI

# We need to create new contract object to interact with it
simple_storage = w3.eth.contract(address = tx_receipt.contractAddress, abi = abi)

# Calling view function with web3.py from SimpleStorage contract created in Remix
# We can interact with 2 ways "CALL" or "TRANSACT"
# Call -> Simulate making the call and getting a return value (Calls don't make a state change to blockchain (Blue button in Remix))
# Transact -> Actually make a state change (Orange button in Remix)

# Initial value of favourite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")

# Running "store" function from SimpleStorage contract created in Remix
# Adding +1 to nonce as "nonce" is already used above and it have to be original and one only

# 1 -> building new transaction as we use orange button so its not call but transact (have impact on blockchain)
store_transaction = simple_storage.functions.store(666).buildTransaction({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": my_address, "nonce": nonce + 1})
# 2 -> we are signing this new transaction
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key = private_key)
# 3 -> sending signed new transaction
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
transaction_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

# Checking if our value has been updated
print("Contract Updated!")
print(simple_storage.functions.retrieve().call())

# It will be probplematic to work as this with Ganache, that's why we need command line interface of Ganache instead of UI
# Now we will setup all to use Ganache CLI intead of Ganache UI, this will be also used by Brownie in future
# Installing NodeJS
# Installing Yarn -> it is package manager similar to pip
