import axios from 'axios'
import {
  addDemoDocument,
  answerDemoQuestion,
  createDemoWorkspace,
  deleteDemoDocument,
  deleteDemoProfile,
  getDemoReportContent,
  saveDemoProfile
} from './demo.js'

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'
const demoWorkspace = createDemoWorkspace()

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 90000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '网络请求失败'
    return Promise.reject(new Error(msg))
  }
)

export async function sendChatMessage(question) {
  if (DEMO_MODE) return answerDemoQuestion(question, demoWorkspace)
  return apiClient.post('/chat/', { question })
}

/**
 * 通过 SSE 接收回答。onChunk 会收到 content、sources、report_file 或 error。
 */
export async function sendChatMessageStream(question, onChunk, signal) {
  if (DEMO_MODE) {
    if (signal?.aborted) throw new DOMException('请求已取消', 'AbortError')
    const result = answerDemoQuestion(question, demoWorkspace)
    const chunks = result.content.match(/.{1,18}/gs) || [result.content]
    for (const chunk of chunks) {
      if (signal?.aborted) throw new DOMException('请求已取消', 'AbortError')
      await new Promise((resolve) => setTimeout(resolve, 24))
      onChunk?.({ content: chunk })
    }
    onChunk?.({ sources: result.sources, report_file: result.reportFile })
    return result
  }

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

  if (!res.body) {
    throw new Error('服务器没有返回流式响应')
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let metadata = {}

  const consume = (raw) => {
    if (!raw.startsWith('data:')) return false
    const payload = raw.slice(5).trim()
    if (payload === '[DONE]') return true

    const obj = JSON.parse(payload)
    if (obj.error) throw new Error(obj.error)
    metadata = { ...metadata, ...obj }
    onChunk?.(obj)
    return false
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() || ''

    for (const event of events) {
      if (consume(event)) return metadata
    }
  }

  if (buffer.trim()) consume(buffer.trim())
  return metadata
}

export async function uploadDocument(file, onProgress) {
  if (DEMO_MODE) {
    for (const progress of [25, 58, 82, 100]) {
      await new Promise((resolve) => setTimeout(resolve, 90))
      onProgress?.(progress)
    }
    return addDemoDocument(demoWorkspace, file?.name)
  }

  const formData = new FormData()
  formData.append('file', file)

  return apiClient.post('/upload/document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    }
  })
}

// 保留旧命名，避免其他页面或本地脚本升级时中断。
export const uploadPdf = uploadDocument

export async function listDocuments() {
  if (DEMO_MODE) return demoWorkspace.documents
  return apiClient.get('/documents')
}

export async function deleteDocument(filename) {
  if (DEMO_MODE) {
    if (!deleteDemoDocument(demoWorkspace, filename)) throw new Error('没有找到这份演示文档')
    return { filename, deleted_chunks: 0 }
  }
  return apiClient.delete(`/documents/${encodeURIComponent(filename)}`)
}

export async function getMemorySummary() {
  if (DEMO_MODE) return { profiles: demoWorkspace.profiles, events: demoWorkspace.events }
  return apiClient.get('/memory/summary')
}

export async function saveProfile(key, value) {
  if (DEMO_MODE) return saveDemoProfile(demoWorkspace, key, value)
  return apiClient.put(`/memory/profiles/${encodeURIComponent(key)}`, { value })
}

export async function deleteProfile(key) {
  if (DEMO_MODE) {
    if (!deleteDemoProfile(demoWorkspace, key)) throw new Error('没有找到这条演示记忆')
    return { key, deleted: true }
  }
  return apiClient.delete(`/memory/profiles/${encodeURIComponent(key)}`)
}

export function reportDownloadUrl(filename) {
  if (DEMO_MODE) {
    const content = getDemoReportContent(filename)
    return `data:text/markdown;charset=utf-8,${encodeURIComponent(content)}`
  }
  return `/api/reports/${encodeURIComponent(filename)}`
}

export async function genWeeklyReport() {
  return sendChatMessage('帮我生成本周周报')
}
