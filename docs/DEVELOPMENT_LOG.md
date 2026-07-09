# Development Log

本文件是 Resume Growth Coach 的交接记录。它记录会影响行为、测试、启动方式或数据契约的较大修改；小型拼写和纯格式调整可以不单独记录。

## 使用规则

每次较大修改完成后追加一个条目，至少包含日期和提交号、修改范围、验证结果、遗留问题、按 P0/P1/P2 排序的后续计划，以及启动或数据注意事项。

项目成果面向用户的内容必须保持纯英文；本文件属于开发交接资料，可使用中文优先、英文混用。

## 2026-07-09: Ollama 启动保障和刁钻测试补强

### 修改内容

- 启动脚本会确认 Ollama API、确认 `qwen2.5:3b`、必要时执行 pull，并发送一次真实生成请求。
- Ollama 请求默认超时为 60 秒，`RGC_OLLAMA_TIMEOUT_SECONDS` 在每次请求时读取，并限制在 1 到 300 秒。
- 增加 UI 输入校验、XSS 转义、错误上传、空文件、超大 JD、缺失分析对象和模型超时参数的回归测试。
- `tools/quality_gate.py` 继续作为独立、无需 Ollama 的可复用检查入口。

### 验证结果

- 本机 `qwen2.5:3b` 已通过真实生成 smoke test。
- 质量门禁覆盖 health、analysis、recommendations、malformed PDF、输入上限、UI escaping 和 404。
- 本次完成后：`36 passed, 1 warning`；quality gate 的 pytest 和 API contract checks 全部通过。

### 仍存在的问题

- 默认评分仍是规则驱动的 heuristic，不等同于真实招聘概率；技能同义词和职责理解仍有限。
- 尚未做浏览器级自动化测试，当前 UI 主要通过 FastAPI `TestClient` 验证 HTML 响应。
- Ollama 进程和模型下载依赖本机安装、网络和磁盘空间；不可用时会进入 fallback。
- 尚未对 PDF、超长文本和模型首次加载做系统性的性能基准测试。

### 后续计划

- **P0**：维护角色模板和技能别名的 golden cases，防止评分因关键词误匹配而异常升高。
- **P1**：加入真实浏览器 smoke test，检查提交、错误恢复和结果展示的完整流程。
- **P1**：增加 PDF fixtures、Unicode、乱码和大文件性能测试。
- **P2**：为评分提供可解释的分项权重和校准数据，不把单一总分当作确定结论。

### 交接注意事项

- 推荐使用根目录 `Start-ResumeGrowthCoach.cmd`，不需要手动激活虚拟环境。
- 提交前执行 `scripts/run-quality-gate.ps1`。
- 不要把真实简历、真实 JD、`local_data/` 或 `.env` 提交到 Git。
