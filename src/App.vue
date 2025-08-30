<script setup lang="js">
import { Toaster } from '@/components/ui/sonner';
import { RouterView } from 'vue-router';
import 'vue-sonner/style.css';
</script>

<template>
  <RouterView />
  <Toaster richColors/>
</template>