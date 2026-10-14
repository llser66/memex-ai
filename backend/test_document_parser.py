import tempfile
import unittest
import zipfile
from pathlib import Path

from app.services.document_service import DocumentParseError, extract_document_pages


class DocumentParserTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extracts_utf8_text_file(self):
        path = self.root / "notes.txt"
        path.write_text("第一行\n第二行", encoding="utf-8")

        pages = extract_document_pages(path)

        self.assertEqual(pages, [{"page": 1, "text": "第一行\n第二行"}])

    def test_extracts_markdown_file_with_utf8_bom(self):
        path = self.root / "readme.md"
        path.write_bytes("# 项目\n\n内容".encode("utf-8-sig"))

        pages = extract_document_pages(path)

        self.assertEqual(pages[0]["page"], 1)
        self.assertIn("# 项目", pages[0]["text"])
        self.assertIn("内容", pages[0]["text"])

    def test_extracts_docx_paragraphs(self):
        path = self.root / "report.docx"
        document_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body>
            <w:p><w:r><w:t>项目总结</w:t></w:r></w:p>
            <w:p><w:r><w:t>这是第二段。</w:t></w:r></w:p>
          </w:body>
        </w:document>"""
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", document_xml)

        pages = extract_document_pages(path)

        self.assertEqual(pages[0]["page"], 1)
        self.assertIn("项目总结", pages[0]["text"])
        self.assertIn("这是第二段。", pages[0]["text"])

    def test_rejects_legacy_doc_format_with_actionable_message(self):
        path = self.root / "legacy.doc"
        path.write_bytes(b"legacy word binary")

        with self.assertRaisesRegex(DocumentParseError, "另存为 .docx"):
            extract_document_pages(path)

    def test_rejects_empty_text_document(self):
        path = self.root / "empty.txt"
        path.write_bytes(b"\xef\xbb\xbf  \n")

        with self.assertRaisesRegex(DocumentParseError, "没有可索引的文本"):
            extract_document_pages(path)

    def test_rejects_unknown_extension(self):
        path = self.root / "data.csv"
        path.write_text("a,b", encoding="utf-8")

        with self.assertRaisesRegex(DocumentParseError, "不支持"):
            extract_document_pages(path)


if __name__ == "__main__":
    unittest.main()
