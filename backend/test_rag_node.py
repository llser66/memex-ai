from app.agent.rag_node import rag_node


state = {
    "question": "我的简历里面有哪些AI项目？",
    "rag_contexts": [],
    "memory_context": "",
    "tool_results": [],
    "final_answer": "",
    "next_node": "rag"
}


result = rag_node(state)


print("RAG节点执行结果：")
print("----------------------------")

print("下一节点：")
print(result["next_node"])

print("\n检索到的资料：")
print("----------------------------")

for i, context in enumerate(
    result["rag_contexts"],
    start=1
):
    print(f"\n第{i}条：")
    print(context)