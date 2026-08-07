from fastapi import APIRouter
from pydantic import BaseModel


from app.rag.retriever import search
from app.rag.generator import generate_answer



router = APIRouter(
    prefix="/chat",
    tags=["AI问答"]
)



class ChatRequest(BaseModel):

    question:str



@router.post("/")
def chat(
    request:ChatRequest
):


    # 1. 检索知识库

    documents = search(
        request.question
    )


    # 2. DeepSeek生成回答

    answer = generate_answer(
        request.question,
        documents
    )


    return {

        "question":
        request.question,


        "answer":
        answer,


        "sources":
        [
            doc["metadata"]
            for doc in documents
        ]

    }