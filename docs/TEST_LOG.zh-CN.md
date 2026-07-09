# 刁钻测试日志

本文件是针对正确性、稳定性、极端情况和实际使用流程的主要测试日志。测试结果只描述当前实现行为，不代表分数可以预测录用结果。

英文主文档是 [TEST_LOG.md](TEST_LOG.md)。两份文件必须保持语义一致；先更新英文文件，再在同一个提交中更新本中文翻译。

## 2026-07-09 测试轮次

自动化结果：`36 passed, 1 warning`；`tools/quality_gate.py` 的全部 API contract checks 通过。

### 已检查

- 空简历、空 JD、空上传文件、缺少文件和不支持的扩展名。
- 超过 1,000,000 字符的简历和 JD。
- 页面渲染时是否转义恶意 HTML。
- 缺失 document 和 analysis ID 是否稳定返回 404。
- malformed PDF 是否返回 400 而不是 traceback。
- Ollama 可用、模型缺失、模型 JSON 损坏和超时配置。
- 同一 canonical role 的直接分数和推荐分数是否一致，以及当前岗位是否被排除。
- 极短文本、没有技能的 JD，以及没有项目证据的技能清单简历。

### 可疑发现与处理

| 可疑点 | 结果 | 处理 |
|---|---|---|
| 任意简历都产生相同 fallback 结果 | 已修复 | 先运行 deterministic analysis；LLM 失败只影响解释，不覆盖结构化匹配和分数 |
| 推荐岗位重复当前岗位 | 已修复 | 推荐使用 canonical role title，并排除当前岗位 |
| 推荐分数与直接查询不同 | 已修复 | 推荐和直接分析使用相同 canonical title scoring 路径 |
| 只有技能清单的简历可能接近满分 | 已修复/受限 | evidence coverage 会降低分数；无证据时不能达到 100 |
| 用户 HTML 可能注入页面 | 通过 | Jinja autoescape 已启用，并有回归测试 |
| 校验失败后用户输入消失 | 通过 | UI 保留已提交内容，并有回归测试 |
| Ollama 已安装但 API 没有监听 | 通过 | 启动脚本会启动服务并执行真实生成 smoke test |

### 未检查或需要专项测试

- 尚未进行真实浏览器点击级测试，因此跨浏览器表单、滚动和网络错误渲染仍未验证。
- 尚未完整测试包含表格、图片、扫描件或复杂多页布局的 PDF 提取准确率。
- 尚未进行并发、进程崩溃恢复和 SQLite 写入压力测试。
- 尚未验证首次下载模型、显存不足和端口冲突的全部分支。
- 尚未建立人工标注数据集，因此分数与真实录用结果的相关性未验证。

### 使用感受

- 正常 text-to-analysis 流程连贯；错误输入会保留，结果能区分 direct score、evidence coverage 和 model status。
- 启动器比手动激活环境更稳定，但模型首次加载可能需要等待。
- fallback 仍然可用，但用户必须知道它不是本地模型生成的结果。

### 极端情况结论

- 已覆盖的极端输入不会产生未处理异常，会返回 400/404/413 或安全转义后的 200 HTML 页面。
- Ollama 真实 smoke test 已通过。Ollama 不可用时 deterministic fallback 应继续工作，但仍建议额外测试主动停止服务的场景。

## 可复用命令

```powershell
./scripts/run-quality-gate.ps1
```

或：

```powershell
.\.venv\Scripts\python.exe tools\quality_gate.py
```

## 2026-07-09 P1 修复验证

- 验证网页只上传 resume 和 job description 文件即可提交。
- 验证超大文件经过有上限的分块读取后被拒绝。
- 验证删除 resume 会同时删除关联 analysis 记录。
- 验证 Ollama 非英文用户可见输出会安全 fallback。
- 验证真实 `qwen2.5:3b` smoke test 通过。
- 最终自动化结果：`41 passed, 1 warning`。
