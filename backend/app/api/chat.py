from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.retriever import search
from app.rag.generator import generate_answer

from app.database.session import SessionLocal
from app.services.memory_service import get_recent_events, get_all_profiles


router = APIRouter(
    prefix="/chat",
    tags=["AI问答"]
)


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(request: ChatRequest):
    # =========================
    # 1. 检索 ChromaDB 知识库
    # =========================
    documents = search(request.question)

    # 提取纯文本上下文
    contexts = [doc["text"] for doc in documents]

    # =========================
    # 2. 获取 PostgreSQL 用户记忆
    # =========================
    db = SessionLocal()
    try:
        events = get_recent_events(db, limit=5)
        profiles = get_all_profiles(db)

        # 在关闭 session 前，先读取数据，防止 DetachedInstanceError
        events_data = [
            {
                "created_at": event.created_at,
                "event_type": event.event_type,
                "description": event.description,
                "related_doc": event.related_doc,
            }
            for event in events
        ]

        profiles_data = [
            {"key": profile.key, "value": profile.value}
            for profile in profiles
        ]

    finally:
        db.close()

    # =========================
    # 3. 把记忆转换成文本
    # =========================
    memory_context = ""

    if profiles_data:
        memory_context += "\n用户画像：\n"
        for profile in profiles_data:
            memory_context += f"- {profile['key']}: {profile['value']}\n"

    if events_data:
        memory_context += "\n用户历史事件：\n"
        for event in events_data:
            memory_context += f"- 时间：{event['created_at']}\n"
            memory_context += f"  类型：{event['event_type']}\n"
            memory_context += f"  描述：{event['description']}\n"
            if event['related_doc']:
                memory_context += f"  关联文档：{event['related_doc']}\n"

    # =========================
    # 4. 生成回答
    # =========================
    answer = generate_answer(
        request.question,
        contexts,           # ✅ 传入字符串列表
        memory_context
    )

    # =========================
    # 5. 返回结果
    # =========================
    return {
        "question": request.question,
        "answer": answer,
        "sources": [doc["metadata"] for doc in documents]
    }