from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import fitz   # PyMuPDF


router = APIRouter(
    prefix="/upload",
    tags=["文件上传"]
)


# 文件保存目录
UPLOAD_DIR = Path("../../data/files")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # 判断文件类型
    if not file.filename.endswith(".pdf"):
        return {
            "error": "只支持PDF文件"
        }


    # 保存路径
    file_path = UPLOAD_DIR / file.filename


    # 保存文件
    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)


    # 读取PDF
    doc = fitz.open(file_path)


    text = ""

    for page in doc:
        text += page.get_text()


    # 返回前500字符
    preview = text[:500]


    return {
        "filename": file.filename,
        "message": "上传成功",
        "preview": preview
    }