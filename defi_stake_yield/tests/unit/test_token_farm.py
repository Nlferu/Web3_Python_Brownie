from brownie import network, exceptions, config
from scripts.helpful_scripts import DECIMALS, LOCAL_BLOCKCHAIN_ENVIRONMENTS, INITIAL_PRICE_FEED_VALUE, get_account, get_contract
from scripts.deploy import KEPT_BALANCE, deploy_token_farm_and_dapp_token
import pytest, time

# We are testing all functions from TokenFarm.sol


def test_set_price_feed_contract():
    """
        We are testing below functions here:
        * setPriceFeedContract
    """
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index = 1)
    price_feed_address = get_contract("dai_usd_price_feed")
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    set_tx = token_farm.setPriceFeedContract(dapp_token.address, price_feed_address, {"from": account})
    set_tx.wait(1)
    print(f'set_tx: {set_tx}')
    print(f'DappToken address: {token_farm.tokenPriceFeedMapping(dapp_token.address)}')
    feed_tx = token_farm.tokenPriceFeedMapping(dapp_token.address)
    print(f'feed_tx: {feed_tx}')
    # Assert
    assert feed_tx == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(dapp_token.address, price_feed_address, {"from": non_owner})


# Below "amount_staked" will be taken from "conftest.py", which is fixture for tests in python (More info in Obsidian BlockChain tab)
def test_stake_tokens(amount_staked):
    """
        We are testing below functions here:
        * stakeTokens
        * updateUniqueTokensStaked
        * stakers
    """
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    user_staking_balance_before = token_farm.stakingBalance(dapp_token, account.address)
    tokens_staked_before = token_farm.uniqueTokensStaked(account.address)
    # stakers_before = token_farm.stakers(0) -> this will throw error as it does not exist before calling "stakeTokens" function, as "stakers" array is empty
    
    # Act
    # When approving we actually allow some tokens amount to be throw into any kind of transaction, in this case "staking"
    ap_tx = dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    ap_tx.wait(1)
    st_tx = token_farm.stakeTokens(amount_staked, dapp_token, {"from": account})
    st_tx.wait(1)
 
    user_staking_balance_after = token_farm.stakingBalance(dapp_token, account.address)
    print(f'Before Stake {user_staking_balance_before}, After Stake {user_staking_balance_after}')
    tokens_staked_after = token_farm.uniqueTokensStaked(account.address)
    print(f'Before Token Update {tokens_staked_before}, After Token Update {tokens_staked_after}')
    stakers_after = token_farm.stakers(0)
    print(f"Staker's Before {None}, Staker's After {stakers_after}")
    # Assert
    assert user_staking_balance_after == amount_staked
    assert tokens_staked_before == 0
    assert tokens_staked_after == 1
    assert stakers_after == account.address
    # Below will allow us to use those data in our other tests
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    """
        We are testing below functions here:
        * issueTokens
    """
    # Arrange
    # We are staking 1 dapp_token == in price to 1 ETH
    # soo... we should get 2,000 dapp tokens in reward
    # since the price of eth is $2,000 (It is taken from MockV3Aggregator from helpful_scripts, where initial value is set to $2000)
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index = 1)
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    # Below "balanceOf" function is from ERC20 contract
    starting_balance = dapp_token.balanceOf(account.address)
    
    # Act
    tx = token_farm.issueTokens({"from": account})
    tx.wait(1)
    ending_balance = dapp_token.balanceOf(account.address)
    print(f'Starting Balance: {starting_balance}, Ending Balance: {ending_balance}')
    # Assert
    # We have to divide INITIAL_PRICE_FEED_VALUE on 10 as we are rewarding user only 10% staked amount
    assert ending_balance == starting_balance + (INITIAL_PRICE_FEED_VALUE / 10)
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.issueTokens({"from": non_owner})


def test_token_is_allowed():
    """
        We are testing below functions here:
        * addAllowedTokens
        * tokenIsAllowed
        * allowedTokens
        * arrayLengthGetter
    """
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index = 1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    not_allowed = token_farm.tokenIsAllowed(config["networks"]["goerli"]["weth_token"])
    # Act
    tx_add = token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    tx_add.wait(1)

    allowed_token = token_farm.tokenIsAllowed(dapp_token.address)
    print(f'Allowed Tokens: {allowed_token}')
    
    stakers_len, tokens_len = token_farm.arrayLengthGetter()
    """
        To get array length from Contract we have to create function, which returns it in Contract!

        Tokens, which are allowed since start are those, which Mock's we are deploying, although
        we are deploying "dapp_token" by ourself's, so allowed tokens are: dapp_token, weth_token(mock) and dai_token(mock)
        once we run "addAllowedTokens" function we will add dapp_token again at the end of array, so there will be 4 items
    """
    print(f'Stakers Array Length: {stakers_len}, Allowed Tokens Array Length {tokens_len}')
    # Assert
    assert token_farm.allowedTokens(0) == dapp_token.address
    assert not_allowed == False
    assert allowed_token == True
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedTokens(dapp_token.address, {"from": non_owner})
    # Below will prevent stream of text error popping (tx.wait(1) didnt work here not sure why)
    #time.sleep(1)


def test_unStakeTokens(amount_staked):
    """
        We are testing below functions here:
        * unStakeTokens
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    user_staking_balance_before = token_farm.stakingBalance(dapp_token, account.address)
    tokens_staked_before = token_farm.uniqueTokensStaked(account.address)
    stakers_len_before, tokens_len = token_farm.arrayLengthGetter()
    # Act
    st_tx = token_farm.unStakeTokens(dapp_token.address, {"from": account})
    st_tx.wait(1)

    print("After unStake: ----------------------------------------------------------------------------------")
    print(f'Kept Balance: {KEPT_BALANCE}')
    user_staking_balance_after = token_farm.stakingBalance(dapp_token, account.address)
    print(f'Before unStake Balance {user_staking_balance_before}, After unStake Balance {user_staking_balance_after}')
    tokens_staked_after = token_farm.uniqueTokensStaked(account.address)
    print(f'Before unStake Tokens Amount: {tokens_staked_before}, After unStake Tokens Amount: {tokens_staked_after}')
    stakers_len_after, tokens_len = token_farm.arrayLengthGetter()
    print(f'Stakers Array Length Before unStake: {stakers_len_before}, Stakers Array Length After unStake: {stakers_len_after}')
    # Assert
    assert dapp_token.balanceOf(account.address) == KEPT_BALANCE
    assert user_staking_balance_after == user_staking_balance_before - amount_staked
    assert tokens_staked_before == 1
    assert tokens_staked_after == 0
    assert stakers_len_before == 1
    assert stakers_len_after == 0


def test_get_user_total_value_with_different_tokens(amount_staked, random_erc20, dai_token):
    """
        We are testing below functions here:
        * getUserTotalValue
        * getUserSingleTokenValue
        * getTokenValue
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    print("After Staking --------------------------------------------------------------")

    # Staking random_erc20 token
    token_farm.addAllowedTokens(random_erc20.address, {"from": account})
    token_farm.setPriceFeedContract(random_erc20.address, get_contract("eth_usd_price_feed"), {"from": account})
    random_erc20_stake_amount = amount_staked * 2
    random_erc20.approve(token_farm.address, random_erc20_stake_amount, {"from": account})
    token_farm.stakeTokens(random_erc20_stake_amount, random_erc20.address, {"from": account})

    # Staking dai_token
    token_farm.addAllowedTokens(dai_token.address, {"from": account})
    token_farm.setPriceFeedContract(dai_token.address, get_contract("dai_usd_price_feed"), {"from": account})
    dai_token_stake_amount = amount_staked * 3
    dai_token.approve(token_farm.address, dai_token_stake_amount, {"from": account})
    token_farm.stakeTokens(dai_token_stake_amount, dai_token.address, {"from": account})

    # getTokenValue (price, decimals)
    dapp_price, dapp_decimals = token_farm.getTokenValue(dapp_token.address)
    rerc20_price, rerc20_decimals = token_farm.getTokenValue(random_erc20.address)
    dai_price, dai_decimals = token_farm.getTokenValue(dai_token.address)
    print(f'Dapp Token Price: {dapp_price}, Token Decimals: {dapp_decimals}')
    print(f'Random_ERC20 Token Price: {rerc20_price}, Token Decimals: {rerc20_decimals}')
    print(f'DAI Token Price: {dai_price}, Token Decimals: {dai_decimals}')

    # getUserSingleTokenValue (single STAKED token balance)
    dapp_token_val = token_farm.getUserSingleTokenValue(account.address, dapp_token)
    rerc20_token_val = token_farm.getUserSingleTokenValue(account.address, random_erc20)
    dai_token_val = token_farm.getUserSingleTokenValue(account.address, dai_token)
    print(f'Dapp Token Value: {dapp_token_val}')
    print(f'Random_ERC20 Token Value: {rerc20_token_val}')
    print(f'DAI Token Value: {dai_token_val}')

    # getUserTotalValue (total STAKED all tokens value)
    total_tokens_val = token_farm.getUserTotalValue(account.address)
    print(f'Total Tokens Value: {total_tokens_val}')

    assert token_farm.getTokenValue(dapp_token.address) == (INITIAL_PRICE_FEED_VALUE, DECIMALS)
    # Below are 2 options as if we run whole test there will be additionaly (3 * amount_staked) of dapp_token from different accounts
    assert total_tokens_val == INITIAL_PRICE_FEED_VALUE * 9 # While Running `brownie test -s`
    #assert total_tokens_val == INITIAL_PRICE_FEED_VALUE * 6 # While Running `brownie test -s -k`
