"""聊天 API：普通问答和 SSE 流式问答。"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.generate_node import build_generation_memory
from app.agent.graph import (
    build_agent_graph,
    create_initial_state,
    prepare_agent_state,
)
from app.rag.generator import generate_answer_stream


router = APIRouter(
    prefix="/chat",
    tags=["AI问答"]
)


class ChatRequest(BaseModel):
    question: str


agent = build_agent_graph()


def _validate_question(question: str) -> str:
    question = question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="问题不能为空。")
    if len(question) > 4000:
        raise HTTPException(status_code=422, detail="问题长度不能超过 4000 个字符。")
    return question


def _sse(payload) -> str:
    if payload == "[DONE]":
        return "data: [DONE]\n\n"
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/")
def chat(request: ChatRequest):
    question = _validate_question(request.question)
    result = agent.invoke(create_initial_state(question))

    return {
        "question": question,
        "answer": result.get("final_answer", ""),
        "sources": result.get("sources", []),
        "report_file": result.get("report_file"),
    }


@router.post("/stream")
def chat_stream(request: ChatRequest):
    """执行上下文节点后，以 SSE 逐 token 返回最终回答。"""
    question = _validate_question(request.question)

    try:
        state = prepare_agent_state(question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    def event_stream():
        try:
            memory_context = build_generation_memory(state)
            for content in generate_answer_stream(
                question,
                state.get("rag_contexts", []) or [],
                memory_context,
            ):
                yield _sse({"content": content})

            yield _sse({
                "sources": state.get("sources", []) or [],
                "report_file": state.get("report_file"),
            })
            yield _sse("[DONE]")
        except Exception as exc:
            yield _sse({"error": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
