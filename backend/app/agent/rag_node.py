"""
RAG 节点
--------
负责调用 retriever.search() 从 ChromaDB 中检索与用户问题最相关的文档块。
并将检索结果转换成后续生成节点需要的格式。
"""

from app.rag.retriever import search

def rag_node(state: dict) -> dict:
    question = state["question"]

    # search() 返回一个列表，每个元素是 {"text": 文本块, "metadata": 来源信息}
    docs = search(question)

    # 提取纯文本内容，用于生成回答
    contexts = [doc["text"] for doc in docs]

    # 提取元数据，用于最终返回给用户查看来源
    sources = [doc["metadata"] for doc in docs]

    # 返回更新后的状态字段，同时指定下一步去 generate 节点
    return {
        "rag_contexts": contexts,
        "sources": sources,
        "next_node": "generate"
    }