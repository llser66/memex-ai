from sqlalchemy import text

from app.database.session import engine, Base
from app.database import models


# 创建数据表
Base.metadata.create_all(bind=engine)


# 测试数据库连接
with engine.connect() as conn:

    result = conn.execute(
        text("SELECT 1")
    )

    print(
        "数据库连接成功:",
        result.fetchone()
    )