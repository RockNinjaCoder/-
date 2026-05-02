# 智能数据分析系统 - 开发任务清单

## 📋 任务总览（4 Phase）

---

# Phase 1：前后端基础框架搭建 & 测试运行

## 1.1 后端基础框架搭建
- [ ] 创建后端项目目录结构 `backend/`
- [ ] 创建虚拟环境 `python -m venv backend/venv`
- [ ] 安装基础依赖 `pip install fastapi uvicorn`
- [ ] 创建 .env 配置文件（API密钥、数据库路径）
- [ ] 初始化 Git 仓库
- [ ] 创建 FastAPI 应用入口 `backend/app/main.py`
- [ ] 配置 CORS 跨域
- [ ] 编写基础路由测试 `Hello World` 接口
- [ ] 启动后端服务验证 `uvicorn`

## 1.2 前端基础框架搭建
- [ ] 使用 Vite 创建 React 项目 `npm create vite@latest frontend -- --template react`
- [ ] 安装基础依赖 `npm install`
- [ ] 安装路由 `npm install react-router-dom`
- [ ] 安装状态管理 `npm install zustand`
- [ ] 安装图表库 `npm install echarts echarts-for-react`
- [ ] 安装 UI 组件库 `npm install antd`
- [ ] 配置 vite.config.js 路径别名
- [ ] 创建前端项目目录结构
- [ ] 编写基础页面组件测试
- [ ] 启动前端服务验证 `npm run dev`

## 1.3 数据库初始化
- [ ] 设计并创建 `sessions` 表
- [ ] 设计并创建 `messages` 表
- [ ] 设计并创建 `db_schemas` 表
- [ ] 设计并创建 `query_logs` 表
- [ ] 创建 `init_db.py` 数据库初始化脚本
- [ ] 实现数据库连接管理模块
- [ ] 执行数据库初始化并验证

## 1.4 基础功能验证测试
- [ ] 后端健康检查接口测试
- [ ] 前端页面加载测试
- [ ] 数据库连接测试
- [ ] 验证 Phase 1 完成标准：前后端均可独立运行

---

# Phase 2：前端 UI 研发

## 2.1 布局组件开发
- [ ] 实现 MainLayout 主布局（三栏布局）
- [ ] 实现 ChatSidebar 左侧聊天管理面板（宽度250px）
- [ ] 实现 ChatArea 中间问答区域（flex:1自适应）
- [ ] 实现 VisualizationPanel 右侧可视化面板（宽度400px）
- [ ] 实现布局响应式适配

## 2.2 聊天功能 UI 开发
- [ ] 实现 ChatMessage 消息组件（区分用户/AI消息）
- [ ] 实现 ChatInput 输入框组件
- [ ] 实现 MessageList 消息列表组件
- [ ] 实现会话列表展示组件
- [ ] 实现新建会话按钮
- [ ] 实现消息时间戳显示

## 2.3 会话管理 UI 开发
- [ ] 实现会话切换下拉列表
- [ ] 实现会话删除功能
- [ ] 实现会话重命名功能
- [ ] 实现会话搜索功能
- [ ] 实现空会话状态提示

## 2.4 可视化 UI 开发
- [ ] 实现 ChartRenderer 图表渲染组件
- [ ] 实现图表类型选择器（折线图/柱状图/饼图/散点图）
- [ ] 实现图表配置面板
- [ ] 实现图表数据切换
- [ ] 实现图表缩放和导出功能

## 2.5 前端状态管理
- [ ] 配置 Zustand store
- [ ] 实现 sessionStore（会话状态管理）
- [ ] 实现 chatStore（聊天消息状态管理）
- [ ] 实现 chartStore（图表配置状态管理）

## 2.6 前端 API 层开发
- [ ] 创建 api/chat.js（聊天消息接口）
- [ ] 创建 api/session.js（会话管理接口）
- [ ] 创建 api/query.js（数据查询接口）
- [ ] 创建 api/stream.js（SSE流式请求接口）
- [ ] 实现请求拦截器（携带Token等）
- [ ] 实现响应错误处理

## 2.7 流式通信 UI 开发
- [ ] 实现 EventSource 或 fetch 流式接收
- [ ] 实现 StreamingMessage 流式消息组件
- [ ] 实现打字机效果动画
- [ ] 实现流式加载状态指示器
- [ ] 实现流式传输中止功能
- [ ] 实现连接错误提示和重试按钮

## 2.8 UI 优化与美化
- [ ] 统一设计风格和配色方案
- [ ] 实现暗色/亮色主题切换（可选）
- [ ] 添加加载动画和过渡效果
- [ ] 优化移动端适配
- [ ] 实现深色模式支持

---

# Phase 3：后端接口研发

## 3.1 会话管理接口
- [ ] 创建 `app/models/session.py` 会话数据模型
- [ ] 创建 `app/api/session.py` 会话API路由
- [ ] 实现 `POST /api/sessions` 创建会话
- [ ] 实现 `GET /api/sessions` 会话列表
- [ ] 实现 `GET /api/sessions/{id}` 会话详情
- [ ] 实现 `DELETE /api/sessions/{id}` 删除会话
- [ ] 实现会话持久化存储

## 3.2 消息管理接口
- [ ] 创建 `app/models/message.py` 消息数据模型
- [ ] 创建 `app/api/chat.py` 消息API路由
- [ ] 实现消息存储功能
- [ ] 实现消息历史查询
- [ ] 实现消息分页加载

## 3.3 MiniMax LLM 接入
- [ ] 创建 `app/core/llm/minimax_adapter.py`
- [ ] 实现 LLM 配置管理（API Key、Base URL）
- [ ] 实现 ChatOpenAI 封装
- [ ] 实现模型调用封装
- [ ] 测试 MiniMax 模型连接

## 3.4 上下文记忆模块
- [ ] 创建 `app/core/memory/conversation_memory.py`
- [ ] 实现 ConversationBufferMemory 封装
- [ ] 实现会话上下文加载/保存
- [ ] 实现上下文窗口管理
- [ ] 实现上下文压缩（可选）

## 3.5 SQL 生成引擎
- [ ] 创建 `app/core/nlp/sql_generator.py`
- [ ] 实现 Schema 信息读取
- [ ] 设计 Prompt 模板（包含表结构、示例）
- [ ] 实现自然语言到 SQL 转换
- [ ] 实现 SQL 语法验证
- [ ] 实现 SQL 纠错机制

## 3.6 查询执行引擎
- [ ] 创建 `app/core/db/executor.py`
- [ ] 实现 SQL 执行器
- [ ] 实现安全检查（仅允许 SELECT）
- [ ] 实现查询结果格式化
- [ ] 实现异常处理和错误返回

## 3.7 可视化配置生成
- [ ] 创建 `app/core/nlp/chart_recommender.py`
- [ ] 分析查询结果数据特征
- [ ] 推荐合适的图表类型
- [ ] 生成 ECharts 配置
- [ ] 实现数据转换逻辑

## 3.8 SSE 流式通信接口
- [ ] 创建 `app/api/stream.py` 流式API路由
- [ ] 实现 `GET /api/chat/stream/{session_id}` 端点
- [ ] 实现 StreamingResponse 流式响应
- [ ] 实现 MiniMax 流式调用封装
- [ ] 实现 text/event-stream 格式化
- [ ] 实现心跳保持连接
- [ ] 实现流式异常处理

## 3.9 服务层整合
- [ ] 创建 `app/services/chat_service.py`
- [ ] 创建 `app/services/query_service.py`
- [ ] 创建 `app/services/visualization_service.py`
- [ ] 实现业务逻辑整合
- [ ] 统一异常处理

---

# Phase 4：前后端联调

## 4.1 接口对接
- [ ] 对接会话管理 API（创建/切换/删除）
- [ ] 对接聊天消息 API（发送/接收/历史）
- [ ] 对接 SSE 流式 API（实时响应）
- [ ] 对接数据库查询 API（自然语言查询）
- [ ] 对接可视化配置 API（图表渲染）

## 4.2 功能测试
- [ ] 测试会话创建/切换/删除流程
- [ ] 测试多轮对话上下文记忆
- [ ] 测试自然语言查询数据库
- [ ] 测试 SSE 流式响应显示
- [ ] 测试图表自动渲染
- [ ] 测试图表类型切换
- [ ] 测试异常情况处理（网络错误、查询超时等）

## 4.3 性能测试
- [ ] 测试数据库查询性能
- [ ] 测试前端渲染性能
- [ ] 测试 SSE 连接稳定性
- [ ] 优化慢查询
- [ ] 实现请求缓存（可选）

## 4.4 安全加固
- [ ] SQL 注入防护验证
- [ ] 输入内容过滤验证
- [ ] 查询结果大小限制
- [ ] API 认证（可选）

## 4.5 部署准备
- [ ] 创建 Dockerfile（后端）
- [ ] 配置生产环境构建
- [ ] 编写部署文档
- [ ] 准备服务器环境

## 4.6 文档编写
- [ ] 编写 README.md
- [ ] 编写 API 接口文档
- [ ] 编写用户使用手册
- [ ] 代码审查与优化
- [ ] 最终版本提交

---

## 📊 任务优先级参考

### 🔴 Phase 1 - 核心基础（必须优先完成）
1. 后端项目初始化 + FastAPI 启动
2. 前端项目初始化 + Vite 启动
3. 数据库初始化 + 连接验证
4. 基础功能测试通过

### 🟡 Phase 2 - UI 研发（可并行开发）
1. 布局组件开发
2. 聊天功能 UI
3. 会话管理 UI
4. 可视化 UI

### 🟡 Phase 3 - 后端研发（可并行开发）
1. MiniMax LLM 接入
2. 会话管理接口
3. SQL 生成引擎
4. SSE 流式接口

### 🟢 Phase 4 - 联调测试（前置 Phase 2、3 完成）
1. 接口对接
2. 功能测试
3. 性能测试
4. 部署上线

---

## 📅 预估工时

| Phase | 内容 | 预估时间 | 说明 |
|-------|------|---------|------|
| Phase 1 | 基础框架搭建 & 测试 | 1 天 | 前后端项目初始化、数据库 |
| Phase 2 | 前端 UI 研发 | 2-3 天 | 布局、聊天、可视化 |
| Phase 3 | 后端接口研发 | 2-3 天 | LLM、SQL、SSE |
| Phase 4 | 前后端联调 | 1-2 天 | 对接、测试、部署 |
| **总计** | | **6-9 天** | 完整开发周期 |