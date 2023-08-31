import { defineStore } from "pinia";
import { ref } from "vue";
import { useWalletStore } from "./wallet";

type State = {
  connectWalletModal?: boolean;
  showLeftSearchTokensModal?: boolean;
  showRightSearchTokensModal?: boolean;
};

export const useModalsStore = defineStore("modals", () => {
  const showConnectWalletModal = ref<State["connectWalletModal"]>(false);
  const showLeftSearchTokensModal =
    ref<State["showLeftSearchTokensModal"]>(false);
  const showRightSearchTokensModal =
    ref<State["showRightSearchTokensModal"]>(false);

  function showConnectWalletModalSet(payload: State["connectWalletModal"]) {
    showConnectWalletModal.value = payload;
  }

  function showConnectWalletModalOpen() {
    showConnectWalletModalSet(true);
  }

  function showConnectWalletModalHide() {
    showConnectWalletModalSet(false);
    useWalletStore().setConnecting({
      link: undefined,
    });
  }

  function showLeftSearchTokensModalSet(
    payload: State["showLeftSearchTokensModal"],
  ) {
    showLeftSearchTokensModal.value = payload;
  }

  function showLeftSearchTokensModalOpen() {
    showLeftSearchTokensModalSet(true);
  }

  function showLeftSearchTokensModalHide() {
    showLeftSearchTokensModalSet(false);
  }

  function showRightSearchTokensModalSet(
    payload: State["showRightSearchTokensModal"],
  ) {
    showRightSearchTokensModal.value = payload;
  }

  function showRightSearchTokensModalOpen() {
    showRightSearchTokensModalSet(true);
  }

  function showRightSearchTokensModalHide() {
    showRightSearchTokensModalSet(false);
  }

  return {
    showConnectWalletModal,
    showLeftSearchTokensModal,
    showRightSearchTokensModal,
    showConnectWalletModalSet,
    showConnectWalletModalOpen,
    showConnectWalletModalHide,
    showLeftSearchTokensModalSet,
    showLeftSearchTokensModalOpen,
    showLeftSearchTokensModalHide,
    showRightSearchTokensModalSet,
    showRightSearchTokensModalOpen,
    showRightSearchTokensModalHide,
  };
});
