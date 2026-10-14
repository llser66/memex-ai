<template>
  <article class="message-row" :class="role">
    <div class="message-avatar" :class="role">
      {{ role === 'user' ? '你' : 'M' }}
    </div>

    <div class="message-content">
      <div class="message-label">{{ role === 'user' ? '你' : 'Memex AI' }}</div>
      <div class="message-bubble" :class="{ pending: streaming && !content }">
        <div v-if="content" class="message-text" v-html="rendered" />
        <div v-else-if="streaming" class="thinking-state">
          <span class="thinking-orb" />
          正在检索你的工作记忆
        </div>
        <div v-else class="message-text muted">没有收到回答。</div>
      </div>

      <div v-if="sources?.length" class="source-strip">
        <div class="source-title">依据来源</div>
        <div class="source-list">
          <span v-for="(source, index) in sources" :key="`${source.source}-${index}`" class="source-chip">
            <span class="source-chip-mark">↗</span>
            {{ source.source }} · 第 {{ source.page }} 页
          </span>
        </div>
      </div>

      <a v-if="reportFile" class="report-link" :href="reportDownloadUrl(reportFile)" download>
        <span class="report-link-icon">↓</span>
        下载 {{ reportFile }}
      </a>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { reportDownloadUrl } from '../api/index.js'

const props = defineProps({
  role: { type: String, default: 'assistant' },
  content: { type: String, default: '' },
  sources: { type: Array, default: () => [] },
  reportFile: { type: String, default: '' },
  streaming: { type: Boolean, default: false }
})

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

const rendered = computed(() => {
  if (!props.content) return ''
  return escapeHtml(props.content)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/^- (.+)$/gm, '<span class="md-list-item">• $1</span>')
    .replace(/\n/g, '<br>')
})
</script>
