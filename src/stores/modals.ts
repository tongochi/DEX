import { defineStore } from "pinia";
import { ref } from "vue";
import { useWalletStore } from "./wallet";

type State = {
  connectWalletModal?: boolean;
  showSearchTokensModal?: boolean;
};

export const useModalsStore = defineStore("modals", () => {
  const showConnectWalletModal = ref<State["connectWalletModal"]>(false);
  const showSearchTokensModal = ref<State["connectWalletModal"]>(false);

  function setShowConnectWalletModal(payload: State["connectWalletModal"]) {
    showConnectWalletModal.value = payload;
  }

  function showConnectWalletModalFn() {
    setShowConnectWalletModal(true);
  }

  function hideConnectWalletModalFn() {
    setShowConnectWalletModal(false);
    useWalletStore().setConnecting({
      link: undefined,
    });
  }

  function setShowSearchTokensModal(payload: State["showSearchTokensModal"]) {
    showSearchTokensModal.value = payload;
  }

  function showSearchTokensModalFn() {
    setShowSearchTokensModal(true);
  }

  function hideSearchTokensModalFn() {
    setShowSearchTokensModal(false);
  }

  return {
    showConnectWalletModal,
    showConnectWalletModalFn,
    hideConnectWalletModalFn,
    showSearchTokensModal,
    setShowSearchTokensModal,
    showSearchTokensModalFn,
    hideSearchTokensModalFn,
  };
});
