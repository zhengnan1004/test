from sqlalchemy.orm import Session
from . import models, schemas
from .auth import hash_password, verify_password
from typing import Optional, Tuple, List
from sqlalchemy import func

def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """根据邮箱获取用户"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """根据ID获取用户"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserRegisterRequest):
    """创建新用户"""
    # 检查用户名是否已存在
    if get_user_by_username(db, user.username):
        return None, "用户名已存在"
    
    # 检查邮箱是否已存在（如果提供了邮箱）
    if user.email and get_user_by_email(db, user.email):
        return None, "邮箱已被注册"
    
    # 创建用户对象
    hashed_password = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        email=user.email,
        role=user.role or "user"
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user, None
    except Exception as e:
        db.rollback()
        return None, f"创建用户失败: {str(e)}"

# 新增：设置头像（存DB）
def set_user_avatar(db: Session, user_id: int, *, data: bytes, mime: str) -> Tuple[Optional[models.User], Optional[str]]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None, "user_not_found"
    try:
        user.avatar = data
        user.avatar_mime = mime
        user.avatar_size = len(data)
        db.commit()
        db.refresh(user)
        return user, None
    except Exception as e:
        db.rollback()
        return None, str(e)

# 新增：获取头像
def get_user_avatar(db: Session, user_id: int) -> Tuple[Optional[bytes], Optional[str], Optional[int]]:
    user = get_user_by_id(db, user_id)
    if not user or not user.avatar:
        return None, None, None
    return user.avatar, user.avatar_mime, user.avatar_size

def authenticate_user(db: Session, username: str, password: str):
    """验证用户登录"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """获取用户列表"""
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdateRequest):
    """更新用户信息"""
    # 获取用户
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None, "用户不存在"
    
    # 检查用户名是否已被其他用户使用
    if user_update.username and user_update.username != db_user.username:
        existing_user = get_user_by_username(db, user_update.username)
        if existing_user and existing_user.id != user_id:
            return None, "用户名已被其他用户使用"
    
    # 检查邮箱是否已被其他用户使用
    if user_update.email and user_update.email != db_user.email:
        existing_user = get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != user_id:
            return None, "邮箱已被其他用户使用"
    
    # 更新用户信息
    try:
        if user_update.username is not None:
            db_user.username = user_update.username
        if user_update.email is not None:
            db_user.email = user_update.email
        if user_update.password is not None:
            db_user.password_hash = hash_password(user_update.password)
        if user_update.is_active is not None:
            db_user.is_active = user_update.is_active
        if user_update.role is not None:
            db_user.role = user_update.role
        
        db.commit()
        db.refresh(db_user)
        return db_user, None
    except Exception as e:
        db.rollback()
        return None, f"更新用户失败: {str(e)}"

def delete_user(db: Session, user_id: int):
    """删除用户"""
    # 获取用户
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None, "用户不存在"
    
    try:
        # 删除用户
        db.delete(db_user)
        db.commit()
        return db_user, None
    except Exception as e:
        db.rollback()
        return None, f"删除用户失败: {str(e)}"

# ========================
# 文档记录相关 CRUD
# ========================

def create_document_record(
    db: Session,
    *,
    filename: str,
    file_path: str | None,
    username: str,
    dify_file_id: str,
    upload_time=None,
    access: str | None = None,
):
    """新建文档上传记录，初始状态为 uploaded。"""
    from datetime import datetime
    
    doc = models.Document(
        filename=filename,
        file_path=file_path,
        username=username,
        dify_file_id=dify_file_id,
        status="uploaded",
        access=access,
        upload_time=upload_time or datetime.now(),
    )
    try:
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc, None
    except Exception as e:
        db.rollback()
        # 打印错误方便排查（例如列不存在导致无法写入 file_path）
        print(f"[create_document_record] 写入失败: {e}")
        return None, str(e)


def update_document_classification(
    db: Session,
    *,
    dify_file_id: str,
    classification: str | None,
    dify_workflow_run_id: str | None = None,
    error_message: str | None = None,
    status: str | None = None,
):
    """根据 dify_file_id 更新分类结果和状态。"""
    doc = db.query(models.Document).filter(models.Document.dify_file_id == dify_file_id).first()
    if not doc:
        return None, "document_not_found"
    if classification is not None:
        doc.classification = classification
    if dify_workflow_run_id is not None:
        doc.dify_workflow_run_id = dify_workflow_run_id
    if error_message is not None:
        doc.error_message = error_message
    if status is not None:
        doc.status = status
    else:
        # 若未明确给出，则依据是否有错误信息推断
        doc.status = "classified" if not error_message else "classification_failed"
    try:
        db.commit()
        db.refresh(doc)
        return doc, None
    except Exception as e:
        db.rollback()
        return None, str(e)


def get_document_by_dify_file_id(db: Session, dify_file_id: str) -> Optional[models.Document]:
    """根据 dify_file_id 获取文档记录。"""
    return db.query(models.Document).filter(models.Document.dify_file_id == dify_file_id).first()


def update_document_file(
    db: Session,
    *,
    dify_file_id: str,
    filename: str,
    file_path: str,
    upload_time,
    access: Optional[str] = None,
) -> Tuple[Optional[models.Document], Optional[str]]:
    """替换文档文件（仅更新数据库中的文件元信息，不重新上传到 Dify）。

    - 根据 dify_file_id 定位文档
    - 覆盖 filename、file_path、upload_time
    - 可选更新 access
    - status 置为 uploaded
    """
    doc = get_document_by_dify_file_id(db, dify_file_id)
    if not doc:
        return None, "document_not_found"
    try:
        doc.filename = filename
        doc.file_path = file_path
        doc.upload_time = upload_time
        if access is not None:
            doc.access = access
        doc.status = "uploaded"
        db.commit()
        db.refresh(doc)
        return doc, None
    except Exception as e:
        db.rollback()
        return None, str(e)

def get_documents_list(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    username: Optional[str] = None,
    filename: Optional[str] = None
) -> Tuple[List[models.Document], int]:
    """
    获取文档列表，支持分页和筛选
    """
    query = db.query(models.Document)
    
    # 按用户名筛选
    if username:
        query = query.filter(models.Document.username == username)
    
    # 按文件名筛选（模糊匹配）
    if filename:
        query = query.filter(models.Document.filename.ilike(f"%{filename}%"))
    
    # 获取总数
    total = query.count()
    
    # 分页并排序（按创建时间倒序）
    documents = query.order_by(models.Document.created_at.desc()).offset(skip).limit(limit).all()
    
    return documents, total

def update_document_classification_only(
    db: Session,
    *,
    dify_file_id: str,
    classification: str,
) -> Tuple[Optional[models.Document], Optional[str]]:
    """
    仅更新文档的分类信息
    
    Args:
        db: 数据库会话
        dify_file_id: 文档的Dify文件ID
        classification: 新的分类名称
    
    Returns:
        Tuple[Optional[models.Document], Optional[str]]: (更新后的文档对象, 错误信息)
    """
    doc = db.query(models.Document).filter(models.Document.dify_file_id == dify_file_id).first()
    if not doc:
        return None, "文档不存在"
    
    try:
        doc.classification = classification
        # 如果之前分类失败，现在手动更新分类，将状态改为classified
        if doc.status == "classification_failed":
            doc.status = "classified"
        doc.updated_at = func.now()
        db.commit()
        db.refresh(doc)
        return doc, None
    except Exception as e:
        db.rollback()
        return None, f"更新分类失败: {str(e)}"


# ========================
# 课程相关 CRUD
# ========================

def create_course(
    db: Session,
    *,
    course_title: str,
    course_description: str | None,
    generated_text: str | None,
    username: str,
    visibility: str = "draft"
):
    """创建新课程记录"""
    course = models.Course(
        course_title=course_title,
        course_description=course_description,
        generated_text=generated_text,
        username=username,
        visibility=visibility
    )
    try:
        db.add(course)
        db.commit()
        db.refresh(course)
        return course, None
    except Exception as e:
        db.rollback()
        return None, f"创建课程失败: {str(e)}"


def get_course_by_id(db: Session, course_id: int) -> Optional[models.Course]:
    """根据ID获取课程"""
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def get_courses_by_username(
    db: Session, 
    username: str,
    skip: int = 0, 
    limit: int = 100
) -> Tuple[List[models.Course], int]:
    """根据用户名获取课程列表"""
    query = db.query(models.Course).filter(models.Course.username == username)
    
    # 获取总数
    total = query.count()
    
    # 分页并排序（按创建时间倒序）
    courses = query.order_by(models.Course.created_at.desc()).offset(skip).limit(limit).all()
    
    return courses, total


def get_all_courses(
    db: Session,
    skip: int = 0, 
    limit: int = 100,
    username: Optional[str] = None,
    visibility: Optional[str] = None
) -> Tuple[List[models.Course], int]:
    """获取所有课程列表，支持分页和筛选"""
    query = db.query(models.Course)
    
    # 按用户名筛选
    if username:
        query = query.filter(models.Course.username == username)
    
    # 按可见性筛选
    if visibility:
        query = query.filter(models.Course.visibility == visibility)
    
    # 获取总数
    total = query.count()
    
    # 分页并排序（按创建时间倒序）
    courses = query.order_by(models.Course.created_at.desc()).offset(skip).limit(limit).all()
    
    return courses, total


def update_course(
    db: Session,
    course_id: int,
    *,
    course_title: str | None = None,
    course_description: str | None = None,
    generated_text: str | None = None,
    visibility: str | None = None
) -> Tuple[Optional[models.Course], Optional[str]]:
    """更新课程信息"""
    course = get_course_by_id(db, course_id)
    if not course:
        return None, "课程不存在"
    
    try:
        if course_title is not None:
            course.course_title = course_title
        if course_description is not None:
            course.course_description = course_description
        if generated_text is not None:
            course.generated_text = generated_text
        if visibility is not None:
            course.visibility = visibility
        
        db.commit()
        db.refresh(course)
        return course, None
    except Exception as e:
        db.rollback()
        return None, f"更新课程失败: {str(e)}"


def delete_course(db: Session, course_id: int) -> Tuple[Optional[models.Course], Optional[str]]:
    """删除课程"""
    course = get_course_by_id(db, course_id)
    if not course:
        return None, "课程不存在"
    
    try:
        db.delete(course)
        db.commit()
        return course, None
    except Exception as e:
        db.rollback()
        return None, f"删除课程失败: {str(e)}"


# ========================
# AI 反馈相关 CRUD
# ========================

def create_ai_feedback(
    db: Session,
    *,
    chat_id: str,
    session_id: str,
    user_id: Optional[str],
    question: str,
    answer: Optional[str],
    feedback_type: str = "null",
):
    # 生成comment_id：从100开始，查找当前最大的comment_id
    max_comment_id = db.query(func.coalesce(func.max(models.AiFeedback.comment_id), 99)).scalar()
    next_comment_id = max_comment_id + 1
    
    record = models.AiFeedback(
        chat_id=chat_id,
        session_id=session_id,
        user_id=user_id,
        question=question,
        answer=answer or "",
        feedback_type=(feedback_type or "null"),
        comment_id=next_comment_id,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record, None
    except Exception as e:
        db.rollback()
        return None, str(e)


def update_ai_feedback_type(db: Session, *, feedback_id: int, feedback_type: str):
    record = db.query(models.AiFeedback).filter(models.AiFeedback.id == feedback_id).first()
    if not record:
        return None, "feedback_not_found"
    try:
        record.feedback_type = feedback_type
        db.commit()
        db.refresh(record)
        return record, None
    except Exception as e:
        db.rollback()
        return None, str(e)


def update_ai_feedback_by_comment_id(db: Session, *, comment_id: int, feedback_type: str):
    record = db.query(models.AiFeedback).filter(models.AiFeedback.comment_id == comment_id).first()
    if not record:
        return None, "feedback_not_found"
    try:
        record.feedback_type = feedback_type
        db.commit()
        db.refresh(record)
        return record, None
    except Exception as e:
        db.rollback()
        return None, str(e)


def get_ai_feedback_records(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    feedback_type: Optional[str] = None,
    user_id: Optional[str] = None,
    comment_id: Optional[int] = None
):
    """获取AI反馈记录列表"""
    query = db.query(models.AiFeedback)
    
    # 根据comment_id过滤（优先级最高）
    if comment_id is not None:
        query = query.filter(models.AiFeedback.comment_id == comment_id)
    
    # 根据feedback_type过滤
    if feedback_type:
        query = query.filter(models.AiFeedback.feedback_type == feedback_type)
    
    # 根据user_id过滤
    if user_id:
        query = query.filter(models.AiFeedback.user_id == user_id)
    
    # 按创建时间倒序排列
    query = query.order_by(models.AiFeedback.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    records = query.offset(skip).limit(limit).all()
    
    return records, total, None


def get_ai_feedback_stats(db: Session):
    """获取AI反馈统计信息"""
    try:
        # 获取总体统计
        total_count = db.query(models.AiFeedback).count()
        good_count = db.query(models.AiFeedback).filter(models.AiFeedback.feedback_type == "good").count()
        not_satisfied_count = db.query(models.AiFeedback).filter(models.AiFeedback.feedback_type == "not satisfied").count()
        
        # 获取差评问题列表
        not_satisfied_questions_raw = db.query(
            models.AiFeedback.question,
            models.AiFeedback.answer,
            models.AiFeedback.comment_id,
            models.AiFeedback.created_at
        ).filter(
            models.AiFeedback.feedback_type == "not satisfied"
        ).order_by(
            models.AiFeedback.created_at.desc()
        ).all()
        
        # 将元组转换为字典格式
        not_satisfied_questions = []
        for question, answer, comment_id, created_at in not_satisfied_questions_raw:
            not_satisfied_questions.append({
                "question": question,
                "answer": answer,
                "comment_id": comment_id,
                "created_at": created_at
            })
        
        return {
            "total_count": total_count,
            "good_count": good_count,
            "not_satisfied_count": not_satisfied_count,
            "not_satisfied_questions": not_satisfied_questions
        }, None
    except Exception as e:
        return None, str(e)


def get_ai_feedback_by_comment_id(db: Session, comment_id: int):
    """根据comment_id获取AI反馈记录"""
    record = db.query(models.AiFeedback).filter(models.AiFeedback.comment_id == comment_id).first()
    if not record:
        return None, "feedback_not_found"
    return record, None


def update_ai_feedback_content(
    db: Session, 
    *, 
    comment_id: int, 
    question: str, 
    answer: str
):
    """根据comment_id更新AI反馈记录的问题和答案"""
    record = db.query(models.AiFeedback).filter(models.AiFeedback.comment_id == comment_id).first()
    if not record:
        return None, "feedback_not_found"
    try:
        record.question = question
        record.answer = answer
        db.commit()
        db.refresh(record)
        return record, None
    except Exception as e:
        db.rollback()
        return None, str(e)


def delete_ai_feedback_by_comment_id(db: Session, comment_id: int):
    """根据comment_id删除AI反馈记录"""
    record = db.query(models.AiFeedback).filter(models.AiFeedback.comment_id == comment_id).first()
    if not record:
        return None, "feedback_not_found"
    try:
        db.delete(record)
        db.commit()
        return record, None
    except Exception as e:
        db.rollback()
        return None, str(e)