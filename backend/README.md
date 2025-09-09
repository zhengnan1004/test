# 课程工作流后端服务

这是一个基于FastAPI的后端服务，用于连接前端表单和Dify工作流平台，并提供用户认证功能。

## 功能

- 用户注册和登录认证
- 接收前端课程数据（标题、描述、可见性）
- 调用Dify API启动工作流
- 返回工作流执行结果

## 配置步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `config.env` 文件，设置数据库连接：

```env
# PostgreSQL数据库连接
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库1

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 配置Dify API

编辑 `config.env` 文件，设置以下参数：

```env
# Dify API密钥 (从Dify平台获取)
DIFY_API_KEY=your-actual-api-key

# Dify API基础URL
DIFY_BASE_URL=https://api.dify.ai/v1

# 工作流ID (从Dify平台获取)
WORKFLOW_ID=your-actual-workflow-id
```

### 3. 获取Dify配置

1. 登录Dify平台
2. 进入你的应用
3. 在API设置中获取API密钥
4. 在工作流设置中获取工作流ID

## 运行服务

### Windows
```bash
start.bat
```

### 手动启动
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API接口

### 用户认证

#### 用户注册
- **POST** `/api/auth/register`
- **请求体**:
  ```json
  {
    "username": "用户名",
    "password": "密码",
    "email": "邮箱（可选）"
  }
  ```
- **验证规则**:
  - 用户名至少3个字符
  - 密码至少6个字符
  - 邮箱格式正确（如果提供）

#### 用户登录
- **POST** `/api/auth/login`
- **请求体**:
  ```json
  {
    "username": "用户名",
    "password": "密码"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "JWT令牌",
    "token_type": "bearer",
    "username": "用户名"
  }
  ```

#### 获取用户列表
- **GET** `/api/auth/users?skip=0&limit=100`

#### 修改用户信息
- **PUT** `/api/auth/users/{user_id}`
- **请求体**:
  ```json
  {
    "username": "新用户名（可选）",
    "email": "新邮箱（可选）",
    "password": "新密码（可选）",
    "is_active": true/false（可选）
  }
  ```
- **说明**: 可以部分更新用户信息，未提供的字段保持不变

#### 删除用户账户
- **DELETE** `/api/auth/users/{user_id}`
- **响应**:
  ```json
  {
    "message": "用户删除成功",
    "deleted_user": {
      "id": 1,
      "username": "用户名",
      "email": "邮箱",
      "is_active": true,
      "created_at": "创建时间"
    }
  }
  ```
- **注意**: 此操作不可逆，删除后用户数据将永久丢失

### 课程工作流

#### 启动工作流
- **POST** `/api/course/workflow`
- **请求体**:
  ```json
  {
    "title": "课程标题",
    "description": "课程描述",
    "visibility": "draft"
  }
  ```

#### 获取工作流状态
- **GET** `/api/course/workflow/{task_id}`

## 故障排除

### 500错误
- 检查 `config.env` 文件是否正确配置
- 确认Dify API密钥和工作流ID有效
- 查看控制台日志获取详细错误信息

### 网络错误
- 确认网络连接正常
- 检查Dify API地址是否正确

## 开发

服务运行在 `http://localhost:8000`

API文档访问：`http://localhost:8000/docs`

### 测试认证接口

```bash
python test_auth.py
```

### 数据库管理

- 初始化数据库：`python init_db.py`
- 查看数据库表结构：通过DBeaver等工具连接PostgreSQL数据库

