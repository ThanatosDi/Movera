<script lang="ts" setup>
import { Button } from '@/components/ui/button';
import { RoutersEnum } from '@/enums/RoutersEnum';
import { Plus } from 'lucide-vue-next';
import { useI18n } from 'vue-i18n';


const { t } = useI18n()

</script>

<template>
  <!-- 新增任務按鈕 -->
  <div class="pt-2 pb-4 col-span-1 col-start-1">
    <RouterLink
      :to="RoutersEnum.CreateTask"
      class="text-gray-500 hover:text-gray-300 text-base"
    >
      <Button
        class="bg-green-400 hover:bg-green-500 text-base text-black font-bold py-2 px-4 rounded-full w-full transition-colors"
      >
        <Plus class="w-4 h-4 mr-2" />{{ t('components.sidebarTool.createTaskBtn') }}
      </Button>
    </RouterLink>
  </div>
</template>