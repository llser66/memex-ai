from app.database.chroma import collection
from app.services.embed_service import generate_embeddings


def search(query: str, top_k: int = 3):

    # 1. 将用户问题转换成向量
    query_vector = generate_embeddings(
        [query]
    )

    # 2. 查询 Chroma
    result = collection.query(
        query_embeddings=query_vector,
        n_results=top_k
    )

    # 3. 整理 Chroma 返回的数据
    documents = []

    if not result["documents"]:
        return documents

    if not result["documents"][0]:
        return documents

    for i in range(len(result["documents"][0])):

        documents.append(
            {
                "text": result["documents"][0][i],
                "metadata": result["metadatas"][0][i]
            }
        )

    return documents