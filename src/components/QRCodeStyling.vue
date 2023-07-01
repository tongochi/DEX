<template>
  <div id="qr-code" ref="qrCode"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import QRCodeStyling from 'qr-code-styling';
import { useWalletStore } from '../stores';

const { text } = defineProps<{ text: string }>()

const qrCode = ref(null);
let qrCodeInstance = null;

const store = useWalletStore();

onMounted(() => {
  qrCodeInstance = new QRCodeStyling({
    data: text.value,
    // Other QR code options...
  });
  qrCodeInstance.append(qrCode.value);
});

store.$subscribe((mutation, state) => {
  if (mutation.storeId === 'wallet' && mutation.type === 'direct') {
    qrCodeInstance.update({ data: state.connecting.link });
  }
});
</script>

<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
