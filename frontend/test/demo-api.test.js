import test from 'node:test'
import assert from 'node:assert/strict'

import {
  addDemoDocument,
  answerDemoQuestion,
  createDemoWorkspace,
  deleteDemoProfile,
  getDemoReportContent,
  saveDemoProfile
} from '../src/api/demo.js'

test('demo knowledge answers include a concrete source', () => {
  const workspace = createDemoWorkspace()
  const result = answerDemoQuestion('我的资料里有哪些 AI 项目？', workspace)

  assert.match(result.content, /Memex AI/)
  assert.equal(result.sources[0].source, 'AI 产品作品集.md')
  assert.equal(result.sources[0].page, 3)
})

test('demo weekly report provides a downloadable markdown report', () => {
  const workspace = createDemoWorkspace()
  const result = answerDemoQuestion('帮我生成本周周报', workspace)

  assert.equal(result.reportFile, 'memex-ai-weekly-report.md')
  assert.match(getDemoReportContent(result.reportFile), /本周工作周报/)
})

test('demo workspace supports document and profile interactions', () => {
  const workspace = createDemoWorkspace()
  const document = addDemoDocument(workspace, 'candidate-notes.txt')
  const profile = saveDemoProfile(workspace, '目标岗位', 'AI 产品工程师')

  assert.equal(document.filename, 'candidate-notes.txt')
  assert.ok(workspace.documents.some((item) => item.filename === 'candidate-notes.txt'))
  assert.equal(profile.value, 'AI 产品工程师')
  assert.ok(workspace.profiles.some((item) => item.key === '目标岗位'))

  assert.equal(deleteDemoProfile(workspace, '目标岗位'), true)
  assert.equal(workspace.profiles.some((item) => item.key === '目标岗位'), false)
})
