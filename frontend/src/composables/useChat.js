import { ref } from 'vue'
import { sendChatMessage, sendChatMessageStream } from '../api/index.js'

/**
 * 聊天逻辑组合式函数
 * 管理消息列表、输入、发送状态，并提供发送消息方法
 */
export function useChat() {
  const messages = ref([])
  const input = ref('')
  const loading = ref(false)

  /**
   * 添加一条消息
   * @param {string} role - 'user' 或 'assistant'
   * @param {string} content - 消息文本
   * @param {Array} sources - 来源信息（仅助手消息可能需要）
   */
  function addMessage(role, content, sources = []) {
    messages.value.push({
      role,
      content,
      sources,
      streaming: false
    })
  }

  /**
   * 发送消息（优先使用流式，失败则回退普通接口）
   */
  async function sendMessage() {
    const question = input.value.trim()
    if (!question || loading.value) return

    // 添加用户消息
    addMessage('user', question)
    input.value = ''
    loading.value = true

    // 添加一个空的助手消息，用于流式更新
    addMessage('assistant', '', [])
    const assistantMsg = messages.value[messages.value.length - 1]
    assistantMsg.streaming = true

    try {
      // 尝试流式接收
      await sendChatMessageStream(question, (chunk) => {
        // chunk 可能是 { content: "..." } 或直接字符串，根据后端返回调整
        if (chunk && chunk.content) {
          assistantMsg.content += chunk.content
        } else if (typeof chunk === 'string') {
          assistantMsg.content += chunk
        }
      })
      assistantMsg.streaming = false
    } catch (err) {
      // 流式失败，回退普通接口
      console.warn('流式请求失败，回退普通接口:', err)
      try {
        const res = await sendChatMessage(question)
        assistantMsg.content = res.answer || '抱歉，回答失败'
        assistantMsg.sources = res.sources || []
        assistantMsg.streaming = false
      } catch (err2) {
        assistantMsg.content = '抱歉，请求失败。请确认后端服务已启动。'
        assistantMsg.streaming = false
      }
    } finally {
      loading.value = false
    }
  }

  return {
    messages,
    input,
    loading,
    sendMessage
  }
}