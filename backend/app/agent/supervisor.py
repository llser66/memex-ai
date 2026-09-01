from app.agent.state import AgentState


def supervisor_node(state: AgentState):
    """
    Supervisor：
    根据用户问题决定下一步应该执行哪个节点。
    目前支持：
      - 周报生成 → tool
      - 涉及个人记忆/历史 → memory
      - 其他问题 → rag
    """

    question = state["question"]
    question_lower = question.lower()

    # -------------------------
    # 1. 判断是否属于周报工具任务
    # -------------------------
    if (
        "周报" in question
        or "周总结" in question
        or "本周工作" in question
        or "生成周报" in question
    ):
        return {
            "next_node": "tool"
        }

    # -------------------------
    # 2. 判断是否属于记忆任务
    # -------------------------
    if (
        "我最近" in question
        or "我之前" in question
        or "我的" in question
        or "我上传" in question
        or "记得" in question
        or "历史" in question
    ):
        return {
            "next_node": "memory"
        }

    # -------------------------
    # 3. 默认进入 RAG
    # -------------------------
    return {
        "next_node": "rag"
    }