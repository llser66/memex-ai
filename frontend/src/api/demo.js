const DEMO_NOW = '2026-10-14T09:00:00.000Z'

function source(source, page) {
  return { source, page }
}

export function createDemoWorkspace() {
  return {
    documents: [
      {
        filename: 'AI 产品作品集.md',
        chunks: 16,
        pages: 5,
        size: 18400,
        exists: true
      },
      {
        filename: '2026-Q3 工作记录.docx',
        chunks: 24,
        pages: 8,
        size: 42800,
        exists: true
      },
      {
        filename: 'Agent 研究笔记.pdf',
        chunks: 31,
        pages: 12,
        size: 96800,
        exists: true
      }
    ],
    profiles: [
      { key: '职业方向', value: 'AI 应用与 Agent 产品', updated_at: DEMO_NOW },
      { key: '工作偏好', value: '重视产品体验，也关注可落地的工程实现', updated_at: DEMO_NOW }
    ],
    events: [
      {
        id: 'demo-event-1',
        event_type: 'upload_document',
        description: '用户上传了文档：AI 产品作品集.md',
        related_doc: 'AI 产品作品集.md',
        created_at: DEMO_NOW
      },
      {
        id: 'demo-event-2',
        event_type: 'save_profile',
        description: '用户更新了个人记忆：职业方向',
        related_doc: null,
        created_at: DEMO_NOW
      }
    ],
    nextEventId: 3
  }
}

export function answerDemoQuestion(question, workspace) {
  const normalized = String(question || '').trim().toLowerCase()

  if (!normalized) {
    return {
      content: '试着问我一个和资料有关的问题，例如“我的资料里有哪些 AI 项目？”。',
      sources: [],
      reportFile: ''
    }
  }

  if (normalized.includes('周报')) {
    return {
      content: '# 本周工作周报\n\n## 本周完成\n- 完善 Memex AI 的多格式知识库上传流程。\n- 接通 RAG 问答、来源展示和 SSE 流式回答。\n- 补齐个人记忆、文档管理与报告下载链路。\n\n## 下一步\n- 继续优化在线 Demo 的展示和真实部署链路。',
      sources: [source('2026-Q3 工作记录.docx', 6)],
      reportFile: 'memex-ai-weekly-report.md'
    }
  }

  if (normalized.includes('最近') || normalized.includes('上传') || normalized.includes('文件')) {
    const names = workspace.documents.map((document) => `- ${document.filename}（${document.chunks} 个片段）`).join('\n')
    return {
      content: `当前知识库里有 ${workspace.documents.length} 份资料：\n${names}\n\n这些资料已经可以作为后续问答的检索上下文。`,
      sources: [source('AI 产品作品集.md', 1)],
      reportFile: ''
    }
  }

  if (normalized.includes('背景') || normalized.includes('技能') || normalized.includes('项目')) {
    return {
      content: '根据你的工作资料，你正在围绕 AI 产品、Agent 工作流和知识体验持续构建项目。当前最完整的实践是 Memex AI：它把多格式资料、RAG 问答、个人记忆和周报生成串成了一个可操作的工作区。',
      sources: [source('AI 产品作品集.md', 3), source('2026-Q3 工作记录.docx', 4)],
      reportFile: ''
    }
  }

  return {
    content: '我在你的资料里找到了一条相关上下文：Memex AI 的目标是把分散的工作资料整理成可检索、可追溯、可继续使用的个人工作记忆。你可以继续问我它的技术方案、项目进度或下一步计划。',
    sources: [source('AI 产品作品集.md', 3)],
    reportFile: ''
  }
}

export function createDemoDocument(filename) {
  const safeName = String(filename || '示例资料.md').split(/[\\/]/).pop() || '示例资料.md'
  const extension = safeName.split('.').pop()?.toLowerCase()
  const pageCount = extension === 'pdf' ? 6 : extension === 'docx' ? 8 : 4
  const chunkCount = extension === 'pdf' ? 18 : extension === 'docx' ? 22 : 12
  return {
    filename: safeName,
    chunks: chunkCount,
    pages: pageCount,
    size: 24000,
    exists: true
  }
}

export function addDemoDocument(workspace, filename) {
  const document = createDemoDocument(filename)
  workspace.documents = [
    ...workspace.documents.filter((item) => item.filename !== document.filename),
    document
  ]
  workspace.events.unshift({
    id: `demo-event-${workspace.nextEventId++}`,
    event_type: 'upload_document',
    description: `用户上传了文档：${document.filename}`,
    related_doc: document.filename,
    created_at: new Date().toISOString()
  })
  return document
}

export function deleteDemoDocument(workspace, filename) {
  const before = workspace.documents.length
  workspace.documents = workspace.documents.filter((document) => document.filename !== filename)
  if (workspace.documents.length === before) return false
  workspace.events.unshift({
    id: `demo-event-${workspace.nextEventId++}`,
    event_type: 'delete_document',
    description: `用户删除了文档：${filename}`,
    related_doc: filename,
    created_at: new Date().toISOString()
  })
  return true
}

export function saveDemoProfile(workspace, key, value) {
  const existing = workspace.profiles.find((profile) => profile.key === key)
  if (existing) {
    existing.value = value
    existing.updated_at = new Date().toISOString()
    return existing
  }

  const profile = { key, value, updated_at: new Date().toISOString() }
  workspace.profiles.unshift(profile)
  workspace.events.unshift({
    id: `demo-event-${workspace.nextEventId++}`,
    event_type: 'save_profile',
    description: `用户更新了个人记忆：${key}`,
    related_doc: null,
    created_at: profile.updated_at
  })
  return profile
}

export function deleteDemoProfile(workspace, key) {
  const before = workspace.profiles.length
  workspace.profiles = workspace.profiles.filter((profile) => profile.key !== key)
  return workspace.profiles.length !== before
}

export function getDemoReportContent(filename) {
  if (filename !== 'memex-ai-weekly-report.md') return ''
  return '# 本周工作周报\n\n## 本周完成\n- 完善 Memex AI 的多格式知识库上传流程。\n- 接通 RAG 问答、来源展示和 SSE 流式回答。\n- 补齐个人记忆、文档管理与报告下载链路。\n\n## 下一步\n- 继续优化在线 Demo 的展示和真实部署链路。\n'
}
