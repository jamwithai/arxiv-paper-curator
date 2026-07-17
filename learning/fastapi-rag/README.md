# FastAPI RAG Learning Lab

这是一套以**独立实现能力**为目标的 10 周学习项目。你不会通过复制完整答案来“学会” FastAPI；你会在行为测试、递进提示和证据复盘的约束下，亲手构建一个可测试、可观测、可用 Docker Compose 部署的多用户 RAG 知识库 API。

## 你的目标

10 周后，你应能独立完成以下工作：

- 设计并实现带 `/api/v1` 版本前缀的 FastAPI HTTP API；
- 使用 Pydantic 定义请求、响应和 OpenAPI 契约；
- 使用异步 SQLAlchemy、PostgreSQL 与 Alembic 管理持久化；
- 实现短期访问 JWT、依赖注入与所有者数据隔离；
- 安全接收 PDF，并通过单 worker 的 `BackgroundTasks` 显式管理处理状态与失败重试；
- 使用 Docling 解析、结构感知分块，并在 OpenSearch 中完成 BM25、向量和混合检索；
- 使用 Ollama 完成嵌入与有引用的普通/SSE RAG 问答；
- 使用 Redis、结构化日志和 Langfuse 完成缓存与可观测性；
- 通过自动化测试、双语检索评估和本地 Docker Compose 部署证明系统有效。

最终验收是一场 **180 分钟的独立实战**：不查看课程实现，从给定空骨架完成认证、核心资源 API、受控的模拟检索问答和关键测试，并解释异步、依赖注入、租户隔离、RAG 与安全设计。精确端点、允许资料、必测行为和评分门槛见 [CURRICULUM.md 的终验契约](CURRICULUM.md#3-小时独立实战契约)。

完整路线见 [CURRICULUM.md](CURRICULUM.md)。

## 学习规则

1. **核心代码由你写。** 课程提供问题、行为契约、失败测试和递进提示，不提前提供可复制实现。
2. **每次只解决一个可验证任务。** 当天任务通过之前，不增加数据库、缓存、RAG 等未来能力。
3. **遵循红—绿—重构。** 先观察测试按预期失败，再写最少代码使其通过，最后只在证据支持时重构。
4. **三级提示逐级解锁。** 先独立尝试；卡住后依次查看概念提示、接口提示、伪代码提示。每次查看前记录当前判断。
5. **测试通过不是唯一目标。** 你还必须用自己的话解释行为、错误和取舍，并在学习日志中留下证据。
6. **按小阶段自行提交。** 每个可验证阶段结束后由你检查 diff 并提交；课程不会自动执行 Git commit。
7. **按证据推进。** 未达到当前周验收门槛时，先补练习，不以“看过”代替“掌握”。

## 技术边界

### 固定技术栈

- Python 3.12、uv、Ruff、MyPy、pytest、HTTPX
- FastAPI、Pydantic
- 异步 SQLAlchemy 2.x、asyncpg、PostgreSQL、Alembic
- Docling、本地文件卷
- OpenSearch：BM25、向量检索、原生 hybrid query + RRF
- Ollama：轻量 Qwen 生成模型、`nomic-embed-text` 嵌入模型
- Redis：知识库版本化问答缓存
- Langfuse：检索、提示词与生成链路追踪
- Docker Compose：单 worker API 与本地依赖服务

### 必修 API 范围

- 注册、登录、当前用户；
- 知识库 CRUD；
- PDF 上传、游标分页列表、详情、完整级联删除、失败重试；
- BM25、向量、混合检索；
- 普通 JSON 问答与标准 Server-Sent Events 问答；
- `/api/v1/health/live` 与 `/api/v1/health/ready`。

### 明确不做

- 不构建前端或 Gradio；
- 不做多轮会话记忆；
- 不做团队共享或公开知识库；
- 不把 `BackgroundTasks` 描述成持久任务队列；
- 不在核心验收中要求 Agentic RAG。

刷新令牌轮换与撤销、反馈、重建索引和 Agentic RAG 属于进阶扩展。

## 如何继续学习

以后每次向导师发送 **“继续学习”** 时，先读取 [progress/current-state.md](progress/current-state.md) 与 [progress/learning-log.md](progress/learning-log.md)，再按唯一的 `Status` 分支执行：

- `environment-blocked`：只处理 `Blockers`，验证工具与运行时可用后改为 `ready`；不进入诊断题或编码；
- `ready`：导师一次只提出当前课次的一道诊断题，等待回答、追问和记录后再推进；
- `in-progress`：先复现 `Last test result`，围绕当前失败继续，不开启新课次；
- `blocked`：只处理已记录阻塞，得到新证据后改回 `in-progress`；
- `completed`：先复核当前课次全部门槛；若当前是 D01–D05，直接把 `Current session` 推进到下一计划课次并设为 `ready`；只有 D06 才依据本周 `weekly-review.md` 的决策推进。

每次学习结束都更新当前状态和学习日志；WNN D06 还要更新 [progress/weekly-review.md](progress/weekly-review.md)。`current-state.md` 永远只保留一个当前状态，不追加第二份相互冲突的状态。

## 第一次学习

> 前提：本机已安装 Python 3.12 与 uv。若尚未安装，不要降低课程 Python 版本来绕过环境问题。

在仓库根目录运行：

```bash
uv sync --project learning/fastapi-rag
uv run --project learning/fastapi-rag pytest learning/fastapi-rag/tests/day01 -q
```

第一次测试应当是**预期红灯**：三个测试会明确提示你创建 `app/main.py`。这不是项目故障，而是 Day 1 的起点。

然后阅读 [lessons/day-01.md](lessons/day-01.md)，先回答开场诊断题，再开始编码。不要提前打开提示文件。

## 常用命令

以下命令均从仓库根目录运行：

```bash
# 安装或同步课程子项目依赖
uv sync --project learning/fastapi-rag

# 运行 Day 1 行为测试
uv run --project learning/fastapi-rag pytest learning/fastapi-rag/tests/day01 -q

# 检查课程代码风格
uv run --project learning/fastapi-rag ruff check \
  learning/fastapi-rag/app learning/fastapi-rag/tests

# 检查课程应用类型
uv run --project learning/fastapi-rag mypy learning/fastapi-rag/app

# Day 1 通过后，在课程子项目目录启动开发服务器
uv run --project learning/fastapi-rag uvicorn app.main:app \
  --app-dir learning/fastapi-rag --reload
```

开发服务器启动后，OpenAPI 页面位于 `http://127.0.0.1:8000/docs`。

## 当前交付边界

本次只包含完整 10 周框架、Day 1 课程、Day 1 行为测试、三级提示和学习记录模板。后续课程与参考材料会根据掌握证据逐步解锁；当前目录中没有 Day 1 核心实现，也没有后续周答案。
