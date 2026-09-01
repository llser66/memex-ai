from app.agent.state import AgentState


state: AgentState = {
    "question": "我最近上传过什么文件？",
    "rag_contexts": [],
    "memory_context": "",
    "tool_results": [],
    "final_answer": "",
    "next_node": "supervisor"
}


print("Agent State:")
print(state)