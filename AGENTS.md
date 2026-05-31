# AGENTS.md

## 项目概述

AI 知识库助手——自动从 GitHub Trending 和 Hacker News 采集 AI/LLM/Agent 领域技术动态，经 AI 分析后结构化存储为 JSON，并支持通过 Telegram / 飞书多渠道分发，帮助团队高效追踪前沿动态。

## 技术栈

| 层级 | 技术 |
|------|------|
| 运行时 | Python 3.12 |
| Agent 框架 | OpenCode + 国产大模型 |
| 工作流编排 | LangGraph |
| 数据采集 | OpenClaw |

## 编码规范

### 格式化 & Lint

| 语言 | 格式化 | Import 排序 | Lint | 类型检查 |
|------|--------|-------------|------|----------|
| Python | black（行宽 120） | isort | ruff | mypy --strict |
| TypeScript | — | — | eslint | strict mode |

- TypeScript 适用范围：通知 Bot 前端/CLI + Web Dashboard（当前待开发）
- 所有工具配置统一在 `pyproject.toml` / `eslint.config.js`

### 命名

- 变量 / 函数：**snake_case**
- 类：**PascalCase**
- 常量：**UPPER_SNAKE_CASE**
- 以 `_` 前缀的函数/方法视为私有，不强制文档

### 文档

- Docstring 采用 **Google 风格**（Args / Returns / Raises）
- 所有公开函数签名必须有 docstring
- `_` 前缀私有函数可省略
- dataclass 类本身需要 docstring，简单派生方法（`to_dict`、`__post_init__` 等）不强制
- re-export 函数（`from x import y`）不强制

### 日志

- **禁止裸 `print()`**，统一使用 `logging` 模块
- 使用 `logging.getLogger(__name__)` 获取 logger
- 日志级别：**INFO** 覆盖关键业务节点 + 业务中间细节；**DEBUG** 仅用于开发临时调试
- 日志格式在入口统一配置一次（`dictConfig` 或 `basicConfig`），不散落各处
- **禁止**在日志中输出密钥或用户隐私数据，CI 跑 `detect-secrets` 扫描

### 类型注解

- Python：所有公开函数签名必须有类型注解，CI 跑 `mypy --strict`
- TypeScript：启用 strict mode

### 异常处理

- 所有 I/O 操作必须异常捕获，不允许静默吞错
- 定义项目级自定义异常基类 `JKNotesError`，按模块派生子类（如 `FetchError`、`ParseError`）
- 网络请求使用 `tenacity` 做有限次数重试 + 指数退避
- 捕获后一律 raise 或返回 `Optional[T]`，不返回无说明的裸 `None`

### 魔法字符串

- 业务逻辑中的魔法字符串必须提取为常量
- HTTP header、日志模板、Auth 前缀等基础设施字符串除外
- 重复出现的字符串必须提取

### TODO

- 只允许 `TODO(#issue号):` 格式（如 `TODO(#42): 补充重试逻辑`）
- 裸 TODO 禁止提交到长期分支（main / develop 等）
- CI 检测裸 TODO，发现即失败

### 依赖管理

- **conda**：负责创建虚拟环境和管理 Python 解释器版本
- **uv**：负责安装所有包（`uv pip install`），依赖声明在 `pyproject.toml`
- `uv.lock` 提交到仓库
- 开发依赖放在 `[project.optional-dependencies]` 的 `dev` 组下

### 环境变量

- 统一加 `JK_` 前缀（如 `JK_GITHUB_TOKEN`），避免和系统变量冲突
- 开发环境使用 `.env` 文件 + `python-dotenv` 加载
- `.env` 必须在 `.gitignore` 中
- 必须提供 `.env.example`，列出所有需要的变量名和说明

### 测试

- 测试框架：pytest + pytest-cov
- 单测覆盖率全仓库整体 ≥ 80%
- 排除 `__init__.py` 和 `if __name__ == "__main__"` 块
- 外部 API 调用使用 mock 替代
- 知识条目 JSON 用 **pydantic** 定义 schema，写入时强制校验；CI 扫描 `knowledge/articles/` 做批量 schema 验证

### Git & 协作

- 分支模型：GitHub Flow（main + feature 分支）
- Commit message：Conventional Commits（`feat:`, `fix:`, `docs:` 等）
- PR 合并条件：至少 1 人 review + CI 全绿
- **禁止**裸 TODO 提交到长期分支

### CI（GitHub Actions）

- 触发条件：push 到 main + 所有 PR
- 步骤（按顺序，任意失败即中断）：
  1. detect-secrets（敏感信息扫描）
  2. ruff lint
  3. isort check
  4. black check
  5. mypy --strict
  6. pytest + coverage
  7. 裸 TODO 检测

### 规范更新

- 规范修改走 PR + 1 人 review，和代码同等待遇
- 新 PR 必须符合最新规范（CI 拦截）
- 已有代码不强制立即对齐

## 项目结构

```
jk-notes/
├── .opencode/
│   ├── agents/          # Agent 角色定义与配置
│   └── skills/          # 可复用技能模块
├── knowledge/
│   ├── raw/             # 原始采集数据（HTML / API 响应）
│   └── articles/        # 结构化知识条目（JSON）
├── AGENTS.md
└── README.md
```

## 知识条目 JSON 格式

```json
{
  "id": "gh-20260526-001",
  "title": "LangGraph v0.3 发布：新增子图并行执行",
  "source_url": "https://github.com/langchain-ai/langgraph/releases/tag/v0.3.0",
  "source_type": "github_trending | hacker_news",
  "summary": "一句话摘要，不超过 200 字",
  "tags": ["langgraph", "agent", "release"],
  "category": "framework_update | paper | tool | opinion",
  "status": "draft | reviewed | published",
  "collected_at": "2026-05-26T08:00:00Z",
  "reviewed_at": null,
  "published_at": null,
  "metadata": {}
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| id | 是 | `{来源缩写}-{日期}-{序号}` |
| title | 是 | 原文标题或自拟标题 |
| source_url | 是 | 原始链接，不可为空 |
| source_type | 是 | 枚举值 |
| summary | 是 | ≤200 字中文摘要 |
| tags | 是 | 2-5 个标签 |
| category | 是 | 枚举值 |
| status | 是 | 状态流转：draft → reviewed → published |
| collected_at | 是 | ISO 8601 |
| reviewed_at | 否 | 通过审查后填写 |
| published_at | 否 | 分发成功后填写 |
| metadata | 否 | 扩展字段 |

## Agent 角色概览

| 角色 | 职责 | 输入 | 输出 |
|------|------|------|------|
| **采集 Agent** | 爬取 GitHub Trending / HN 前页，提取条目链接与原始摘要 | 定时触发 / 手动指令 | `knowledge/raw/` 下的原始数据 |
| **分析 Agent** | 读取原始数据，调用大模型生成中文摘要与标签分类 | `knowledge/raw/` | 状态为 `draft` 的 JSON 写入 `knowledge/articles/` |
| **整理 Agent** | 审查 draft 条目质量，标记 `reviewed`；按渠道格式化后分发 | `knowledge/articles/` 中 status=draft 的条目 | 状态更新为 `reviewed` / `published`，推送至 Telegram / 飞书 |

## 红线

- **禁止**在代码中硬编码 API Key / Token / Secret，一律走环境变量
- **禁止**写入 `knowledge/raw/` 之外的原始数据
- **禁止**跳过 status 流转直接标记为 `published`
- **禁止**删除或覆盖已有 `id` 的知识条目，只能追加或更新状态
- **禁止**向外部服务发送未标记 `reviewed` 的条目
- **禁止**在日志中输出任何密钥或用户隐私数据

## Agent skills

### Issue tracker

Issues tracked on GitHub (yliu6681/jk-notes). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout. See `docs/agents/domain.md`.
