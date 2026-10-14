import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi import HTTPException, UploadFile

from app.api import upload as upload_api


def make_docx_bytes(text: str) -> bytes:
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>
    </w:document>'''
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", xml)
    return buffer.getvalue()


class FakeCollection:
    def __init__(self):
        self.upserted = None

    def get(self, **_kwargs):
        return {"ids": [], "metadatas": []}

    def upsert(self, **kwargs):
        self.upserted = kwargs


class DocumentUploadTests(unittest.IsolatedAsyncioTestCase):
    async def upload(self, filename: str, content: bytes):
        with tempfile.TemporaryDirectory() as temp_dir:
            collection = FakeCollection()
            db = Mock()
            upload = UploadFile(filename=filename, file=io.BytesIO(content))
            with patch.object(upload_api, "UPLOAD_DIR", Path(temp_dir)), \
                    patch.object(upload_api, "collection", collection), \
                    patch.object(upload_api, "generate_embeddings", return_value=[[0.1]]), \
                    patch.object(upload_api, "SessionLocal", return_value=db), \
                    patch.object(upload_api, "add_event"):
                result = await upload_api._index_document(upload)

            return result, collection

    async def test_indexes_txt_document(self):
        result, collection = await self.upload("notes.txt", "项目记录".encode("utf-8"))

        self.assertEqual(result["format"], "txt")
        self.assertEqual(result["pages"], 1)
        self.assertEqual(collection.upserted["documents"], ["项目记录"])

    async def test_indexes_docx_document(self):
        result, collection = await self.upload("report.docx", make_docx_bytes("项目总结"))

        self.assertEqual(result["format"], "docx")
        self.assertIn("项目总结", collection.upserted["documents"][0])

    async def test_rejects_unsupported_extension(self):
        upload = UploadFile(filename="data.csv", file=io.BytesIO(b"a,b"))

        with self.assertRaisesRegex(HTTPException, "支持 PDF"):
            await upload_api._index_document(upload)


if __name__ == "__main__":
    unittest.main()
