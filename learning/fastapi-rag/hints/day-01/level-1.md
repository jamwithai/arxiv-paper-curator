# Day 1 — Level 1 提示：概念方向

> 只有在你已经运行预期红灯、独立尝试并把当前判断记录到学习日志后，才继续阅读。打开本文件就立即把 `Hint level used` 更新为 `1`，然后再阅读；若尚未完成前置动作，请关闭本文件。

测试客户端需要三个东西：

1. 一个可被导入的 FastAPI 应用对象；
2. 一个把 HTTP GET 与目标 URL 绑定起来的路径操作；
3. 一个框架能够序列化为 JSON 的返回值。

先画出这条链路，不写语法：

```text
HTTP GET + URL
        ↓
FastAPI 路由匹配
        ↓
Python callable
        ↓
可序列化值
        ↓
HTTP status + headers + JSON body
```

现在回到你的代码，逐项检查：

- Uvicorn 和测试能否通过约定名称找到应用对象？
- method 与 path 是否精确匹配契约？
- 返回值的键和值是否精确匹配测试？
- 应用和操作元数据是否会出现在 OpenAPI？

先尝试修正。仍然卡住时，记录新的测试证据，再打开 Level 2。
