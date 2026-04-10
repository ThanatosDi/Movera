<script setup lang="ts">
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps<{
  taskName: string
  disabled: boolean
}>()

const emit = defineEmits<{
  (e: 'confirm'): void
}>()

const handleConfirm = () => {
  emit('confirm')
}
</script>

<template>
  <AlertDialog>
    <AlertDialogTrigger as-child>
      <Button
        :disabled="disabled"
        variant="destructive"
        size="sm"
        class="dark:bg-red-500 dark:hover:bg-red-600 text-white font-bold"
      >
        <Trash2 class="size-4 mr-2" />
        {{ t('common.delete') }}
      </Button>
    </AlertDialogTrigger>
    <AlertDialogContent class="bg-background text-foreground border border-border">
      <AlertDialogHeader>
        <AlertDialogTitle>{{ t('taskDetailView.deleteDialogTitle') }}</AlertDialogTitle>
        <AlertDialogDescription class="text-current">
          {{ t('taskDetailView.deleteDialogDesc', { taskName }) }}
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel class="bg-background text-foreground border dark:border-foreground">{{
          t('common.cancel') }}
        </AlertDialogCancel>
        <AlertDialogAction
          class="bg-green-400 hover:bg-green-800 text-black"
          @click="handleConfirm"
        >{{ t('common.continue') }}</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
