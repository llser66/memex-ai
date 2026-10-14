import { ref } from 'vue'
import { uploadDocument } from '../api/index.js'

export function useFileUpload() {
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const uploadResult = ref(null)
  const uploadError = ref('')

  async function handleUpload(file) {
    if (!file) return null

    uploading.value = true
    uploadProgress.value = 0
    uploadResult.value = null
    uploadError.value = ''

    try {
      const result = await uploadDocument(file, (progress) => {
        uploadProgress.value = progress
      })
      uploadProgress.value = 100
      uploadResult.value = result
      return result
    } catch (error) {
      uploadError.value = error.message || '上传失败，请重试。'
      throw error
    } finally {
      uploading.value = false
    }
  }

  return {
    uploading,
    // 兼容旧组件命名，同时提供语义更清晰的字段。
    isUploading: uploading,
    uploadProgress,
    uploadResult,
    uploadError,
    handleUpload
  }
}
