
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_fund_me
from brownie import network, accounts, exceptions
import pytest

def test_can_fund_and_withdraw():
    account = get_account()
    fund_me = deploy_fund_me()
    entrance_fee = fund_me.getEntranceFee() + 100
    # tx = transaction
    tx = fund_me.fund({"from": account, "value": entrance_fee})
    tx.wait(1)
    # addressToAmountFunded has attribute "address" as it is coded as mapping with index [msg.sender] which = "owner" and "owner" is "address public" as coded on top 
    # assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == 0

# To run test only on our local chains
def test_only_owner_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    fund_me = deploy_fund_me()
    thief_account = accounts.add()
    # fund_me.withdraw({"from": bad_actor})
    # We are telling our test that we want this withdraw to happen
    # Below is telling our test if below revert's with "VirtualMachineError" that is ok/good because if it throws error thief cannot withdraw our money
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": thief_account})
