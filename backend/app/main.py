from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router


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