# 专业测试报告

## 测试范围

本报告评估当前 Resume Growth Coach MVP 的正确性、稳定性、数据安全、本地模型集成和实际使用流程。报告不表示匹配分数可以预测真实录用结果。

## 当前结论

**适合本地 MVP 开发和演示，有条件通过；尚未达到生产级。**

核心 API、deterministic scoring、fallback、网页文件上传、文件大小控制、文档删除、保留清理和 Chromium 浏览器 smoke 流程均已覆盖并通过。跨浏览器覆盖、完整 migration、高负载压力测试和分数校准仍未完成。

## 验证证据

- 回归测试：`49 passed，无 warning`。
- API quality gate：通过。
- 真实 `qwen2.5:3b` smoke test：通过。
- 真实无头 Chromium smoke test：通过。
- 数据库 schema 校验：通过，版本 `1`。
- Python 编译检查：上一轮修复中已通过。
- Git 工作区：当前修改提交后应保持干净。

## 已修复问题

- UI/API 现在支持文本或 `.txt/.pdf` 文件输入。
- 上传采用分块读取，并限制为 5 MB。
- analysis、skill matches、growth goals 使用一个事务保存。
- 删除文档时会删除关联 analysis 记录。
- 提供默认 dry-run 的按时间清理命令。
- 已覆盖五组评分 golden cases 和并发 SQLite API 流程。
- 已覆盖 12 路文件型 SQLite 并发 API smoke 流程。
- LLM 非英文用户可见字段会安全 fallback。
- fallback 文档已改为 deterministic fallback，不再描述不存在的第二模型。

## 按优先级剩余问题

### P0

当前没有已知 P0 问题。

### P1

- Chromium 浏览器 smoke 覆盖已配置并通过。
- Firefox/WebKit、跨浏览器行为和 CI 浏览器执行仍未验证。

### P2

- 已有 schema version marker 和结构保护，但尚未实现历史 SQLite migration 脚本。
- 12 路 SQLite 并发 smoke test 已通过；高负载写入和压力行为仍未正式测试。
- 匹配分数没有人工标注数据校准。
- Starlette 测试客户端现在使用兼容的 `httpx2` 开发依赖；当前环境中的原有警告已消除。

## 下一道质量门禁建议

在宣称生产级之前，应将浏览器测试加入 CI、建立 migration 策略、扩展 SQLite 并发压力测试，并定义标注分数校准数据。在此之前，项目应描述为“经过测试的 local MVP”。
