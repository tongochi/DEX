import {toNano, internal, beginCell, Address} from "ton";
import {jettonWalletAddress, collectionAddress, get_wallet_info} from "./config"


async function main(nftToReturnAddress: string) {
    const {key, walletContract, walletAddress} =  await get_wallet_info()
    let seqno = await walletContract.getSeqno();
    // Тело транзакции для разлока токенов, отправляется на адрес bond nft
    let msgBody = beginCell()
                    .storeUint(0x5fcc3d14, 32)
                    .storeUint(Date.now(), 64)
                    .storeAddress(Address.parse(collectionAddress))
                    .storeAddress(walletAddress)
                    .storeBit(false)  // no custom payload
                    .storeCoins(toNano('0.15'))  // most will be returned
                    .storeBit(false)  // no forward payload
                .endCell();

    await walletContract.sendTransfer({
            secretKey: key.secretKey,
            seqno: seqno,
            messages: [internal({
                to: nftToReturnAddress,
                value: toNano("0.25"),  // most will be returned
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

main("EQCFNk3AktRMWKLqldoYtZaslE9yv4OoOzbAAq9zEjE3mQ09");