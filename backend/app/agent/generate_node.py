"""
Generate 节点（最终生成）
------------------------
将 RAG 检索到的上下文、Memory 节点提供的记忆、Tool 节点的执行结果整合起来，
调用 DeepSeek 生成最终的回答。
"""

from app.rag.generator import generate_answer

def generate_node(state: dict) -> dict:
    question = state["question"]
    contexts = state.get("rag_contexts", [])
    memory = state.get("memory_context", "")
    tool_results = state.get("tool_results", [])

    # 如果有工具执行结果（例如周报生成成功），追加到 memory 上下文中，
    # 这样 LLM 在回答时也能知道工具的执行情况
    if tool_results:
        extra = "\n".join(tool_results)
        if memory:
            memory += "\n[工具执行结果]\n" + extra
        else:
            memory = "[工具执行结果]\n" + extra

    # 调用 generate_answer，传入问题、检索到的上下文、记忆（含工具结果）
    answer = generate_answer(question, contexts, memory)

    return {
        "final_answer": answer,
        "sources": state.get("sources", []),
        "next_node": "end"      # end 表示流程结束，LangGraph 会识别并停止
    }