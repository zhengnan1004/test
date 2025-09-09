from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary, Text
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user", nullable=False)  # user | admin
    # 头像相关
    avatar = Column(LargeBinary, nullable=True)              # 原始二进制
    avatar_mime = Column(String(100), nullable=True)         # MIME 类型，如 image/png
    avatar_size = Column(Integer, nullable=True)             # 字节大小
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Document(Base):
    """文档上传与分类记录"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    file_path = Column(String(1024), nullable=True)
    username = Column(String(100), nullable=False, index=True)
    dify_file_id = Column(String(255), nullable=False, unique=True, index=True)
    dify_workflow_run_id = Column(String(255), nullable=True, index=True)
    classification = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="uploaded")  # uploaded | classified | classification_failed
    access = Column(String(50), nullable=True)
    error_message = Column(String(1024), nullable=True)
    upload_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Document(filename='{self.filename}', username='{self.username}', status='{self.status}')>"


class Course(Base):
    """课程模型"""
    __tablename__ = "course"
    
    id = Column(Integer, primary_key=True, index=True)
    course_title = Column(String(255), nullable=False, index=True)
    course_description = Column(Text, nullable=True)
    generated_text = Column(Text, nullable=True)
    username = Column(String(100), nullable=False, index=True)
    visibility = Column(String(50), default="draft")  # draft | published
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Course(title='{self.course_title}', username='{self.username}', visibility='{self.visibility}')>"


class AiFeedback(Base):
    """聊天AI回复与反馈记录"""
    __tablename__ = "ai_feedback"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, nullable=True, index=True)  # 从100开始的顺序编号
    chat_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    feedback_type = Column(String(50), nullable=False, default="null")  # null | good | not satisfied
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AiFeedback(chat_id='{self.chat_id}', session_id='{self.session_id}', feedback_type='{self.feedback_type}', comment_id='{self.comment_id}')>"