"""
聊天 API
--------
接收用户问题，通过 Agent 图执行，返回最终答案和来源。
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.graph import build_agent_graph

router = APIRouter(
    prefix="/chat",
    tags=["AI问答"]
)

class ChatRequest(BaseModel):
    question: str

# 构建一次 Agent 图（模块加载时）
agent = build_agent_graph()

@router.post("/")
def chat(request: ChatRequest):
    # 初始状态，所有字段均为空
    initial_state = {
        "question": request.question,
        "rag_contexts": [],
        "memory_context": "",
        "tool_results": [],
        "final_answer": "",
        "next_node": "supervisor",
        "sources": []
    }

    # 运行整个 Agent 流程
    result = agent.invoke(initial_state)

    # 返回结果
    return {
        "question": request.question,
        "answer": result.get("final_answer", ""),
        "sources": result.get("sources", [])
    }