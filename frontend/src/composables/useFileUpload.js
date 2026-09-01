import { ref } from 'vue'
import { uploadPdf } from '../api/index.js'

export function useFileUpload() {
  const uploading = ref(false)
  const uploadSuccess = ref('')
  const uploadError = ref('')

  async function handleUpload(file) {
    if (!file) return
    uploading.value = true
    uploadSuccess.value = ''
    uploadError.value = ''
    try {
      const res = await uploadPdf(file)
      uploadSuccess.value = res.filename
      return res
    } catch (err) {
      uploadError.value = '上传失败，请重试'
      console.error(err)
      throw err
    } finally {
      uploading.value = false
    }
  }

  return {
    uploading,
    uploadSuccess,
    uploadError,
    handleUpload
  }
}