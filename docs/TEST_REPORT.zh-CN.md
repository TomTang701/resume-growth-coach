# 专业测试报告

## 测试范围

本报告评估当前 local-first Resume Growth Coach 的实现：deterministic resume/JD 分析、Portfolio Planner 行为、文档解析、持久化、本地模型 fallback、隐私边界和可复现验证。本报告不表示匹配分数可以预测真实录用结果。

本报告记录已分别验证的行为。当前简历资格声明必须始终通过绑定到精确当前提交的本地 evidence manifest 刷新。

## 当前结论

**项目已通过本地、可复现的作品集使用验证。它刻意保持 local-only，不是已部署的生产服务。**

已验证的实现包括 FastAPI、通过 Docker Compose 运行的 PostgreSQL、Alembic migration、用于隔离本地测试的 SQLite 支持、在可选 Ollama 输出之前执行的 deterministic 分析、跨浏览器 UI smoke 覆盖，以及用于简历 bullet 资格的 evidence gate。

## 已验证证据

- 回归测试：`pytest -q` 为 `70 passed`。
- API quality gate：通过，覆盖 health、analysis、recommendations、UI 文件上传、清理、损坏 PDF、输入限制、HTML escaping 和 not-found 行为。
- Chromium、Firefox 和 WebKit 浏览器 smoke：均通过页面加载、文本与模板分析、Portfolio Planner 展示、校验恢复和文件上传。
- Docker Compose/PostgreSQL smoke：通过；同时检查发布端口只绑定到 loopback。
- 精确 HEAD 的 GitHub Actions CI 会运行 workflow policy、测试与 Alembic migration、Chromium/Firefox/WebKit browser-smoke 矩阵和 Docker smoke；evidence manifest 会记录对应精确提交的结果。
- 本地 evidence manifest：已验证提交的全部简历资格检查均为 true，包括文档和脱敏演示数据检查。
- 公开演示只使用脱敏的示例简历和 JD 数据。

## 已覆盖行为

- 文本、`.txt` 和 `.pdf` 输入，包括有界文件读取、校验错误、规范化和旧编码 fallback。
- Deterministic 技能匹配、项目证据分析、差距评分和岗位模板推荐。
- Portfolio Planner 可接收内置模板、手动粘贴描述或上传 JD；会抑制重复的项目建议。
- 持久化、文档删除、数据保留清理，以及由 Alembic 管理的全新 PostgreSQL 和 SQLite schema。
- 当本地模型不可用时，Ollama summary 会退回 deterministic fallback。
- 由 evidence 推导的简历 bullet 资格：API 调用方不能通过提交自己的 verification flags 解锁项目。

## 有意保留的边界与待完成项

### P0

当前没有已知 P0 问题。

### P1

- README 截图刷新等待手动提供的脱敏 UI 截图。Agent 生成的图片不作为验证证据。

### P2

- 尚未提供高并发负载行为和人工标注的分数校准数据集。
- 项目没有部署，也不自动化招聘平台活动。

## 复现验证

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools\quality_gate.py
.\.venv\Scripts\python.exe tools\browser_smoke.py
.\scripts\run-docker-smoke.ps1
```

在精确提交的 CI 变绿且 tracked worktree 干净后，记录简历资格证据：

```powershell
.\scripts\record-verification-evidence.ps1
```

## 描述边界

可以使用由本地实现和记录证据支撑的描述：FastAPI、PostgreSQL、Alembic、Docker Compose、deterministic 分析、Ollama fallback、API/browser 测试和精确提交 CI。不要声称 production deployment、招聘预测准确率、招聘平台自动化、跨浏览器覆盖或尚未验证的 load-test 结果。
