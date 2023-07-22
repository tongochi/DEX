<script setup lang="ts">
import { storeToRefs } from 'pinia';
import QRCodeStyling from './QRCodeStyling.vue';
import { useWalletStore } from '../stores/wallet';
import { useModalsStore } from '../stores/modals';
import AppExtraButton from './AppExtraButton.vue';
import AppModal from './AppModal.vue';

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
  const d = await postData('https://api.tongochi.org/dex/ton-proof/generatePayload');
  const { payload } = await d.json();

  const link = store.entity?.connect(walletConnectionSource[wallets], { tonProof: payload });

  store.setConnecting({
    link,
  });
  store.waitingForConnectSet(true);
}

const { connecting } = storeToRefs(store)
</script>

<template>
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
            <a class="my-4 text-white-1 text-center" target="_blank" :href="connecting?.link">Or open with the link</a>
          </div>
        </div>
      </template>
    </AppModal>
</template>

<style scoped>

</style>
