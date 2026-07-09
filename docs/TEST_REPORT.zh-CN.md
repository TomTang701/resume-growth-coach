# 专业测试报告

## 测试范围

本报告评估当前 Resume Growth Coach MVP 的正确性、稳定性、数据安全、本地模型集成和实际使用流程。报告不表示匹配分数可以预测真实录用结果。

## 当前结论

**适合本地 MVP 开发和演示，有条件通过；尚未达到生产级。**

核心 API、deterministic scoring、fallback、网页文件上传、文件大小控制、文档删除和保留清理均已覆盖并通过。浏览器级覆盖、并发/压力测试、migration 和分数校准仍未完成。

## 验证证据

- 回归测试：`43 passed, 1 warning`。
- API quality gate：通过。
- 真实 `qwen2.5:3b` smoke test：通过。
- Python 编译检查：上一轮修复中已通过。
- Git 工作区：当前修改提交后应保持干净。

## 已修复问题

- UI/API 现在支持文本或 `.txt/.pdf` 文件输入。
- 上传采用分块读取，并限制为 5 MB。
- analysis、skill matches、growth goals 使用一个事务保存。
- 删除文档时会删除关联 analysis 记录。
- 提供默认 dry-run 的按时间清理命令。
- LLM 非英文用户可见字段会安全 fallback。
- fallback 文档已改为 deterministic fallback，不再描述不存在的第二模型。

## 按优先级剩余问题

### P0

当前没有已知 P0 问题。

### P1

- 当前环境没有 Playwright/Selenium，无法执行浏览器级端到端测试。
- 仍需要配置浏览器测试 profile，验证真实文件选择、提交、错误恢复和结果渲染。

### P2

- 尚未实现 SQLite migration 工具，schema 变化仍依赖 `create_all`。
- 尚未正式测试 SQLite 并发写入和压力行为。
- 匹配分数没有人工标注数据校准。
- 测试环境仍有一个 Starlette/httpx 弃用警告。

## 下一道质量门禁建议

在宣称生产级之前，应安装浏览器自动化 profile、建立 migration 策略、执行 SQLite 并发测试，并定义标注分数校准数据。在此之前，项目应描述为“经过测试的 local MVP”。

