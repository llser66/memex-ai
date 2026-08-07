def split_pages(
    pages,
    source,
    chunk_size=500,
    overlap=50
):

    chunks=[]


    for page in pages:

        text = page["text"]

        page_num = page["page"]


        start=0


        while start < len(text):

            end=start+chunk_size


            chunk_text=text[start:end]


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