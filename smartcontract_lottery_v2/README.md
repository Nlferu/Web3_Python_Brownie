LOTTERY V2

1. Users can enter lottery with ETH based on USD fee
2. Admin will choose when the lottery is over
3. The lottery will select a random winner

How do we want to test this?

1. mainnet-fork -> because we work only on some onchain contracts and some math
2. development with mocks
3. testnet

4. We will be using VRFCoordinatorV2Mock for this lottery
