<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { onMounted, watch } from 'vue';
import {TonConnect} from '@tonconnect/sdk';
import { ConnectedWalletFromAPI, useWalletStore } from './stores/wallet';
import AppConnectWallet from './components/AppConnectWallet.vue';
import AppExtraButton from './components/AppExtraButton.vue';
import { notify } from '@kyvg/vue3-notification';
import ky from 'ky';
import WebApp from '@twa-dev/sdk'
import useSWRV, { mutate as m } from 'swrv'
import { fetcher, coinsToNumber } from './utils';
import { gql } from 'graphql-request';
import { Spinner } from 'flowbite-vue'
import AppSwapForm from './components/AppSwapForm.vue';

const storeWallet = useWalletStore()

const gResponse = gql`
    query GetBalances($owner_wc: Int!, $owner_address: String!) {
      account: account_states(
        workchain: $owner_wc,
        address: $owner_address
      ) {
        balance: account_storage_balance_grams
      },

      balances: account_states(
        parsed_jetton_wallet_owner_address_workchain: $owner_wc,
        parsed_jetton_wallet_owner_address_address: $owner_address
      ) {
        minter_wc: parsed_jetton_wallet_jetton_address_workchain
        minter_address: parsed_jetton_wallet_jetton_address_address
        balance: parsed_jetton_wallet_balance
        decimals: parsed_jetton_content_decimals_value
      }
    }
  `;

export interface Balance {
    account:  Account[];
    balances: BalanceElement[];
}

export interface Account {
    balance: string;
}

export interface BalanceElement {
    minter_wc:      number;
    minter_address: string;
    balance:        string;
    decimals:       null;
}

// https://dton.io/graphql - default key
// ?getBalances - unique parameter on our client
const { data, error } = useSWRV('https://dton.io/graphql?getBalances', (...args: string[]) => {
  const [url] = args;

  return fetcher(url, '', {});
});
const castedData = data as unknown as Balance;

watch(
  () => storeWallet.wallet?.address.raw, 
  async () => {
    const splittedRaw = storeWallet.wallet?.address.raw.split(':');

    const r = await fetcher('https://dton.io/graphql?getBalances', gResponse, {
      "owner_wc": splittedRaw![0],
      "owner_address": splittedRaw![1].toUpperCase(),
    });

    m('https://dton.io/graphql?getBalances', r)
  }
);

const disconnect = async () => {
  if (storeWallet?.entity?.connected) {
      await storeWallet?.entity?.disconnect();
      storeWallet.setWallet(undefined);
      localStorage.removeItem('wallet');
  }
}

onMounted(async () => {
  WebApp.ready();
  WebApp.expand();

  const tonConnect = new TonConnect({
    manifestUrl: 'https://about.systemdesigndao.xyz/ton-connect.manifest.json',
  });

  storeWallet.setEntity(tonConnect);

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
            const { token } = await ky.post('https://ton-dapp-backend.systemdesigndao.xyz/ton-proof/checkProof', {
              body: JSON.stringify(obj),
            }).json() as { token: string };
            const data = await ky.get(`https://ton-dapp-backend.systemdesigndao.xyz/dapp/getAccountInfo?network=${obj.network}`, {
                    headers: {
                      Authorization: `Bearer ${token}`,
                      'Content-Type': 'application/json',
                    }
            }).json() as ConnectedWalletFromAPI;

            localStorage.setItem('wallet', JSON.stringify(data));

            storeWallet.setWallet(data);

            notify({
              text: "Connected the wallet",
              group: 'custom-template-success',
            });
          } catch (err) {
            console.error(err);
            notify({
              text: (err as any).toString(),
              group: 'custom-template-error',
            });
          }
					return;
				}

				console.error(tonProof.error);
			}
	});

  return unsubscribe;
})

watch(() => storeWallet?.entity?.connected, async () => {
  if (storeWallet?.entity?.connected === false) {
    storeWallet.entity.restoreConnection();
  }

  if (storeWallet?.entity?.connected === true) {
    const localWallet = localStorage.getItem('wallet');
    if (localWallet) {
      const data = JSON.parse(localWallet);
      storeWallet.setWallet(data);
      storeWallet.setLoading(false);
      notify({
        text: "Restored connection",
        group: 'custom-template-success',
      });
    }
  }
})

const { wallet, loading } = storeToRefs(storeWallet)
</script>

<template>
  <div v-if="loading === false">
    <div v-if="wallet === undefined">
        <main class="bg-[#0F0F0F] h-screen flex justify-center items-center">
          <AppConnectWallet />
        </main>
    </div>
    <div v-else>
      <header>

      </header>
      <main class="flex flex-col bg-[#0F0F0F] h-screen p-[1.25rem]">
        <div class="w-full flex justify-center">
          <div class="text-white-1" v-if="data === undefined"><spinner color="green" size="8" /></div>
            <div v-else>
                <div v-if="error === undefined"><span class="text-white-1">{{error}}</span></div>
                <div><span class="text-white-1">{{ coinsToNumber(castedData.account[0].balance, 9) }} 💎</span>
            </div>
          </div>
        </div>
      <AppSwapForm />
      <div class="flex justify-center mt-1.5">
        <AppExtraButton text="Disconnect" :on_click="disconnect" width="w-[220px]" height="h-[60px]" />
      </div>
      </main>
    </div>
  </div>
  <div v-else class="flex justify-center items-center h-screen bg-[#0F0F0F] text-white-1">
    loading wallet state...
  </div>
  <notifications
      group="custom-template-success"
      :duration="5000"
      position="top right"
    >
      <template #body="{ item }">
        <div class="absolute top-0 right-0 w-fit h-fit bg-[#68CD86] flex items-center justify-center p-1">
          <div class="text-center text-white-1 font-[0.8rem]">
            {{ item.text }}
          </div>
        </div>
      </template>
  </notifications>
  <notifications
      group="custom-template-error"
      :duration="5000"
      position="top right"
    >
      <template #body="{ item }">
        <div class="absolute top-0 right-0 w-fit h-fit bg-[#EB7767] flex items-center justify-center p-1">
          <div class="text-center text-white-1 font-[0.8rem]">
            {{ item.text }}
          </div>
        </div>
      </template>
  </notifications>
  <notifications
      group="custom-template-warning"
      :duration="5000"
      position="top right"
    >
      <template #body="{ item }">
        <div class="absolute top-0 right-0 w-fit h-fit bg-[#ebdc67] flex items-center justify-center p-1">
          <div class="text-center text-white-1 font-[0.8rem]">
            {{ item.text }}
          </div>
        </div>
      </template>
  </notifications>
</template>