# Adversarial Test Log

本文件记录针对正确性、稳定性和使用流程的刁钻测试。测试结论只说明当前实现的行为，不代表评分具有招聘预测能力。

## 2026-07-09 测试轮次

自动化结果：`36 passed, 1 warning`；`tools/quality_gate.py` 的 API contract checks 全部通过。

### 检查范围

- 空 resume、空 JD、空上传文件、没有文件和不支持的扩展名。
- 超过 1,000,000 字符的 resume 和 JD。
- 恶意 HTML 输入是否被模板转义。
- 不存在的 document/analysis ID 是否返回稳定的 404。
- malformed PDF 是否返回 400 而非 traceback。
- Ollama 可用、模型缺失、模型返回 malformed JSON、模型超时配置。
- 同一 canonical role 的直接分数与推荐岗位分数是否一致，推荐是否排除当前岗位。
- 极短文本、无技能 JD、只有技能列表而没有项目证据的评分行为。

### 发现的可疑点与处理

| 可疑点 | 结果 | 处理 |
|---|---|---|
| 任意简历都显示同一个 fallback 结果 | 已修复 | deterministic analysis 先运行，LLM 失败只影响解释，不覆盖分数和结构化匹配 |
| 推荐岗位与当前岗位重复 | 已修复 | 推荐使用 canonical role title 并排除当前 role |
| 推荐分数与直接查询不同 | 已修复 | 推荐岗位使用与直接查询相同的 canonical title scoring |
| 只有技能清单却得到接近满分 | 已修复/受限 | 增加 evidence coverage factor，并测试无项目证据不得满分 |
| 用户输入 HTML 造成页面注入风险 | 通过 | Jinja autoescape 生效，加入自动化回归测试 |
| 错误提交后用户输入消失 | 通过 | UI 保留输入内容，加入自动化回归测试 |
| Ollama 已安装但服务未监听 | 通过 | 启动脚本自动启动服务并做真实生成 smoke test |

### 未检查或仍需专项检查

- 未进行真实浏览器点击级测试，因此没有验证不同浏览器的表单行为、滚动和网络失败显示。
- 未对包含表格、图片、扫描件或多页复杂布局的 PDF 做完整准确率测试。
- 未进行并发请求、进程崩溃恢复和 SQLite 写入压力测试。
- 未验证 Ollama 在模型首次下载、显存不足、端口被其他程序占用时的所有分支。
- 未建立人工标注数据集，因此不能证明分数和真实招聘结果相关。

### 使用感受

- 正常 text -> analysis 流程连贯，错误输入会留在页面，结果能区分 direct score、evidence coverage、model status。
- 启动入口比手动激活虚拟环境更稳定，但首次启动模型时仍可能等待较长时间。
- fallback 仍是可用的降级体验，但用户必须理解它不是本地模型生成结果。

### 极端情况结论

- 当前已覆盖的极端输入不会导致未处理异常，返回 400/404/413 或安全转义后的 200 页面。
- 真实 Ollama smoke test 已成功；模型不可用时应继续返回 deterministic fallback，仍需在关闭 Ollama 的真实进程场景复测。

## 可复用命令

```powershell
./scripts/run-quality-gate.ps1
```

或：

```powershell
.\.venv\Scripts\python.exe tools\quality_gate.py
```
