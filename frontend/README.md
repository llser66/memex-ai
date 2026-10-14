# Memex AI 前端

Vue 3 + Vite 单页应用。开发服务器默认运行在 `3000` 端口，并将 `/api` 请求代理到 `http://127.0.0.1:8000`。资料上传支持 PDF、Word（`.docx`）、TXT 和 Markdown。

## 公开 Demo

构建不连接真实后端的在线演示版：

```bash
VITE_DEMO_MODE=true npm run build -- --base=/memex-ai/
```

Demo 模式使用预置示例资料，并在浏览器内模拟问答、来源、记忆、文档上传和周报下载；不会把 DeepSeek API Key 或本地数据库暴露到浏览器。

```bash
npm install
npm run dev
```

生产构建：

```bash
npm run build
```
