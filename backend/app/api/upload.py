"""文档上传与知识库索引 API。"""

import hashlib
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.database.chroma import collection
from app.database.session import SessionLocal
from app.services.chunk_service import split_pages
from app.services.embed_service import generate_embeddings
from app.services.memory_service import add_event
from app.services.document_service import (
    SUPPORTED_DOCUMENT_EXTENSIONS,
    DocumentParseError,
    extract_document_pages,
)


router = APIRouter(
    prefix="/upload",
    tags=["文件上传"]
)


BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "data" / "files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def _safe_filename(filename: str | None) -> str:
    safe_name = Path(filename or "").name
    if not safe_name or safe_name in {".", ".."}:
        raise HTTPException(status_code=400, detail="文件名无效。")
    return safe_name


async def _index_document(
    file: UploadFile,
    allowed_extensions: set[str] | frozenset[str] = SUPPORTED_DOCUMENT_EXTENSIONS,
):
    filename = _safe_filename(file.filename)
    extension = Path(filename).suffix.lower()
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="目前只支持 PDF、Word（.docx）、TXT 和 Markdown 文件。",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空。")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="文件不能超过 20 MB。")

    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(content)

    try:
        pages = extract_document_pages(file_path)
    except DocumentParseError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunks = split_pages(pages, source=filename)
    if not chunks:
        raise HTTPException(status_code=400, detail="文档中没有可索引的文本。扫描件需要先进行 OCR。")

    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    vectors = generate_embeddings(texts)

    # 同名文件视为重新索引，先删除旧片段，避免重复检索结果。
    existing = collection.get(
        where={"source": filename},
        include=["metadatas"],
    )
    old_ids = existing.get("ids") or []
    if old_ids:
        collection.delete(ids=old_ids)

    content_hash = hashlib.sha256(content).hexdigest()[:20]
    source_hash = hashlib.sha256(filename.encode("utf-8")).hexdigest()[:8]
    ids = [f"{content_hash}_{source_hash}_{index}" for index in range(len(texts))]
    collection.upsert(
        documents=texts,
        embeddings=vectors,
        metadatas=metadatas,
        ids=ids,
    )

    db = SessionLocal()
    try:
        add_event(
            db=db,
            event_type="upload_document",
            description=f"用户上传了文档：{filename}",
            related_doc=filename,
        )
    finally:
        db.close()

    return {
        "filename": filename,
        "message": "文档上传成功，知识库已更新。",
        "format": extension.lstrip("."),
        "pages": len(pages),
        "chunks": len(chunks),
        # 保留兼容字段，避免旧前端显示异常。
        "chunk_count": len(chunks),
    }


@router.post("/document")
async def upload_document(file: UploadFile = File(...)):
    return await _index_document(file)


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """兼容旧客户端的 PDF 上传入口。"""
    return await _index_document(file, allowed_extensions={".pdf"})
