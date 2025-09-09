from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from .. import crud, schemas, auth
from ..database import get_db
from ..auth import get_current_user
from typing import List

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    要求：
    - 用户名至少3个字符
    - 密码至少6个字符
    - 邮箱格式正确（可选）
    """
    try:
        # 创建用户
        db_user, error_msg = crud.create_user(db, user)
        
        if error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/login", response_model=schemas.TokenResponse)
async def login_user(user_credentials: schemas.UserLoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    try:
        # 验证用户
        user = crud.authenticate_user(db, user_credentials.username, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户已被禁用"
            )
        
        # 创建访问令牌
        access_token = auth.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "user_id": user.id,
            "role": user.role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@router.get("/users", response_model=List[schemas.UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    获取用户列表（管理员功能）
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserRegisterRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    创建新用户（管理员功能）
    """
    try:
        # 创建用户
        db_user, error_msg = crud.create_user(db, user)
        
        if error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    获取单个用户信息
    """
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int, 
    user_update: schemas.UserUpdateRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    修改用户账户信息
    
    可以修改：
    - 用户名
    - 邮箱
    - 密码
    - 账户状态（启用/禁用）
    """
    try:
        # 更新用户信息
        db_user, error_msg = crud.update_user(db, user_id, user_update)
        
        if error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户失败: {str(e)}"
        )

@router.patch("/users/{user_id}/toggle-status", response_model=schemas.UserResponse)
async def toggle_user_status(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    切换用户状态（启用/禁用）
    """
    try:
        # 获取用户
        user = crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 切换状态
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换用户状态失败: {str(e)}"
        )

@router.delete("/users/{user_id}", response_model=schemas.UserDeleteResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    删除用户账户
    
    注意：此操作不可逆，删除后用户数据将永久丢失
    """
    try:
        # 删除用户
        deleted_user, error_msg = crud.delete_user(db, user_id)
        
        if error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        return {
            "message": "用户删除成功",
            "deleted_user": deleted_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )

# =============== 头像接口 ===============
@router.post("/users/{user_id}/avatar", response_model=schemas.AvatarUploadResponse)
async def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    上传用户头像到数据库（二进制存储）。
    - Content-Type: multipart/form-data
    - 表单字段名: file
    - 只允许图片类型（image/*）
    - 建议最大 2MB
    """
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="仅支持图片文件")
        data = await file.read()
        if len(data) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片大小不能超过2MB")
        user, err = crud.set_user_avatar(db, user_id, data=data, mime=file.content_type)
        if err:
            raise HTTPException(status_code=404 if err == "user_not_found" else 500, detail=err)
        return {
            "message": "头像上传成功",
            "user_id": user.id,
            "avatar": {"mime": user.avatar_mime or file.content_type, "size": user.avatar_size or len(data)}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {e}")

@router.get("/users/{user_id}/avatar")
async def get_avatar(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """获取用户头像二进制（直接返回图片）。"""
    data, mime, size = crud.get_user_avatar(db, user_id)
    if data is None:
        raise HTTPException(status_code=404, detail="头像不存在")
    return Response(content=data, media_type=mime or "application/octet-stream")


