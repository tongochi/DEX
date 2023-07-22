<script setup lang="ts">
import { ref} from 'vue';
import TonWeb from 'tonweb';
import { Router, ROUTER_REVISION, ROUTER_REVISION_ADDRESS } from '@ston-fi/sdk';
import { bytesToBase64 } from 'ton3-core/dist/utils/helpers';
import AppExtraButton from '../components/AppExtraButton.vue';
import { useModalsStore } from '../stores/modals';
import AppModal from '../components/AppModal.vue';
import { useJettonStore } from '../stores/jettons';
import { notify } from '@kyvg/vue3-notification';
import { useWalletStore } from '../stores/wallet';

const storeWallet = useWalletStore();
const storeModals = useModalsStore();
const storeJettons = useJettonStore();
const leftToken = ref('');

function isNumber(evt: any) {
      evt = (evt) ? evt : window.event;
      var charCode = (evt.which) ? evt.which : evt.keyCode;
      if ((charCode > 31 && (charCode < 48 || charCode > 57)) && charCode !== 46) {
        evt.preventDefault();;
      } else {
        return true;
      }
}

const swapJettons = async (leftJetton: string, rightJetton: string, amount: string) => {
  try {
      const WALLET_ADDRESS = storeWallet.wallet?.address.bounceable!; // YOUR WALLET ADDRESS

      const REFERRAL_ADDRESS = 'EQDsQeFKUlh8iFjF_7DyUA7j0Y6kvI4CFEXiU7Gd7qQgks-7'; // REFERRAL ADDRESS (OPTIONAL)

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

      notify({
              text: "Request for transaction sended now, checkout the wallet",
              group: 'custom-template-warning',
            });

      const result = await storeWallet.entity?.sendTransaction(transaction);

      console.log('Transaction was sent successfully', result);

      notify({
              text: "Transaction was sent successfully, wait for transfering token and get cashback",
              group: 'custom-template-success',
            });
  } catch (e) {
      console.error(e);

      notify({
              text: (e as any).toString(),
              group: 'custom-template-error',
            });
  }
}
</script>
<template>
            <div class="w-full mt-[5.31rem] mb-[1.25rem]">
          <div class="max-w-[28.1875rem] h-[19.1875rem] mx-auto">
            <div class="flex justify-between h-[3.75rem] items-center">
              <span class="text-[#CDFD51] text-[1.5625rem] tracking-[-0.0625rem] leading-[3.75rem] font-normal">
                Swap tokens
              </span>
              <div class="flex">
                <!-- class="mr-[1.44rem]" -->
                <button @click="storeJettons.leftTokenSwapToRightToken" :disabled="(storeJettons.leftToken === undefined && storeJettons.rightToken === undefined)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 19 19" fill="none">
                    <path d="M2.52065 3.29832L2.41498 3.41754L2.30233 3.30489L0.15 1.15256V6.975H5.97244L3.99452 4.99708L3.89671 4.89927L3.98629 4.79388C5.31552 3.22985 7.28238 2.225 9.5 2.225C13.47 2.225 16.6937 5.3992 16.7735 9.35H18.8488C18.7687 4.25477 14.6143 0.15 9.5 0.15C6.71725 0.15 4.2303 1.36949 2.52065 3.29832ZM15.0055 14.0029L15.1033 14.1007L15.0137 14.2061C13.6845 15.7702 11.7176 16.775 9.5 16.775C5.52997 16.775 2.30628 13.6008 2.22651 9.65H0.151178C0.231289 14.7452 4.38567 18.85 9.5 18.85C12.2791 18.85 14.7697 17.6305 16.4793 15.7017L16.585 15.5825L16.6977 15.6951L18.85 17.8474V12.025H13.0276L15.0055 14.0029Z" fill="#CDFD51" stroke="black" stroke-width="0.3"/>
                  </svg>
                </button>
                <!-- <svg xmlns="http://www.w3.org/2000/svg" width="28" height="21" viewBox="0 0 28 21" fill="none">
                  <path d="M1 4.1665H4.16667" stroke="#CDFD51" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M7.33333 7.33334C6.49347 7.33334 5.68802 6.99971 5.09415 6.40585C4.50028 5.81198 4.16665 5.00653 4.16665 4.16667C4.16665 3.32682 4.50028 2.52136 5.09415 1.9275C5.68802 1.33363 6.49347 1 7.33333 1C7.74918 1 8.16096 1.08191 8.54516 1.24105C8.92936 1.40019 9.27845 1.63344 9.5725 1.9275C9.86656 2.22155 10.0998 2.57064 10.259 2.95484C10.4181 3.33904 10.5 3.75082 10.5 4.16667C10.5 4.58253 10.4181 4.99431 10.259 5.37851C10.0998 5.7627 9.86656 6.1118 9.5725 6.40585C9.27845 6.6999 8.92936 6.93316 8.54516 7.0923C8.16096 7.25144 7.74918 7.33334 7.33333 7.33334Z" stroke="#CDFD51" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M10.5 4.16657L26.3334 4.1665" stroke="#CDFD51" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M26.3337 16.8333H23.167" stroke="#CDFD51" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19.9997 20.0001C20.8395 20.0001 21.645 19.6665 22.2389 19.0726C22.8327 18.4787 23.1664 17.6733 23.1664 16.8334C23.1664 15.9936 22.8327 15.1881 22.2389 14.5942C21.645 14.0004 20.8395 13.6667 19.9997 13.6667C19.1598 13.6667 18.3544 14.0004 17.7605 14.5942C17.1666 15.1881 16.833 15.9936 16.833 16.8334C16.833 17.6733 17.1666 18.4787 17.7605 19.0726C18.3544 19.6665 19.1598 20.0001 19.9997 20.0001Z" stroke="#CDFD51" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M16.8334 16.8333L1 16.8333" stroke="#CDFD51" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg> -->
              </div>
            </div>
            <div class="w-full mt-[0rem] mb-[1.25rem] flex justify-between">
              <div class="flex flex-col flex-1 cursor-pointer" @click="storeModals.showLeftSearchTokensModalOpen">
                  <span class="text-[0.875rem] text-[#797979] tracking-[-0.04375rem] leading-normal not-italic">
                    You sell
                  </span>
                  <div class="flex items-center mt-[0.25rem]">
                    <button class="text-[1.125rem] text-[#F9F9F9] tracking-[-0.05625rem] leading-normal not-italic">
                      {{ storeJettons.leftToken?.symbol ?? 'Select' }}
                    </button>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M10.6203 7.63804L5.04729 2.32804C4.9543 2.23939 4.83076 2.18994 4.70229 2.18994C4.57382 2.18994 4.45028 2.23939 4.35729 2.32804L4.35129 2.33404C4.30606 2.37701 4.27004 2.42874 4.24542 2.48607C4.22081 2.5434 4.20812 2.60514 4.20812 2.66754C4.20812 2.72993 4.22081 2.79167 4.24542 2.849C4.27004 2.90634 4.30606 2.95806 4.35129 3.00104L9.59929 8.00104L4.35129 12.999C4.30606 13.042 4.27004 13.0937 4.24542 13.1511C4.22081 13.2084 4.20812 13.2701 4.20812 13.3325C4.20812 13.3949 4.22081 13.4567 4.24542 13.514C4.27004 13.5713 4.30606 13.6231 4.35129 13.666L4.35729 13.672C4.45028 13.7607 4.57382 13.8101 4.70229 13.8101C4.83076 13.8101 4.9543 13.7607 5.04729 13.672L10.6203 8.36204C10.6693 8.31534 10.7083 8.25918 10.735 8.19695C10.7616 8.13472 10.7754 8.06773 10.7754 8.00004C10.7754 7.93234 10.7616 7.86535 10.735 7.80312C10.7083 7.7409 10.6693 7.68473 10.6203 7.63804Z" fill="white"/>
                    </svg>
                    <AppModal :show="storeModals.showLeftSearchTokensModal" :close="storeModals.showLeftSearchTokensModalHide">
                      <template #content>
                        <span class="text-[#CDFD51] text-left flex w-full pl-[30px] text-[1.5625rem] font-normal mt-[1rem]">
                          Select token
                        </span>
                        <template v-for="jetton in storeJettons.entity">
                          <button :class="`w-[calc(100%-26px-26px)] mx-auto h-[60px] rounded-[20px] bg-[#00000080] cursor-pointer mt-[16px] disabled:bg-black-1`" @click="() => {
                            if (storeJettons.rightToken?.symbol === jetton.symbol) {
                              storeJettons.rightTokenSet(undefined);
                            }
                            storeJettons.leftTokenSet(storeJettons.findJettonBySymbol(jetton.symbol));
                            storeModals.showLeftSearchTokensModalHide();
                          }">
                            <span class="text-white-1 flex justify-center items-center h-full">{{ jetton.symbol }}</span>
                          </button>
                        </template>
                      </template>
                    </AppModal>
                  </div>
                </div>
                <div>
                  <div class="flex flex-col flex-1 justify-end">
                    <div class="flex justify-end items-center">
                      <!-- <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="mr-[0.25rem]">
                        <path d="M11.4837 2.79045C11.4316 2.73784 11.3695 2.69612 11.3011 2.66771C11.2327 2.63931 11.1593 2.62479 11.0853 2.625H10.6875V1.6875C10.6873 1.53837 10.628 1.39539 10.5226 1.28994C10.4171 1.18448 10.2741 1.12517 10.125 1.125H2.03032C1.5913 1.12501 1.17027 1.29941 0.859839 1.60984C0.549408 1.92027 0.375006 2.3413 0.375 2.78032V9.21968C0.375006 9.6587 0.549408 10.0797 0.859839 10.3902C1.17027 10.7006 1.5913 10.875 2.03032 10.875H11.0631C11.2119 10.8747 11.3545 10.8156 11.4599 10.7106C11.5653 10.6055 11.6249 10.4631 11.6256 10.3143L11.6478 3.18942C11.6482 3.11537 11.634 3.04196 11.6058 2.97346C11.5776 2.90497 11.5361 2.84276 11.4837 2.79045ZM10.8762 10.125H2.03032C1.79021 10.125 1.55994 10.0296 1.39016 9.85984C1.22038 9.69006 1.125 9.45979 1.125 9.21968V2.78032C1.125 2.54021 1.22038 2.30994 1.39016 2.14016C1.55994 1.97038 1.79021 1.875 2.03032 1.875H9.9375V2.625H2.0625V3.375H10.8972L10.8762 10.125Z" fill="#797979"/>
                        <path d="M9.1875 6.1875H9.9375V6.9375H9.1875V6.1875Z" fill="#797979"/>
                      </svg>
                      <span class="text-[0.875rem] text-[#797979] text-right tracking-[-0.04375rem] leading-normal not-italic font-normal">
                      0
                      </span> -->
                    </div>
                    <div class="flex items-center mt-[0.25rem]">
                      <input v-model="leftToken" type="number" @keypress="isNumber" class="text-[1.5rem] text-[#F9F9F9] text-right tracking-[-0.075rem] leading-normal not-italic font-normal bg-transparent w-full caret-white border-none focus:outline-none" :disabled="(storeJettons.leftToken === undefined && storeJettons.rightToken === undefined)" autofocus />
                    </div>
                    </div>
                  </div>
                <div>
              </div>
            </div>
            <div class="w-full mt-[0.81rem] mb-[0.94rem] h-[0.0625rem] bg-[#797979]"></div>
            <div class="w-full mt-[0rem] mb-[1.25rem] flex justify-between" >
              <div class="flex flex-col flex-1 cursor-pointer" @click="storeModals.showRightSearchTokensModalOpen">
                  <span class="text-[0.875rem] text-[#797979] tracking-[-0.04375rem] leading-normal not-italic">
                    You receive
                  </span>
                  <AppModal :show="storeModals.showRightSearchTokensModal" :close="storeModals.showRightSearchTokensModalHide">
                      <template #content>
                        <span class="text-[#CDFD51] text-left flex w-full pl-[30px] text-[1.5625rem] font-normal mt-[1rem]">
                          Select token
                        </span>
                        <template v-for="jetton in storeJettons.entity">
                          <button :class="`w-[calc(100%-26px-26px)] mx-auto h-[60px] rounded-[20px] bg-[#00000080] cursor-pointer mt-[16px] disabled:bg-black-1`" @click="() => {
                            if (storeJettons.leftToken?.symbol === jetton.symbol) {
                              storeJettons.leftTokenSet(undefined);
                            }
                            storeJettons.rightTokenSet(storeJettons.findJettonBySymbol(jetton.symbol));
                            storeModals.showRightSearchTokensModalHide();
                          }">
                            <span class="text-white-1 flex justify-center items-center h-full">{{ jetton.symbol }}</span>
                          </button>
                        </template>
                      </template>
                  </AppModal>
                  <div class="flex items-center mt-[0.25rem]">
                    <span class="text-[1.125rem] text-[#F9F9F9] tracking-[-0.05625rem] leading-normal not-italic">
                      {{ storeJettons.rightToken?.symbol ?? 'Select' }}
                    </span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M10.6203 7.63804L5.04729 2.32804C4.9543 2.23939 4.83076 2.18994 4.70229 2.18994C4.57382 2.18994 4.45028 2.23939 4.35729 2.32804L4.35129 2.33404C4.30606 2.37701 4.27004 2.42874 4.24542 2.48607C4.22081 2.5434 4.20812 2.60514 4.20812 2.66754C4.20812 2.72993 4.22081 2.79167 4.24542 2.849C4.27004 2.90634 4.30606 2.95806 4.35129 3.00104L9.59929 8.00104L4.35129 12.999C4.30606 13.042 4.27004 13.0937 4.24542 13.1511C4.22081 13.2084 4.20812 13.2701 4.20812 13.3325C4.20812 13.3949 4.22081 13.4567 4.24542 13.514C4.27004 13.5713 4.30606 13.6231 4.35129 13.666L4.35729 13.672C4.45028 13.7607 4.57382 13.8101 4.70229 13.8101C4.83076 13.8101 4.9543 13.7607 5.04729 13.672L10.6203 8.36204C10.6693 8.31534 10.7083 8.25918 10.735 8.19695C10.7616 8.13472 10.7754 8.06773 10.7754 8.00004C10.7754 7.93234 10.7616 7.86535 10.735 7.80312C10.7083 7.7409 10.6693 7.68473 10.6203 7.63804Z" fill="white"/>
                    </svg>
                  </div>
                </div>
                <div>
                  <div class="flex flex-col flex-1 justify-end">
                    <div class="flex justify-end items-center">
                      <!-- <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="mr-[0.25rem]">
                        <path d="M11.4837 2.79045C11.4316 2.73784 11.3695 2.69612 11.3011 2.66771C11.2327 2.63931 11.1593 2.62479 11.0853 2.625H10.6875V1.6875C10.6873 1.53837 10.628 1.39539 10.5226 1.28994C10.4171 1.18448 10.2741 1.12517 10.125 1.125H2.03032C1.5913 1.12501 1.17027 1.29941 0.859839 1.60984C0.549408 1.92027 0.375006 2.3413 0.375 2.78032V9.21968C0.375006 9.6587 0.549408 10.0797 0.859839 10.3902C1.17027 10.7006 1.5913 10.875 2.03032 10.875H11.0631C11.2119 10.8747 11.3545 10.8156 11.4599 10.7106C11.5653 10.6055 11.6249 10.4631 11.6256 10.3143L11.6478 3.18942C11.6482 3.11537 11.634 3.04196 11.6058 2.97346C11.5776 2.90497 11.5361 2.84276 11.4837 2.79045ZM10.8762 10.125H2.03032C1.79021 10.125 1.55994 10.0296 1.39016 9.85984C1.22038 9.69006 1.125 9.45979 1.125 9.21968V2.78032C1.125 2.54021 1.22038 2.30994 1.39016 2.14016C1.55994 1.97038 1.79021 1.875 2.03032 1.875H9.9375V2.625H2.0625V3.375H10.8972L10.8762 10.125Z" fill="#797979"/>
                        <path d="M9.1875 6.1875H9.9375V6.9375H9.1875V6.1875Z" fill="#797979"/>
                      </svg>
                      <span class="text-[0.875rem] text-[#797979] text-right tracking-[-0.04375rem] leading-normal not-italic font-normal">
                      0
                      </span> -->
                    </div>
                    <div class="flex items-center mt-[0.25rem]">
                      <!-- <span class="text-[1.5rem] text-[#F9F9F9] text-right tracking-[-0.075rem] leading-normal not-italic font-normal">
                        0.00
                      </span> -->
                      </div>
                    </div>
                  </div>
                <div>
              </div>
            </div>
            <AppExtraButton :text="(storeJettons.leftToken !== undefined && storeJettons.rightToken !== undefined) ? 'Swap' : 'Select tokens' " width="max-w-[450px] w-full" height="h-[61px]" @click="swapJettons(storeJettons.leftToken?.addressMinterBouncable!, storeJettons.rightToken?.addressMinterBouncable!, (Number(leftToken) * (10 ** storeJettons.leftToken?.decimals!)).toString())" :disabled="(storeJettons.leftToken === undefined && storeJettons.rightToken === undefined)" />
          </div>
        </div>
</template>
