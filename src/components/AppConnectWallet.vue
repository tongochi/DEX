<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref, onMounted, nextTick } from 'vue'
import {TonConnect} from '@tonconnect/sdk'
import { toUserFriendlyAddress } from '@tonconnect/sdk';
import { Address } from 'ton3-core';
import QRCodeStyling from './QRCodeStyling.vue';
import TonWeb from 'tonweb';
import { ConnectedWalletFromAPI, useWalletStore } from '../stores'

const store = useWalletStore()

defineProps<{ anyProp: string }>()

const walletConnectionSource = {
  tonkeeper: {
    universalLink: 'https://app.tonkeeper.com/ton-connect',
    bridgeUrl: 'https://bridge.tonapi.io/bridge',
  },
  tonhub: {
    universalLink: "https://tonhub.com/ton-connect",
    bridgeUrl: "https://connect.tonhubapi.com/tonconnect",
  },
};

async function postData(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    cache: "no-cache",
    body: JSON.stringify(data),
  });
  return response;
}


const connect = async (wallets: 'tonkeeper' | 'tonhub') => {
  // console.log(new Address(rawAddress).toString('base64', { bounceable: true }));
  const d = await postData('https://ton-dapp-backend.systemdesigndao.xyz/ton-proof/generatePayload');
  const { payload } = await d.json();
    
  const link = store.entity?.connect(walletConnectionSource[wallets], { tonProof: payload });

  store.setConnecting({
    link,
  })
}

const sendTx = async () => {
  const transaction = {
      validUntil: Date.now() + 1000000,
      messages: [
          {
            address: store.wallet?.address.raw!,
            amount: "60000000", 
          }
      ]
  }

  try {
      const result = await store.entity?.sendTransaction(transaction);

      alert('Transaction was sent successfully');
  } catch (e) {
      console.error(e);
  }
}

onMounted(() => {  
  const tonConnect = new TonConnect({
    manifestUrl: 'https://about.systemdesigndao.xyz/ton-connect.manifest.json',
  });

  store.setEntity(tonConnect);

  const unsubscribe = tonConnect.onStatusChange(async wallet => {
			if (!wallet) {
				return;
			}

			const tonProof = wallet.connectItems?.tonProof;

			if (tonProof) {
				if ('proof' in tonProof) {
          const obj = {
              proof: {
                ...tonProof.proof,
                state_init: wallet.account.walletStateInit,
              },
              network: wallet.account.chain,
              address: wallet.account.address
          };
          try {
            const { token } = await (await postData('https://ton-dapp-backend.systemdesigndao.xyz/ton-proof/checkProof', obj)).json();
            const data = await (await fetch(`https://ton-dapp-backend.systemdesigndao.xyz/dapp/getAccountInfo?network=${obj.network}`, {
                    headers: {
                      Authorization: `Bearer ${token}`,
                      'Content-Type': 'application/json',
                    }
            })).json() as ConnectedWalletFromAPI;
            store.setWallet(data);
          } catch (err) {
            console.error(err);
          }
					return;
				}

				console.error(tonProof.error);
			}
	});

  return unsubscribe;
})

const { wallet, connecting } = storeToRefs(store)
</script>

<template>
  <div v-if="wallet === undefined" style="display: flex; flex-direction: column;">
    <button @click="connect('tonkeeper')">Connect tonkeeper</button>
    <button @click="connect('tonhub')">Connect tonhub</button>
    <QRCodeStyling v-if="connecting?.link" :text="connecting.link" />
  </div>
  <div v-else>
    <pre>{{wallet}}</pre>
    <button @click="sendTx">Send tx</button>
  </div>
</template>
