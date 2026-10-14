<template>
  <section class="sidebar-section document-section">
    <div class="section-heading">
      <div>
        <span class="eyebrow">Knowledge base</span>
        <h2>知识库</h2>
      </div>
      <span class="count-badge">{{ documents.length }}</span>
    </div>

    <div v-if="loading" class="list-placeholder">正在同步文档…</div>
    <div v-else-if="!documents.length" class="list-placeholder">
      还没有文档，上传第一份 PDF 开始建立记忆。
    </div>
    <div v-else class="document-list">
      <div v-for="document in documents" :key="document.filename" class="document-item">
        <div class="document-icon">{{ getDocumentType(document.filename) }}</div>
        <div class="document-info">
          <div class="document-name" :title="document.filename">{{ document.filename }}</div>
          <div class="document-meta">{{ document.pages }} 页 · {{ document.chunks }} 个片段</div>
        </div>
        <button
          class="icon-button danger-on-hover"
          title="从知识库删除"
          :disabled="deleting === document.filename"
          @click="emit('delete', document.filename)"
        >
          {{ deleting === document.filename ? '…' : '×' }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  documents: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  deleting: { type: String, default: '' }
})

const emit = defineEmits(['delete'])

function getDocumentType(filename) {
  const extension = filename?.split('.').pop()?.toUpperCase()
  return extension || 'DOC'
}
</script>
