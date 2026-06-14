---
name: open-source-reuse-advisor
description: "Find and compare existing open-source projects before building a requested feature, product, app, agent, library, plugin, script, website, or tool. Use whenever the user says they want to implement/build/make/develop/create something and asks or implies any of: search GitHub, find similar repositories, avoid reinventing the wheel, check whether this already exists, find existing code, find open-source alternatives, compare libraries/tools/apps, reuse existing projects, fork or adapt a repo, or get project links for download/reference/upgrade. Also use when the user asks in Chinese phrases such as 找类似项目, 查 GitHub, 有没有现成的, 避免重复造轮子, 开源替代, 复用代码, 二开, fork, 借鉴已有项目."
---

# Open Source Reuse Advisor

## Core Rule

Treat the task as an evidence-based reuse investigation, not as a claim that all of GitHub has been searched. Never say a project does not exist globally. Say only what was or was not found in the searched sources.

## GitHub Token Handling

Before the first GitHub search in a session, check whether a usable token exists:

```bash
python scripts/search_sources.py --token-status
```

If the status is `missing`, `invalid`, or `expired`, ask the user for a GitHub personal access token. Explain that a token improves GitHub API limits and can be a fine-grained token with only public repository read/search access when the task only searches public repositories. Do not print the token back to the user.

After the user provides the token, store it locally with:

```bash
python scripts/search_sources.py --save-token
```

When running in an interactive terminal, the script prompts for the token securely. When running as an agent without an interactive prompt, set `GITHUB_TOKEN` only for that command invocation or ask the user how they want it stored. Prefer the script's local token file over embedding tokens in commands.

Token lookup order:

1. `GITHUB_TOKEN` environment variable
2. Local token file managed by `scripts/search_sources.py`

If GitHub returns authentication errors during search, run `--token-status` again. If the token is invalid, ask for a replacement and save it locally. Do not repeatedly ask when the saved token is valid.

## Workflow

1. Restate the user's need as a feature brief:
   - Core job-to-be-done
   - Must-have features
   - Nice-to-have features
   - Platform, language, license, deployment, privacy, or budget constraints
   - Integration points and non-goals

2. Build 4-8 search queries:
   - Product-language queries, such as `local first markdown knowledge base backlinks`
   - Ecosystem queries, such as `npm vector database ui`, `pypi pdf table extraction`
   - Alternative/comparison queries, such as `open source alternative to obsidian`
   - GitHub-specific queries with `in:readme`, topics, language, or stars filters when useful
   - Chinese and English variants when the user's domain terms are likely bilingual

3. Search multiple sources when available:
   - GitHub repositories first
   - Package registries that match the likely ecosystem: npm, PyPI, crates.io, Maven, Go packages, Docker Hub
   - Web search for project homepages, awesome lists, Hacker News, Product Hunt, papers, or docs
   - Official project repositories and docs for final facts

4. Use `scripts/search_sources.py` for fast initial discovery when internet access is available. Run it with the user's requirement and optional queries:

```bash
python scripts/search_sources.py "local first markdown knowledge base backlinks full text search" --limit 8 --github --npm --pypi
```

The script returns JSON candidates with links and metadata. If GitHub authentication is available via `GITHUB_TOKEN`, it uses it; otherwise it falls back to unauthenticated GitHub REST search and package registry APIs. The script is only a candidate generator; still verify important claims by opening the repository or official package page.

5. For each serious candidate, inspect enough source material to support the recommendation:
   - README and docs
   - Stars, forks, last push, release cadence, issues when available
   - License and commercial-use implications
   - Main language, package availability, API shape, architecture hints
   - Installation maturity, examples, tests, and maintenance signals

6. Score and compare candidates. Read `references/scoring-rubric.md` when producing a formal comparison, ranking, or final recommendation.

## Ranking Heuristics

Prefer projects that satisfy the user's actual feature intent over projects with merely similar names. A smaller active project with the exact API or architecture may outrank a popular but unrelated project.

Use these signals together:
 - Functional overlap with the requested core features
 - Missing features and likely effort to add them
 - Extra features that reduce future work
 - Maintenance health and community adoption
 - License compatibility and governance risk
 - Integration fit with the user's stack
 - Documentation quality and time-to-first-use
 - Forkability: modular code, clear architecture, tests, examples

## Output Format

Respond in Chinese unless the user asks otherwise. Include source links.

Use this structure for normal results:

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
   - 建议：直接使用 / fork / 借鉴架构 / 组合使用 / 暂不相关

对比结论：
- 最接近：
- 最适合直接用：
- 最适合二开：
- 是否值得从零做：
- 下一步：
```

If no strong match is found, still list partial matches and say:

```text
我没有在本次检索范围内发现高度重合项目；这不等于 GitHub/全网不存在。最接近的是...
```

## Recommendation Labels

- `直接使用`: Meets most must-have requirements and has acceptable license/maintenance.
- `fork 二开`: Core architecture matches, but several important features need changes.
- `借鉴架构`: Product direction differs, but implementation ideas are useful.
- `组合使用`: No single project matches, but multiple libraries can cover the need.
- `从零实现`: Existing projects have low overlap, unacceptable license risk, or high adaptation cost.
- `暂不相关`: Search hit shares keywords but not the user's core intent.

## Boundaries

Do not present stars as proof of quality. Do not recommend using code without license review. Do not clone or run unknown repositories unless the user explicitly asks and the execution risk is considered. For legal or commercial license decisions, summarize risks and recommend qualified legal review when stakes are high.
