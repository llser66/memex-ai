"""知识库文档列表和删除 API。"""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.database.chroma import collection
from app.database.session import SessionLocal
from app.services.memory_service import add_event


router = APIRouter(prefix="/documents", tags=["知识库"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "data" / "files"


def _safe_filename(filename: str) -> str:
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name or safe_name in {".", ".."}:
        raise HTTPException(status_code=400, detail="文件名无效。")
    return safe_name


@router.get("")
def list_documents():
    result = collection.get(include=["metadatas"])
    metadatas = result.get("metadatas") or []
    grouped = {}

    for metadata in metadatas:
        if not metadata:
            continue
        source = metadata.get("source")
        if not source:
            continue
        item = grouped.setdefault(source, {"filename": source, "chunks": 0, "pages": set()})
        item["chunks"] += 1
        if metadata.get("page") is not None:
            item["pages"].add(metadata["page"])

    documents = []
    for item in grouped.values():
        path = UPLOAD_DIR / item["filename"]
        documents.append({
            "filename": item["filename"],
            "chunks": item["chunks"],
            "pages": len(item["pages"]),
            "size": path.stat().st_size if path.is_file() else None,
            "exists": path.is_file(),
        })

    return sorted(documents, key=lambda doc: doc["filename"].lower())


@router.delete("/{filename}")
def delete_document(filename: str):
    filename = _safe_filename(filename)
    existing = collection.get(
        where={"source": filename},
        include=["metadatas"],
    )
    ids = existing.get("ids") or []
    if ids:
        collection.delete(ids=ids)

    file_path = UPLOAD_DIR / filename
    if file_path.is_file():
        file_path.unlink()

    db = SessionLocal()
    try:
        add_event(
            db=db,
            event_type="delete_document",
            description=f"用户删除了文档：{filename}",
            related_doc=filename,
        )
    finally:
        db.close()

    return {"filename": filename, "deleted_chunks": len(ids)}
