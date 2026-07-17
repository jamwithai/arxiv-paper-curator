# Day 1 — Level 2 提示：接口约束

> 只有在 Level 1 后再次尝试、运行测试，并把新的失败结果记录到学习日志后，才继续阅读。打开本文件就立即把 `Hint level used` 更新为 `2`，然后再阅读；若尚未完成前置动作，请关闭本文件。

把问题缩小到一个文件和一个公开接口：

```text
File: learning/fastapi-rag/app/main.py
Module: app.main
Exported object: app
Object type: FastAPI
```

应用元数据必须逐字匹配：

```text
title   = FastAPI RAG Learning API
version = 0.1.0
```

路径操作契约必须逐字匹配：

```text
method  = GET
path    = /api/v1/health/live
summary = Check liveness
status  = 200
body    = {"status": "alive"}
```

把这些分成两个问题：先让测试能够导入 `app`，再让 HTTP/OpenAPI 行为匹配。不要创建第二个模块或额外抽象。

先尝试修正。仍然卡住时，记录新的测试证据，再打开 Level 3。
