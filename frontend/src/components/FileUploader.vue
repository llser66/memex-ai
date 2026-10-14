<template>
  <div class="uploader-wrap">
    <div
      class="upload-dropzone"
      :class="{ 'is-dragging': isDragging, 'is-uploading': isUploading }"
      @click="triggerFileInput"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.docx,.txt,.md,.markdown,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/markdown"
        class="visually-hidden"
        @change="onFileChange"
      />

      <template v-if="!isUploading">
        <div class="upload-icon">↑</div>
        <div class="upload-title">拖入资料，或点击选择</div>
        <div class="upload-caption">PDF / Word / TXT / Markdown · 自动建立索引</div>
      </template>

      <template v-else>
        <div class="upload-icon spinning">◌</div>
        <div class="upload-title">正在建立索引</div>
        <div class="upload-caption">{{ uploadProgress }}% · 首次加载模型可能需要一点时间</div>
        <div class="progress-track">
          <div class="progress-value" :style="{ width: `${uploadProgress}%` }" />
        </div>
      </template>
    </div>

    <div v-if="uploadResult" class="upload-result">
      <span class="status-dot success" />
      <span>{{ uploadResult.filename }} 已加入知识库</span>
    </div>
    <div v-if="uploadError" class="upload-result error">
      <span class="status-dot danger" />
      <span>{{ uploadError }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useFileUpload } from '../composables/useFileUpload.js'

const emit = defineEmits(['uploaded', 'error'])
const fileInput = ref(null)
const isDragging = ref(false)

const {
  isUploading,
  uploadProgress,
  uploadResult,
  uploadError,
  handleUpload
} = useFileUpload()

function triggerFileInput() {
  fileInput.value?.click()
}

function openFilePicker() {
  triggerFileInput()
}

defineExpose({ openFilePicker })

async function upload(file) {
  if (!file) return
  const supportedExtensions = ['.pdf', '.docx', '.txt', '.md', '.markdown']
  const filename = file.name.toLowerCase()
  if (!supportedExtensions.some((extension) => filename.endsWith(extension))) {
    emit('error', new Error('支持 PDF、Word（.docx）、TXT 和 Markdown 文件。'))
    return
  }

  try {
    const result = await handleUpload(file)
    emit('uploaded', result)
  } catch (error) {
    emit('error', error)
  }
}

function onFileChange(event) {
  upload(event.target.files[0])
  event.target.value = ''
}

function onDrop(event) {
  isDragging.value = false
  upload(event.dataTransfer.files[0])
}
</script>
