<script setup>
import RegexPreview from '@/components/RegexPreview.vue';
import { Button } from '@/components/ui/button';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { toTypedSchema } from '@vee-validate/zod';
import { Plus } from 'lucide-vue-next';
import { useForm } from 'vee-validate';
import { ref } from 'vue';
import * as z from 'zod';

// 表單驗證 schema
const formSchema = toTypedSchema(z.object({
  TaskName: z.string()
    .min(1, '任務名稱為必填欄位')
    .min(2, '任務名稱至少需要 2 個字符')
    .max(50, '任務名稱不能超過 50 個字符')
    .regex(/^[a-zA-Z0-9\u4e00-\u9fa5_\-\s]+$/, '任務名稱只能包含字母、數字、中文、底線、連字號和空格'),

  FileNameInclude: z.string()
    .min(1, '檔案名稱包含為必填欄位')
    .min(1, '請輸入檔案名稱關鍵字')
    .max(100, '檔案名稱關鍵字不能超過 100 個字符'),

  MoveTo: z.string()
    .min(1, '移動至為必填欄位')
    .min(3, '路徑至少需要 3 個字符')
    .max(500, '路徑不能超過 500 個字符')
    .regex(/^[^\<\>\:\"\|\?\*]+$/, '路徑包含無效字符'),

  SrcFilenameRegex: z.string()
    .optional()
    .refine((val) => {
      if (!val) return true; // 可選欄位
      try {
        new RegExp(val);
        return true;
      } catch {
        return false;
      }
    }, '正規表達式格式無效'),

  DstFilenameRegex: z.string()
    .optional()
}))

const form = useForm({
  validationSchema: formSchema,
  initialValues: {
    TaskName: '',
    FileNameInclude: '',
    MoveTo: '',
    SrcFilenameRegex: '',
    DstFilenameRegex: ''
  }
})

// 正規表達式相關的響應式變數
const srcRegex = ref('')
const dstRegex = ref('')

const onSubmit = form.handleSubmit((values) => {
  console.log('Form submitted!', values)
  // 這裡可以添加提交到後端的邏輯
  alert('任務創建成功！\n' + JSON.stringify(values, null, 2))
}, (errors) => {
  console.log('Form validation failed:', errors)
  // 滾動到第一個錯誤欄位
  const firstErrorField = Object.keys(errors)[0]
  if (firstErrorField) {
    const element = document.querySelector(`[name="${firstErrorField}"]`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      element.focus()
    }
  }
})

// 處理正規表達式更新
const updateSrcRegex = (value) => {
  srcRegex.value = value
  form.setFieldValue('SrcFilenameRegex', value)
}

const updateDstRegex = (value) => {
  dstRegex.value = value
  form.setFieldValue('DstFilenameRegex', value)
}
</script>
<template>
  <main class="flex-1 flex flex-col p-4 space-y-4 overflow-auto min-h-0">
    <div class="pt-2 pb-2 col-span-1 col-start-1">
      <h1 class="text-2xl">建立任務</h1>
    </div>
    <div class="bg-gray-800 p-4 rounded-md">
      <form
        @submit="onSubmit"
        class="text-white text-lg flex flex-col gap-6"
      >
        <FormField
          v-slot="{ componentField }"
          name="TaskName"
        >
          <FormItem>
            <FormLabel class="text-lg">
              任務名稱 <span class="text-red-500">*</span>
            </FormLabel>
            <FormControl>
              <Input
                type="text"
                v-bind="componentField"
                class="rounded-full text-lg border-2"
                placeholder="輸入任務名稱"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField
          v-slot="{ componentField }"
          name="FileNameInclude"
        >
          <FormItem>
            <FormLabel class="text-lg">
              檔案名稱包含 <span class="text-red-500">*</span>
            </FormLabel>
            <FormControl>
              <Input
                type="text"
                v-bind="componentField"
                class="rounded-full text-lg border-2"
                placeholder="輸入檔案名稱關鍵字"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField
          v-slot="{ componentField }"
          name="MoveTo"
        >
          <FormItem>
            <FormLabel class="text-lg">
              移動至 <span class="text-red-500">*</span>
            </FormLabel>
            <FormControl>
              <Input
                type="text"
                v-bind="componentField"
                class="rounded-full text-lg border-2"
                placeholder="輸入目標資料夾路徑，例如：/Anime/動漫名稱"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField
          v-slot="{ componentField }"
          name="SrcFilenameRegex"
        >
          <FormItem>
            <FormLabel class="text-lg">
              檔案名稱正規表示法 <span class="text-gray-400 text-sm">(可選)</span>
            </FormLabel>
            <FormControl>
              <Input
                type="text"
                v-bind="componentField"
                @input="(e) => { updateSrcRegex(e.target.value); componentField['onInput'](e) }"
                class="rounded-full text-lg border-2"
                placeholder="例如: 公爵千金的家庭教師 - (\d{2})(v2)? .+\.mp4"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField
          v-slot="{ componentField }"
          name="DstFilenameRegex"
        >
          <FormItem>
            <FormLabel class="text-lg">
              重新命名正規表示法 <span class="text-gray-400 text-sm">(可選)</span>
            </FormLabel>
            <FormControl>
              <Input
                type="text"
                v-bind="componentField"
                @input="(e) => { updateDstRegex(e.target.value); componentField['onInput'](e) }"
                class="rounded-full text-lg border-2"
                placeholder="例如: 公爵千金的家庭教師 - S01E\\1 [1080P][WEB-DL][AAC AVC][CHT].mp4"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <!-- 正規表達式預覽組件 -->
        <RegexPreview
          :src-regex="srcRegex"
          :dst-regex="dstRegex"
          @update:src-regex="updateSrcRegex"
          @update:dst-regex="updateDstRegex"
        />

        <!-- 提交按鈕區域 -->
        <div class="mt-6 pt-4 border-t border-gray-600">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-400">
              <span class="text-red-500">*</span> 為必填欄位
            </div>
            <Button
              type="submit"
              :disabled="!form.meta.value.valid"
              :class="[
                'text-base font-bold py-2 px-4 rounded-full transition-all duration-200',
                form.meta.value.valid
                  ? 'bg-green-400 hover:bg-green-500 text-black'
                  : 'bg-gray-600 text-gray-400 cursor-not-allowed'
              ]"
            >
              <Plus class="w-4 h-4 mr-2" />
              {{ form.isSubmitting.value ? '創建中...' : '新增任務' }}
            </Button>
          </div>
        </div>
      </form>
    </div>

    <!-- 底部間距和頁腳 -->
    <div class="mt-8 pt-6 border-t border-gray-700">
      <div class="text-center text-gray-500 text-sm">
        <p>設定完成後，系統將自動監控指定資料夾並處理符合條件的檔案</p>
      </div>
    </div>

    <!-- 確保底部有足夠間距 -->
    <div class="pb-6"></div>
  </main>
</template>