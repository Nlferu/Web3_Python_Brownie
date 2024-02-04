
* Disclosure:

As we won't be deploying any contracts here we won't need any Mocks also. That means we can set all networks to default mainnet-fork-dev as it is fork setup by us earlier
in brownie. All mocks can be get from mainnet (we are passing all addresses to "brownie-config.yaml").

1. Swap some ETH for WETH
2. Deposit some ETH (WETH) into Aave
3. Borrow some asset with the ETH collateral
4. Challenge -> Sell that borrowed asset (Short Selling) ? (Couldn't find any information about that)
5. Repay everything back

Testing:
Integration test: Kovan
Unit test: Mainnet-fork (Mock all of mainnet!)(As we won't be deploying any contracts we do not need any mocks)
