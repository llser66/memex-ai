from fastapi import APIRouter, UploadFile, File
from pathlib import Path

from app.services.pdf_service import extract_pdf_pages
from app.services.chunk_service import split_pages
from app.services.embed_service import generate_embeddings
from app.database.chroma import document_collection


router = APIRouter(
    prefix="/upload",
    tags=["文件上传"]
)


# 项目根目录/data/files
BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = BASE_DIR / "data" / "files"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    if not file.filename.endswith(".pdf"):
        return {
            "error": "只支持PDF文件"
        }


    # 保存PDF

    file_path = UPLOAD_DIR / file.filename


    # 保存文件
    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)



    # 1. PDF解析（保留页码）

    pages = extract_pdf_pages(
        file_path
    )


    # 2. 文本切chunk

    chunks = split_pages(
        pages,
        source=file.filename
    )


    # 提取文本

    texts = [
        chunk["text"]
        for chunk in chunks
    ]


    # 提取metadata

    metadatas = [
        chunk["metadata"]
        for chunk in chunks
    ]


    # 3. Embedding

    vectors = generate_embeddings(
        texts
    )


    # 4. 存入ChromaDB

    ids = [
        f"{file.filename}_{i}"
        for i in range(len(texts))
    ]


    document_collection.add(
        documents=texts,
        embeddings=vectors,
        metadatas=metadatas,
        ids=ids
    )


    return {
        "filename":file.filename,
        "message":"PDF上传成功，知识库建立完成",
        "pages":len(pages),
        "chunks":len(chunks)
    }