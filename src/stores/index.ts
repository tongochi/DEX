import { TonConnect } from '@tonconnect/sdk';
import { defineStore } from 'pinia';
import { ref } from 'vue';
  
export interface Address {
  bounceable:     string;
  non_bounceable: string;
  raw:            string;
}

export interface ConnectedWalletFromAPI {
  address: Address;
  balance: number;
  status:  string;
}

type State = {
  entity?: TonConnect;
  wallet?: ConnectedWalletFromAPI;
  connecting?: {
    link?: string;
  }
}

export const useWalletStore = defineStore('wallet', () => {
    const entity = ref<State['entity']>(undefined);
    const wallet = ref<State['wallet']>(undefined);
    const connecting = ref<State['connecting']>(undefined);

    function setEntity(payload: TonConnect) {
      entity.value = payload;
    };

    function setWallet(payload: ConnectedWalletFromAPI) {
      wallet.value = payload;
    };

    function setConnecting(payload: State['connecting']) {
      connecting.value = {
        ...payload
      };
    };

    return {
      entity,
      wallet,
      connecting,
      setEntity,
      setWallet,
      setConnecting,
    }
  });