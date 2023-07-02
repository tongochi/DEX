<template>
  <div id="qr-code" ref="qrCode"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import QRCodeStyling from 'qr-code-styling';
import { useWalletStore } from '../stores';

const { text } = defineProps<{ text: string }>()

const qrCode = ref<null | HTMLElement>(null);
let qrCodeInstance: null | QRCodeStyling = null;

const store = useWalletStore();

onMounted(() => {
  qrCodeInstance = new QRCodeStyling({
    data: text,
  });
  qrCode.value && qrCodeInstance.append(qrCode.value);
});

store.$subscribe((mutation, state) => {
  if (mutation.storeId === 'wallet' && mutation.type === 'direct') {
    qrCodeInstance?.update({ data: state?.connecting?.link });
  }
});
</script>
