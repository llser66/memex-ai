from fastapi import APIRouter, UploadFile, File
from pathlib import Path

from app.database.session import SessionLocal
from app.services.memory_service import add_event

from app.services.pdf_service import extract_pdf_pages
from app.services.chunk_service import split_pages
from app.services.embed_service import generate_embeddings

from app.database.chroma import collection


router = APIRouter(
    prefix="/upload",
    tags=["文件上传"]
)


# ============================================================
# 项目根目录 / data / files
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = BASE_DIR / "data" / "files"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# PDF 上传接口
# ============================================================

@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # 1. 判断文件类型
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "只支持PDF文件"
        }


    # --------------------------------------------------------
    # 2. 保存 PDF 文件
    # --------------------------------------------------------

    file_path = UPLOAD_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)


    # --------------------------------------------------------
    # 3. PDF 解析
    #    保留页码信息
    # --------------------------------------------------------

    pages = extract_pdf_pages(
        file_path
    )


    # --------------------------------------------------------
    # 4. 文本切分
    # --------------------------------------------------------

    chunks = split_pages(
        pages,
        source=file.filename
    )


    # --------------------------------------------------------
    # 5. 提取 chunk 文本
    # --------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]


    # --------------------------------------------------------
    # 6. 提取 metadata
    # --------------------------------------------------------

    metadatas = [
        chunk["metadata"]
        for chunk in chunks
    ]


    # --------------------------------------------------------
    # 7. Embedding
    # --------------------------------------------------------

    vectors = generate_embeddings(
        texts
    )


    # --------------------------------------------------------
    # 8. 生成 ChromaDB ID
    # --------------------------------------------------------

    ids = [
        f"{file.filename}_{i}"
        for i in range(len(texts))
    ]


    # --------------------------------------------------------
    # 9. 保存到 ChromaDB
    # --------------------------------------------------------

    collection.add(
        documents=texts,
        embeddings=vectors,
        metadatas=metadatas,
        ids=ids
    )


    # ========================================================
    # 10. 保存"上传文件"事件到 PostgreSQL
    # ========================================================

    db = SessionLocal()

    try:

        add_event(
            db=db,
            event_type="upload_document",
            description=f"用户上传了文档：{file.filename}",
            related_doc=file.filename
        )

    finally:

        db.close()


    # --------------------------------------------------------
    # 11. 返回结果
    # --------------------------------------------------------

    return {
        "filename": file.filename,
        "message": "PDF上传成功，知识库建立完成",
        "pages": len(pages),
        "chunks": len(chunks)
    }