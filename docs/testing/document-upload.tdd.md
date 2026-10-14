# 多格式知识库上传 TDD 证据

## Source plan

本轮没有单独的 plan 文件；用户旅程根据“Word、TXT、Markdown 文件也可以直接上传”推导。

## User journeys

- 作为用户，我想上传 TXT 或 Markdown 文件，让纯文本资料可以进入知识库并参与问答。
- 作为用户，我想上传 Word `.docx` 文件，让办公文档可以进入知识库并参与问答。
- 作为用户，我想上传不支持或没有正文的文件时得到明确错误，而不是产生空索引。

## RED / GREEN evidence

- RED：新增 `backend/test_document_parser.py` 后运行 `python -m unittest test_document_parser.py`，因缺少 `app.services.document_service` 产生预期 `ModuleNotFoundError`。
- GREEN：实现解析器、统一上传接口和前端格式选择后运行 `python -m unittest test_document_parser.py test_document_upload.py`，结果为 `Ran 9 tests ... OK`。
- Checkpoint：RED 测试提交 `d1b227c`；GREEN 实现提交 `ce2847b`。

## Test specification

| # | 保证内容 | 测试或命令 | 类型 | 结果 |
|---|---|---|---|---|
| 1 | UTF-8 TXT 会转换为第一页文本 | `test_document_parser.py:test_extracts_utf8_text_file` | 单元 | PASS |
| 2 | 带 BOM 的 Markdown 可以解析 | `test_document_parser.py:test_extracts_markdown_file_with_utf8_bom` | 单元 | PASS |
| 3 | DOCX 段落可以从 `word/document.xml` 提取 | `test_document_parser.py:test_extracts_docx_paragraphs` | 单元 | PASS |
| 4 | 空文档和未知扩展名会给出可读错误 | `test_document_parser.py` 对应两个用例 | 单元 | PASS |
| 5 | TXT 和 DOCX 上传会进入切片、Embedding 和索引流程 | `test_document_upload.py` | 集成（mock 外部索引） | PASS |
| 6 | 新 `/upload/document` 路由已注册 | `GET /openapi.json` | API 验证 | PASS |
| 7 | Vue 前端生产构建通过 | `npm run build -- --outDir .tmp-build-document` | 构建 | PASS |
| 8 | Python 源码可编译 | `python -m compileall -q app test_document_parser.py` | 语法 | PASS |

## Coverage and known gaps

当前虚拟环境没有安装 `coverage`（`python -m coverage --version` 返回 `No module named coverage`），本轮未生成覆盖率百分比；没有为了覆盖率检查擅自增加依赖。真实 DeepSeek、PostgreSQL 和前端代理链路此前已在本地环境验证通过；本报告中的上传集成测试使用 mock，避免测试资料写入用户知识库。
