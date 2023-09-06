import {toNano, internal, beginCell, Address} from "ton";
import {collectionJettonWalletAddress, get_wallet_info, collectionAddress} from "./config"


async function main(newOwnerAddress: string) {
    const {key, walletContract, walletAddress} = await get_wallet_info()
    let seqno = await walletContract.getSeqno();

    let msgBody = beginCell()
        .storeUint(3, 32)
        .storeUint(Date.now(), 64)
        .storeAddress(Address.parse(newOwnerAddress))
        .endCell()

    await walletContract.sendTransfer({
        secretKey: key.secretKey,
        seqno: seqno,
        messages: [internal({
            to: collectionAddress,
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

const newOwnerAddress = "";
main(newOwnerAddress);