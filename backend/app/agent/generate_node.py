"""
Generate 节点（最终生成）
------------------------
将 RAG 检索到的上下文、Memory 节点提供的记忆、Tool 节点的执行结果整合起来，
调用 DeepSeek 生成最终的回答。
"""

from app.rag.generator import generate_answer


def build_generation_memory(state: dict) -> str:
    """合并长期记忆和工具执行结果，供最终生成节点复用。"""
    memory = state.get("memory_context", "") or ""
    tool_results = state.get("tool_results", []) or []

    if tool_results:
        extra = "\n".join(tool_results)
        if memory:
            memory += "\n[工具执行结果]\n" + extra
        else:
            memory = "[工具执行结果]\n" + extra

    return memory


def generate_node(state: dict) -> dict:
    question = state["question"]
    contexts = state.get("rag_contexts", [])
    memory = build_generation_memory(state)

    # 调用 generate_answer，传入问题、检索到的上下文、记忆（含工具结果）
    answer = generate_answer(question, contexts, memory)

    return {
        "final_answer": answer,
        "sources": state.get("sources", []),
        "next_node": "end"      # end 表示流程结束，LangGraph 会识别并停止
    }
