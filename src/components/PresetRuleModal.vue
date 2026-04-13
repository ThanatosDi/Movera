<script setup lang="ts">
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { request } from '@/composables/useHttpService'
import type { PresetRule } from '@/schemas'
import { FileCode, Settings } from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { RoutersEnum } from '@/enums/RoutersEnum'

const { t } = useI18n()
const router = useRouter()

const props = defineProps<{
  open: boolean
  ruleType: 'parse' | 'regex'
  fieldType: 'src' | 'dst'
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'select': [pattern: string]
}>()

const rules = ref<PresetRule[]>([])
const isLoading = ref(false)

watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    isLoading.value = true
    try {
      rules.value = await request<PresetRule[]>(
        'GET',
        `/api/v1/preset-rules?rule_type=${props.ruleType}&field_type=${props.fieldType}`,
      )
    } catch {
      rules.value = []
    } finally {
      isLoading.value = false
    }
  }
})

function selectRule(rule: PresetRule) {
  emit('select', rule.pattern)
  emit('update:open', false)
}

function goToSettings() {
  emit('update:open', false)
  router.push(RoutersEnum.Setting)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <FileCode class="size-5" />
          {{ t('components.presetRuleModal.title') }}
        </DialogTitle>
        <DialogDescription>
          {{ ruleType.toUpperCase() }} / {{ fieldType.toUpperCase() }}
        </DialogDescription>
      </DialogHeader>

      <div v-if="isLoading" class="p-4 text-center text-muted-foreground">
        {{ t('common.loading') }}
      </div>

      <div v-else-if="rules.length === 0" class="p-6 text-center space-y-3">
        <p class="text-sm text-muted-foreground">{{ t('components.presetRuleModal.empty') }}</p>
        <Button variant="outline" size="sm" @click="goToSettings">
          <Settings class="size-4 mr-1" />
          {{ t('components.presetRuleModal.emptyHint') }}
        </Button>
      </div>

      <div v-else class="space-y-1 max-h-80 overflow-y-auto">
        <button
          v-for="rule in rules"
          :key="rule.id"
          class="w-full text-left p-3 rounded-md hover:bg-accent transition-colors border border-transparent hover:border-border"
          @click="selectRule(rule)"
        >
          <div class="font-medium text-sm">{{ rule.name }}</div>
          <div class="font-mono text-xs text-muted-foreground mt-1 truncate">{{ rule.pattern }}</div>
        </button>
      </div>
    </DialogContent>
  </Dialog>
</template>
