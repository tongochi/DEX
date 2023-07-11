<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { onMounted, watch } from 'vue'
import {TonConnect} from '@tonconnect/sdk'
import QRCodeStyling from './QRCodeStyling.vue';
import { ConnectedWalletFromAPI, useWalletStore } from '../stores/wallet'
import { useModalsStore } from '../stores/modals'
import { uintToHex } from 'ton3-core/dist/utils/helpers';
import { Address, BOC, Slice } from 'ton3-core';
import AppExtraButton from './AppExtraButton.vue'
import AppModal from './AppModal.vue'

const store = useWalletStore()
const storeModals = useModalsStore();

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

const { connecting } = storeToRefs(store)
</script>

<template>
  <div class="flex justify-center flex-col h-screen w-screen items-center">
    <AppExtraButton text="Connect wallet" :on_click="storeModals.showConnectWalletModalOpen" width="w-[217px]" height="h-[54px]" />
    <AppModal :show="storeModals.showConnectWalletModal" :close="storeModals.showConnectWalletModalHide">
      <template #content>
        <span class="text-[#CDFD51] text-left flex w-full pl-[30px] text-[1.5625rem] font-normal">
          Connect wallet
        </span>
        <div class="w-[calc(100%-26px-26px)] mx-auto h-[60px] rounded-[20px] bg-[#00000080] cursor-pointer mt-[32px]" @click="connect('tonkeeper')">
          <span class="text-white-1 flex justify-center items-center h-full">Connect tonkeeper</span>
        </div>
        <div class="w-[calc(100%-26px-26px)] mx-auto h-[60px] rounded-[20px] bg-[#00000080] mt-[18px] cursor-pointer" @click="connect('tonhub')">
          <span class="text-white-1 flex justify-center items-center h-full">Connect tonhub</span>
        </div>
        <div class="flex justify-center mt-4">
          <div v-if="connecting?.link" class="flex justify-center flex-col">
            <QRCodeStyling :text="connecting.link" />  
            <a class="mt-4 text-white-1 text-center" target="_blank" :href="connecting?.link">Or open with the link</a>
          </div>
        </div>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.header {
  width: 87.5625rem;
  height: 3.4375rem;
  flex-shrink: 0;
}
</style>