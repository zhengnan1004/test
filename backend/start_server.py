#!/usr/bin/env python3
"""
修复编码问题的FastAPI服务启动脚本
"""

import uvicorn
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_env_with_encoding_fix():
    """修复编码问题加载环境变量"""
    try:
        # 手动设置关键环境变量，避免编码问题
        env_file = Path(__file__).parent / "config.env"
        
        if env_file.exists():
            print(f"📁 找到配置文件: {env_file}")
            
            # 手动读取并设置环境变量
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                        print(f"✅ 设置环境变量: {key}")
        else:
            print("⚠️  配置文件不存在，使用默认值")
            
        # 确保关键环境变量存在
        if 'DATABASE_URL' not in os.environ:
            os.environ['DATABASE_URL'] = "postgresql://postgres:Zhengnan4568@localhost:5432/database1"
            print("✅ 设置默认数据库连接")
            
    except Exception as e:
        print(f"⚠️  环境变量加载失败: {e}")
        # 设置默认值
        os.environ['DATABASE_URL'] = "postgresql://postgres:Zhengnan4568@localhost:5432/database1"

def check_database_connection():
    """检查数据库连接"""
    try:
        print("🔍 检查数据库连接...")
        
        # 先测试基本连接
        from app.database import engine
        
        print("✅ 数据库引擎创建成功")
        
        # 测试连接
        with engine.connect() as conn:
            print("✅ 数据库连接成功！")
            
            # 检查数据库版本
            from sqlalchemy import text
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"📊 PostgreSQL版本: {version}")
        
        # 如果连接成功，再测试模型
        print("📋 检查数据模型...")
        from app import models
        
        print("✅ 数据模型导入成功")
        
        # 创建表
        print("📋 创建数据库表...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功！")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        print(f"🔍 错误类型: {type(e).__name__}")
        print("💡 请检查以下配置：")
        print("   1. PostgreSQL服务是否正在运行")
        print("   2. 数据库连接信息是否正确")
        print("   3. 数据库是否存在")
        print("   4. 用户名和密码是否正确")
        print()
        return False

if __name__ == "__main__":
    print("🚀 启动用户认证服务（编码修复版）...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print()
    
    # 修复编码问题
    load_env_with_encoding_fix()
    
    # 检查数据库连接
    if not check_database_connection():
        print("⚠️  数据库连接失败，但服务仍将启动")
        print("   某些功能可能无法正常工作")
        print()
    
    print("⏹️  按 Ctrl+C 停止服务")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
