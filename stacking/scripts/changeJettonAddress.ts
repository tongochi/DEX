import {toNano, internal, beginCell, Address} from "ton";
import {jettonWalletAddress, collectionJettonWalletAddress, get_wallet_info} from "./config"


async function main() {
    const {key, walletContract, walletAddress} =  await get_wallet_info()
    let seqno = await walletContract.getSeqno();
    
    let msgBody = beginCell()
                    .storeUint(4, 32)
                    .storeUint(Date.now(), 64)
                    .storeAddress(Address.parse(collectionJettonWalletAddress))
                .endCell()

    await walletContract.sendTransfer({
            secretKey: key.secretKey,
            seqno: seqno,
            messages: [internal({
                to: jettonWalletAddress,
                value: toNano("0.01"),  
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