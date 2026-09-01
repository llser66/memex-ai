import axios from 'axios'

// 创建 axios 实例，基础路径为 /api，由 vite 代理到后端
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 60000,             // 60秒超时，生成回答可能较慢
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器：统一处理错误
apiClient.interceptors.response.use(
  (response) => response.data,   // 直接返回 response.data，方便调用
  (error) => {
    // 提取后端返回的 detail 或错误消息
    const msg = error.response?.data?.detail || error.message || '网络请求失败'
    return Promise.reject(new Error(msg))
  }
)

/**
 * 普通聊天接口（一次性返回完整回答）
 * @param {string} question
 * @returns {Promise} { answer, sources, question }
 */
export async function sendChatMessage(question) {
  return apiClient.post('/chat/', { question })
}

/**
 * 流式聊天接口（SSE）
 * @param {string} question - 用户问题
 * @param {function} onChunk - 回调函数，接收解析后的 JSON 对象（如 {content: "..."}）
 * @param {AbortSignal} [signal] - 可选的取消信号
 */
export async function sendChatMessageStream(question, onChunk, signal) {
  const res = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
    signal
  })

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}))
    throw new Error(errData.detail || `HTTP ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (!line.startsWith('data:')) continue
      const raw = line.slice(5).trim()
      if (raw === '[DONE]') return

      try {
        const obj = JSON.parse(raw)
        onChunk(obj)
      } catch (e) {
        // 忽略解析异常，继续处理后续数据
      }
    }
  }
}

/**
 * 上传 PDF 文件
 * @param {File} file - 用户选择的 PDF 文件
 * @param {function} [onProgress] - 上传进度回调，接收 0-100 的整数
 * @returns {Promise} 后端返回的上传结果
 */
export async function uploadPdf(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient.post('/upload/pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
  })
}

/**
 * 一键生成周报（走 Agent 的工具节点）
 * @returns {Promise} 包含周报生成结果
 */
export async function genWeeklyReport() {
  return apiClient.post('/chat/', { question: '帮我生成本周周报' })
}