# Developer Handoff

## 快速接手

1. 阅读 `PROJECT_SPEC.md`、`docs/DEVELOPMENT_LOG.md` 和 `docs/TEST_LOG.md`。
2. 确认工作区干净，再运行 `scripts/run-quality-gate.ps1`。
3. 本地运行时双击 `Start-ResumeGrowthCoach.cmd`；它会检查 Ollama 和 `qwen2.5:3b`。
4. 修改 scoring、parsing、recommendations、persistence 或 API contract 后，必须更新测试和日志。

## 大修改交接模板

在 `docs/DEVELOPMENT_LOG.md` 追加：

```markdown
## YYYY-MM-DD: short change title

### 修改内容
- ...

### 验证结果
- command: ...
- result: ...

### 仍存在的问题
- ...

### 后续计划
- **P0**: ...
- **P1**: ...
- **P2**: ...
```

在 `docs/TEST_LOG.md` 追加：

```markdown
## YYYY-MM-DD 测试轮次

### 检查范围
- ...

### 可疑点与结果
- ...

### 未检查
- ...

### 使用感受和极端情况
- ...
```

## 变更完成条件

- 面向用户的分析、roadmap、recommendation 和 bullet draft 保持纯英文。
- 规则层先于 Ollama，模型失败不能让 API 失效。
- 直接岗位和推荐岗位使用同一评分函数；推荐必须排除当前岗位。
- 新 bug 必须先转成可复现测试，再修复并保留回归测试。
- 推送前通过 pytest、quality gate、`git diff --check`，并检查没有真实个人资料进入 tracked files。

