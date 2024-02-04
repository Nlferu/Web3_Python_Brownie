from brownie import config, network, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.1, "ether")
# Max amount to withdraw after borrowing is "available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")". which is "0.04125", so "2 ** 256 - 1" won't work here
# as it would throw primal value, which was 0.1
max_amount = Web3.toWei(0.04, "ether")

# TO CALL BELOW WE HAVE TO FIRST FILL OUR ACCOUNT WITH "WETH" USING "GET_WETH.PY" FUNCTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def main():
    account = get_account()
    # Weth address
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # Call get_weth() in case we do not already have any weth
    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()
    # Depositing some ETH (WETH) into Aave
    lending_pool = get_lending_pool()
    # Approve sending out ERC20 tokens approve_erc20(amount, spender, erc20_address, account)
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    
    # Parameters for "deposit" function taken from: https://docs.aave.com/developers/v/2.0/the-core-protocol/lendingpool
    # deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode), onBehalfOf - will be our address, referralCode - It is deprecated, so we always use 0
    print("Depositing Collateral...")
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    print("Collateral Deposited!")
    # Calling return account data function
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    
    # Borrowing some DAI (In order to do that we need some conversion rate first DAI/ETH(We need Price Feed))
    print("Borrowing in Progress...")
    
    dai_usd_price = get_asset_price(config["networks"][network.show_active()]["dai_usd_price_feed"])
    eth_usd_price = get_asset_price(config["networks"][network.show_active()]["eth_usd_price_feed"])
    #dai_eth_price = dai_usd_price / eth_usd_price
    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    
    # We multiply by 0.95 as a buffer, to make sure our health factor is "better" as we do not want to be liquidated
    # We are converting our borrowable_eth -> borrowable_dai * 95%
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.5)
    print(f'We are going to borrow {amount_dai_to_borrow} DAI')
    # Now we will borrow below (calling borrow function from ILendingPool interface)
    # "borrow" function args are: (address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)
    dai_address = config["networks"][network.show_active()]["dai_token_address"]
    borrow_tx = lending_pool.borrow(dai_address, Web3.toWei(amount_dai_to_borrow, "ether"), 1, 0, account.address, {"from": account}, )
    borrow_tx.wait(1)
    print("Borrowing Complete!")
    # Printing new account data information
    get_borrowable_data(lending_pool, account)
    
    # Repaying everything
    # Before we can repay we have to approve erc20 for DAI (Approve located in "repay_all" function)
    # "repay" function args are: (address asset, uint256 amount, uint256 rateMode, address onBehalfOf)
    # We are not able to repay all as we have to pay interests, that is why we deduct "amount_dai_to_borrow" by 1
    amount_dai_to_repay = Web3.toWei((amount_dai_to_borrow - 1), "ether")
    print(f'DAI to borrow: {amount_dai_to_borrow}')
    print(f'DAI to repay: {amount_dai_to_repay}')
    repay_all(amount_dai_to_repay, lending_pool, account)
    # Printing new account data information
    get_borrowable_data(lending_pool, account)
    print("You just deposited, borrowed, and repayed with Aave, Brownie, and Chainlink!")
    withdraw_all_collateral(lending_pool, account)
    print("You just withdrew all collateral")
    get_borrowable_data(lending_pool, account)


def withdraw_all_collateral(lending_pool, account):
    print("Withdrawing collateral...")
    tx = lending_pool.withdraw(config["networks"][network.show_active()]["weth_token"], max_amount, account, {"from": account})
    tx.wait(1)
    print("Withdrew!")
    return tx


def repay_all(amount, lending_pool, account):
    print("Approving And Repaying Everything...")
    approve_erc20(Web3.toWei(amount, "ether"), lending_pool, config["networks"][network.show_active()]["dai_token_address"], account)
    repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token_address"], amount, 1, account.address, {"from": account})
    repay_tx.wait(1)
    print("Repaying Complete!")


def get_asset_price(price_feed_address):
    # As always grabbing ABI and Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    # latestRoundData has 5 arguments, to pick it's price(answer) we are chosing in array of 5 args (0, 1, 2, 3, 4), so price is 1 -> [1] at the end of function
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f'The DAI/ETH price is {converted_latest_price}')
    return float(converted_latest_price)


# Creating function, which return our account data: so how much collateral do we have, our debt, available borrow power, liquidation treshold, loan to value and health factor
# Calling "getAccountData" function from ILendingPool interface
def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    print(f'You have {total_collateral_eth} worth of ETH deposited.')
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f'You have {total_debt_eth} worth of ETH borrowed.')
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    print(f'You can borrow {available_borrow_eth} worth of ETH.')
    current_liquidation_threshold = round(current_liquidation_threshold/100, 2)
    ltv = round(ltv/100, 2)
    health_factor = round(health_factor/10 ** 18, 2)
    print(f'Liquidation threshold {current_liquidation_threshold}%, Max LTV is {ltv}%, Health Factor {health_factor}')
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    # Get ERC20 token
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("ERC20 Approved!")
    #print(tx.info())
    #print(tx.revert_msg)
    return tx


def get_lending_pool():
    # Goes thru the lending pool addresses provider from the Aave documentation and returns below "lending_pool" contract that we can now interact with
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool_addresses_provider"])
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
