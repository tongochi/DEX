<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { onMounted, ref, watch } from 'vue';
import {TonConnect} from '@tonconnect/sdk';
import TonWeb from 'tonweb';
import { ConnectedWalletFromAPI, useWalletStore } from './stores';
import { Router, ROUTER_REVISION, ROUTER_REVISION_ADDRESS } from '@ston-fi/sdk';
import { bytesToBase64, uintToHex } from 'ton3-core/dist/utils/helpers';
import { Address, BOC, Coins, Slice } from 'ton3-core';
import AppConnectWallet from './components/AppConnectWallet.vue';

const store = useWalletStore()

const usdToSton = ref('');
const stonToUsd = ref('');

async function postData(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    cache: "no-cache",
    body: JSON.stringify(data),
  });
  return response;
}

const jettons = [
  { name: 'jusdt', addressMinterBouncable: 'EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA', addressMinterRaw: '0:729C13B6DF2C07CBF0A06AB63D34AF454F3D320EC1BCD8FB5C6D24D0806A17C2' },
  { name: 'ston', addressMinterBouncable: 'EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO', addressMinterRaw: '0:3690254DC15B2297610CDA60744A45F2B710AA4234B89ADB630E99D79B01BD4F' },
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
        minAskAmount: 0,
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
                amount: params.gasAmount.add(TonWeb.utils.toNano('0.2')),
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

enum JettonOps {
    TRANSFER = '0xf8a7ea5',
    TRANSFER_NOTIFICATION = '0x7362d09c',
    INTERNAL_TRANSFER = '0x178d4519',
    EXCESSES = '0xd53276db',
    BURN = '0x595f07bc',
    BURN_NOTIFICATION = '0x7bdd97de',
}

const loadTransferNotification = (body: Slice, payload: { opUint32Hex: string }) => {
    const queryId = body.loadBigUint(64);
    const jettonAmount = body.loadCoins();
    const from = body.loadAddress();
    const forwardPayload = body.loadBit() ? Slice.parse(body.loadRef()) : body;

    return {
      ...payload,
      queryId,
      jettonAmount,
      from,
      forwardPayload,
    };
};
          
const parseBocBase64 = (bocBase64: string) => {
  // 0x7362d09c - jetton transfer notification
  const [ deserialized ] = BOC.from(bocBase64);
  const slice = deserialized.slice();
  const opUint32 = slice.loadUint(32);
  const opUint32Hex = `0x${uintToHex(opUint32)}`;
  console.log(opUint32, opUint32Hex);

  if (opUint32Hex === JettonOps.TRANSFER) {

    const queryId = slice.loadBigUint(64);
    const amount = slice.loadCoins();

    console.log(queryId, amount);
  }

  if (opUint32Hex === JettonOps.TRANSFER_NOTIFICATION) {
    console.log(loadTransferNotification(slice, { opUint32Hex }))
  }

  if (opUint32Hex === JettonOps.EXCESSES) {
    console.log('exc');
    const queryId = slice.loadBigUint(64);
    console.log(queryId);
  }
}

onMounted(async () => {
  console.log(new Address('EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO').toString('raw')); // ston
  console.log(new Address('EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA').toString('raw')); // jusdt

  const t = [
      {
        "value": "te6ccuEBAQEADgAcABjVMnbbAAAjjN/pQ8OUt8hp"
      },
      {
        "value": "te6ccuEBAQEANQBqAGZzYtCcAAAjjN/pQ8NQmasQyAgAcx8ShmRebO0RtS6aLAfKsNbqQjkLW5af0gSg4DEpTNB4dPjD"
      },
      {
        "value": "te6ccuECAgEAAIcAAKIBDgGcsbvyF40AJ2UWV0N7lpkTAdb95TxFNxE9HIjlqdHz4aWCR2O824iiD8udFrK3g1yK0sey6Cp0sHXOSza+HqKlBympoxdkp8BPAAABzAADAQBoYgAcx8ShmRebO0RtS6aLAfKsNbqQjkLW5af0gSg4DEpTNCAhYOwAAAAAAAAAAAAAAAAAAApFK8Y="
      },
      {
        "value": "te6ccuEBAQEADgAcABjVMnbbAAAAAAAAMDkRbQJP"
      },
      {
        "value": "te6ccuECAwEAAQkAAKIBfgISAZxuyoebGfZ8VzQxmyLY+6Oo2rpK18db4nkdZrmefxPrZFc/gN3BkihD30iN0Kd042EItJTJrQPP/9yR20Ub+9gHKamjF2SloxkAAAHLAAMBAdViAEEnePzvnrqta5YU7cinRN3z8ZRMnEoV9MC37fAb1kQDoO5rKAAAAAAAAAAAAAAAAAAAD4p+pQAAAAAAADA5Q7msoAgA7zuZAqJxsqAciTilI8/iTnGEeq62piAAHtRKd6wOcJwQPy5RAwIAjyWThWGAApWA5YrFIkZa+bJ7vYJARri8uevEBP6Td4tUTty6RJsBACy/jkW+aeL88vemIpoefVf/8+hTSg/CQ6wpZifdJdDUUHgZZmo="
      },
      {
        "value": "te6ccuEBAQEADgAcABjVMnbbAAAAAAAAMDkRbQJP"
      },
      {
        "value": "te6ccuECAwEAAQkAAKIBfgISAZz9bCinap+6c7eTfDZgllrnln8kh4WJMDktj2xgCFtAopyo79YwlyTNV0WPrkJUbfiPwPFJ3KwxR9KkhOouE4QCKamjF2SloBwAAAHKAAMBAdViAEEnePzvnrqta5YU7cinRN3z8ZRMnEoV9MC37fAb1kQDoO5rKAAAAAAAAAAAAAAAAAAAD4p+pQAAAAAAADA5Q7msoAgA7zuZAqJxsqAciTilI8/iTnGEeq62piAAHtRKd6wOcJwQPy5RAwIAjyWThWGAApWA5YrFIkZa+bJ7vYJARri8uevEBP6Td4tUTty6RJsBACy/jkW+aeL88vemIpoefVf/8+hTSg/CQ6wpZifdJdDUUGtul2o="
      }
    ];

  parseBocBase64(t[0].value); // cashback
  parseBocBase64(t[1].value); // token recieved, 41.25 SCALE
  parseBocBase64(t[2].value); // receive 41.25 SCALE

  parseBocBase64(t[3].value); // cashback
  parseBocBase64(t[4].value); // 1 STON to 1 jUSDT

  parseBocBase64(t[5].value); // cashback
  parseBocBase64(t[6].value); // 1 STON to 1 jUSDT

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

const { wallet, loading } = storeToRefs(store)

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
    <div v-if="wallet === undefined">
      <header class="bg-[#0F0F0F]">
            <AppConnectWallet />
        </header>
        <main class="bg-[#0F0F0F] h-screen">
        </main>
    </div>
    <div v-else>
      <header>

      </header>
      <main class="flex flex-col bg-[#0F0F0F] h-screen">
        <pre class="text-white-1">{{wallet}}</pre>
      <div class="flex flex-col justify-center mt-2">
        <input v-model="usdToSton" type="number" @keypress="isNumber" class="block w-full p-2 text-gray-900 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" />
        <button @click="swapJettons(jettons[0].addressMinterBouncable, jettons[1].addressMinterBouncable, (Number(usdToSton) * 1e6).toString())" class="text-white-1 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mt-1 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Swap jettons ({{usdToSton}} jUSDT -> STON)</button>
      </div>
      <div class="flex flex-col justify-center mt-2">
        <input v-model="stonToUsd" type="number" @keypress="isNumber" class="block w-full p-2 text-gray-900 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" />
        <button @click="swapJettons(jettons[1].addressMinterBouncable, jettons[0].addressMinterBouncable, new Coins(stonToUsd).toNano())" class="text-white-1 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mt-1 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Swap jettons ({{stonToUsd}} STON -> jUSDT)</button>
      </div>
      <div class="flex justify-center mt-1.5">
        <button @click="disconnect" class="w-full text-white-1 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mt-1 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Disconnect</button>
      </div>
      </main>
    </div>
  </div>
  <div v-else class="flex justify-center items-center h-screen bg-[#0F0F0F] text-white-1">
    loading wallet state...
  </div>
</template>

<style scoped>
.header {
  width: 87.5625rem;
  height: 3.4375rem;
  flex-shrink: 0;
}
</style>