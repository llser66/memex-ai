<template>
  <div class="msg" :class="role">
    <div class="avatar">{{ role === 'user' ? '👤' : '🤖' }}</div>
    <div class="bubble">
      <div v-if="content" class="text" v-html="rendered"></div>
      <div v-else-if="streaming" class="typing">
        正在思考<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
      </div>
      <div v-if="sources && sources.length" class="sources">
        <span class="src-label">📚 来源</span>
        <span v-for="(s, i) in sources" :key="i" class="src-tag">
          {{ s.source }} · 第{{ s.page }}页
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  role: String,
  content: String,
  sources: Array,
  streaming: Boolean
})

// 简单的 Markdown 渲染（加粗、换行）
const rendered = computed(() => {
  if (!props.content) return ''
  return props.content
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
})
</script>

<style scoped>
.msg {
  display: flex;
  gap: 12px;
  animation: msgIn 0.3s ease;
}

.msg.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
  border: 1px solid var(--border);
}

.bubble {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  line-height: 1.6;
  font-size: 0.95rem;
}

.msg.user .bubble {
  background: var(--user-bubble);
  border-bottom-right-radius: 4px;
}

.msg.assistant .bubble {
  background: var(--assistant-bubble);
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
}

.text {
  word-break: break-word;
}

.typing {
  color: var(--text-secondary);
  font-style: italic;
}

.dot {
  animation: blink 1.4s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

.sources {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.src-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.src-tag {
  background: var(--bg-hover);
  font-size: 0.72rem;
  padding: 4px 10px;
  border-radius: 12px;
  color: var(--text-secondary);
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}
</style>