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

## 2026-07-09：P1 测试问题修复

### 修改内容

- 网页新增可选的 resume 和 job description 文件上传。
- 将无上限文件读取改为分块读取，并限制在配置的 5 MB 上限内。
- 将 analysis、skill matches 和 growth goals 改为一次事务提交。
- 增加文档删除接口，同时删除关联的 analysis、matches 和 goals。
- 增加明确的 `scripts/run-ollama-smoke-test.ps1`，并修复 PowerShell 成功状态判断。
- 拒绝 Ollama 用户可见字段中的中文文本，确保 fallback 输出保持英文。
- 更新 README 和本地规范，明确 fallback 是 deterministic fallback，而不是第二个模型。

### 验证结果

- `41 passed, 1 warning`。
- API quality gate 通过。
- 真实 `qwen2.5:3b` smoke test 通过。

### 仍存在的问题

- 尚未实现浏览器级端到端测试、并发测试和生产级数据加密。
- 依赖弃用警告仍然存在。

### 未来计划

- **P0**：当前没有已知 P0 问题。
- **P1**：加入 Playwright 浏览器覆盖，以及本地数据保留/清理命令。
- **P2**：加入 SQLite migration、并发测试和分数校准数据。

## 2026-07-09：数据保留清理后续处理

### 修改内容

- 增加 `app/services/retention.py`，支持按时间清理文档及关联记录。
- 增加 `tools/cleanup_local_data.py`；默认只 dry-run，必须显式使用 `--delete` 才会删除。
- 增加 dry-run 数量、关联 analysis 删除和非法保留天数的回归测试。
- 更新 README 以及测试/报告文档。

### 验证结果

- 修复 UTC 时间弃用写法并更新 Starlette 测试客户端依赖后：`49 passed，无 warning`。
- API quality gate 通过。
- 真实 Ollama smoke test 仍使用 `qwen2.5:3b` 通过。
- 当前环境没有安装 Playwright/Selenium，因此未执行浏览器自动化。

### 仍存在的问题

- 浏览器级端到端覆盖仍未完成。
- SQLite migration、并发/压力测试和分数校准数据仍未完成。
- 当前环境已通过 `httpx2` 依赖更新消除 Starlette/httpx 警告。

### 未来计划

- **P0**：当前没有已知 P0 问题。
- **P1**：增加可选 Playwright 测试 profile，并在配置好浏览器的环境执行 smoke test。
- **P2**：增加 migration 工具、SQLite 并发测试和标注分数校准 fixtures。

## 2026-07-09：基线与并发后续处理

### 修改内容

- 在 `tests/fixtures/score_baseline.json` 增加五组 deterministic score golden cases。
- 增加三个并发 resume/JD/analysis 请求的真实 API 流程测试。
- 使用新证据更新专业测试报告和两份语言的测试日志。

### 验证结果

- `49 passed，无 warning`。
- 五组评分基线均通过，预期分数稳定。
- 并发 SQLite API 流程通过，analysis ID 独立且结果可读取。

### 仍存在的问题

- 浏览器自动化仍受 Playwright/Selenium 环境缺失阻塞。
- SQLite schema migration 工具和标注分数校准数据仍未实现。
- 原有 Starlette/httpx 警告已通过 `httpx2` 依赖更新解决。

### 未来计划

- **P0**：当前没有已知 P0 问题。
- **P1**：配置 Playwright 并执行浏览器 smoke test。
- **P2**：增加 migration/version 管理、扩展并发压力测试，并用标注数据替代启发式基线做校准。

## 2026-07-09：测试客户端依赖清理

### 修改内容

- 在 `requirements.txt` 和 `pyproject.toml` 中用兼容的 `httpx2` 开发依赖替代已弃用的 Starlette `httpx` fallback。

### 验证结果

- 更新后的依赖文件代表干净环境安装；当前虚拟环境已安装 `httpx2==2.5.0`。
- 依赖修改后必须完成全量测试，才能正式关闭该警告。

### 后续发现

- 第一次直接执行 `cleanup_local_data.py --help` 发现根目录导入路径问题；现在 CLI 会在导入 `app` 前加入项目根目录。

## 2026-07-09：浏览器与 Schema 保护后续处理

### 修改内容

- 增加 Playwright/Chromium `tools/browser_smoke.py`，覆盖页面加载、文本分析、校验恢复和文件上传。
- 在 `app/database.py` 增加 schema version marker 以及必需表/列校验。
- 增加 `tools/check_database_schema.py`，可显式检查本地数据库。
- 将并发 API smoke test 从 3 路扩展到 12 路。
- 将 Playwright 加入开发依赖并记录新命令。

### 验证结果

- 浏览器 smoke test 通过。
- 数据库 schema 校验通过，`version=1`。
- `49 passed`，无 warning。
- API quality gate 通过。

### 仍存在的问题

- schema marker 是保护机制，不是完整的历史 migration 系统；未来 schema 变化仍需要升级脚本。
- 浏览器测试目前只覆盖 Chromium，尚未形成跨浏览器或 CI 矩阵。
- 12 路并发只是 smoke test，不是高负载压力测试。
- 仍没有人工标注的分数校准数据。

### 未来计划

- **P0**：当前没有已知 P0 问题。
- **P1**：增加 migration 脚本，并在 CI 执行浏览器 smoke test。
- **P2**：增加 Firefox/WebKit 覆盖、高负载测试和标注分数校准。

## 2026-07-25：Portfolio Planner 与证据门槛

### 修改内容

- 在本地 UI 和 API 中增加后端/全栈、AI 应用岗位模板。
- 增加 Portfolio Planner 卡片，区分进行中的项目和不重复的后续项目建议。
- 增加 PostgreSQL/Alembic、Docker Compose、CI 和验证证据记录脚本。
- 将简历 bullet 资格改为读取本地验证清单；API 请求体不能再自报验证通过。

### 验证结果

- 全量回归：`57 passed`。
- API quality gate 和 Chromium smoke 通过，覆盖模板和 Planner 路径。
- 本地模式证据运行记录 Docker/CI 未完成，因此简历资格保持为 false。

### 仍存在的问题

- 本机没有 Docker Desktop，尚不能记录 Compose smoke 证据。
- 实现尚未提交和推送，因此还不能取得 GitHub CI 证据。

### 未来计划

- **P0**：当前没有已知 P0 问题。
- **P1**：发布后运行 Docker smoke 和精确 HEAD 的 GitHub Actions。
- **P2**：在 CI 中增加浏览器覆盖和分数校准数据集。

## 2026-07-25：运行时证据闭环

### 修改内容

- 将过期的静态 Portfolio Planner 卡片替换为基于本地验证清单的动态状态。
- 为 Chromium 冒烟测试增加确定性的“不完整证据”覆盖。
- 在 GitHub Actions 中增加独立的 Chromium 浏览器冒烟任务。

### 验证结果

- 全量回归及质量/API 门禁：59 passed。
- Chromium 浏览器冒烟和 Docker Compose/PostgreSQL 冒烟均在本地通过。
- 精确 HEAD 的 CI（含浏览器任务）通过：https://github.com/TomTang701/resume-growth-coach/actions/runs/30180380459
- 本地证据清单现已将所有 resume-eligible 条件记录为 true。

### 仍存在的问题

- Firefox/WebKit 覆盖、高并发负载测试和人工标注的分数校准仍属于后续工作。
