"""将支持的资料格式统一转换为知识库可消费的分页文本。"""

from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from app.services.pdf_service import extract_pdf_pages


SUPPORTED_DOCUMENT_EXTENSIONS = frozenset({
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".markdown",
})

TEXT_DOCUMENT_EXTENSIONS = frozenset({".txt", ".md", ".markdown"})
WORD_DOCUMENT_EXTENSIONS = frozenset({".docx"})
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


class DocumentParseError(ValueError):
    """用户上传的文档无法转换为可索引文本。"""


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _decode_text(content: bytes) -> str:
    """按常见中文文档编码解码纯文本文件。"""
    for encoding in ("utf-8-sig", "utf-16", "gb18030", "cp1252"):
        try:
            return _normalize_text(content.decode(encoding))
        except UnicodeDecodeError:
            continue
    return _normalize_text(content.decode("utf-8", errors="replace"))


def _extract_docx_text(file_path: Path) -> str:
    try:
        with zipfile.ZipFile(file_path) as archive:
            document_xml = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile, OSError) as exc:
        raise DocumentParseError("DOCX 文件损坏或格式不完整，请重新保存后上传。") from exc

    try:
        root = ET.fromstring(document_xml)
    except ET.ParseError as exc:
        raise DocumentParseError("DOCX 文档内容无法解析，请重新保存后上传。") from exc

    paragraph_tag = f"{{{WORD_NAMESPACE}}}p"
    text_tag = f"{{{WORD_NAMESPACE}}}t"
    break_tags = {
        f"{{{WORD_NAMESPACE}}}br",
        f"{{{WORD_NAMESPACE}}}cr",
    }
    tab_tag = f"{{{WORD_NAMESPACE}}}tab"
    paragraphs = []

    for paragraph in root.iter(paragraph_tag):
        parts = []
        for node in paragraph.iter():
            if node.tag == text_tag:
                parts.append(node.text or "")
            elif node.tag in break_tags:
                parts.append("\n")
            elif node.tag == tab_tag:
                parts.append("\t")
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def _ensure_text(pages: list[dict]) -> list[dict]:
    if not any((page.get("text") or "").strip() for page in pages):
        raise DocumentParseError("文档中没有可索引的文本。扫描件需要先进行 OCR。")
    return pages


def extract_document_pages(file_path: Path) -> list[dict]:
    """提取 PDF、DOCX、TXT 和 Markdown，并统一返回 page/text 结构。"""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        try:
            return _ensure_text(extract_pdf_pages(file_path))
        except DocumentParseError:
            raise
        except Exception as exc:
            raise DocumentParseError(f"PDF 解析失败：{exc}") from exc

    if suffix in TEXT_DOCUMENT_EXTENSIONS:
        try:
            text = _decode_text(file_path.read_bytes())
        except OSError as exc:
            raise DocumentParseError("文本文件无法读取，请重新上传。") from exc
        return _ensure_text([{"page": 1, "text": text}])

    if suffix in WORD_DOCUMENT_EXTENSIONS:
        return _ensure_text([{"page": 1, "text": _extract_docx_text(file_path)}])

    if suffix == ".doc":
        raise DocumentParseError("旧版 .doc 文件暂不支持，请在 Word 中另存为 .docx 后再上传。")

    raise DocumentParseError("文件类型不支持，目前支持 PDF、Word（.docx）、TXT 和 Markdown 文件。")
