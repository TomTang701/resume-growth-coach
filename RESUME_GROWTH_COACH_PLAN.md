# Resume Growth Coach 项目计划

本文件只保存项目设计计划，不代表已经开始实现项目代码。

## 1. 项目定位

Resume Growth Coach 是一个 local-first AI + backend 项目，用于分析用户简历和目标 job description，识别技能差距，并生成可执行的自我提升路线。

项目目标不是简单改写简历，而是帮助用户回答三个问题：

- 当前简历和目标岗位匹配在哪里？
- 缺少哪些技能、项目证据或关键词？
- 接下来 2 周、1 个月、3 个月应该补什么？

这个项目用于补强简历中的以下能力：

- FastAPI backend
- local LLM integration
- document parsing
- structured scoring
- SQLite persistence
- API testing
- goal planning workflow

## 2. 与现有项目的区别

当前简历已有项目：

- iPhone Mirroring for Windows：systems / tooling / Windows packaging
- Amazon Clone：React frontend
- Pet Adoption Management Platform：PHP / MySQL full-stack course project

Resume Growth Coach 的差异化重点：

- 不是传统 CRUD 或 PHP 页面项目。
- 不重复 Dog Adoption 的 database workflow。
- 重点展示 modern backend service + local AI workflow。
- 与真实求职场景高度相关，方便在面试中解释设计动机。

## 3. 技术栈

默认技术栈：

- Backend: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- UI: server-rendered HTML + HTMX 或 minimal Jinja templates
- PDF parsing: pdfplumber
- Local AI: Ollama
- Default model: qwen2.5:3b
- Fallback model: qwen2.5:1.5b
- Tests: pytest + FastAPI TestClient

MVP 不使用复杂 React 前端，优先把 backend、AI workflow、document parsing 和 testing 做扎实。

## 4. 核心功能

### Resume/JD 输入

- 支持粘贴 resume text。
- 支持粘贴 job description text。
- 支持上传 `.txt`。
- 支持上传 `.pdf` 并用 pdfplumber 抽取文本。

### Deterministic analysis

先用规则和关键词匹配做确定性分析，避免项目变成纯 LLM wrapper。

需要提取：

- resume skills
- resume projects
- education signals
- job required skills
- job preferred skills
- job responsibilities
- matched keywords
- missing keywords
- matched project evidence

### Local LLM analysis

Ollama 只负责解释和建议：

- resume fit summary
- skill gap explanation
- project improvement suggestions
- learning roadmap
- English resume bullet drafts

如果 Ollama 不可用，系统仍然返回 deterministic analysis。

### 输出结果

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

所有可直接放进简历的输出必须是英文。

## 5. API 设计

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

用途：运行 resume/JD 匹配分析。

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

用途：读取成长计划。

输出：

- 2-week goals
- 1-month goals
- 3-month goals

## 6. 数据表设计

MVP SQLite tables：

- `documents`
  - stores resume text and metadata
- `job_descriptions`
  - stores JD text and extracted metadata
- `analyses`
  - stores score, summary, model status, timestamps
- `skill_matches`
  - stores matched and missing skills
- `growth_goals`
  - stores 2-week, 1-month, and 3-month plans

不保存敏感账号密码。MVP 是 single-user local app，不做登录系统。

## 7. UI 设计

单页本地 web app：

- 左侧：resume input 和 JD input
- 中间：run analysis button 和 model status
- 右侧：analysis result

结果区域包含：

- score card
- matched skills table
- missing skills table
- project evidence list
- growth roadmap
- resume bullet drafts

页面说明可以中文优先、中英混合；但用于简历的输出必须英文。

## 8. 测试计划

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

- 输入当前 resume 和一个 SWE internship JD。
- 系统能返回 matched skills、missing skills 和 practical growth roadmap。
- Ollama 不运行时仍能返回 deterministic analysis。
- README 能让新用户从 clean checkout 跑起来。

## 9. MVP 边界

MVP 包含：

- FastAPI backend
- SQLite persistence
- simple local UI
- text/pdf parsing
- deterministic skill scoring
- Ollama integration
- fallback without Ollama
- pytest tests
- README setup guide

MVP 不包含：

- 多用户登录
- 云部署
- 支付功能
- 大规模 vector database
- 复杂 React frontend
- 自动修改真实简历文件

## 10. 推荐两周实施节奏

### Days 1-2

- Create repo and project skeleton.
- Add FastAPI app, SQLite setup, SQLAlchemy models.
- Add basic document upload/paste APIs.

### Days 3-4

- Implement text and PDF parsing.
- Add deterministic keyword extraction.
- Add skill matching and scoring.

### Days 5-6

- Add analysis persistence.
- Add API tests for document and analysis flows.

### Days 7-8

- Add Ollama client.
- Add structured prompt templates.
- Add fallback behavior when Ollama is offline.

### Days 9-10

- Build simple HTML/HTMX UI.
- Display score, gaps, evidence, and roadmap.

### Days 11-12

- Add sample sanitized resume and JD.
- Improve README with screenshots or sample output.

### Days 13-14

- Polish tests.
- Verify clean setup.
- Prepare resume bullet drafts for this project.

## 11. 未来可写入简历的英文 bullet 草稿

完成 MVP 后，可考虑写入简历：

- Built a local-first AI resume growth coach with FastAPI, SQLite, SQLAlchemy, and Ollama to compare resumes against job descriptions.
- Implemented deterministic skill matching and gap scoring before LLM generation, reducing dependence on prompt-only analysis.
- Added PDF/text parsing, persisted analysis history, and generated 2-week, 1-month, and 3-month self-improvement roadmaps.
- Tested document upload, analysis, and offline LLM fallback flows with pytest and FastAPI TestClient.

这些 bullet 只有在对应功能真实完成并验证后才能加入正式简历。

## 12. 仓库建议

推荐新项目仓库名：

`resume-growth-coach`

推荐 GitHub visibility：

- public：如果使用 sanitized samples，适合作为简历展示项目。
- private：开发早期可以先 private，稳定后再 public。

不要提交真实个人简历、真实 JD 或包含个人隐私的数据样本。
