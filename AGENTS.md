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

- 遵循 **PEP 8**，行宽上限 120
- 变量 / 函数使用 **snake_case**，类使用 **PascalCase**
- Docstring 采用 **Google 风格**（Args / Returns / Raises）
- **禁止裸 `print()`**，统一使用 `logging` 模块
- 类型注解覆盖所有公开函数签名
- 所有 I/O 操作必须异常捕获，不允许静默吞错

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
