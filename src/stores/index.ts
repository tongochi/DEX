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
  };
  loading?: boolean;
  connectWalletModal?: boolean;
}

export const useWalletStore = defineStore('wallet', () => {
    const entity = ref<State['entity']>(undefined);
    const wallet = ref<State['wallet']>(undefined);
    const connecting = ref<State['connecting']>(undefined);
    const loading = ref<State['loading']>(localStorage.getItem('wallet') ? true : false);
    const showConnectWalletModal = ref<State['connectWalletModal']>(false);

    function setEntity(payload: TonConnect) {
      entity.value = payload;
    };

    function setWallet(payload?: ConnectedWalletFromAPI) {
      wallet.value = payload;
    };

    function setConnecting(payload: State['connecting']) {
      connecting.value = {
        ...payload
      };
    };

    function setLoading(payload: State['loading']) {
      loading.value = payload;
    };

    function setShowConnectWalletModal(payload: State['connectWalletModal']) {
      showConnectWalletModal.value = payload;
    };

    function showConnectWalletModalFn() {
      setShowConnectWalletModal(true);
    };

    function hideConnectWalletModalFn() {
      setShowConnectWalletModal(false);
      setConnecting({
        link: undefined,
      })
    };

    return {
      entity,
      wallet,
      connecting,
      loading,
      setEntity,
      setWallet,
      setConnecting,
      setLoading,
      showConnectWalletModal,
      showConnectWalletModalFn,
      hideConnectWalletModalFn,
    }
  });