# 开发日志

本文件是 Resume Growth Coach 的开发交接记录。它记录会影响行为、测试、启动方式、数据契约或交接工作的较大修改。仅拼写或格式调整不需要单独记录。

英文主文档是 [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)。两份文件必须保持语义一致；先更新英文文件，再在同一个提交中更新本中文翻译。

## 记录规则

每次较大修改必须记录：

- 日期和提交号
- 修改内容及受影响模块
- 验证命令和结果
- 仍存在的问题
- 按 P0、P1、P2 排序的未来计划
- 启动、数据、隐私或交接注意事项

面向用户的项目成果必须保持纯英文。本文件与英文文件互为独立文档，英文文件是默认入口。

## 2026-07-09：Ollama 启动保障与刁钻测试扩展

### 修改内容

- 启动脚本会检查 Ollama API、确认 `qwen2.5:3b`、缺失时执行 pull，并发送一次真实生成 smoke test。
- Ollama 请求默认超时为 60 秒；每次请求都会读取 `RGC_OLLAMA_TIMEOUT_SECONDS`，并限制在 1-300 秒。
- 增加 UI 校验、HTML 转义、无效上传、空文件、超大 JD、缺失分析对象和模型超时配置的回归测试。
- 保留 `tools/quality_gate.py` 作为无需 Ollama 即可运行的可复用质量检查工具。

### 验证结果

- 本地 `qwen2.5:3b` 已通过真实生成 smoke test。
- 质量门禁覆盖 health、analysis、recommendations、malformed PDF、输入上限、UI 转义和 404 行为。
- 最终结果：`36 passed, 1 warning`；pytest 和全部 API contract checks 通过。

### 仍存在的问题

- 当前分数是启发式规则分数，不代表真实录用概率；技能别名和职责理解仍有限。
- 尚未加入浏览器级自动化测试；当前 UI 主要使用 FastAPI `TestClient` 检查 HTML。
- Ollama 依赖本机安装、网络和磁盘空间；不可用时应用会 fallback。
- 尚未系统基准测试 PDF、超长文本和模型首次加载性能。

### 未来计划

- **P0**：维护岗位模板和技能别名 golden cases，避免关键词错误导致分数虚高。
- **P1**：加入真实浏览器 smoke test，覆盖提交、错误恢复和结果渲染。
- **P1**：增加 PDF fixtures、Unicode/编码场景和大文件性能测试。
- **P2**：提供可解释的分项分数并使用标注数据校准；不能把单一总分当作确定结论。

### 交接注意事项

- 使用 `Start-ResumeGrowthCoach.cmd`，不需要手动激活虚拟环境。
- 提交前运行 `scripts/run-quality-gate.ps1`。
- 不要提交真实简历、真实 JD、`local_data/` 或 `.env` 文件。

