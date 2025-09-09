from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('../config.env')

# 数据库连接配置
# 使用硬编码的默认值避免环境变量编码问题
DEFAULT_DATABASE_URL = "postgresql://postgres:Zhengnan4568@localhost:5432/database1"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# 打印连接信息用于调试（不显示密码）
print(f"🔗 数据库连接: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '未知'}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 依赖函数，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
