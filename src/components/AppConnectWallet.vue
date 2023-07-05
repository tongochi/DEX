<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import {TonConnect} from '@tonconnect/sdk'
import QRCodeStyling from './QRCodeStyling.vue';
import TonWeb from 'tonweb';
import { ConnectedWalletFromAPI, useWalletStore } from '../stores'
import { Router, ROUTER_REVISION, ROUTER_REVISION_ADDRESS } from '@ston-fi/sdk';
import { bytesToBase64 } from 'ton3-core/dist/utils/helpers';
import { Coins } from 'ton3-core';

const store = useWalletStore()

const usdToSton = ref('');
const stonToUsd = ref('');

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
  // fcking hell but okey
  if (store?.entity?.connected) {
      await store?.entity?.disconnect();
  }
  const d = await postData('https://ton-dapp-backend.systemdesigndao.xyz/ton-proof/generatePayload');
  const { payload } = await d.json();
    
  const link = store.entity?.connect(walletConnectionSource[wallets], { tonProof: payload });

  store.setConnecting({
    link,
  })
}

const jettons = [
  { name: 'jusdt', addressBouncable: 'EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA' },
  { name: 'ston', addressBouncable: 'EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO' },
];

const disconnect = async () => {
  if (store?.entity?.connected) {
      await store?.entity?.disconnect();
      store.setWallet(undefined);
      localStorage.removeItem('wallet');
  }
}

const swapJettons = async (leftJetton: string, rightJetton: string, amount: string) => {
  try {
      const WALLET_ADDRESS = store.wallet?.address.bounceable!; // YOUR WALLET ADDRESS

      const REFERRAL_ADDRESS = undefined; // REFERRAL ADDRESS (OPTIONAL)

      const JETTON0 = leftJetton;
      const JETTON1 = rightJetton;

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
        // 1000000, 1e6 - 1 TON for jUSDT
        offerAmount: amount,
        minAskAmount: amount,
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
    const localWallet = localStorage.getItem('wallet');
    if (localWallet) {
      const data = JSON.parse(localWallet);
      store.setWallet(data);
      store.setLoading(false);
    }
  }
})

const { wallet, connecting, loading } = storeToRefs(store)

function isNumber(evt: any) {
      evt = (evt) ? evt : window.event;
      var charCode = (evt.which) ? evt.which : evt.keyCode;
      if ((charCode > 31 && (charCode < 48 || charCode > 57)) && charCode !== 46) {
        evt.preventDefault();;
      } else {
        return true;
      }
}
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
      <div class="flex flex-col justify-center">
        <input v-model="usdToSton" type="number" @keypress="isNumber" />
        <button @click="swapJettons(jettons[0].addressBouncable, jettons[1].addressBouncable, (Number(usdToSton) * 1e6).toString())">Swap jettons ({{usdToSton}} jUSDT -> STON)</button>
      </div>
      <div class="flex flex-col justify-center">
        <input v-model="stonToUsd" type="number" @keypress="isNumber" />
        <button @click="swapJettons(jettons[1].addressBouncable, jettons[0].addressBouncable, new Coins(stonToUsd).toNano())">Swap jettons ({{stonToUsd}} STON -> jUSDT)</button>
      </div>
      <button @click="disconnect">Disconnect</button>
    </div>
  </div>
  <div v-else class="flex justify-center items-center h-screen">
    loading wallet state...
  </div>
</template>
