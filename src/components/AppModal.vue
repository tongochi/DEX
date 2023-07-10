<script lang="ts" setup>
import {
    TransitionRoot,
    TransitionChild,
    Dialog,
    DialogPanel,
} from '@headlessui/vue'
import { useWalletStore } from '../stores';

const store = useWalletStore()
</script>

<template>
    <TransitionRoot appear :show="store.showConnectWalletModal" as="template">
      <Dialog as="div" @close="store.hideConnectWalletModalFn" class="relative z-10">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>
  
        <div class="fixed inset-0 overflow-y-auto bg-black-5/80">
          <div
            class="flex min-h-full items-center justify-center p-4 text-center"
          >
            <TransitionChild
              as="template"
              enter="duration-300 ease-out"
              enter-from="opacity-0"
              enter-to="opacity-100"
              leave="duration-200 ease-in"
              leave-from="opacity-100"
              leave-to="opacity-0"
            >
              <DialogPanel
                class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all bg-transparent"
              >
                <div class="relative">
                    <svg xmlns="http://www.w3.org/2000/svg" class="max-h-[532px] max-w-[416px]" viewBox="0 0 416 532" fill="none">
                        <path d="M0.5 512V52.2843C0.5 47.1125 2.55446 42.1526 6.21142 38.4957L38.4957 6.21142C42.1526 2.55446 47.1125 0.5 52.2843 0.5H396C406.77 0.5 415.5 9.23045 415.5 20V476.418C415.5 481.181 413.757 485.779 410.6 489.345L379.095 524.927C375.394 529.107 370.078 531.5 364.495 531.5H20C9.23044 531.5 0.5 522.77 0.5 512Z" fill="#232323" stroke="#CDFD51"/>
                    </svg>
                    <div class="mt-[19px] absolute max-h-[532px] max-w-[416px] flex flex-col justify-start items-center top-0 right-0 left-0 bottom-0">
                        <slot name="content"></slot>
                    </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </template>
  