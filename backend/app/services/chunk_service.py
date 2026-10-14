def split_pages(
    pages,
    source,
    chunk_size=500,
    overlap=50
):

    chunks=[]


    for page in pages:

        text = (page.get("text") or "").strip()

        if not text:
            continue

        page_num = page["page"]


        start=0


        while start < len(text):

            end=start+chunk_size


            chunk_text=text[start:end].strip()

            if not chunk_text:
                start += chunk_size - overlap
                continue


            chunks.append(
                {
                    "text":chunk_text,

                    "metadata":
                    {
                        "source":source,
                        "page":page_num
                    }
                }
            )


            start += chunk_size-overlap


    return chunks
