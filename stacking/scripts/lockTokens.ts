import {toNano, internal, beginCell, Address} from "ton";
import {jettonWalletAddress, collectionAddress, get_wallet_info} from "./config"


async function main() {
    const {key, walletContract, walletAddress} =  await get_wallet_info()
    let seqno = await walletContract.getSeqno();
    
    let msgBody = beginCell()
                    .storeUint(0xf8a7ea5, 32)
                    .storeUint(Date.now(), 64)
                    .storeCoins(toNano('50'))  // jetton amount 
                    .storeAddress(Address.parse(collectionAddress))
                    .storeAddress(walletAddress)
                    .storeUint(0, 1)
                    .storeCoins(toNano('0.1'))
                    .storeUint(0, 1)
                .endCell()

    await walletContract.sendTransfer({
            secretKey: key.secretKey,
            seqno: seqno,
            messages: [internal({
                to: jettonWalletAddress,
                value: toNano("0.2"),  // most will be returned
                body: msgBody,  
                bounce: true
            })]
        });

    // wait for transaction to confirm
    let max_reties = 50;
    while ((await walletContract.getSeqno()) == seqno && (--max_reties)) {
        await sleep(1500);
    }
    console.log("transaction confirmed");
}

function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

main();