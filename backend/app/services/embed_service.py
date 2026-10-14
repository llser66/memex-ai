from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model():
    """按需加载模型，避免健康检查和接口文档启动时下载模型。"""
    return SentenceTransformer("BAAI/bge-small-zh-v1.5")


def generate_embeddings(texts):
    """将文本转换成向量。"""
    if not texts:
        return []
    return get_embedding_model().encode(texts).tolist()
