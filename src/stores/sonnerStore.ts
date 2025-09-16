import { ref } from 'vue'

export const toastPosition = ref<'top-center' | 'bottom-right'>('bottom-right')
export const toastDuration = ref<number>(1200)