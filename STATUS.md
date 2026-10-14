# Memex AI 项目进度

## 当前目标

完成前端视觉与交互重设计，并补齐当前代码中已发现的未完成链路：流式问答、上传接口契约、拖拽上传、文档管理、记忆管理和周报下载。

## 已完成

- 完成 Vue 前端工作区式重设计：侧边栏、欢迎页、快捷提问、响应式移动布局、来源卡片、上传状态和本地对话记录。
- 接通真实 `/chat/stream` SSE 流式问答，并保留普通接口兜底。
- 修复 PDF 上传返回字段、同名重复索引、文件名安全校验、大小限制和空文本处理。
- 补充知识库文档列表/删除、个人记忆查看/保存/删除、周报下载接口。
- 修复拖拽上传组件和上传进度状态，周报结果可直接下载。
- 扩展知识库上传：支持 PDF、Word（`.docx`）、TXT、Markdown，并统一走自动解析、切片和向量索引；同名文件仍会重新索引。
- 增加数据库启动时建表、Embedding 模型按需加载、严格按本周筛选周报事件。
- 更新根 README、前端 README 和 `.env.example`。

## 实际检查

- `npm run build -- --outDir .tmp-build`：通过。
- Python AST 语法检查：29 个文件通过。
- 后端 venv 导入与 OpenAPI 检查：通过，新增接口均已注册。
- FastAPI 普通问答、SSE、文档列表、报告下载契约测试：通过（模型调用使用模拟响应，文档和报告使用本地现有数据）。
- Docker Compose 配置检查：通过（提供验证用 `POSTGRES_PASSWORD`）。
- `git diff --check`：通过，仅有 Git 的换行符提示。

## 当前问题与决定

- 采用现有技术栈，不新增 UI 框架或不必要依赖。
- 保持单用户本地工作区定位；本轮不扩展登录和多租户体系。
- 已完成真实 DeepSeek 最小请求验证：普通接口返回 HTTP 200 和 `OK`，并返回 3 条来源；DeepSeek key 配置有效。
- 本次启动实测前端 Vite 已在 `http://127.0.0.1:3000/` 返回 HTTP 200。
- 重启 Windows 后 Docker Engine 已恢复，`docker info` 返回 Server `29.5.3`，PostgreSQL 容器显示 `healthy`。
- 后端 `/health`、前端 `/api/documents` 和 `/api/memory/summary` 均已实测返回 HTTP 200；前端代理的 `/api/chat/stream` 返回 `text/event-stream` 并包含 `[DONE]`；旧 Docker 运行目录保留在本地备份中，未删除镜像、容器、卷或数据库。
- 多格式解析与上传单元/集成测试共 9 个通过，前端构建和 `/upload/document` OpenAPI 注册检查通过。
- 新增 `VITE_DEMO_MODE` 公开演示模式：预置知识库数据、模拟流式问答、来源展示、记忆管理、文档加入和 Markdown 周报下载。
- Demo 数据层测试 3 个通过；公开构建命令为 `VITE_DEMO_MODE=true npm run build -- --base=/memex-ai/`。

## 下一步

- 当前本地开发环境已启动并完成真实链路验收；公开 Demo 用于 HR 直接体验，真实后端仍保留在本地开发链路。TDD 证据见 `docs/testing/document-upload.tdd.md`。
