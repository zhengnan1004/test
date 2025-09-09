from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class UserRegisterRequest(BaseModel):
    """用户注册请求模型"""
    username: str
    password: str
    email: Optional[str] = None
    role: Optional[str] = "user"
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('用户名至少需要3个字符')
        if len(v) > 50:
            raise ValueError('用户名不能超过50个字符')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        if len(v) > 100:
            raise ValueError('密码不能超过100个字符')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            if '@' not in v or '.' not in v:
                raise ValueError('邮箱格式不正确')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in ['user', 'admin']:
            raise ValueError('角色只能是 user 或 admin')
        return v

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLoginRequest(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """登录令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: int
    role: str

class UserUpdateRequest(BaseModel):
    """用户信息更新请求模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('用户名至少需要3个字符')
            if len(v) > 50:
                raise ValueError('用户名不能超过50个字符')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 6:
                raise ValueError('密码至少需要6个字符')
            if len(v) > 100:
                raise ValueError('密码不能超过100个字符')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            if '@' not in v or '.' not in v:
                raise ValueError('邮箱格式不正确')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in ['user', 'admin']:
            raise ValueError('角色只能是 user 或 admin')
        return v

class UserDeleteResponse(BaseModel):
    """用户删除响应模型"""
    message: str
    deleted_user: UserResponse

# 头像响应（基础信息）
class AvatarInfo(BaseModel):
    mime: str
    size: int

class AvatarUploadResponse(BaseModel):
    message: str
    user_id: int
    avatar: AvatarInfo

# 文档分类更新相关模型
class DocumentClassificationUpdateRequest(BaseModel):
    """文档分类更新请求模型"""
    classification: str
    
    @validator('classification')
    def validate_classification(cls, v):
        if not v or not v.strip():
            raise ValueError('分类不能为空')
        if len(v) > 255:
            raise ValueError('分类名称不能超过255个字符')
        return v.strip()

class DocumentClassificationUpdateResponse(BaseModel):
    """文档分类更新响应模型"""
    code: int
    message: str
    data: Optional[dict] = None

class DocumentInfo(BaseModel):
    """文档信息模型"""
    id: int
    filename: str
    dify_file_id: str
    classification: Optional[str]
    status: str
    access: Optional[str]
    upload_time: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# =============== AI反馈相关 ===============
class AiFeedbackCreate(BaseModel):
    chat_id: str
    session_id: str
    user_id: Optional[str] = None
    question: str
    answer: Optional[str] = None
    feedback_type: Optional[str] = "null"

    @validator('feedback_type')
    def validate_feedback_type(cls, v):
        allowed = ["null", "good", "not satisfied"]
        if v not in allowed:
            raise ValueError(f"feedback_type必须是 {allowed} 之一")
        return v


class AiFeedbackUpdate(BaseModel):
    feedback_type: str

    @validator('feedback_type')
    def validate_feedback_type(cls, v):
        allowed = ["null", "good", "not satisfied"]
        if v not in allowed:
            raise ValueError(f"feedback_type必须是 {allowed} 之一")
        return v


class AiFeedbackResp(BaseModel):
    id: int
    chat_id: str
    session_id: str
    user_id: Optional[str]
    question: str
    answer: Optional[str]
    feedback_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class AiFeedbackRecord(BaseModel):
    """AI反馈记录模型（用于列表查询）"""
    id: int
    comment_id: Optional[int]
    question: str
    answer: Optional[str]  # 添加answer字段
    feedback_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class AiFeedbackStats(BaseModel):
    """AI反馈统计信息模型"""
    total_count: int
    good_count: int
    not_satisfied_count: int
    not_satisfied_questions: List[dict]


class AiFeedbackListResponse(BaseModel):
    """AI反馈记录列表响应模型"""
    code: int
    message: str
    data: List[AiFeedbackRecord]
    total: int
    skip: int
    limit: int


class AiFeedbackStatsResponse(BaseModel):
    """AI反馈统计响应模型"""
    code: int
    message: str
    data: AiFeedbackStats