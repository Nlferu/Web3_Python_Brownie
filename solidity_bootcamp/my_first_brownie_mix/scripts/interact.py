from brownie import MyFirstContract, ERC20Basic, config, accounts, network


def main():
    account = accounts.add(config["wallets"]["from_key"])
    myFirstContract = MyFirstContract[-1]
    tx = myFirstContract.setNumber(123456, {'from': account})
    tx.wait(1)
    num_to_add = 3
    addNumber = myFirstContract.addNumber(num_to_add)
    print("Number is: ", myFirstContract.getNumber({'from': account}))
    print(f'Adding {num_to_add} to primal number: {addNumber}')
    mint_erc20()
    print("Tokens Sent!")


def mint_erc20():
    account = accounts.add(config["wallets"]["from_key"])
    myERC20Contract = ERC20Basic[-1]
    tx = myERC20Contract.transfer("0xe0c5aDdCfbd028FF4e69CDd6565efA5EedCFd743", 500, {"from": account})
    tx.wait(1)
