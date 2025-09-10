from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Query, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import traceback
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4

# 导入认证相关模块
from app.routers import auth
from app.database import engine, SessionLocal
from app import models
from app import crud
from app import schemas
from app.auth import get_current_user
from sqlalchemy.orm import Session

# 加载环境变量（始终指向 backend/config.env）
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
load_dotenv(str(BASE_DIR / 'config.env'))

# 注意：数据库表创建已移到启动脚本中，避免启动时的连接错误

app = FastAPI(title="课程工作流后端服务", version="1.0.0")

# 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")

# 数据模型
class CourseData(BaseModel):
    title: str
    description: str
    visibility: str = "draft"

class CourseDataForm(BaseModel):
    title: str
    description: str
    visibility: str = "draft"

class DifyWorkflowRequest(BaseModel):
    inputs: dict
    response_mode: str = "blocking"
    user: str = "web_user"

class RunWorkflowWithFileRequest(BaseModel):
    upload_file_id: str
    # 其余参数全部可选，不传时用环境变量默认值
    user: Optional[str] = None
    variable_name: Optional[str] = None
    document_type: Optional[str] = None  # document/image/audio/video
    response_mode: Optional[str] = None
    inputs: Optional[dict] = None


class RunWorkflowWithTextRequest(BaseModel):
    text_input: str
    # 其余参数全部可选，不传时用环境变量默认值
    user: Optional[str] = None
    variable_name: Optional[str] = "text_input"  # 默认的文本输入变量名
    response_mode: Optional[str] = "blocking"  # 默认阻塞模式
    inputs: Optional[dict] = None

# ========== 新增：Dify 工作台（文本触发）请求模型 ==========
class DifyWorkbenchTextRequest(BaseModel):
    """用于对接新的 Dify 工作台：用户输入文本并启动运行"""
    query: str
    inputs: Optional[dict] = None
    response_mode: Optional[str] = "blocking"  # 或 "streaming"
    user: Optional[str] = None

# ========== 新增：Dify 注释API请求和响应模型 ==========
class DifyAnnotationRequest(BaseModel):
    """用于向Dify AI平台发送注释数据的请求模型"""
    question: str
    answer: str

class DifyAnnotationResponse(BaseModel):
    """Dify注释API的响应模型"""
    id: str
    question: str
    answer: str
    hit_count: int
    created_at: int

def build_workflow_inputs(file_id: str, filename: str, user: str, extra_params: dict = None) -> dict:
    """
    构建工作流输入参数
    """
    import json
    
    # 基础文件参数
    inputs = {
        DIFY_FILE_VARIABLE_NAME: {
            "transfer_method": "local_file",
            "upload_file_id": file_id,
            "type": DIFY_FILE_DOCUMENT_TYPE,
        },
        # 添加工作流可能需要的其他参数
        "title": filename,  # 使用文件名作为标题
        "filename": filename,  # 文件名
        "user": user,  # 用户信息
    }
    
    # 添加环境变量中配置的额外参数
    try:
        if DIFY_WORKFLOW_EXTRA_PARAMS and DIFY_WORKFLOW_EXTRA_PARAMS != "{}":
            extra_config = json.loads(DIFY_WORKFLOW_EXTRA_PARAMS)
            inputs.update(extra_config)
    except json.JSONDecodeError:
        print(f"警告: 无法解析 DIFY_WORKFLOW_EXTRA_PARAMS: {DIFY_WORKFLOW_EXTRA_PARAMS}")
    
    # 添加传入的额外参数
    if extra_params:
        inputs.update(extra_params)
    
    return inputs

# Dify API配置
# 为了分别控制“工作流/生成文章”和“文件上传”，支持多套密钥
WORKFLOW_KEY_DEFAULT = "your-workflow-api-key-here"
UPLOAD_KEY_DEFAULT = "your-upload-api-key-here"
FILE_WORKFLOW_KEY_DEFAULT = "your-file-workflow-api-key-here"

DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")

# 可选：按你截图的“SORT”风格提供更细分的覆盖项（若设置则优先使用）
DIFY_SORT_UPLOAD_URL = os.getenv("DIFY_SORT_UPLOAD_URL")
DIFY_SORT_WORKFLOW_URL = os.getenv("DIFY_SORT_WORKFLOW_URL")
DIFY_SORT_API_KEY = os.getenv("DIFY_SORT_API_KEY")

# 运行工作流（含文件）默认配置，可通过环境变量修改
DIFY_DEFAULT_USER = os.getenv("DIFY_DEFAULT_USER", "web_user")
DIFY_FILE_VARIABLE_NAME = os.getenv("DIFY_FILE_VARIABLE_NAME", "file_input")
DIFY_FILE_DOCUMENT_TYPE = os.getenv("DIFY_FILE_DOCUMENT_TYPE", "document")

# 工作流额外参数配置（JSON格式字符串）
DIFY_WORKFLOW_EXTRA_PARAMS = os.getenv("DIFY_WORKFLOW_EXTRA_PARAMS", "{}")

  # 工作流（生成文章）密钥：优先读取 DIFY_WORKFLOW_API_KEY；若未设置则回退到 DIFY_API_KEY
DIFY_WORKFLOW_API_KEY = os.getenv(
    "DIFY_WORKFLOW_API_KEY",
    os.getenv("DIFY_API_KEY", WORKFLOW_KEY_DEFAULT),
)

# 上传密钥：优先读取 DIFY_UPLOAD_API_KEY；若未设置则回退到 DIFY_API_KEY
DIFY_UPLOAD_API_KEY = os.getenv(
    "DIFY_UPLOAD_API_KEY",
    os.getenv("DIFY_API_KEY", UPLOAD_KEY_DEFAULT),
)

# 文件驱动的工作流密钥：优先读取 DIFY_FILE_WORKFLOW_API_KEY；若未设置则回退到 DIFY_WORKFLOW_API_KEY
DIFY_FILE_WORKFLOW_API_KEY = os.getenv(
    "DIFY_FILE_WORKFLOW_API_KEY",
    os.getenv("DIFY_WORKFLOW_API_KEY", FILE_WORKFLOW_KEY_DEFAULT),
)

# 文本驱动的工作流密钥：优先读取 DIFY_TEXT_WORKFLOW_API_KEY；若未设置则回退到 DIFY_WORKFLOW_API_KEY
DIFY_TEXT_WORKFLOW_API_KEY = os.getenv(
    "DIFY_TEXT_WORKFLOW_API_KEY",
    os.getenv("DIFY_WORKFLOW_API_KEY", FILE_WORKFLOW_KEY_DEFAULT),
)

# 草稿解锁密钥（放在后端环境变量）
COURSE_DRAFT_SECRET = os.getenv("COURSE_DRAFT_SECRET", "123456")
# 付费文档访问密钥（查看/下载/删除前校验）
PAID_DOCUMENT_SECRET = os.getenv("PAID_DOCUMENT_SECRET", "paid123")

# 聊天助手（创建会话）转发配置
CHAT_ASSISTANT_BASE_URL = os.getenv("CHAT_ASSISTANT_BASE_URL", "http://localhost")
CHAT_ASSISTANT_API_KEY = os.getenv(
    "CHAT_ASSISTANT_API_KEY",
    # 默认使用你提供的APIKEY，建议线上改为环境变量
    "ragflow-diOGQ3M2UwODQ3NzExZjA5Y2I3YjZiMT",
)

# Dify注释API配置
DIFY_ANNOTATION_BASE_URL = os.getenv("DIFY_ANNOTATION_BASE_URL", "http://localhost/v1")
DIFY_ANNOTATION_API_KEY = os.getenv(
    "DIFY_ANNOTATION_API_KEY",
    # 默认使用你提供的APIKEY，建议线上改为环境变量
    "app-V9CLtE61GyYyUGW7PA1ffrWB",
)

 

@app.get("/", tags=["system"])
def root():
    return {"msg": "Course Workflow API is running"}

# 新增：草稿密钥校验接口
@app.post("/api/courses/draft/verify", tags=["courses"])
def verify_draft_secret(secret: str = Form(...)):
    if not secret:
        raise HTTPException(status_code=400, detail="缺少密钥")
    if secret == COURSE_DRAFT_SECRET:
        return {"code": 200, "message": "验证通过"}
    raise HTTPException(status_code=401, detail="密钥错误")



# ========================
# 新的 Dify 工作台：文本触发运行
# ========================

# ========================
# Dify 注释API接口
# ========================

@app.post("/api/annotations/{comment_id}/upload-to-dify", tags=["annotations"])
def upload_annotation_to_dify(comment_id: int):
    """
    根据comment_id将AI回复上传到Dify标注平台
    
    用于将本地数据库中已存在的好的AI回复上传到Dify进行标注
    """
    try:
        print(f"=== 开始将comment_id={comment_id}的回复上传到Dify标注平台 ===")
        
        # 从本地数据库获取记录
        db = SessionLocal()
        try:
            record, err = crud.get_ai_feedback_by_comment_id(db, comment_id)
            
            if err == "feedback_not_found":
                raise HTTPException(status_code=404, detail=f"未找到comment_id为{comment_id}的注释记录")
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            print(f"找到记录: question={record.question[:50]}..., answer={record.answer[:50]}...")
            
            # 构建请求URL
            annotation_url = f"{DIFY_ANNOTATION_BASE_URL.rstrip('/')}/apps/annotations"
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {DIFY_ANNOTATION_API_KEY}",
                "Content-Type": "application/json",
            }
            
            # 构建请求体
            payload = {
                "question": record.question,
                "answer": record.answer,
            }
            
            print(f"请求URL: {annotation_url}")
            print(f"使用的API密钥: {DIFY_ANNOTATION_API_KEY[:10]}...")
            
            # 发送请求到Dify
            response = requests.post(
                annotation_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"Dify注释API响应状态码: {response.status_code}")
            print(f"Dify注释API响应内容: {response.text}")
            
            if response.status_code in (200, 201):
                try:
                    result = response.json()
                    print("注释数据成功上传到Dify标注平台")
                    
                    # 更新本地记录状态（可选：标记为已上传）
                    # 这里可以添加一个字段来标记是否已上传到Dify
                    
                    return {
                        "code": 200,
                        "message": "成功上传到Dify标注平台",
                        "data": {
                            "comment_id": comment_id,
                            "dify_id": result.get("id", ""),
                            "question": record.question,
                            "answer": record.answer,
                            "hit_count": result.get("hit_count", 0),
                            "created_at": result.get("created_at", int(datetime.now().timestamp())),
                            "uploaded_at": int(datetime.now().timestamp())
                        }
                    }
                except Exception as e:
                    print(f"解析响应JSON失败: {e}")
                    raise HTTPException(status_code=500, detail=f"解析响应失败: {str(e)}")
            else:
                error_msg = f"Dify注释API错误 (状态码: {response.status_code}): {response.text}"
                print(f"API错误: {error_msg}")
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
        finally:
            db.close()
            
    except HTTPException:
        raise
    except requests.exceptions.Timeout as e:
        error_msg = "请求超时，请稍后重试"
        print(f"超时错误: {error_msg}")
        raise HTTPException(status_code=408, detail=error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"网络请求错误: {str(e)}"
        print(f"网络错误: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"服务器内部错误: {str(e)}"
        print(f"未预期的错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/annotations/{comment_id}", tags=["annotations"])
def get_dify_annotation_by_id(comment_id: int):
    """
    根据comment_id获取特定的Dify注释记录
    
    从ai_feedback表中查询对应的注释数据
    """
    try:
        print(f"=== 开始查询注释记录: comment_id={comment_id} ===")
        
        db = SessionLocal()
        try:
            # 从ai_feedback表中查询记录
            record, err = crud.get_ai_feedback_by_comment_id(db, comment_id)
            
            if err == "feedback_not_found":
                raise HTTPException(status_code=404, detail=f"未找到comment_id为{comment_id}的注释记录")
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            print(f"成功查询到注释记录: comment_id={comment_id}")
            
            # 返回标准化的响应格式
            return {
                "code": 200,
                "message": "查询成功",
                "data": {
                    "id": str(record.comment_id),  # 使用comment_id作为id
                    "question": record.question or "",
                    "answer": record.answer or "",
                    "hit_count": 0,  # ai_feedback表中没有hit_count字段，设为0
                    "created_at": int(record.created_at.timestamp()) if record.created_at else 0,
                    "feedback_type": record.feedback_type,
                    "user_id": record.user_id,
                    "chat_id": record.chat_id,
                    "session_id": record.session_id
                }
            }
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"查询注释记录时发生错误: {str(e)}"
        print(f"异常错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.put("/api/annotations/{comment_id}", tags=["annotations"])
def update_dify_annotation_by_id(comment_id: int, body: DifyAnnotationRequest):
    """
    根据comment_id更新特定的Dify注释记录
    
    更新ai_feedback表中的question和answer字段
    """
    try:
        print(f"=== 开始更新注释记录: comment_id={comment_id} ===")
        
        # 验证输入数据
        if not body.question or not body.question.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")
        if not body.answer or not body.answer.strip():
            raise HTTPException(status_code=400, detail="答案不能为空")
        
        print(f"更新数据: question={body.question[:50]}..., answer={body.answer[:50]}...")
        
        db = SessionLocal()
        try:
            # 首先检查记录是否存在
            record, err = crud.get_ai_feedback_by_comment_id(db, comment_id)
            
            if err == "feedback_not_found":
                raise HTTPException(status_code=404, detail=f"未找到comment_id为{comment_id}的注释记录")
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            # 更新记录
            updated_record, err = crud.update_ai_feedback_content(
                db, 
                comment_id=comment_id,
                question=body.question,
                answer=body.answer
            )
            
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            print(f"成功更新注释记录: comment_id={comment_id}")
            
            # 返回标准化的响应格式
            return {
                "code": 200,
                "message": "更新成功",
                "data": {
                    "id": str(updated_record.comment_id),
                    "question": updated_record.question,
                    "answer": updated_record.answer,
                    "hit_count": 0,
                    "created_at": int(updated_record.created_at.timestamp()) if updated_record.created_at else 0,
                    "feedback_type": updated_record.feedback_type,
                    "user_id": updated_record.user_id,
                    "chat_id": updated_record.chat_id,
                    "session_id": updated_record.session_id
                }
            }
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"更新注释记录时发生错误: {str(e)}"
        print(f"异常错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.delete("/api/annotations/{comment_id}", tags=["annotations"])
def delete_dify_annotation_by_id(comment_id: int):
    """
    根据comment_id删除特定的Dify注释记录
    
    从ai_feedback表中删除对应的记录
    """
    try:
        print(f"=== 开始删除注释记录: comment_id={comment_id} ===")
        
        db = SessionLocal()
        try:
            # 首先检查记录是否存在
            record, err = crud.get_ai_feedback_by_comment_id(db, comment_id)
            
            if err == "feedback_not_found":
                raise HTTPException(status_code=404, detail=f"未找到comment_id为{comment_id}的注释记录")
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            # 删除记录
            deleted_record, err = crud.delete_ai_feedback_by_comment_id(db, comment_id)
            
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            print(f"成功删除注释记录: comment_id={comment_id}")
            
            return {
                "code": 200,
                "message": "删除成功",
                "data": {
                    "deleted_id": str(deleted_record.comment_id),
                    "question": deleted_record.question,
                    "answer": deleted_record.answer
                }
            }
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"删除注释记录时发生错误: {str(e)}"
        print(f"异常错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/workbench/run-text", tags=["workbench"])
def run_dify_workbench_with_text(body: DifyWorkbenchTextRequest):
    """
    将用户输入的纯文本转发到 Dify 新工作台（/chat-messages），并启动执行。

    - 使用固定的工作台 API Key（如需安全，请改为读取环境变量）。
    - 支持可选 inputs 与 response_mode；默认阻塞模式。
    - 直接透传 Dify 返回结果。
    """
    try:
        if not body.query or not str(body.query).strip():
            raise HTTPException(status_code=400, detail="query 不能为空")

        # 优先使用环境变量，否则使用你提供的密钥（仅后端保存）
        effective_key = os.getenv("DIFY_WORKBENCH_API_KEY", "app-V9CLtE61GyYyUGW7PA1ffrWB")

        # 基础 URL：优先环境变量；若未设置，默认指向本地 http://localhost/v1
        # 这样可避免将本地 App-Key 发送到云端造成 401
        base_url = os.getenv("DIFY_WORKBENCH_BASE_URL", os.getenv("DIFY_BASE_URL", "http://localhost/v1"))
        target_url = f"{base_url.rstrip('/')}/chat-messages"

        # 规范 response_mode
        response_mode = body.response_mode if body.response_mode in ("blocking", "streaming") else "blocking"
        user_value = (body.user or DIFY_DEFAULT_USER)

        headers = {
            "Authorization": f"Bearer {effective_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": body.inputs or {},
            "query": body.query,
            "response_mode": response_mode,
            "user": user_value,
        }

        resp = requests.post(target_url, headers=headers, json=payload, timeout=180)
        if resp.status_code in (200, 201):
            try:
                result_json = resp.json()
                # 写入 ai_feedback 表
                try:
                    db = SessionLocal()
                    try:
                        # 提取 answer
                        answer_text = None
                        if isinstance(result_json, dict):
                            data_obj = result_json.get("data") or {}
                            if isinstance(data_obj, dict):
                                answer_text = data_obj.get("answer") or data_obj.get("content") or data_obj.get("text")
                            if not answer_text:
                                answer_text = result_json.get("answer") or result_json.get("content") or result_json.get("text")
                            if not answer_text:
                                msgs = result_json.get("messages") or []
                                if isinstance(msgs, list) and msgs:
                                    last = msgs[-1] or {}
                                    inner = last.get("data") or {}
                                    answer_text = inner.get("answer") or last.get("content") or last.get("text")

                        # 生成 chat_id / session_id
                        chat_id = "workbench"
                        session_id = (
                            (result_json.get("conversation_id") if isinstance(result_json, dict) else None)
                            or f"session_{uuid4().hex}"
                        )

                        rec, err = crud.create_ai_feedback(
                            db,
                            chat_id=chat_id,
                            session_id=session_id,
                            user_id=payload.get("user"),
                            question=payload.get("query", ""),
                            answer=answer_text,
                            feedback_type="null",
                        )
                        if not err and isinstance(result_json, dict):
                            # 将 comment_id 回写到响应
                            if "data" in result_json and isinstance(result_json["data"], dict):
                                result_json["data"]["comment_id"] = rec.comment_id
                            else:
                                result_json["comment_id"] = rec.comment_id
                    finally:
                        db.close()
                except Exception:
                    import traceback as _tb
                    print("[workbench ai_feedback] 捕获到异常但忽略:\n" + _tb.format_exc())
                return result_json
            except Exception:
                return {"code": resp.status_code, "data": resp.text}
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/course/workflow", tags=["courses"])
async def start_course_workflow(
    title: str = Form(..., description="课程标题"),
    description: str = Form(..., description="课程描述"),
    visibility: str = Form("draft", description="可见性"),
    current_user: str = Form("web_user", description="用户名（未登录时使用默认值）")
):
    """
    启动课程创建工作流并将数据存储到数据库
    """
    try:
        print("=== 开始处理课程工作流请求 ===")
        
        # 验证配置（工作流密钥）
        if DIFY_WORKFLOW_API_KEY == WORKFLOW_KEY_DEFAULT:
            error_msg = "Dify API密钥未配置，请在config.env文件中设置DIFY_API_KEY"
            print(f"配置错误: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        print(f"接收到课程数据: title={title}, description={description}, visibility={visibility}")
        print(f"当前用户: {current_user}")
        print(f"使用配置 - WORKFLOW_KEY: {DIFY_WORKFLOW_API_KEY[:10]}..., BASE_URL: {DIFY_BASE_URL}")
        
        # 构建发送到Dify的数据
        dify_request = DifyWorkflowRequest(
            inputs={
                "title": title,
                "CourseDescription": description,
                "visibility": visibility
            },
            response_mode="blocking",
            user=current_user
        )
        
        print(f"构建的Dify请求: {dify_request.dict()}")
        
        # 发送请求到Dify
        # 选择实际使用的工作流密钥：优先 SORT_API_KEY 其后回退到工作流密钥 
        effective_workflow_key = DIFY_SORT_API_KEY or DIFY_WORKFLOW_API_KEY

        headers = {
            "Authorization": f"Bearer {effective_workflow_key}",
            "Content-Type": "application/json"
        }
        
        # Dify 文档（截图）显示执行工作流为 POST /workflows/run
        workflow_url = DIFY_SORT_WORKFLOW_URL or f"{DIFY_BASE_URL}/workflows/run"
        print(f"请求URL: {workflow_url}")
        print(f"请求头: {headers}")
        
        print("正在发送请求到Dify...")
        response = requests.post(
            workflow_url,
            headers=headers,
            json=dify_request.dict(),
            timeout=120  # 2分钟超时
        )
        
        print(f"Dify响应状态码: {response.status_code}")
        print(f"Dify响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("工作流启动成功")
            
            # 从Dify响应中提取生成的文本
            generated_text = ""
            try:
                data = result.get("data", {})
                outputs = data.get("outputs", {})
                generated_text = outputs.get("text", "")
                print(f"提取的生成文本: {generated_text[:100]}...")  # 只打印前100个字符
            except Exception as e:
                print(f"提取生成文本时出错: {e}")
                generated_text = "文本生成失败"
            
            # 将课程数据存储到数据库
            db = SessionLocal()
            try:
                course, error = crud.create_course(
                    db,
                    course_title=title,
                    course_description=description,
                    generated_text=generated_text,
                    username=current_user,
                    visibility=visibility
                )
                
                if error:
                    print(f"保存课程到数据库失败: {error}")
                    # 即使保存失败，也返回工作流成功的结果
                    return {
                        "success": True,
                        "message": "工作流启动成功，但保存到数据库失败",
                        "workflow_run_id": result.get("workflow_run_id"),
                        "task_id": result.get("task_id"),
                        "data": result.get("data", {}),
                        "database_error": error
                    }
                else:
                    print(f"课程已成功保存到数据库，ID: {course.id}")
                    return {
                        "success": True,
                        "message": "工作流启动成功，课程已保存到数据库",
                        "workflow_run_id": result.get("workflow_run_id"),
                        "task_id": result.get("task_id"),
                        "data": result.get("data", {}),
                        "course_id": course.id
                    }
            finally:
                db.close()
        else:
            error_msg = f"Dify API错误 (状态码: {response.status_code}): {response.text}"
            print(f"API错误: {error_msg}")
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
    except requests.exceptions.Timeout as e:
        error_msg = "请求超时，工作流执行时间过长"
        print(f"超时错误: {error_msg}")
        print(f"异常详情: {str(e)}")
        raise HTTPException(status_code=408, detail=error_msg)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"网络请求错误: {str(e)}"
        print(f"网络错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
        
    except Exception as e:
        error_msg = f"服务器内部错误: {str(e)}"
        print(f"未预期的错误: {error_msg}")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


# 注意：原来的 /api/files/upload 接口已被移除
# 现在使用 /api/documents 接口进行文件上传和自动分类


@app.get("/api/files/status", tags=["system"])
def get_upload_status():
    """
    获取文件上传服务状态
    """
    return {
        "status": "running",
        "base_url": DIFY_BASE_URL,
        "workflow_api_configured": DIFY_WORKFLOW_API_KEY != WORKFLOW_KEY_DEFAULT,
        "upload_api_configured": DIFY_UPLOAD_API_KEY != UPLOAD_KEY_DEFAULT,
        "file_workflow_api_configured": DIFY_FILE_WORKFLOW_API_KEY != FILE_WORKFLOW_KEY_DEFAULT,
    }


@app.post("/api/paid/verify", tags=["system"])
def verify_paid_secret(secret: str = Form("", description="付费资源访问密钥")):
    """
    校验付费资源访问密钥。前端在执行查看/下载/删除等操作前调用。
    """
    try:
        if not secret or secret.strip() == "":
            raise HTTPException(status_code=400, detail="密钥不能为空")
        if secret == PAID_DOCUMENT_SECRET:
            return {"code": 200, "message": "验证通过"}
        raise HTTPException(status_code=401, detail="密钥不正确")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents", tags=["documents"])
def get_documents_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    username: Optional[str] = Query(None, description="按用户名筛选"),
    filename: Optional[str] = Query(None, description="按文件名筛选")
):
    """
    获取文档列表，支持分页和筛选
    """
    db = SessionLocal()
    try:
        documents, total = crud.get_documents_list(
            db, 
            skip=skip, 
            limit=limit, 
            username=username, 
            filename=filename
        )
        
        # 转换为可序列化的格式
        result = []
        for doc in documents:
            result.append({
                "id": doc.id,
                "filename": doc.filename,
                "username": doc.username,
                "dify_file_id": doc.dify_file_id,
                "classification": doc.classification,
                "status": doc.status,
                "access": doc.access,
                "upload_time": doc.upload_time.isoformat() if doc.upload_time else None,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "file_path": doc.file_path
            })
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "documents": result,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    finally:
        db.close()


# 更新AI反馈的类型（good 或 not not satisfied）
@app.put("/api/v1/ai-feedback/{comment_id}", tags=["ai-feedback"])
def update_ai_feedback(comment_id: int, body: schemas.AiFeedbackUpdate):
    try:
        db = SessionLocal()
        try:
            record, err = crud.update_ai_feedback_by_comment_id(db, comment_id=comment_id, feedback_type=body.feedback_type)
            if err == "feedback_not_found":
                raise HTTPException(status_code=404, detail="反馈记录不存在")
            if err:
                raise HTTPException(status_code=500, detail=err)
            return {
                "code": 200,
                "message": "反馈已更新",
                "data": {
                    "id": record.id,
                    "comment_id": record.comment_id,
                    "feedback_type": record.feedback_type,
                }
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 获取AI反馈记录列表
@app.get("/api/v1/ai-feedback/records", response_model=schemas.AiFeedbackListResponse, tags=["ai-feedback"])
def get_ai_feedback_records(
    skip: int = 0,
    limit: int = 100,
    feedback_type: Optional[str] = None,
    user_id: Optional[str] = None,
    comment_id: Optional[int] = None
):
    """获取AI反馈记录列表"""
    try:
        db = SessionLocal()
        try:
            records, total, err = crud.get_ai_feedback_records(
                db, 
                skip=skip, 
                limit=limit, 
                feedback_type=feedback_type, 
                user_id=user_id,
                comment_id=comment_id
            )
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            return {
                "code": 200,
                "message": "获取成功",
                "data": records,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 获取AI反馈统计信息
@app.get("/api/v1/ai-feedback/stats", response_model=schemas.AiFeedbackStatsResponse, tags=["ai-feedback"])
def get_ai_feedback_stats():
    """获取AI反馈统计信息"""
    try:
        db = SessionLocal()
        try:
            stats, err = crud.get_ai_feedback_stats(db)
            if err:
                raise HTTPException(status_code=500, detail=err)
            
            return {
                "code": 200,
                "message": "获取成功",
                "data": stats
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{dify_file_id}/text", tags=["documents"])
def get_document_plain_text(dify_file_id: str):
    """
    返回文档的纯文本内容（当前支持 .txt 与 .docx）。
    用于前端在线预览 docx/txt 原文。
    """
    db = SessionLocal()
    try:
        doc = crud.get_document_by_dify_file_id(db, dify_file_id)
        if not doc:
            raise HTTPException(status_code=404, detail="未找到文档记录")
        if not doc.file_path:
            raise HTTPException(status_code=404, detail="该记录没有保存文件路径")

        file_path = Path(doc.file_path)
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="文件不存在或已被移动")

        suffix = file_path.suffix.lower()
        if suffix == ".txt":
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # 兼容常见的 gbk/gb18030
                content = file_path.read_text(encoding="gb18030", errors="ignore")
            return {"code": 200, "data": {"text": content}}
        elif suffix == ".docx":
            try:
                from docx import Document
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"后端未安装读取docx的依赖: {e}")
            try:
                d = Document(str(file_path))
                text = "\n".join(p.text for p in d.paragraphs)
                return {"code": 200, "data": {"text": text}}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"解析docx失败: {e}")
        else:
            raise HTTPException(status_code=415, detail=f"暂不支持预览该类型: {suffix}")
    finally:
        db.close()

@app.get("/api/documents/{dify_file_id}/download", tags=["documents"])
def download_document(dify_file_id: str):
#def download_document(dify_file_id: str, current_user = Depends(get_current_user)):
    """
    通过 dify_file_id 下载本地存储的原始文件。
    """
    db = SessionLocal()
    try:
        doc = crud.get_document_by_dify_file_id(db, dify_file_id)
        if not doc:
            raise HTTPException(status_code=404, detail="未找到文档记录")
        if not doc.file_path:
            raise HTTPException(status_code=404, detail="该记录没有保存文件路径")

        file_path = Path(doc.file_path)
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="文件不存在或已被移动")

        # 以文件名作为下载名
        download_name = file_path.name
        return FileResponse(
            path=str(file_path),
            filename=download_name,
            media_type="application/octet-stream",
        )
    finally:
        db.close()


@app.put("/api/documents/{dify_file_id}/replace", tags=["documents"])
async def replace_document_file(
    dify_file_id: str,
    file: UploadFile = File(..., description="新的文件内容"),
    access: Optional[str] = Form(None, description="访问权限：FREE 或 PAID"),
    via_dify: bool = Form(False, description="是否上传到Dify并重新分类，默认否"),
    current_user = Depends(get_current_user)
):
    """
    替换现有文档的文件。仅更新数据库中的文件元信息与本地文件，保留原 dify_file_id。
    """
    db = SessionLocal()
    try:
        # 查找原记录
        doc = crud.get_document_by_dify_file_id(db, dify_file_id)
        if not doc:
            raise HTTPException(status_code=404, detail="未找到文档记录")

        # 校验扩展名
        file_extension = Path(file.filename).suffix.lower()
        allowed_exts = [".txt", ".doc", ".docx", ".pdf"]
        if file_extension not in allowed_exts:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_extension}")

        # 保存到 uploads 目录，生成新文件名避免覆盖
        uploads_dir = BASE_DIR / "app" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        new_name = f"repl_{uuid4().hex}{file_extension}"
        target_path = uploads_dir / new_name
        content = await file.read()
        with open(target_path, "wb") as f:
            f.write(content)

        # 更新数据库记录
        from datetime import datetime
        updated_doc, err = crud.update_document_file(
            db,
            dify_file_id=dify_file_id,
            filename=file.filename,
            file_path=str(target_path),
            upload_time=datetime.now(),
            access=access,
        )
        if err:
            raise HTTPException(status_code=500, detail=err)

        # 如果需要走 Dify：上传并触发工作流，然后更新记录
        if via_dify:
            effective_upload_key = DIFY_SORT_API_KEY or DIFY_UPLOAD_API_KEY
            if effective_upload_key == UPLOAD_KEY_DEFAULT:
                raise HTTPException(status_code=500, detail="Dify上传API密钥未配置")

            files = { 'file': (file.filename, content, file.content_type) }
            data = { 'user': current_user if isinstance(current_user, str) else getattr(current_user, 'username', 'web_user') }
            headers = { "Authorization": f"Bearer {effective_upload_key}" }
            upload_url = DIFY_SORT_UPLOAD_URL or f"{DIFY_BASE_URL}/files/upload"
            upload_response = requests.post(upload_url, headers=headers, files=files, data=data, timeout=60)
            if upload_response.status_code not in (200, 201):
                raise HTTPException(status_code=upload_response.status_code, detail=f"文件上传到Dify失败: {upload_response.text}")
            upload_result = upload_response.json()
            new_file_id = upload_result.get("id")

            # 触发工作流
            effective_workflow_key = DIFY_SORT_API_KEY or DIFY_FILE_WORKFLOW_API_KEY
            if effective_workflow_key == FILE_WORKFLOW_KEY_DEFAULT:
                raise HTTPException(status_code=500, detail="Dify工作流API密钥未配置")
            workflow_inputs = build_workflow_inputs(new_file_id, file.filename, data['user'], extra_params={"CourseDescription": file.filename})
            workflow_headers = { "Authorization": f"Bearer {effective_workflow_key}", "Content-Type": "application/json" }
            workflow_url = DIFY_SORT_WORKFLOW_URL or f"{DIFY_BASE_URL}/workflows/run"
            workflow_payload = { "inputs": workflow_inputs, "response_mode": "blocking", "user": data['user'] }
            wf_resp = requests.post(workflow_url, headers=workflow_headers, json=workflow_payload, timeout=180)

            # 更新数据库中的 dify_file_id、classification、status
            try:
                doc = crud.get_document_by_dify_file_id(db, dify_file_id)
                if doc:
                    doc.dify_file_id = new_file_id
                    if wf_resp.status_code == 200:
                        result = wf_resp.json()
                        classification = "未分类"
                        try:
                            outputs = (result or {}).get("data", {}).get("outputs", {})
                            text_output = outputs.get("text", "")
                            if text_output:
                                import json
                                parsed = json.loads(text_output)
                                classification = parsed.get("classification") or parsed.get("type") or classification
                        except Exception:
                            pass
                        doc.classification = classification
                        doc.status = "classified"
                    else:
                        doc.status = "uploaded"
                db.commit()
                db.refresh(doc)
                updated_doc = doc
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))

        return {
            "code": 200,
            "message": "文件已替换" + ("，并已提交Dify重新分类" if via_dify else ""),
            "data": {
                "id": updated_doc.id,
                "filename": updated_doc.filename,
                "dify_file_id": updated_doc.dify_file_id,
                "file_path": updated_doc.file_path,
                "access": updated_doc.access,
                "status": updated_doc.status,
            },
        }
    finally:
        db.close()

@app.post("/api/documents", tags=["documents"])
async def upload_and_classify_document(
    file: UploadFile = File(..., description="要上传的文档文件"),
    access: str = Form("FREE", description="访问权限：FREE 或 PAID"),
    current_user: str = Form("web_user", description="用户名"),
    background_tasks: BackgroundTasks = None
):
    """
    上传文档并自动进行分类
    简化版API，上传文件后自动触发工作流进行分类
    """
    try:
        print("=== 开始处理文档上传和分类请求 ===")
        
        # 验证文件
        if not file:
            raise HTTPException(status_code=400, detail="必须提供文件")
        
        # 检查文件类型（只允许文档类型）
        allowed_extensions = ['.txt', '.pdf', '.doc', '.docx', '.md', '.rtf']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_extension}")
        
        print(f"接收到文档: {file.filename}, 用户: {current_user}, 访问权限: {access}")
        
        # 第一步：将文件保存到本地目录并记录路径
        uploads_dir = BASE_DIR / 'app' / 'uploads'
        os.makedirs(uploads_dir, exist_ok=True)
        safe_filename = file.filename
        local_path = uploads_dir / safe_filename
        # 若同名文件存在，追加序号避免覆盖
        counter = 1
        while local_path.exists():
            stem = os.path.splitext(safe_filename)[0]
            ext = os.path.splitext(safe_filename)[1]
            local_path = uploads_dir / f"{stem}_{counter}{ext}"
            counter += 1

        file_content = await file.read()
        with open(local_path, 'wb') as f:
            f.write(file_content)

        # 第二步：上传文件到Dify
        effective_upload_key = DIFY_SORT_API_KEY or DIFY_UPLOAD_API_KEY
        
        if effective_upload_key == UPLOAD_KEY_DEFAULT:
            raise HTTPException(status_code=500, detail="Dify上传API密钥未配置")
        
        # 准备上传数据
        files = {
            'file': (os.path.basename(str(local_path)), file_content, file.content_type)
        }
        
        data = {
            'user': current_user
        }
        
        headers = {
            "Authorization": f"Bearer {effective_upload_key}"
        }
        
        upload_url = DIFY_SORT_UPLOAD_URL or f"{DIFY_BASE_URL}/files/upload"
        print(f"上传文件到: {upload_url}")
        
        upload_response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            data=data,
            timeout=60
        )
        
        print(f"文件上传响应: {upload_response.status_code}")
        
        if upload_response.status_code not in (200, 201):
            error_msg = f"文件上传失败: {upload_response.status_code} - {upload_response.text}"
            print(error_msg)
            raise HTTPException(status_code=upload_response.status_code, detail=error_msg)
        
        # 获取上传的文件ID
        upload_result = upload_response.json()
        file_id = upload_result.get("id")
        filename = upload_result.get("name")
        
        print(f"文件上传成功，ID: {file_id}")

        # 异步写入“上传记录”到数据库（含本地路径，状态 uploaded）
        def _bg_create_document():
            db = SessionLocal()
            try:
                doc, err = crud.create_document_record(
                    db,
                    filename=filename,
                    file_path=str(local_path),
                    username=current_user,
                    dify_file_id=file_id,
                    upload_time=datetime.now(),
                    access=access,
                )
                if err:
                    print(f"保存文档记录失败: {err}")
                else:
                    print(f"已保存文档记录: id={doc.id}, file_path={doc.file_path}")
            finally:
                db.close()

        if background_tasks is not None:
            background_tasks.add_task(_bg_create_document)
        
        # 第二步：自动触发工作流进行分类
        effective_workflow_key = DIFY_SORT_API_KEY or DIFY_FILE_WORKFLOW_API_KEY
        
        if effective_workflow_key == FILE_WORKFLOW_KEY_DEFAULT:
            raise HTTPException(status_code=500, detail="Dify工作流API密钥未配置")
        
        # 构建工作流请求：自动使用文件名作为 CourseDescription 以满足工作流必填项
        workflow_inputs = build_workflow_inputs(
            file_id,
            filename,
            current_user,
            extra_params={"CourseDescription": filename}
        )
        
        workflow_headers = {
            "Authorization": f"Bearer {effective_workflow_key}",
            "Content-Type": "application/json",
        }
        
        workflow_url = DIFY_SORT_WORKFLOW_URL or f"{DIFY_BASE_URL}/workflows/run"
        workflow_payload = {
            "inputs": workflow_inputs,
            "response_mode": "blocking",
            "user": current_user,
        }
        
        print(f"触发分类工作流: {workflow_url}")
        print(f"工作流输入: {workflow_inputs}")
        print(f"使用的API密钥: {effective_workflow_key[:10]}...")
        print(f"工作流请求头: {workflow_headers}")
        
        workflow_response = requests.post(
            workflow_url,
            headers=workflow_headers,
            json=workflow_payload,
            timeout=180
        )
        
        print(f"工作流响应: {workflow_response.status_code}")
        
        if workflow_response.status_code == 200:
            workflow_result = workflow_response.json()
            print(f"完整的的工作流响应: {workflow_result}")
            print(f"工作流响应的所有键: {list(workflow_result.keys())}")
            
            classification_data = workflow_result.get("data", {})
            print(f"工作流返回的data字段: {classification_data}")
            print(f"data字段的类型: {type(classification_data)}")
            if classification_data:
                print(f"data字段的所有键: {list(classification_data.keys())}")
            
            # 根据工作流输出结构获取分类结果
            # 工作流返回的数据结构: data.outputs.text 包含JSON字符串
            classification = "未分类"
            
            # 尝试从 outputs.text 中获取分类结果
            outputs = classification_data.get("outputs", {})
            text_output = outputs.get("text", "")
            
            print(f"outputs字段: {outputs}")
            print(f"text_output: {text_output}")
            
            if text_output:
                try:
                    # 解析JSON字符串
                    import json
                    parsed_output = json.loads(text_output)
                    print(f"解析后的输出: {parsed_output}")
                    
                    # 获取分类结果
                    classification = parsed_output.get("type", "未分类")
                    print(f"从JSON中提取的分类: {classification}")
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
                    # 如果JSON解析失败，尝试直接使用text_output
                    classification = text_output
            else:
                # 回退到原来的逻辑
                classification = classification_data.get("type", classification_data.get("classification", "未分类"))
            
            print(f"最终解析出的分类结果: {classification}")
            
            # 异步更新分类结果到数据库（状态 classified）
            def _bg_update_document_success():
                db = SessionLocal()
                try:
                    crud.update_document_classification(
                        db,
                        dify_file_id=file_id,
                        classification=classification,
                        dify_workflow_run_id=workflow_result.get("workflow_run_id"),
                        error_message=None,
                        status="classified",
                    )
                finally:
                    db.close()

            if background_tasks is not None:
                background_tasks.add_task(_bg_update_document_success)

            # 构建返回结果
            result = {
                "code": 200,
                "message": "分类成功,已同步至知识库",
                "data": {
                    "filename": filename,
                    "classification": classification,
                    "username": current_user,
                    "access": access,  # 使用前端传递的访问权限
                    "upload_time": upload_result.get("created_at", ""),
                    "file_id": file_id,
                    "workflow_run_id": workflow_result.get("workflow_run_id")
                }
            }
            
            print("文档上传和分类完成")
            return result
            
        else:
            # 工作流失败，但文件上传成功
            error_msg = f"分类失败: {workflow_response.status_code} - {workflow_response.text}"
            print(error_msg)

            # 异步写入失败状态
            def _bg_update_document_failed():
                db = SessionLocal()
                try:
                    crud.update_document_classification(
                        db,
                        dify_file_id=file_id,
                        classification="分类失败",
                        dify_workflow_run_id=None,
                        error_message=error_msg,
                        status="classification_failed",
                    )
                finally:
                    db.close()

            if background_tasks is not None:
                background_tasks.add_task(_bg_update_document_failed)
            
            return {
                "code": 200,
                "message": "文件上传成功，但分类失败",
                "data": {
                    "filename": filename,
                    "classification": "分类失败",
                    "username": current_user,
                    "access": access,  # 使用前端传递的访问权限
                    "file_id": file_id,
                    "error": error_msg
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"处理文档时发生错误: {str(e)}"
        print(f"异常错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/search/query", tags=["search"])
async def search_with_text(body: RunWorkflowWithTextRequest, current_user = Depends(get_current_user)):
    """
    使用用户输入的文本调用 Dify 搜索应用。
    """
    try:
        print("=== 开始处理文本搜索请求 ===")
        
        # 使用文本搜索的 API 密钥
        effective_search_key = DIFY_TEXT_WORKFLOW_API_KEY

        if effective_search_key == FILE_WORKFLOW_KEY_DEFAULT:
            raise HTTPException(status_code=500, detail="搜索API密钥未配置，请设置 DIFY_TEXT_WORKFLOW_API_KEY")

        # 构建搜索请求
        effective_user = body.user or DIFY_DEFAULT_USER
        # 确保 response_mode 是有效值
        if body.response_mode and body.response_mode not in ["blocking", "streaming"]:
            effective_response_mode = "blocking"
        else:
            effective_response_mode = body.response_mode or "blocking"

        headers = {
            "Authorization": f"Bearer {effective_search_key}",
            "Content-Type": "application/json",
        }
        
        # 调用 Dify 搜索接口
        search_url = f"{DIFY_BASE_URL}/chat-messages"
        payload = {
            "inputs": body.inputs or {},
            "query": body.text_input,  # 搜索查询文本
            "response_mode": effective_response_mode,
            "user": effective_user,
        }

        print(f"搜索请求 URL: {search_url}")
        print(f"搜索查询: {body.text_input}")
        print(f"使用的API密钥: {effective_search_key[:10]}...")
        print(f"搜索请求头: {headers}")

        response = requests.post(search_url, headers=headers, json=payload, timeout=180)
        print(f"搜索响应: {response.status_code}")

        if response.status_code == 200:
            search_result = response.json()
            print(f"完整的搜索响应: {search_result}")
            
            return {
                "success": True,
                "message": "搜索成功",
                "data": {
                    "query": body.text_input,
                    "answer": search_result.get("answer", ""),
                    "message_id": search_result.get("message_id"),
                    "conversation_id": search_result.get("conversation_id"),
                    "result": search_result
                }
            }
        else:
            error_msg = f"搜索失败: {response.status_code} - {response.text}"
            print(error_msg)
            raise HTTPException(status_code=response.status_code, detail=error_msg)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"处理搜索请求时发生错误: {str(e)}"
        print(f"异常错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.delete("/api/documents/{dify_file_id}", tags=["documents"])
def delete_document(dify_file_id: str, current_user = Depends(get_current_user)):
    """
    删除文档记录和本地文件
    """
    db = SessionLocal()
    try:
        # 获取文档记录
        doc = crud.get_document_by_dify_file_id(db, dify_file_id)
        if not doc:
            raise HTTPException(status_code=404, detail="未找到文档记录")
        
        # 删除本地文件
        if doc.file_path:
            try:
                file_path = Path(doc.file_path)
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
                    print(f"已删除本地文件: {file_path}")
                else:
                    print(f"本地文件不存在: {file_path}")
            except Exception as e:
                print(f"删除本地文件失败: {e}")
                # 即使本地文件删除失败，也继续删除数据库记录
        
        # 删除数据库记录
        try:
            db.delete(doc)
            db.commit()
            print(f"已删除数据库记录: id={doc.id}, filename={doc.filename}")
        except Exception as e:
            db.rollback()
            print(f"删除数据库记录失败: {e}")
            raise HTTPException(status_code=500, detail=f"删除数据库记录失败: {str(e)}")
        
        return {
            "code": 200,
            "message": "文档删除成功",
            "data": {
                "deleted_id": doc.id,
                "filename": doc.filename,
                "dify_file_id": dify_file_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"删除文档时发生错误: {str(e)}"
        print(f"异常错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        db.close()


@app.put("/api/documents/{dify_file_id}/classification", tags=["documents"])
def update_document_classification(
    dify_file_id: str,
    classification_update: schemas.DocumentClassificationUpdateRequest,
    current_user = Depends(get_current_user)
):
    """
    修改文档分类并存入数据库
    """
    db = SessionLocal()
    try:
        # 获取文档记录
        doc = crud.get_document_by_dify_file_id(db, dify_file_id)
        if not doc:
            raise HTTPException(status_code=404, detail="未找到文档记录")
        
        # 检查权限：只有文档所有者或管理员可以修改分类
        if current_user.role != "admin" and doc.username != current_user.username:
            raise HTTPException(status_code=403, detail="没有权限修改此文档的分类")
        
        # 更新文档分类
        updated_doc, error = crud.update_document_classification_only(
            db, 
            dify_file_id=dify_file_id,
            classification=classification_update.classification
        )
        
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        return {
            "code": 200,
            "message": "文档分类更新成功",
            "data": {
                "id": updated_doc.id,
                "filename": updated_doc.filename,
                "dify_file_id": updated_doc.dify_file_id,
                "classification": updated_doc.classification,
                "status": updated_doc.status,
                "updated_at": updated_doc.updated_at.isoformat() if updated_doc.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"更新文档分类时发生错误: {str(e)}"
        print(f"异常错误: {error_msg}")
        print(f"异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        db.close()


# ========================
# 课程管理相关接口
# ========================

@app.get("/api/courses", tags=["courses"])
def get_courses_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    username: Optional[str] = Query(None, description="按用户名筛选"),
    visibility: Optional[str] = Query(None, description="按可见性筛选")
):
    """
    获取课程列表，支持分页和筛选
    """
    db = SessionLocal()
    try:
        courses, total = crud.get_all_courses(
            db, 
            skip=skip, 
            limit=limit, 
            username=username,
            visibility=visibility
        )
        
        # 转换为可序列化的格式
        result = []
        for course in courses:
            result.append({
                "id": course.id,
                "course_title": course.course_title,
                "course_description": course.course_description,
                "generated_text": course.generated_text,
                "username": course.username,
                "visibility": course.visibility,
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "updated_at": course.updated_at.isoformat() if course.updated_at else None
            })
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "courses": result,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    finally:
        db.close()


@app.get("/api/courses/{course_id}", tags=["courses"])
def get_course_detail(course_id: int, current_user = Depends(get_current_user)):
    """
    获取课程详情
    """
    db = SessionLocal()
    try:
        course = crud.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "id": course.id,
                "course_title": course.course_title,
                "course_description": course.course_description,
                "generated_text": course.generated_text,
                "username": course.username,
                "visibility": course.visibility,
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "updated_at": course.updated_at.isoformat() if course.updated_at else None
            }
        }
    finally:
        db.close()


@app.put("/api/courses/{course_id}", tags=["courses"])
def update_course_info(
    course_id: int,
    course_update: CourseData,
    current_user: str = Form("web_user")
):
    """
    更新课程信息
    """
    db = SessionLocal()
    try:
        # 首先检查课程是否存在
        course = crud.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        # 检查权限（只有课程创建者可以修改）
        if course.username != current_user:
            raise HTTPException(status_code=403, detail="没有权限修改此课程")
        
        # 更新课程信息
        updated_course, error = crud.update_course(
            db,
            course_id,
            course_title=course_update.title,
            course_description=course_update.description,
            visibility=course_update.visibility
        )
        
        if error:
            raise HTTPException(status_code=500, detail=f"更新课程失败: {error}")
        
        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "id": updated_course.id,
                "course_title": updated_course.course_title,
                "course_description": updated_course.course_description,
                "visibility": updated_course.visibility,
                "updated_at": updated_course.updated_at.isoformat() if updated_course.updated_at else None
            }
        }
    finally:
        db.close()


@app.delete("/api/courses/{course_id}", tags=["courses"])
def delete_course_record(
    course_id: int,
    current_user: str = Form("web_user")
):
    """
    删除课程记录
    """
    db = SessionLocal()
    try:
        # 首先检查课程是否存在
        course = crud.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        # 检查权限（只有课程创建者可以删除）
        if course.username != current_user:
            raise HTTPException(status_code=403, detail="没有权限删除此课程")
        
        # 删除课程
        deleted_course, error = crud.delete_course(db, course_id)
        
        if error:
            raise HTTPException(status_code=500, detail=f"删除课程失败: {error}")
        
        return {
            "code": 200,
            "message": "删除成功",
            "data": {
                "deleted_id": deleted_course.id,
                "course_title": deleted_course.course_title
            }
        }
    finally:
        db.close()