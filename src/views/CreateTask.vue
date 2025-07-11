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
import { Plus } from 'lucide-vue-next';
import { useForm } from 'vee-validate';
import { ref } from 'vue';

const form = useForm({
  // validationSchema: formSchema,
})

// 正規表達式相關的響應式變數
const srcRegex = ref('')
const dstRegex = ref('')

const onSubmit = form.handleSubmit((values) => {
  console.log('Form submitted!', values)
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
      <form @submit="onSubmit" class="text-white text-lg flex flex-col gap-6">
        <FormField v-slot="{ componentField }" name="TaskName">
          <FormItem>
            <FormLabel class="text-lg">任務名稱</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField" class="rounded-full text-lg border-2 " />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="FileNameInclude">
          <FormItem>
            <FormLabel class="text-lg">檔案名稱包含</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField" class="rounded-full text-lg border-2 " />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="MoveTo">
          <FormItem>
            <FormLabel class="text-lg">移動至</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField" class="rounded-full text-lg border-2" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="SrcFilenameRegex">
          <FormItem>
            <FormLabel class="text-lg">檔案名稱正規表示法</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField"
                @input="(e) => { updateSrcRegex(e.target.value); componentField['onInput'](e) }"
                class="rounded-full text-lg border-2" placeholder="例如: 公爵千金的家庭教師 - (\d{2})(v2)? .+\.mp4" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="DstFilenameRegex">
          <FormItem>
            <FormLabel class="text-lg">重新命名正規表示法</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField"
                @input="(e) => { updateDstRegex(e.target.value); componentField['onInput'](e) }"
                class="rounded-full text-lg border-2"
                placeholder="例如: 公爵千金的家庭教師 - S01E\\1 [1080P][WEB-DL][AAC AVC][CHT].mp4" />
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
          <Button type="submit"
            class="bg-green-400 hover:bg-green-400 text-base text-black font-bold py-2 px-4 rounded-full">
            <Plus class="w-4 h-4 mr-2" />新增任務
          </Button>
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