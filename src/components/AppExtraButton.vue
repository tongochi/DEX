<script lang="ts" setup>
defineProps<{ on_click?: () => void, text: string, width: string, height: string, color?: string, }>();
</script>

<template>
    <button :class="`flex ${width} ${height} justify-center items-center cursor-pointer ${color ?? 'bg-[#CDFD51]'} rounded-[1rem]`" @click="on_click">
        <span class="text-[#0F0E0E]">
          {{ text }}
        </span>
    </button>
</template>