from app.database.chroma import document_collection
from app.services.embed_service import generate_embeddings


def search(query):

    # 生成问题向量
    query_vector = generate_embeddings(
        [query]
    )


    result = document_collection.query(
        query_embeddings=query_vector,
        n_results=3
    )


    documents = []


    for i in range(
        len(result["documents"][0])
    ):

        documents.append(
            {
                "text":
                    result["documents"][0][i],

                "metadata":
                    result["metadatas"][0][i]
            }
        )


    return documents