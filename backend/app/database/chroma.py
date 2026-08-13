import chromadb
from chromadb.config import Settings
from pathlib import Path

# 动态获取项目根目录（不管在哪里启动都能存对地方）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR),
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(name="memex_documents")