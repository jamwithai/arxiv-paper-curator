# Day 1 — 你的第一个可验证 FastAPI 契约

**课次：** W01D01  
**时间：** 60–90 分钟  
**核心原则：** 先看见一个准确的失败，再写最少代码改变它。

## 今日产出

今天只交付一个 HTTP 行为：

```text
GET /api/v1/health/live
HTTP 200
Content-Type: application/json
{"status": "alive"}
```

同时，OpenAPI 必须描述这个操作：

```text
API title: FastAPI RAG Learning API
API version: 0.1.0
Operation summary: Check liveness
```

今天不写数据库、业务服务、配置系统、自定义异常、认证或 RAG。

## 时间预算

| 阶段 | 建议时间 |
|---|---:|
| 开场诊断 | 10 分钟 |
| HTTP 与 FastAPI 最小概念 | 15 分钟 |
| 运行并阅读红灯测试 | 10 分钟 |
| 独立实现最小行为 | 25 分钟 |
| 解释、日志与检查 | 15 分钟 |
| 缓冲 | 5 分钟 |

如果 90 分钟耗尽，立即停止并在学习日志中记录当前测试结果、已用提示级别和阻塞点；不要用复制答案掩盖问题。

## 开场诊断题

先不要写代码，也不要查看提示。请用自己的话回答：

> 一个 Python 函数返回 `{"status": "alive"}`，和客户端收到一个正文为同样 JSON 的 HTTP 响应，有哪些不同？至少说出三个 HTTP 层的信息。

把回答写入 [../progress/learning-log.md](../progress/learning-log.md) 的新记录。导师应先根据这一个回答追问，不一次抛出多道题。

## 你只需要理解的最小概念

### 1. HTTP 响应不只是 Python 值

客户端观察到的是状态码、响应头和响应体。Python 字典只是应用内部的值；Web 框架负责把它转换为网络协议中的响应。

### 2. FastAPI 应用是 ASGI 应用

测试客户端和 Uvicorn 都需要找到一个 FastAPI 应用对象。课程约定模块路径为 `app.main`，导出的对象名称为 `app`。

### 3. 路径操作连接 HTTP 与 Python

路径操作声明将 HTTP method 与 URL path 绑定到一个 Python callable。今天只需要一个 GET 操作。

### 4. OpenAPI 是可验证契约

FastAPI 会根据应用和路径操作元数据生成 OpenAPI。标题、版本、路径、summary 和响应状态都会被测试，而不只是“浏览器能打开”。

### 5. `async` 不是装饰

今天的操作不执行等待式 I/O，因此不要因为 FastAPI 支持异步就假设必须使用 `async def`。先判断工作是否需要 `await`；你可以选择最简单且能解释的定义方式。

## 先运行预期红灯

从仓库根目录运行：

```bash
uv sync --project learning/fastapi-rag
uv run --project learning/fastapi-rag pytest learning/fastapi-rag/tests/day01 -q
```

预期结果是 3 个失败，核心消息为：

```text
Day 1 starts red: create app/main.py and export a FastAPI instance named 'app'.
```

如果失败原因是 `uv`、Python 版本或依赖缺失，先修复环境；那不是课程要求的红灯。不要在环境错误上继续编码。

## 任务约束

只创建一个文件：

```text
learning/fastapi-rag/app/main.py
```

该文件必须满足以下行为：

- 从 `app.main` 导出名称为 `app` 的 FastAPI 实例；
- 应用 title 为 `FastAPI RAG Learning API`；
- 应用 version 为 `0.1.0`；
- 注册 `GET /api/v1/health/live`；
- operation summary 为 `Check liveness`；
- 成功返回状态码 200；
- JSON 正文严格等于 `{"status": "alive"}`。

禁止增加：

- 数据库、repository 或 service；
- Pydantic 模型；
- router 分包；
- 配置类；
- 自定义异常与 middleware；
- 认证、缓存、日志、Docker 或 RAG；
- 测试未要求的其他端点。

这些内容以后会在出现真实需求时逐步加入。今天提前加入只会模糊你正在学习的 HTTP 契约。

## TDD 工作流

1. 运行测试并确认是上面的**预期红灯**。
2. 只阅读第一条失败，说明测试当前在验证什么。
3. 创建 `app/main.py`，写满足契约的最少代码。
4. 再次运行 Day 1 测试：

   ```bash
   uv run --project learning/fastapi-rag pytest learning/fastapi-rag/tests/day01 -q
   ```

5. 如果失败，只处理当前失败暴露的行为；不要猜测未来需求。
6. 测试全部通过后运行：

   ```bash
   uv run --project learning/fastapi-rag ruff check \
     learning/fastapi-rag/app learning/fastapi-rag/tests
   uv run --project learning/fastapi-rag mypy learning/fastapi-rag/app
   ```

7. 启动应用并在 `/docs` 中手工调用一次：

   ```bash
   uv run --project learning/fastapi-rag uvicorn app.main:app \
     --app-dir learning/fastapi-rag --reload
   ```

8. 观察实际状态码、`content-type` 和 JSON，不要只看页面上出现了文字。

## 卡住时的三级提示

只有独立尝试并把当前判断写入学习日志后，才能按顺序打开：

1. [Level 1：概念方向](../hints/day-01/level-1.md)
2. [Level 2：接口约束](../hints/day-01/level-2.md)
3. [Level 3：非 Python 伪代码](../hints/day-01/level-3.md)

不得跳级。每打开一级，都要把 `Hint level used` 更新为对应数字。

## 必须回答的复盘题

实现后，不看代码回答。以下 6 题是题库；导师一次只提出其中一题，等待你的回答、追问和日志记录完成后，才进入下一题：

1. 为什么 Python 字典最终可以成为 JSON 响应？谁完成了转换？
2. 为什么成功状态码是 200？测试还验证了哪个默认错误状态？
3. HTTP method、URL path 和 Python callable 是怎样关联的？
4. 这个 callable 必须是 `async def` 吗？你依据什么判断？
5. title、version 和 summary 分别出现在哪里？为什么它们属于契约？
6. 测试为什么通过 ASGI 客户端请求，而不是直接调用你的 Python 函数？

将答案写进学习日志。无法清楚解释的题目就是下一次复习项，即使测试已经通过。

## 完成门槛

开始独立尝试时，先把 W01D01 从 `ready` 改为 `in-progress`。只有同时满足以下条件，才能再从 `in-progress` 改为 `completed`：

- Day 1 的 3 个测试全部通过；
- Ruff 与 MyPy 通过；
- 在真实 `/docs` 中完成一次调用并观察响应；
- 不看代码回答全部 6 个复盘题；
- [current-state.md](../progress/current-state.md) 和学习日志已更新；
- 如实记录使用过的最高提示级别。

完成后检查 diff，由你自行创建一次小阶段提交。建议提交信息：

```text
feat(learning): complete first FastAPI contract
```

不要在同一提交中开始 W01D02。
