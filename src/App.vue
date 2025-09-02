<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner';
import { toastPosition } from '@/stores/sonnerStore'; // 一個全域 ref
import { RouterView } from 'vue-router';
import 'vue-sonner/style.css';

</script>

<template>
  <RouterView />
  <Toaster
    :duration="10000"
    richColors
    :position="toastPosition"
  />
</template>
