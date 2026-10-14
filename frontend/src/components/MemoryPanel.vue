<template>
  <section class="sidebar-section memory-section">
    <div class="section-heading">
      <div>
        <span class="eyebrow">Personal context</span>
        <h2>我的记忆</h2>
      </div>
      <button class="text-button" @click="showForm = !showForm">
        {{ showForm ? '收起' : '+ 添加' }}
      </button>
    </div>

    <form v-if="showForm" class="memory-form" @submit.prevent="save">
      <input v-model="keyInput" class="small-input" placeholder="名称，例如：职业" maxlength="100" />
      <input v-model="valueInput" class="small-input" placeholder="内容，例如：AI 应用工程师" maxlength="500" />
      <button class="small-primary-button" type="submit" :disabled="saving || !keyInput.trim() || !valueInput.trim()">
        {{ saving ? '保存中…' : '保存记忆' }}
      </button>
    </form>

    <div v-if="profiles.length" class="profile-list">
      <div v-for="profile in profiles" :key="profile.key" class="profile-row">
        <div>
          <span class="profile-key">{{ profile.key }}</span>
          <span class="profile-value">{{ profile.value }}</span>
        </div>
        <button class="icon-button danger-on-hover" title="删除记忆" @click="emit('delete-profile', profile.key)">×</button>
      </div>
    </div>
    <div v-else class="list-placeholder compact">添加几条关于自己的信息，让回答更贴合你的工作背景。</div>

    <div class="activity-block">
      <div class="activity-title">最近活动</div>
      <div v-if="events.length" class="activity-list">
        <div v-for="event in events.slice(0, 4)" :key="event.id" class="activity-row">
          <span class="activity-dot" />
          <div>
            <div class="activity-copy">{{ event.description }}</div>
            <div class="activity-time">{{ formatDate(event.created_at) }}</div>
          </div>
        </div>
      </div>
      <div v-else class="list-placeholder compact">上传文档或保存记忆后，这里会显示活动。</div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  profiles: { type: Array, default: () => [] },
  events: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false }
})

const emit = defineEmits(['save-profile', 'delete-profile'])
const showForm = ref(false)
const keyInput = ref('')
const valueInput = ref('')

function save() {
  emit('save-profile', { key: keyInput.value.trim(), value: valueInput.value.trim() })
  keyInput.value = ''
  valueInput.value = ''
  showForm.value = false
}

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>
