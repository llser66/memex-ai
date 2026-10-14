<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ 'is-open': sidebarOpen }">
      <div class="sidebar-brand">
        <div class="brand-mark">M</div>
        <div>
          <div class="brand-name">Memex</div>
          <div class="brand-caption">个人工作记忆</div>
        </div>
        <button class="mobile-close" aria-label="关闭侧边栏" @click="sidebarOpen = false">×</button>
      </div>

      <button class="new-chat-button" @click="clearConversation">
        <span class="new-chat-icon">＋</span>
        新建对话
        <span class="shortcut-hint">⌘ K</span>
      </button>

      <div class="sidebar-scroll">
        <div class="workspace-card">
          <div class="workspace-icon">✦</div>
          <div>
            <div class="workspace-label">当前工作区</div>
            <div class="workspace-name">我的工作记忆</div>
          </div>
          <span class="live-indicator" title="服务状态正常" />
        </div>

        <div class="sidebar-label">添加资料</div>
        <FileUploader ref="uploaderRef" @uploaded="handleUploaded" @error="handleUploadError" />

        <DocumentList
          :documents="documents"
          :loading="documentsLoading"
          :deleting="deletingDocument"
          @delete="removeDocument"
        />

        <MemoryPanel
          :profiles="memory.profiles"
          :events="memory.events"
          :saving="memorySaving"
          @save-profile="saveMemory"
          @delete-profile="removeMemory"
        />
      </div>

      <div class="sidebar-footer">
        <span class="status-dot success" />
        <span>本地工作区已连接</span>
        <span class="footer-version">v0.2</span>
      </div>
    </aside>

    <main class="main-panel">
      <header class="main-header">
        <div class="header-left">
          <button class="mobile-menu" aria-label="打开侧边栏" @click="sidebarOpen = true">☰</button>
          <div>
            <div class="header-eyebrow">WORK MEMORY / 01</div>
            <h1>和你的资料对话</h1>
          </div>
        </div>
        <div class="header-actions">
          <div class="sync-state"><span class="status-dot success" />知识库已同步</div>
          <button class="header-icon-button" title="清空当前对话" @click="clearConversation">↺</button>
        </div>
      </header>

      <section ref="messagesContainer" class="chat-area">
        <div v-if="messages.length === 0" class="welcome-view">
          <div class="welcome-glow" />
          <div class="welcome-kicker"><span /> YOUR PRIVATE KNOWLEDGE LAYER</div>
          <h2>把散落的资料，<br /><em>变成可对话的工作记忆。</em></h2>
          <p class="welcome-description">
            上传你的简历、项目文档或工作记录。Memex 会记住上下文，
            在你需要的时候给出有依据的回答。
          </p>
          <div class="welcome-actions">
            <button class="primary-button" @click="openUploader">
              <span>↑</span> 上传第一份 PDF
            </button>
            <button class="secondary-button" @click="quickAsk('我的资料里有哪些 AI 项目？')">
              先问一个问题 <span>→</span>
            </button>
          </div>

          <div class="prompt-grid">
            <button class="prompt-card" @click="quickAsk('我的资料里有哪些 AI 项目？')">
              <span class="prompt-icon lavender">⌁</span>
              <span><strong>探索你的资料</strong><small>找到项目、技能和经历</small></span>
              <span class="prompt-arrow">↗</span>
            </button>
            <button class="prompt-card" @click="quickAsk('帮我生成本周周报')">
              <span class="prompt-icon peach">✎</span>
              <span><strong>整理本周工作</strong><small>生成一份结构化周报</small></span>
              <span class="prompt-arrow">↗</span>
            </button>
            <button class="prompt-card" @click="quickAsk('我最近上传过什么文件？')">
              <span class="prompt-icon mint">◷</span>
              <span><strong>回顾最近活动</strong><small>看看知识库发生了什么</small></span>
              <span class="prompt-arrow">↗</span>
            </button>
          </div>
        </div>

        <div v-else class="messages-container">
          <div class="conversation-start">
            <span class="conversation-line" />
            <span>本次对话</span>
            <span class="conversation-line" />
          </div>
          <ChatMessage
            v-for="(message, index) in messages"
            :key="message.id || index"
            :role="message.role"
            :content="message.content"
            :sources="message.sources"
            :report-file="message.reportFile"
            :streaming="message.streaming"
          />
        </div>
      </section>

      <footer class="composer-area">
        <div class="quick-actions">
          <button @click="quickAsk('帮我生成本周周报')"><span>✎</span> 生成周报</button>
          <button @click="quickAsk('我最近上传过什么文件？')"><span>◷</span> 最近活动</button>
          <button @click="quickAsk('总结我的个人工作背景')"><span>✦</span> 总结我的背景</button>
        </div>
        <div class="composer-box" :class="{ focused: inputFocused }">
          <textarea
            v-model="input"
            rows="1"
            placeholder="问问你的工作记忆…"
            :disabled="loading"
            @focus="inputFocused = true"
            @blur="inputFocused = false"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="composer-bottom">
            <span class="composer-hint">Enter 发送 · Shift + Enter 换行</span>
            <button class="send-button" :disabled="loading || !input.trim()" @click="sendMessage">
              <span v-if="!loading">发送 <b>↗</b></span>
              <span v-else class="send-loading">●●●</span>
            </button>
          </div>
        </div>
        <div class="composer-disclaimer">Memex AI 会基于你的资料回答，重要信息请自行核实。</div>
      </footer>
    </main>

    <transition name="toast">
      <div v-if="toast.message" class="toast" :class="{ error: toast.error }">
        <span>{{ toast.error ? '!' : '✓' }}</span>{{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import ChatMessage from './components/ChatMessage.vue'
import DocumentList from './components/DocumentList.vue'
import FileUploader from './components/FileUploader.vue'
import MemoryPanel from './components/MemoryPanel.vue'
import {
  deleteDocument,
  deleteProfile,
  getMemorySummary,
  listDocuments,
  saveProfile,
  sendChatMessage,
  sendChatMessageStream
} from './api/index.js'

const STORAGE_KEY = 'memex-conversation-v1'

const messages = ref(loadConversation())
const input = ref('')
const loading = ref(false)
const inputFocused = ref(false)
const sidebarOpen = ref(false)
const uploaderRef = ref(null)
const messagesContainer = ref(null)
const documents = ref([])
const documentsLoading = ref(false)
const deletingDocument = ref('')
const memory = ref({ profiles: [], events: [] })
const memorySaving = ref(false)
const toast = ref({ message: '', error: false })
let toastTimer

function loadConversation() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(saved) ? saved : []
  } catch {
    return []
  }
}

watch(messages, (value) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value.slice(-80)))
  } catch {
    // 浏览器存储不可用时仍然保留当前会话。
  }
}, { deep: true })

function showToast(message, error = false) {
  toast.value = { message, error }
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = { message: '', error: false }
  }, 3600)
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function refreshDocuments() {
  documentsLoading.value = true
  try {
    documents.value = await listDocuments()
  } catch (error) {
    showToast(`知识库同步失败：${error.message}`, true)
  } finally {
    documentsLoading.value = false
  }
}

async function refreshMemory() {
  try {
    memory.value = await getMemorySummary()
  } catch (error) {
    showToast(`记忆同步失败：${error.message}`, true)
  }
}

async function loadWorkspace() {
  await Promise.all([refreshDocuments(), refreshMemory()])
}

function openUploader() {
  uploaderRef.value?.openFilePicker()
}

function handleUploaded(result) {
  const chunkCount = result.chunks ?? result.chunk_count ?? 0
  messages.value.push({
    id: `upload-${Date.now()}`,
    role: 'assistant',
    content: `已收录 **${result.filename}**。${result.pages || 0} 页内容被切分为 ${chunkCount} 个片段，现在可以直接向它提问。`,
    sources: [],
    reportFile: '',
    streaming: false
  })
  sidebarOpen.value = false
  showToast(`${result.filename} 已加入知识库`)
  refreshDocuments()
  refreshMemory()
  scrollToBottom()
}

function handleUploadError(error) {
  showToast(error?.message || '上传失败，请重试。', true)
}

function quickAsk(question) {
  if (loading.value) return
  input.value = question
  sendMessage()
}

async function sendMessage() {
  const question = input.value.trim()
  if (!question || loading.value) return

  messages.value.push({ id: `user-${Date.now()}`, role: 'user', content: question })
  input.value = ''
  loading.value = true
  messages.value.push({
    id: `assistant-${Date.now()}`,
    role: 'assistant',
    content: '',
    sources: [],
    reportFile: '',
    streaming: true
  })
  const assistantMessage = messages.value[messages.value.length - 1]
  await scrollToBottom()

  try {
    const streamResult = await sendChatMessageStream(question, (chunk) => {
      if (chunk.content) assistantMessage.content += chunk.content
      if (chunk.sources) assistantMessage.sources = chunk.sources
      if (chunk.report_file) assistantMessage.reportFile = chunk.report_file
      scrollToBottom()
    })

    if (streamResult?.sources) assistantMessage.sources = streamResult.sources
    if (streamResult?.report_file) assistantMessage.reportFile = streamResult.report_file
    if (!assistantMessage.content.trim()) throw new Error('流式接口没有返回内容')
    assistantMessage.streaming = false
  } catch (streamError) {
    // 流式接口不可用时保留可靠的普通接口兜底。
    try {
      const result = await sendChatMessage(question)
      assistantMessage.content = result.answer || '抱歉，没有生成回答。'
      assistantMessage.sources = result.sources || []
      assistantMessage.reportFile = result.report_file || ''
      assistantMessage.streaming = false
    } catch (error) {
      assistantMessage.content = `暂时无法完成回答：${error.message || streamError.message}`
      assistantMessage.streaming = false
      showToast('请求失败，请检查后端服务和 DeepSeek 配置。', true)
    }
  } finally {
    loading.value = false
    sidebarOpen.value = false
    await scrollToBottom()
    refreshMemory()
  }
}

function clearConversation() {
  messages.value = []
  input.value = ''
  sidebarOpen.value = false
  showToast('已新建一个空白对话')
}

async function removeDocument(filename) {
  if (!window.confirm(`确定要删除“${filename}”及其知识库索引吗？`)) return
  deletingDocument.value = filename
  try {
    await deleteDocument(filename)
    showToast(`${filename} 已从知识库移除`)
    await refreshDocuments()
    await refreshMemory()
  } catch (error) {
    showToast(`删除失败：${error.message}`, true)
  } finally {
    deletingDocument.value = ''
  }
}

async function saveMemory({ key, value }) {
  if (!key || !value) return
  memorySaving.value = true
  try {
    await saveProfile(key, value)
    await refreshMemory()
    showToast(`已保存记忆：${key}`)
  } catch (error) {
    showToast(`记忆保存失败：${error.message}`, true)
  } finally {
    memorySaving.value = false
  }
}

async function removeMemory(key) {
  if (!window.confirm(`确定删除“${key}”这条记忆吗？`)) return
  try {
    await deleteProfile(key)
    await refreshMemory()
    showToast(`已删除记忆：${key}`)
  } catch (error) {
    showToast(`记忆删除失败：${error.message}`, true)
  }
}

onMounted(() => {
  loadWorkspace()
  scrollToBottom()
})
</script>
