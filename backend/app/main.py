from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.memory import router as memory_router
from app.api.reports import router as reports_router
from app.database import models  # noqa: F401 - 注册 SQLAlchemy 模型
from app.database.session import Base, engine


# 创建FastAPI应用
app = FastAPI(
    title="Memex AI Backend",
    description="Personal AI Work Memory Assistant API",
    version="0.1.0"
)



# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 注册上传接口
app.include_router(upload_router)

# 注册知识库、记忆和报告接口
app.include_router(documents_router)
app.include_router(memory_router)
app.include_router(reports_router)


# 注册聊天接口
app.include_router(chat_router)


@app.on_event("startup")
def initialize_database():
    """首次启动时自动创建记忆相关表。"""
    Base.metadata.create_all(bind=engine)



@app.get("/")
def root():
    return {
        "message": "Memex AI Backend Running"
    }



@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
