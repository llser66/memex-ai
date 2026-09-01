<template>
  <div>
    <!-- 拖拽区域 -->
    <div
      class="border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors
             hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-gray-800/50"
      :class="isDragging
        ? 'border-blue-500 bg-blue-50 dark:bg-gray-800'
        : 'border-gray-300 dark:border-gray-600'"
      @click="triggerFileInput"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        class="hidden"
        @change="onFileChange"
      />

      <template v-if="!isUploading">
        <div class="text-3xl mb-2">📄</div>
        <div class="text-sm text-gray-600 dark:text-gray-300">
          点击或拖拽 PDF 文件到此处上传
        </div>
        <div class="text-xs text-gray-400 mt-1">上传后自动建立知识库索引</div>
      </template>

      <template v-else>
        <div class="py-2">
          <div class="text-sm text-blue-600 dark:text-blue-400 mb-2">
            上传中... {{ uploadProgress }}%
          </div>
          <div class="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-blue-500 rounded-full transition-all"
              :style="{ width: uploadProgress + '%' }"
            />
          </div>
        </div>
      </template>
    </div>

    <!-- 上传结果提示 -->
    <div
      v-if="uploadResult"
      class="mt-2 px-3 py-2 rounded-lg bg-green-50 dark:bg-green-900/30
             border border-green-200 dark:border-green-700 text-xs text-green-700 dark:text-green-300"
    >
      ✅ 上传成功：{{ uploadResult.filename }}
      <span v-if="uploadResult.chunk_count">
        （切分为 {{ uploadResult.chunk_count }} 块）
      </span>
    </div>

    <!-- 错误提示 -->
    <div
      v-if="uploadError"
      class="mt-2 px-3 py-2 rounded-lg bg-red-50 dark:bg-red-900/30
             border border-red-200 dark:border-red-700 text-xs text-red-600 dark:text-red-300"
    >
      ❌ {{ uploadError }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useFileUpload } from '../composables/useFileUpload'

const {
  isUploading,
  uploadProgress,
  uploadResult,
  uploadError,
  handleUpload
} = useFileUpload()

const fileInput = ref(null)
const isDragging = ref(false)

function triggerFileInput() {
  fileInput.value?.click()
}

function onFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    handleUpload(file)
  }
  event.target.value = ''
}

function onDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    handleUpload(file)
  }
}
</script>