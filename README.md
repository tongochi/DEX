## Stacking section structure
### Contracts
Directory with all smart contracts. It includes:
- <b>lockup-nft-collection.fc</b> - main contract and the only contract you should deploy by yourself. 
- <b>nft-item.fc</b> - contract of NFT item from lockup NFT collection.
- <b>imports</b> - directory with some functions and constants (taken from ton.org template).
### Scripts
Directory with some scripts that will help you to interact with smart contract.
- <b>config.ts</b> - file with information about your wallet and sc addresses. You should edit it.
- <b>changeJettonAddress.ts</b> - script that will be needed only once, saves sc jetton wallet address in the storage.
- <b>lockTokens.ts</b> - script for locking your jettons. You can change jettonAmount in this file.
- <b>returnTokens.ts</b> - script for transferring your NFT back to the collection address and getting unlocked jettons. You should change NFT address here.

## Logic of the smart contract
This smart contract implements lockup of ton jettons for a fixed period. It is based on <a href="https://github.com/ton-blockchain/token-contract/tree/main/nft">NFT collection template</a> with the addition of handling some op-codes and "jetton wallet address" section in storage (also one line in "nft-item.fc" was changed). You can lock only one jetton in one smart contract.

To lock your tokens, you need:
- Set lockup_period
- Deploy contract 
- Find out the jetton wallet address of the contract. You can do it by sending any amount of jettons to the contract and visiting https://testnet.tonscan.org/address/{SMART_CONTRACT_ADDRESS}#tokens 
- Change jetton_wallet_address by sending internal message to smart contract (you can use changeJettonAddress script).
- Send jetton to the contract with msgValue and fwdAmount params more than 0.1 TON (you can use lockTokens script)

After that, smart contract will check that you transferred correct jetton and mint NFT that proves that you own the locked tokens. Transferring this NFT to somebody means transferring your locked tokens. Lockup start time and amount of locked jettons are stored in the NFT content (it is the only NFT content for now, will add user-friendly format later). 

To withdraw your tokens, you need:
- Wait for the lockup period end
- Transfer NFT to collection address with msgValue and fwdAmount params more than 0.15 TON (you can use returnTokens script)

NFT collection contract will check that you sent valid NFT and was your lock period ended or not. If everything is OK, then tokens will be returned to your wallet (you will not be able to see transaction in Tonkeeper, but it will be displayed in <a href="https://testnet.tonviewer.com/">Tonviewer</a>). If something is not ok, it means, that you've lost your funds :(.

## TODO
- Human-readable NFT content.
- Burn NFT after withdrawing funds.
- Return NFT to user if he transferred it to the collection address before lockup period end (maybe).

## Swap
Swap is based on ton-connect and [ston.fi](https://ston.fi/) swap contracts. 

User connect theirs wallets to the app, then choose tokens to swap in the form, then the transaction in sent to the wallet to be confirmed and then processed.
