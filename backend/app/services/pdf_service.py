import fitz
from pathlib import Path

def extract_pdf_pages(file_path: Path):
    doc = fitz.open(file_path)
    pages = []
    for page_number, page in enumerate(doc):
        # 关键修改：使用 sort=True 按坐标排序文本
        text = page.get_text("text", sort=True)
        pages.append({
            "page": page_number + 1,
            "text": text
        })
    doc.close()
    return pages