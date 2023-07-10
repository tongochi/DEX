<script lang="ts" setup>
defineProps<{ on_click: () => void, text: string }>();
</script>

<template>
    <div class="relative">
      <svg xmlns="http://www.w3.org/2000/svg" width="217" height="54" viewBox="0 0 217 54" fill="none">
        <path d="M217 36.2228V10C217 4.47715 212.523 0 207 0H22.2211C20.4233 0 18.6586 0.48471 17.113 1.40311L4.89183 8.66476C1.85893 10.4669 0 13.7337 0 17.2617V44C0 49.5228 4.47716 54 10 54H196.903C199.111 54 201.256 53.2695 203.005 51.9224L213.102 44.1452C215.56 42.252 217 39.3252 217 36.2228Z" fill="#CDFD51"/>
      </svg>
      <div class="flex absolute top-0 w-[217px] h-[54px] justify-center items-center cursor-pointer" @click="on_click">
        <span class="text-[#0F0E0E]">
          {{ text }}
        </span>
      </div>
    </div>
</template>