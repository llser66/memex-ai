import fitz
from pathlib import Path


def extract_pdf_pages(file_path: Path):

    doc = fitz.open(file_path)

    pages = []


    for page_number, page in enumerate(doc):

        text = page.get_text()

        pages.append(
            {
                "page": page_number + 1,
                "text": text
            }
        )


    doc.close()

    return pages