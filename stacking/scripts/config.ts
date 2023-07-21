import {getHttpEndpoint} from "@orbs-network/ton-access";
import {mnemonicToWalletKey, mnemonicNew} from "ton-crypto";
import {TonClient, fromNano, toNano, internal, beginCell, Address} from "ton";
import {WalletContractV3R1, WalletContractV3R2, WalletContractV4} from "ton"

// your wallet data
export const mnemonic = "word1 ... word24";  // seed phrase
const WalletContractV = WalletContractV3R2;  // contract version of your wallet

export async function get_wallet_info() {

    // client for working with http
    const endpoint = await getHttpEndpoint({network: "testnet"});
    const client = new TonClient({endpoint});

    const key = await mnemonicToWalletKey(mnemonic.split(' '));  
    const wallet = WalletContractV.create({publicKey: key.publicKey, workchain: 0});
    const walletContract = client.open(wallet);
    const walletAddress = wallet.address;  // main wallet address

    return {key, walletContract, walletAddress};
}
   

// addresses
export const jettonWalletAddress = "";  // jetton wallet address of your wallet
export const collectionAddress = "";  // nft collection address
export const collectionJettonWalletAddress = ""  // nft collection jetton wallet address
