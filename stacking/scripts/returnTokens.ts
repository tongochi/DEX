import {toNano, internal, beginCell, Address} from "ton";
import {jettonWalletAddress, collectionAddress, get_wallet_info} from "./config"


async function main() {
    const {key, walletContract, walletAddress} =  await get_wallet_info()
    let seqno = await walletContract.getSeqno();
    
    const nftToReturnAddress = "";  // nft you should return to get back your jettons 
    let msgBody = beginCell()
                    .storeUint(0x5fcc3d14, 32)
                    .storeUint(Date.now(), 64)
                    .storeAddress(Address.parse(collectionAddress))
                    .storeAddress(null)
                    .storeBit(false)  // no custom payload
                    .storeCoins(toNano('0.25'))  // most will be returned
                    .storeBit(false)  // no forward payload
                .endCell();

    await walletContract.sendTransfer({
            secretKey: key.secretKey,
            seqno: seqno,
            messages: [internal({
                to: nftToReturnAddress,
                value: toNano("0.3"),  // most will be returned
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