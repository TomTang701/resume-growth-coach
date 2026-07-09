# Resume Growth Coach 项目规范

> 来源计划：`RESUME_GROWTH_COACH_PLAN.md`
>
> 状态：本文件是项目规范，不代表已经开始实现代码。

## 1. 语言规则

本规范采用中文优先，允许技术名词中英文混用，方便开发时理解和沟通。

项目成果必须保持纯英文，包括：

- README 中面向招聘者、reviewer 或 GitHub 访客的项目介绍
- demo 页面中展示给用户的核心分析结果
- sample output
- generated resume bullets
- growth roadmap
- project improvement suggestions
- API response 中面向用户展示的分析文本

中文可以用于：

- 本地开发笔记
- issue decomposition
- 代码实现前的思路说明
- 给自己看的任务列表
- UI 辅助说明或输入标签

只要内容可能被当作项目展示成果、简历素材或公开 demo，就必须使用纯英文。

## 2. 项目目标

Resume Growth Coach 是一个 local-first AI backend 项目，用于比较用户简历和目标 job description，识别技能差距、关键词差距和项目证据差距，并生成可执行的成长路线。

它不是简单的 resume rewriter，而是帮助用户回答三个问题：

- 当前简历和目标岗位匹配在哪里？
- 缺少哪些 skills、keywords 或 project evidence？
- 接下来 2 周、1 个月、3 个月应该补什么？

这个项目用于补强简历中的以下能力：

- FastAPI backend development
- local LLM integration
- document parsing
- structured scoring
- SQLite persistence
- API testing
- goal planning workflow

## 3. 范围原则

所有实现决策遵循 Ponytail 思路：

1. 不做 speculative features。
2. 先复用已有代码、框架能力和平台能力，再新增抽象。
3. Python standard library 和已有依赖优先，新依赖靠后。
4. 保持最小可工作的实现，但不能省掉 validation、error handling、privacy、security 和必要测试。
5. 对 parser、scoring、persistence、API behavior 这类非平凡逻辑，留下能防回归的最小测试。

Ponytail 在这里是开发约束，不是偷工减料。实现前仍然要读真实流程，理解数据从上传、解析、分析、持久化到展示的完整路径。

## 4. MVP 不做什么

MVP 不包含：

- multi-user authentication
- cloud deployment
- payment features
- large-scale vector database
- complex React frontend
- 自动修改真实 resume 文件
- 把真实私人 resume、真实 JD 或包含隐私的数据样本提交到 git

## 5. 技术栈

默认技术栈：

- Backend: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- UI: server-rendered HTML with Jinja templates，必要时加 HTMX
- PDF parsing: pdfplumber
- Local AI: Ollama
- Default model: `qwen2.5:3b`
- Fallback model: `qwen2.5:1.5b`
- Tests: pytest + FastAPI TestClient

依赖策略：

- MVP 只加入真正需要的依赖。
- 新依赖必须比少量自写代码更可靠、更清晰，或明显降低风险。
- 每个新增依赖都应在 README 中说明用途。

## 6. 用户流程

1. 用户粘贴 resume text，或上传 `.txt` / `.pdf` resume。
2. 用户粘贴 job description text，或上传 `.txt` / `.pdf` job description。
3. 系统抽取文本并识别有用 sections。
4. 系统先运行 deterministic analysis。
5. 如果 Ollama 可用，系统调用本地 LLM 生成解释和建议。
6. 系统保存 analysis 和 goal plan。
7. 用户查看 score、matched skills、missing skills、evidence、roadmap 和 English resume bullet drafts。

如果 Ollama 不可用，系统仍然必须返回 deterministic analysis 和 fallback goal plan。

## 7. 功能需求

### 7.1 Document Input

支持：

- pasted resume text
- pasted job description text
- uploaded `.txt` files
- uploaded `.pdf` files parsed with pdfplumber

校验：

- 拒绝空文档。
- 拒绝不支持的文件类型。
- 在 local app configuration 中限制文件大小。
- 不把敏感样本静默写入 tracked files。

### 7.2 Deterministic Analysis

deterministic layer 必须在任何 LLM call 之前运行，并提取：

- resume skills
- resume projects
- education signals
- job required skills
- job preferred skills
- job responsibilities
- matched keywords
- missing keywords
- matched project evidence

fit score 必须能从 matched / missing signals 中解释出来，不能只依赖 LLM 给出的 opaque score。

### 7.3 Local LLM Analysis

Ollama 可以生成：

- resume fit summary
- skill gap explanation
- project improvement suggestions
- learning roadmap
- English resume bullet drafts

LLM 约束：

- 所有面向用户展示的 LLM 输出必须是英文。
- resume-ready bullet drafts 必须是英文。
- LLM 不能编造成果，不能把建议中的 future work 写成已经完成。
- prompt 必须区分 verified resume evidence 和 suggested future improvements。
- Ollama offline 或调用失败时不能导致 API 失败。

### 7.4 Output

核心输出：

- overall fit score
- matched skills
- missing skills
- evidence found in resume
- recommended improvement areas
- 2-week goals
- 1-month goals
- 3-month goals
- recommended project additions
- English resume bullet drafts

这些输出中，除字段名和内部标识外，展示给用户或可复制到简历/项目页的文本必须为纯英文。

## 8. API 规范

### `POST /api/documents/resume`

用途：上传或粘贴 resume。

输入：

- text content, or
- `.txt` file, or
- `.pdf` file

输出：

- `resume_id`
- extracted text preview
- detected sections

### `POST /api/documents/job-description`

用途：上传或粘贴 job description。

输出：

- `job_description_id`
- extracted text preview
- detected role keywords

### `POST /api/analyses`

用途：运行 resume/JD matching。

输入：

- `resume_id`
- `job_description_id`
- optional model name

输出：

- `analysis_id`
- deterministic fit score
- Ollama status

### `GET /api/analyses/{analysis_id}`

用途：读取完整分析结果。

输出：

- fit summary
- matched skills
- missing skills
- matched evidence
- project suggestions
- resume bullet drafts

### `GET /api/goals/{analysis_id}`

用途：读取 growth roadmap。

输出：

- 2-week goals
- 1-month goals
- 3-month goals

## 9. 数据模型

MVP SQLite tables：

- `documents`: resume text, type, metadata, timestamps
- `job_descriptions`: JD text, extracted metadata, timestamps
- `analyses`: score, summary, model status, timestamps
- `skill_matches`: matched and missing skills per analysis
- `growth_goals`: 2-week, 1-month, and 3-month plans

隐私要求：

- 不保存 credentials。
- 不提交真实 resumes、真实 job descriptions 或 personally identifying samples。
- 只使用 sanitized sample files。
- local database files 必须加入 `.gitignore`。

## 10. UI 规范

构建单页 local web app：

- 左侧：resume input 和 JD input
- 中间：run analysis button 和 model status
- 右侧：analysis result

结果展示：

- score card
- matched skills table
- missing skills table
- project evidence list
- growth roadmap
- resume bullet drafts

UI 辅助说明可以中文优先、中英文混用；但所有 analysis result、roadmap、project suggestions、resume bullet drafts 必须为英文。

## 11. 测试计划

Unit tests：

- text parsing
- PDF parsing
- keyword extraction
- skill matching
- fit score calculation
- goal generation fallback

API tests：

- upload resume text
- upload JD text
- upload `.txt`
- run analysis
- fetch analysis
- fetch goals
- Ollama unavailable fallback

Manual acceptance：

- 使用 sanitized resume 和 SWE internship JD 运行。
- 确认系统返回 matched skills、missing skills 和 practical roadmap。
- 关闭 Ollama 后，确认 deterministic analysis 仍然可用。
- 从 clean checkout 验证 README setup 可运行。
- 确认项目展示成果、sample output 和 generated bullets 全部为英文。

## 12. 实施计划

### Days 1-2: Skeleton

- 初始化 repo 和 Python project structure。
- 添加 FastAPI app。
- 添加 SQLite 和 SQLAlchemy setup。
- 添加基础 document upload/paste APIs。

### Days 3-4: Parsing and Matching

- 实现 text parsing。
- 实现 PDF parsing。
- 添加 deterministic keyword extraction。
- 添加 skill matching 和 scoring。

### Days 5-6: Persistence and API Tests

- 持久化 analyses。
- 持久化 skill matches 和 growth goals。
- 添加 document 和 analysis flows 的 API tests。

### Days 7-8: Ollama Integration

- 添加 Ollama client。
- 添加 structured prompt templates。
- 添加 timeout/error handling。
- 添加 Ollama offline fallback。

### Days 9-10: Local UI

- 构建 server-rendered HTML UI。
- 展示 score、gaps、evidence 和 roadmap。
- 先保证功能完整，再做视觉 polish。

### Days 11-12: Samples and README

- 添加 sanitized sample resume 和 JD。
- 完善 README setup instructions。
- UI 可用后添加 sample output 或 screenshot。
- README 对外展示内容必须为英文。

### Days 13-14: Polish and Resume Evidence

- polish tests。
- 验证 clean setup。
- 只为已完成、已测试的功能准备 truthful English resume bullet drafts。

## 13. Git 方案

### 13.1 Repository Initialization

当前目录尚未初始化为 git repository。准备开始实现时执行：

```powershell
git init
git branch -M main
```

第一次 commit 前先创建 `.gitignore`，至少排除：

```gitignore
.venv/
__pycache__/
.pytest_cache/
*.pyc
*.sqlite
*.sqlite3
*.db
.env
.env.*
uploads/
local_data/
real_samples/
```

sanitized demo samples 可以放在 `samples/sanitized/` 这类明确目录中。

### 13.2 Branch Model

使用简单分支模型：

- `main`: stable, runnable MVP state
- `feature/<short-name>`: one feature or milestone at a time
- `fix/<short-name>`: small bug fixes
- `docs/<short-name>`: documentation-only work

避免 long-lived branches。测试通过后合并。

### 13.3 Commit Style

commit 要小而清楚：

- `docs: add project specification`
- `chore: initialize fastapi project`
- `feat: add document upload endpoint`
- `feat: add deterministic skill matching`
- `test: cover ollama fallback`
- `fix: reject unsupported upload types`

每个 commit 应让项目处于可运行状态，或明确是 documentation-only 状态。

### 13.4 Suggested Milestone Commits

1. `docs: add project specification`
2. `chore: initialize python project`
3. `feat: add document models and persistence`
4. `feat: add resume and jd upload endpoints`
5. `feat: add text and pdf extraction`
6. `feat: add deterministic matching and scoring`
7. `feat: persist analysis results`
8. `feat: add ollama summary with offline fallback`
9. `feat: add local analysis UI`
10. `test: cover core api flows`
11. `docs: add clean setup guide and sanitized samples`

### 13.5 GitHub Visibility

推荐路径：

1. 开发早期保持 private。
2. 真实 resumes、真实 JDs、local databases 和 `.env` files 不进入 git。
3. 准备 public 前补齐 sanitized samples 和英文 README。
4. 只有当 reviewer 能理解并从 README 跑起来时，再切换 public。

### 13.6 Pre-Push Checklist

push 前检查：

- `pytest` passes。
- app 可以本地启动。
- `.gitignore` 覆盖 local databases、uploads、private samples 和 environment files。
- 没有真实 resume 或真实 job description 被 staged。
- README setup commands 与实际项目一致。
- README、sample output、screenshots 中的成果展示文本为英文。
- resume bullets 只声明已完成、已验证的功能。

## 14. Ponytail 使用说明

Ponytail 可通过 Codex 安装：

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex
```

然后打开 `/plugins`，从 Ponytail marketplace 安装 Ponytail；再打开 `/hooks`，review 并 trust 它的 lifecycle hooks；最后开启新线程。Node.js 必须在 `PATH` 中，hooks 才能运行。

如果插件未安装，就手动遵循同样原则：

- 做 MVP，不做 future platform。
- reuse before writing。
- standard library before dependency。
- native platform feature before custom code。
- 理解真实流程后，用最小 working diff 完成。
- 不为了简短牺牲 validation、data-loss handling、security、privacy、accessibility 或 required tests。

## 15. 未来可写入简历的英文 bullet 草稿

只有在对应功能真实完成并测试后，才可以使用这些 bullet：

- Built a local-first AI resume growth coach with FastAPI, SQLite, SQLAlchemy, and Ollama to compare resumes against job descriptions.
- Implemented deterministic skill matching and gap scoring before LLM generation, reducing dependence on prompt-only analysis.
- Added PDF/text parsing, persisted analysis history, and generated 2-week, 1-month, and 3-month self-improvement roadmaps.
- Tested document upload, analysis, and offline LLM fallback flows with pytest and FastAPI TestClient.

## 16. 开发交接与测试日志规范

项目维护必须同时更新以下文件：

- `docs/DEVELOPMENT_LOG.md`：记录较大修改、验证结果、遗留问题和按 P0/P1/P2 排序的未来计划。
- `docs/TEST_LOG.md`：记录刁钻测试检查范围、可疑点、使用感受、极端情况和未覆盖范围。
- `docs/HANDOFF.md`：记录接手步骤、日志模板和提交前完成条件。

出现 bug 时，先在 `tests/` 或 `tools/quality_gate.py` 中添加能复现问题的自动化测试，再修改实现；测试必须保留为回归保护。评分、解析、推荐岗位、持久化和 API contract 的修改属于大修改，不能只更新日志而不更新测试。

日志可以中文优先，面向用户的项目成果仍必须遵守本规范第 1 节的纯英文要求。
