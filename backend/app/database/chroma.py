import chromadb
from pathlib import Path


# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parents[3]


# 数据库存储位置
CHROMA_PATH = BASE_DIR / "data" / "chroma"


# 创建持久化客户端
client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


# 创建集合
document_collection = client.get_or_create_collection(
    name="documents"
)