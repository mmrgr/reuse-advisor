# Open Source Reuse Advisor

一个用于 **避免重复造轮子** 的 Codex Skill：在你动手实现某个功能、工具、插件、应用或 Agent 之前，先检索 GitHub 和包管理器中的相似开源项目，比较它们与需求的异同，并给出是否应该直接使用、fork 二开、借鉴架构、组合使用或从零实现的建议。

本项目不是“全量 GitHub 语义索引”，也不会承诺证明某个项目一定不存在。它的目标更务实：把“我想做 X”转化为一次结构化的开源复用调查，让开发者在写代码前先知道已有轮子在哪里、能复用到什么程度、风险是什么。

## Features

- **需求拆解**：把用户的自然语言想法拆成核心功能、可选功能、平台/语言/许可证/部署约束和非目标。
- **多查询检索**：根据需求生成多组搜索词，包括产品语义、技术生态、替代品、GitHub README/topic 方向的查询。
- **GitHub 项目发现**：通过 GitHub REST Search API 获取候选仓库、stars、forks、语言、license、更新时间、topics 等元数据。
- **包管理器候选发现**：支持 npm 搜索，并为 PyPI 生成可人工复核的搜索链接。
- **GitHub Token 管理**：支持检测、验证和本地保存 GitHub Token，提高 API 调用稳定性。
- **候选过滤**：默认过滤一部分 awesome-list / curated-list 类型结果，优先找真实可复用项目；也可通过参数重新包含清单类仓库。
- **复用决策矩阵**：从功能重合度、二开成本、维护状态、文档质量、许可证风险、生态适配度等维度判断。
- **中文输出模板**：面向中文用户输出“需求理解、搜索策略、候选项目、异同分析、复用建议、最终结论”。

## What It Is For

适合这些场景：

- “我想做一个功能，先帮我查查有没有现成开源项目。”
- “帮我找 GitHub 上类似的工具，看看能不能 fork 二开。”
- “有没有开源替代品可以参考？”
- “我要开发一个插件/Agent/网站/库，先避免重复造轮子。”
- “帮我比较几个库，判断哪个更适合复用。”

不适合这些场景：

- 证明“整个 GitHub 上绝对没有某个项目”。
- 替代法律层面的许可证审查。
- 自动克隆并运行未知仓库。
- 深度安全审计、供应链审计或商业尽调。

## Project Structure

```text
open-source-reuse-advisor/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── scoring-rubric.md
└── scripts/
    └── search_sources.py
```

- `SKILL.md`：Codex Skill 的核心说明，包含触发条件、工作流、Token 处理规则和输出格式。
- `scripts/search_sources.py`：候选项目检索脚本，支持 GitHub、npm、PyPI 搜索入口和 GitHub Token 检测。
- `references/scoring-rubric.md`：候选项目评分口径，包括相似度、维护状态、许可证和最终建议矩阵。
- `agents/openai.yaml`：Codex UI 展示信息。

## Installation

如果你希望 Codex 自动发现这个 skill，建议把项目目录放到或链接到 Codex skills 目录，例如：

```powershell
C:\Users\<you>\.codex\skills\open-source-reuse-advisor
```

当前项目可以直接放在任意目录使用；如果要被 Codex 自动触发，需要确保 Codex 能扫描到该 skill。

## GitHub Token

GitHub 未认证搜索有较低的速率限制。建议配置 GitHub Token，尤其是频繁检索时。

Token 查找顺序：

1. 环境变量 `GITHUB_TOKEN`
2. 本地文件 `~/.open-source-reuse-advisor/github_token`

检查 token 状态：

```bash
python scripts/search_sources.py --token-status
```

交互式保存 token：

```bash
python scripts/search_sources.py --save-token
```

如果只搜索公开仓库，建议使用细粒度 token，并只授予公开仓库读取/搜索所需的最小权限。不要把 token 写进 README、issue、日志或命令历史。

## CLI Usage

最简单的候选项目搜索：

```bash
python scripts/search_sources.py "local first markdown knowledge base backlinks" --limit 8
```

只搜索 GitHub：

```bash
python scripts/search_sources.py "semantic code search natural language repo search" --github --limit 10
```

同时搜索 GitHub、npm、PyPI：

```bash
python scripts/search_sources.py "pdf table extraction python library" --github --npm --pypi --limit 8
```

添加额外查询词：

```bash
python scripts/search_sources.py "local first notes app" \
  --query "markdown knowledge base backlinks" \
  --query "open source obsidian alternative" \
  --github --npm --limit 8
```

默认会过滤一部分 awesome-list / curated-list 类型仓库。如果你就是想找清单类资源，可以加：

```bash
python scripts/search_sources.py "open source crm" --github --include-lists
```

脚本输出 JSON，示例字段包括：

```json
{
  "source": "github",
  "name": "owner/repo",
  "url": "https://github.com/owner/repo",
  "description": "Project summary",
  "stars": 1234,
  "forks": 56,
  "language": "TypeScript",
  "license": "MIT",
  "updated_at": "2026-06-14T00:00:00Z",
  "archived": false,
  "topics": ["search", "developer-tools"]
}
```

## Skill Usage

在 Codex 中显式调用：

```text
请使用 $open-source-reuse-advisor：我想实现一个本地优先的 Markdown 知识库，支持双链、标签、全文搜索和同步。请搜索 GitHub、npm、PyPI 等来源，找最相似的开源项目，分析相同点、不同点、许可证风险和二开成本，最后建议我直接使用、fork 二开、借鉴架构、组合使用还是从零实现，并附项目链接。
```

更短的调用：

```text
Use $open-source-reuse-advisor to find existing open-source projects similar to my feature idea and recommend reuse, fork, or build from scratch.
```

如果不显式写 `$open-source-reuse-advisor`，触发率取决于 Codex 对请求意图的判断。为了确保触发，建议在提示词中直接写 skill 名称。

## Output Format

典型输出会包含：

```text
需求理解：
- 核心功能：
- 约束条件：
- 我会把“相似”定义为：

搜索策略：
- 查询词：
- 来源：
- 边界说明：

候选项目：
1. 项目名
   - 链接：
   - 简介：
   - 元数据：stars / license / 最近更新 / 语言
   - 相同点：
   - 不同点：
   - 复用风险：
   - 建议：

对比结论：
- 最接近：
- 最适合直接用：
- 最适合二开：
- 是否值得从零做：
- 下一步：
```

## Scoring Model

正式比较时建议使用 `references/scoring-rubric.md` 中的 100 分制：

- 35 分：核心功能重合度
- 15 分：平台、语言、框架或部署模型匹配度
- 15 分：可扩展性和 fork 友好度
- 10 分：维护健康度
- 10 分：文档和示例质量
- 10 分：许可证适配度
- 5 分：生态适配、包管理器可用性或集成能力

推荐解释：

- `直接使用`：需求高度匹配，许可证和维护状态可接受。
- `fork 二开`：核心架构匹配，但需要补若干重要功能。
- `借鉴架构`：产品方向不同，但实现思路值得参考。
- `组合使用`：没有单一项目完全匹配，但多个库能组合覆盖需求。
- `从零实现`：现有项目重合度低、许可证风险高或改造成本过高。
- `暂不相关`：搜索命中共享关键词，但不符合核心意图。

## Design Principles

1. **事实优先**：每个关键结论尽量附来源链接。
2. **不夸大覆盖率**：说清楚搜索了什么，不宣称全网不存在。
3. **功能重合优先于关键词相似**：项目名像不等于功能像。
4. **复用建议必须可执行**：不仅列链接，还要告诉用户怎么用、怎么改、为什么不该用。
5. **许可证风险显式提示**：尤其是 GPL、AGPL、无 license 或自定义 license。
6. **不运行未知代码**：默认只检索和阅读，不自动执行第三方仓库。

## Current Limitations

- GitHub 搜索仍然主要依赖关键词和 README/description/topics 元数据，不是完整语义索引。
- PyPI 当前只生成搜索 URL，没有解析 PyPI 搜索结果页。
- 还没有内置 crates.io、Maven、Go packages、Docker Hub、Product Hunt、Hacker News 的 API 解析器。
- 默认过滤清单类仓库可能漏掉有价值的 awesome list；必要时使用 `--include-lists`。
- 相似度最终判断依赖 agent 阅读 README、docs 和项目元数据后的分析。

## Roadmap

- 增加 crates.io、Maven Central、Go packages、Docker Hub 的结构化搜索。
- 增加 README 拉取和自动摘要。
- 增加 GitHub release、issue、PR 活跃度分析。
- 增加 license 风险标签和商业使用提示。
- 增加本地缓存，减少重复 API 调用。
- 增加候选项目 HTML/Markdown 报告导出。
- 可选接入向量索引，对高质量仓库做语义召回。

## Security Notes

- 不要在命令行参数中传入 GitHub Token，避免进入 shell history。
- 优先使用 `--save-token` 的交互式输入。
- 如果 token 曾经出现在聊天、日志或公开仓库中，应立即在 GitHub 中撤销并重新生成。
- 本项目只需要搜索公开项目时，不应使用高权限 token。

## License

This project is licensed under the MIT License.

Copyright and license details should be kept in the repository's `LICENSE` file when publishing.
