"""生成报告的下载 API。"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(prefix="/reports", tags=["报告"])

BASE_DIR = Path(__file__).resolve().parents[3]
REPORT_DIR = BASE_DIR / "data" / "reports"


@router.get("/{filename}")
def download_report(filename: str):
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.endswith(".md"):
        raise HTTPException(status_code=400, detail="报告文件名无效。")

    report_path = REPORT_DIR / safe_name
    if not report_path.is_file():
        raise HTTPException(status_code=404, detail="报告不存在。")

    return FileResponse(
        report_path,
        media_type="text/markdown; charset=utf-8",
        filename=safe_name,
    )
