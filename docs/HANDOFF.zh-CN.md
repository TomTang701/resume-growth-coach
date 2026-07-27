# 开发交接

本文件是默认的中文交接文档。英文主文档是 [HANDOFF.md](HANDOFF.md)；两份文档必须包含相同信息，只使用不同语言表达。

## 新开发者快速开始

1. 阅读 `PROJECT_SPEC.md`、`docs/DEVELOPMENT_LOG.md`、`docs/TEST_LOG.md` 和 `docs/TEST_REPORT.md`。
2. 确认工作区干净，然后运行 `scripts/run-quality-gate.ps1`。
3. 本地使用时双击 `Start-ResumeGrowthCoach.cmd`；它会检查 Ollama 和 `qwen2.5:3b`。使用完成后运行 `Stop-ResumeGrowthCoach.cmd`；它只会停止由当前 checkout 启动且已验证的本地服务器进程。
4. 修改 scoring、parsing、recommendations、persistence 或 API contract 后，更新测试以及相关日志的中英文两份文件。

## 较大修改日志模板

追加到 `docs/DEVELOPMENT_LOG.md`，并在 `docs/DEVELOPMENT_LOG.zh-CN.md` 中同步：

```markdown
## YYYY-MM-DD：简短修改标题

### 修改内容
- ...

### 验证结果
- command: ...
- result: ...

### 仍存在的问题
- ...

### 未来计划
- **P0**：...
- **P1**：...
- **P2**：...
```

追加到 `docs/TEST_LOG.md`，并在 `docs/TEST_LOG.zh-CN.md` 中同步：

```markdown
## YYYY-MM-DD 测试轮次

### 已检查
- ...

### 可疑发现与处理
- ...

### 未检查
- ...

### 使用感受与极端情况
- ...
```

## 完成要求

- 面向用户的 analysis、roadmap、recommendations 和 bullet drafts 保持纯英文。
- deterministic layer 先于 Ollama；模型失败不能让 API 失败。
- 直接岗位和推荐岗位使用同一评分函数；推荐必须排除当前岗位。
- 新 bug 必须先转化为可复现自动化测试，再修复并保留回归测试。
- 推送前通过 pytest、quality gate 和 `git diff --check`，并确认没有真实个人信息被跟踪。
- 任何日志或交接文档都必须有英文主文件和语义一致的 `.zh-CN.md` 对照文件。
