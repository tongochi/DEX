# Tongochi in-game DEX

This repository consists of two sections: <a href="https://github.com/tongochi/DEX/tree/develop/Swaps">Swaps</a>
and <a href="https://github.com/tongochi/DEX/tree/develop/Staking">Staking</a>. In swaps directory there is the complete
code of <a href="https://api.tongochi.org/dexf">swaps web page</a>. In Staking section, there are smart contracts for
lockup NFT collection and backend of <a href="https://api.tongochi.org/staking">staking web page</a>.

## Staking

### Structure

#### Lockup contracts

Directory with all smart contracts. It includes:

- **lockup_collection_1.fc** and **lockup_collection_2.fc** - two versions of the main contract (second has onchain rewards).

- **nft_item.fc** - contract of NFT item from lockup NFT collection.

- **imports** - directory with some utility functions and constants.

#### Testing scripts

Directory with some scripts that will help you interact with the smart contract.

- **config.ts** - file with information about your wallet and contract addresses. You should edit it.

- **changeJettonAddress.ts** - script that will be needed only once, saves the contract's jetton wallet address in smart
  contract storage.

- **lockTokens.ts** - script for locking your jettons. You can change the jettonAmount and lockupPeriod variables in
  this file.

- **returnTokens.ts** - script for transferring your NFT back to the collection address and getting unlocked jettons.
  You should change the NFT address here.

#### Website backend

Directory with Django app that implements rest api.

### Lockup contracts info

This smart contract implements locking up TON jettons for a variable or fixed period (for version with onchain rewards 
only fixed). It is based on the [NFT collection template](https://github.com/ton-blockchain/token-contract/tree/main/nft) 
from ton.org with the addition of handling custom opcodes and a "jetton wallet address" section in storage. You can lock 
only one jetton type per smart contract instance.

### Contract work pattern

**To lock your tokens, you need:**

- Deploy the contract (you can find out more info about state init parameters in smc code. For version with onchain 
  rewards note that royalty params have the custom structure)

- Find the jetton wallet address of the contract. You can get this by sending any amount of jettons to the contract and
  looking up the address on https://testnet.tonscan.org/address/{SMART_CONTRACT_ADDRESS}#tokens

- Change the jetton_wallet_address by sending an internal message to the smart contract (you can use the
  changeJettonAddress script). This variable contains the address of the jetton wallet, in which locked jettons will be
  stored.

- If you are using the version with on-chain rewards, then replanish the reward pool with the amount you need (you can use
  the addRewards script).

- Send jettons to the contract with msgValue and fwdAmount greater than 0.1 TON (you can use the lockTokens script)

After this, the smart contract will check that you transferred the correct jetton and mint an NFT that proves you own
the locked tokens. Transferring this NFT to somebody transfers ownership of the locked tokens. The lockup start & end
times and amount of locked jettons are stored on-chain in the NFT-item contract storage.

**To withdraw your tokens, you need:**

- Wait for the lockup period to end

- Transfer the NFT back to the collection address with msgValue and fwdAmount greater than 0.15 TON (you can use the
  returnTokens script)

The NFT collection contract will check that you sent a valid NFT and that the lock period has ended. If everything
checks out, the tokens will be returned to your wallet and the NFT will be burned. In the version with on-chain 
rewards, you will receive <code>staking_factor / staking_base</code> jettons in addition to locked ones.

#### Special features

- **Ability to lock any tokens** (tokens with different addresses should be locked in different contract instances).

- **On-chain rewards** with a fixed interest rate.

- **Storing NFT content on-chain**, while duplicating it off-chain, so users can see it in Tonkeeper or Getgems but also
  be assured it cannot be modified.

- **Returning the NFT** back to user if it was sent to the smart contract before the lockup period ended.

- **Burning NFTs after unstaking** (entire NFT balance is transferred to owner during this operation).

- **Notifications when each NFT is transferred**: NFT contract sends 0.01 TON to collection address with special opcode,
  previous owner address and new owner address, **which is extremely useful** for tracking all transactions of NFTs from
  one collection.

### Monetization

Our smart contracts allow locking any tokens, so we plan to make our site a place where anyone can create a staking pool 
with on-chain rewards. In return, we will charge royalties in the form of a percentage of the rewards allocated by the 
project for stakers, as well as a percentage of the TVL of the pool. When creating a smart contract, royalty parameters can
be configured, so the percentage fee will depend on the total amount of funds that the project Will allocate for user
rewards. All fees will be collected from the fees pool, which the project must replenish before launching the staking
program. We are able to withdraw royalty jettons right after fees pool was refilled.

### Off-chain rewards

In the Tongochi game, items can be enhanced by increasing their level attribute from +0 up to +13. However, starting
from +3, there is a chance the item will be destroyed during improvement (even NFT items).

Items level +5 and above, when destroyed, go into a database where players can retrieve them using a developer coupon.
This database stores the last 100 broken +5 level items from all Tongochi players, on a first-in-first-out basis.

Developer coupons are earned by staking PET or LP PET-TON jettons on the Tongochi staking page or using the Tongochi 
swapper. Users receive developer points for these actions that can be exchanged for a coupon.

### Website backend

The website backend uses Django Rest Framework to sync blockchain data with our databases using Tonapi as a blockchain
indexer. All data is available via the [public API](https://api.tongochi.org/stakingapi/).
Developer points for off-chain rewards are also awarded to users through the website backend (1 point for 1 usd value of
staked PET and 1.25 point for 1 usd value of staked LP PET-TON every minute)

#### Special features

- **Instant updates** of all staker and pool data after any contract interactions, thanks
  to [tonconsole streaming API](https://docs.tonconsole.com/tonapi/streaming-api#websocket).

- **Calculating USD equivalents** of jettons & Ston.fi LP tokens by calling get methods of liquidity pools contracts (we
  use TON-JETTON pool to get TON value of jetton/LP token, then TON-USDT pool to get estimated USD value of TON). Will
  add Dedust LP tokens soon.

## Swaps

Swaps is a vue.js app in which you can swap different tokens. It is based on the STON.fi javascript SDK. Users get
developer points each time they use it.
