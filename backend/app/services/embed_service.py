from sentence_transformers import SentenceTransformer


# 加载Embedding模型
model = SentenceTransformer(
    "BAAI/bge-small-zh-v1.5"
)


def generate_embeddings(texts):
    """
    将文本转换为向量

    参数:
        texts:
        [
            "文本1",
            "文本2"
        ]

    返回:
        [
            [0.1,0.2,...],
            [0.3,0.4,...]
        ]
    """

    embeddings = model.encode(
        texts
    )


    return embeddings.tolist()