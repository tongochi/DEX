<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { onMounted, watchEffect, watch } from 'vue'
import {TonConnect} from '@tonconnect/sdk'
import QRCodeStyling from './QRCodeStyling.vue';
import TonWeb from 'tonweb';
import { ConnectedWalletFromAPI, useWalletStore } from '../stores'
import { Router, ROUTER_REVISION, ROUTER_REVISION_ADDRESS } from '@ston-fi/sdk';
import { bytesToBase64 } from 'ton3-core/dist/utils/helpers';

const store = useWalletStore()

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

const jettons = [
  { name: 'jusdt', addressBouncable: 'EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA' },
  { name: 'jusdc', addressBouncable: 'EQB-MPwrd1G6WKNkLz_VnV6WqBDd142KMQv-g1O-8QUA3728' },
];

const disconnect = async () => {
  if (store?.entity?.connected) {
      await store?.entity?.disconnect();
      store.setWallet(undefined);
      localStorage.removeItem('wallet');
  }
}

const swapJettons = async () => {
  try {
      const WALLET_ADDRESS = store.wallet?.address.bounceable!; // YOUR WALLET ADDRESS

      const REFERRAL_ADDRESS = undefined; // REFERRAL ADDRESS (OPTIONAL)

      const JETTON0 = jettons[0].addressBouncable;
      const JETTON1 = jettons[1].addressBouncable;

      const provider = new TonWeb.HttpProvider(undefined, { apiKey: import.meta.env.VITE_TON_HTTP_API_KEY });

      const router = new Router(provider, {
        revision: ROUTER_REVISION.V1,
        address: ROUTER_REVISION_ADDRESS.V1,
      });

      // Build transaction params to swap 1e6 JETTON0 to JETTON1
      // but not less than 1e6 JETTON1
      const params = await router.buildSwapJettonTxParams({
        userWalletAddress: WALLET_ADDRESS,
        offerJettonAddress: JETTON0,
        askJettonAddress: JETTON1,
        offerAmount: new TonWeb.utils.BN(1e6),
        minAskAmount: new TonWeb.utils.BN(1e6),
        queryId: 12345,

        // Set your address if you want to give referral payouts
        // from everyone who using this code to swap jettons
        referralAddress: REFERRAL_ADDRESS,
      });
      
      const transaction = {
          validUntil: Date.now() + 1000000,
          messages: [
              {
                address: params.to.toString(),
                amount: (params.gasAmount.toNumber() * 2).toString(),
                payload: bytesToBase64(await params.payload.toBoc()),
              }
          ]
      }

      const result = await store.entity?.sendTransaction(transaction);

      console.log('Transaction was sent successfully', result);
  } catch (e) {
      console.error(e);
  }
}

onMounted(async () => {  
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

            localStorage.setItem('wallet', JSON.stringify(data));

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

watch(() => store?.entity?.connected, async () => {
  if (store?.entity?.connected === false) {
    store.entity.restoreConnection();
  }

  if (store?.entity?.connected === true) {
    const data = JSON.parse(localStorage.getItem('wallet'));
    store.setWallet(data);
    store.setLoading(false);
  }
})

const { wallet, connecting, loading } = storeToRefs(store)
</script>

<template>
  <div v-if="loading === false">
    <div v-if="wallet === undefined" class="p-1">
      <div class="flex justify-center">
        <button class=" bg-main-light-4 w-40 h-10 rounded-full font-sans border-none" @click="connect('tonkeeper')"><span class="text-white-1">Connect tonkeeper</span></button>
        <button class=" bg-main-light-4 w-40 h-10 rounded-full font-sans border-none ml-1" @click="connect('tonhub')"><span class="text-white-1">Connect tonhub</span></button>
      </div>
      <div class="flex justify-center">
        <QRCodeStyling v-if="connecting?.link" :text="connecting.link" />
      </div>
    </div>
    <div v-else class="flex flex-col">
      <pre>{{wallet}}</pre>
      <button @click="swapJettons">Swap jettons (jUSDT -> jUSDC)</button>
      <button @click="disconnect">Disconnect</button>
    </div>
  </div>
  <div v-else class="flex justify-center items-center h-screen">
    loading wallet state...
  </div>
</template>
