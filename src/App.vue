<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner';
import { toastPosition, toastDuration } from '@/stores/sonnerStore'; // 一個全域 ref
import { RouterView } from 'vue-router';
import 'vue-sonner/style.css';

</script>

<template>
  <RouterView />
  <Toaster
    :duration="toastDuration"
    richColors
    :position="toastPosition"
  />
</template>
