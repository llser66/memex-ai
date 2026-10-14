# Memex AI

Memex AI 是一个面向个人工作资料的 AI 记忆助手：上传 PDF、Word、TXT 或 Markdown 后建立本地向量知识库，通过对话检索资料、查看近期活动，并生成本周工作周报。

## 当前功能

- PDF、Word（`.docx`）、TXT 和 Markdown 上传、解析、文本切片和中文向量索引
- 基于 ChromaDB 的 RAG 问答，并返回文件与页码来源
- LangGraph Supervisor：知识库问答、个人记忆查询、周报工具三路分流
- PostgreSQL 保存用户画像与文档上传/删除事件
- 个人记忆查看、添加和删除
- 知识库文档列表、片段统计和删除
- DeepSeek 普通问答与 SSE 流式问答
- Markdown 周报生成与下载
- Vue 3 响应式聊天界面，支持多格式拖拽上传、来源展示和本地对话记录

## 环境要求

- Python 3.10+
- Node.js 18+
- Docker Desktop（用于 PostgreSQL）
- DeepSeek API Key

复制 `.env.example` 为 `.env`，并填入实际值：

```env
DEEPSEEK_API_KEY=your_key_here
POSTGRES_PASSWORD=change_this_local_password
```

如需修改数据库连接，可同时配置 `POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_HOST`、`POSTGRES_PORT` 和 `POSTGRES_DB`。

## 启动

先启动 PostgreSQL：

```bash
docker compose up -d postgres
```

启动后端：

```bash
cd backend
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

启动前端：

```bash
cd frontend
npm install
npm run dev
```

打开 Vite 输出的地址，默认是 `http://localhost:3000`。

## 主要接口

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/upload/document` | 上传 PDF、DOCX、TXT 或 Markdown 并建立索引 |
| POST | `/upload/pdf` | 兼容旧客户端的 PDF 上传入口 |
| GET | `/documents` | 查看已索引文档 |
| DELETE | `/documents/{filename}` | 删除文档及其索引 |
| POST | `/chat/` | 普通问答 |
| POST | `/chat/stream` | SSE 流式问答 |
| GET | `/memory/summary` | 查看画像和近期事件 |
| PUT | `/memory/profiles/{key}` | 保存一条用户画像 |
| GET | `/reports/{filename}` | 下载 Markdown 周报 |

## 数据位置

- 原始上传文件：`data/files`
- ChromaDB：`data/chroma`
- PostgreSQL 数据：`data/postgres`
- 生成的报告：`data/reports`

这是一个单用户本地工作区版本，当前没有登录、多租户和 OCR 能力；扫描型 PDF 需要先转成可复制文本。旧版二进制 `.doc` 文件请先在 Word 中另存为 `.docx`。
