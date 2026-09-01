from app.rag.retriever import search


result = search("学的什么专业")


print("检索结果数量：", len(result))

print("=" * 50)

for i, doc in enumerate(result):

    print(f"第 {i + 1} 条")
    print("-" * 50)

    print("文本：")
    print(doc["text"])

    print()

    print("Metadata：")
    print(doc["metadata"])

    print("=" * 50)