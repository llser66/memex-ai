<template>
  <div class="app-shell">
    <!-- 顶部导航 -->
    <header class="topbar">
      <div class="logo">
        <span class="logo-icon">🧠</span>
        <div>
          <h1>Memex AI</h1>
          <p class="subtitle">个人 AI 工作记忆助手</p>
        </div>
      </div>
      <button class="upload-btn" @click="triggerUpload" :disabled="uploading">
        <span v-if="!uploading">📄 上传 PDF</span>
        <span v-else>⏳ 上传中...</span>
      </button>
      <input
        type="file"
        accept=".pdf"
        ref="fileInput"
        style="display: none"
        @change="handleFileUpload"
      />
    </header>

    <!-- 主内容区 -->
    <main class="chat-area">
      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">✨</div>
        <h2>你好，我是 Memex AI</h2>
        <p>上传 PDF 文档建立知识库，或直接向我提问</p>
      </div>

      <!-- 消息列表 -->
      <div v-else class="messages-container" ref="messagesContainer">
        <ChatMessage
          v-for="(msg, idx) in messages"
          :key="idx"
          :role="msg.role"
          :content="msg.content"
          :sources="msg.sources"
          :streaming="msg.streaming"
        />
      </div>
    </main>

    <!-- 底部输入区 -->
    <footer class="input-area">
      <!-- 快捷操作按钮（始终显示） -->
      <div class="quick-actions">
        <button class="quick-btn" @click="quickAsk('帮我生成本周周报')">
          📝 生成周报
        </button>
        <button class="quick-btn" @click="quickAsk('我最近上传过什么文件？')">
          🕐 查看最近活动
        </button>
      </div>

      <div class="input-wrapper">
        <textarea
          v-model="input"
          @keydown.enter.exact.prevent="sendMessage"
          placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
          rows="1"
          class="message-input"
          :disabled="loading"
        ></textarea>
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="loading || !input.trim()"
        >
          <span v-if="!loading">发送</span>
          <span v-else>...</span>
        </button>
      </div>
      <p class="footer-hint">Memex AI 可能会出错，请核实重要信息</p>
    </footer>

    <!-- 上传成功提示 -->
    <div v-if="uploadSuccess" class="toast" @click="uploadSuccess = ''">
      ✅ {{ uploadSuccess }}
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import ChatMessage from './components/ChatMessage.vue'
import { sendChatMessageStream, sendChatMessage, uploadPdf } from './api/index.js'

const messages = ref([])
const input = ref('')
const loading = ref(false)
const uploading = ref(false)
const uploadSuccess = ref('')
const fileInput = ref(null)
const messagesContainer = ref(null)

// 自动滚动到底部
async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 快速提问
function quickAsk(q) {
  input.value = q
  sendMessage()
}

// 触发文件选择
function triggerUpload() {
  fileInput.value.click()
}

// 处理文件上传
async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  try {
    const res = await uploadPdf(file)
    uploadSuccess.value = `文件 "${res.filename}" 上传成功，已加入知识库`
    messages.value.push({
      role: 'assistant',
      content: `✅ 文档 **${res.filename}** 上传成功，共 ${res.chunk_count || '若干'} 个片段已存入知识库。现在你可以询问相关内容。`,
      sources: []
    })
    scrollToBottom()
  } catch (err) {
    uploadSuccess.value = '上传失败，请重试'
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}

// 发送消息
async function sendMessage() {
  const question = input.value.trim()
  if (!question || loading.value) return

  messages.value.push({ role: 'user', content: question })
  input.value = ''
  loading.value = true
  scrollToBottom()

  // 添加空的助手消息用于流式显示
  const assistantMsg = {
    role: 'assistant',
    content: '',
    sources: [],
    streaming: true
  }
  messages.value.push(assistantMsg)
  const assistantIndex = messages.value.length - 1

  try {
    await sendChatMessageStream(question, (chunk) => {
      if (chunk && chunk.content) {
        messages.value[assistantIndex].content += chunk.content
        scrollToBottom()
      }
    })
    messages.value[assistantIndex].streaming = false
  } catch (err) {
    // 流式失败回退普通接口
    try {
      const res = await sendChatMessage(question)
      messages.value[assistantIndex].content = res.answer || '抱歉，回答失败'
      messages.value[assistantIndex].sources = res.sources || []
      messages.value[assistantIndex].streaming = false
    } catch (err2) {
      messages.value[assistantIndex].content = '抱歉，请求失败。请确认后端服务已启动。'
      messages.value[assistantIndex].streaming = false
    }
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.app-shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(160deg, #0b0f17 0%, #111827 100%);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(17, 24, 39, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 2rem;
}

.logo h1 {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.upload-btn {
  background: var(--accent);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.upload-btn:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 12px;
}

.empty-icon {
  font-size: 4rem;
  animation: float 3s ease-in-out infinite;
}

.empty-state h2 {
  font-size: 1.5rem;
  font-weight: 600;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.messages-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-area {
  padding: 16px 24px;
  background: rgba(17, 24, 39, 0.9);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--border);
}

/* 快捷按钮区域 */
.quick-actions {
  max-width: 800px;
  margin: 0 auto 12px;
  display: flex;
  gap: 10px;
}

.quick-btn {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.quick-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 12px 18px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
  max-height: 150px;
}

.message-input:focus {
  border-color: var(--accent);
}

.send-btn {
  background: var(--accent);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  white-space: nowrap;
}

.send-btn:hover {
  background: var(--accent-hover);
}

.send-btn:disabled {
  background: #374151;
  cursor: not-allowed;
}

.footer-hint {
  text-align: center;
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-top: 8px;
}

.toast {
  position: fixed;
  top: 80px;
  right: 24px;
  background: #059669;
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 0.9rem;
  cursor: pointer;
  z-index: 100;
  animation: slideIn 0.3s ease;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
</style>