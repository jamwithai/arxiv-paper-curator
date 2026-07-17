# Day 1 — Level 3 提示：非 Python 伪代码

> 只有在 Level 2 后再次尝试、运行测试，并把新的失败结果记录到学习日志后，才继续阅读。打开本文件就立即把 `Hint level used` 更新为 `3`，然后再阅读；若尚未完成前置动作，请关闭本文件。

以下内容故意不是有效 Python。请先解释每一行的职责，再自己翻译成最少的 FastAPI 代码：

```text
LOAD the FastAPI application type

CREATE application AS FastAPI
    WITH title "FastAPI RAG Learning API"
    WITH version "0.1.0"

REGISTER HTTP GET "/api/v1/health/live"
    WITH summary "Check liveness"
    TO a callable that
        RETURNS mapping {status: "alive"}
```

翻译时只寻找 FastAPI 创建应用与注册 GET 路径操作所需的语法。不要添加课程没有要求的类型、类、依赖或目录。

如果翻译后仍失败，请记录完整失败消息并向导师说明你认为失败发生在哪一层：导入、路由、响应还是 OpenAPI。
