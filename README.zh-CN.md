<p align="center">
  <img src="docs/banner.svg" alt="collection-skill 横幅" width="100%"/>
</p>

<p align="center">
  <img src="docs/demo.gif" alt="离线预览：小红书快速通道，确认范围前停止" width="92%"/>
  <br/>
  <sub>当前小红书快速通道的离线预览，读取本地文件。不是实时推理，也没有采集。</sub>
</p>

<h3 align="center">
  发现 · 编目 · 匹配 · 抓取
</h3>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.es.md">Español</a>
</p>

<p align="center">
  <img alt="状态" src="https://img.shields.io/badge/状态-运行中-22c55e?style=flat-square">
  <img alt="许可证" src="https://img.shields.io/badge/许可证-MIT-blue?style=flat-square">
  <img alt="编目工具" src="https://img.shields.io/badge/已编目工具-232-8b5cf6?style=flat-square">
  <img alt="覆盖平台" src="https://img.shields.io/badge/覆盖平台-19-e11d48?style=flat-square">
  <img alt="主要语言" src="https://img.shields.io/badge/主要语言-Python-3776AB?style=flat-square">
  <img alt="平台" src="https://img.shields.io/badge/平台-跨平台-475569?style=flat-square">
  <a href="https://github.com/Yuuqq/collection-skill/actions/workflows/discover.yml"><img alt="Discover &amp; Catalog" src="https://github.com/Yuuqq/collection-skill/actions/workflows/discover.yml/badge.svg"></a>
</p>

---

> 一个**中文社媒采集**技能:说出平台名 —— 小红书、抖音、B站、微博、知乎、贴吧、快手、公众号、淘宝、京东…… —— 即可拿到定向工具 shortlist(前置合规提醒)并开始抓取。背后是自动刷新的采集工具编目(爬虫 / API 采集器 / MCP 技能 / 数据集),同样覆盖任意网站与 API。

## ✨ 特性一览

| | |
|:--|:--|
| 🇨🇳 **中文社媒快速通道** | 说出平台名(小红书 / 抖音 / 微博 / 公众号 / 淘宝…)→ 定向 shortlist + 合规提醒,不走通用菜单。 |
| 🗂️ **精选编目** | 自动发现 GitHub 仓库,归入**五大标准类目**,去重后在各类目内按星标数排序。 |
| 🧭 **渐进式披露** | 绝不一股脑倾倒整个编目 —— 类目菜单 → 工具卡片 → 工作流 → 抓取。 |
| 🗃️ **JSON 为本** | `tool-catalog.json` 是唯一权威数据源,Markdown 视图由脚本生成。 |
| 🔐 **默认安全** | 令牌从 `gh` 密钥环 / 环境变量读取 —— 仓库内不留任何凭据。 |
| ⏱️ **可定时** | 通过 cron / 任务计划程序安装周期性刷新。 |

## 📥 安装

兼容所有支持开放 [Agent Skills](https://agentskills.io) 规范的智能体 —— Claude Code、Cursor、Codex 等:

```bash
npx skills add Yuuqq/collection-skill
```

<details>
<summary>手动安装(git clone)</summary>

克隆到你的智能体 skills 目录:

```bash
# Claude Code(个人级)
git clone https://github.com/Yuuqq/collection-skill.git ~/.claude/skills/collection-skill

# Cursor
git clone https://github.com/Yuuqq/collection-skill.git ~/.cursor/skills/collection-skill

# Codex
git clone https://github.com/Yuuqq/collection-skill.git ~/.codex/skills/collection-skill

# 或项目级: .claude/skills/ · .cursor/skills/ · .codex/skills/
```

</details>

> 发现脚本需要 Python 3.10+;建议用 [`gh` CLI](https://cli.github.com/) 或 `GITHUB_TOKEN` 认证以获得更高的 GitHub API 限额。

## 📦 它做什么

两半共享**同一个知识库**:

<p align="center">
  <img src="docs/flow.svg" alt="collection-skill 工作流程" width="92%"/>
</p>

### ① 发现 & 编目
周期性扫描 GitHub,寻找*采集类*仓库,归入五大类目:

| 标签 | 含义 | 示例 |
|-----|------|------|
| 🕸️ `web-scraper` | 静态 HTML / 简单 HTTP 抓取 | BeautifulSoup、httpx、Selectolax、Scrapy |
| ⚡ `dynamic-scraper` | JS 渲染页面、SPA | Playwright、Selenium、Crawl4AI |
| 🔌 `api-collector` | REST/GraphQL、SDK 拉取、ETL | SDK 驱动的采集器、数据管道 |
| 🤖 `agent-skill` | Claude/GPT 技能、MCP 服务器 | 工具调用框架 |
| 📚 `dataset` | 公开数据集、awesome 列表 | 精选资源仓库 |

### ② 匹配 & 抓取
直接点名中文平台(小红书/抖音/微博/公众号/淘宝…)会跳过通用漏斗:

```
合规提醒  →  平台定向 shortlist  →  加载工作流  →  确认范围  →  抓取
```

其他目标则走短漏斗:

```
类目菜单  →  工具卡片  →  加载工作流  →  确认范围  →  抓取
```

## ⚠️ 合规声明

编目中的多数中文平台爬虫为社区逆向实现,违反平台服务条款(ToS)。本技能收录它们是为了研究 / 已授权场景的信息可见性,并在展示任何工具前强制出现合规提醒。**使用者须自行承担合规责任**:遵守 ToS 与 `robots.txt`,控制请求频率,仅在具合法依据时采集个人数据(尽量匿名化),未经授权不得将抓取内容商用。本技能不会协助规避任何反爬 / 风控机制。

## 📊 编目概览

> 由 `tool-catalog.json` 自动生成 · 最近刷新 `2026-11-23`

| 类目 | 数量 | | 主要语言 |
|------|----:|---|----------|
| 🕸️ web-scraper | 55 | | Python · Java · Jupyter Notebook |
| 🔌 api-collector | 49 | | Python · Rust · Go |
| ⚡ dynamic-scraper | 51 | | Python · TypeScript · HTML |
| 🤖 agent-skill | 45 | | Python · TypeScript · JavaScript |
| 📚 dataset | 32 | | Python · HTML · JavaScript |
| **合计** | **232** | | **Python(124)** 居首 |

> 🆕 **每周都有新工具入库。** 目录每周自动刷新 —— 在[每周 digest](../../releases) 中查看本周新增。Watch 本仓库即可收到通知。

## 🎴 类目卡片

<table>
  <tr>
    <td width="50%" align="center"><img src="docs/card-web-scraper.svg" alt="web-scraper 卡片"/><br><sub><a href="docs/card-web-scraper.svg">🕸️ web-scraper · 55 个工具</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-dynamic-scraper.svg" alt="dynamic-scraper 卡片"/><br><sub><a href="docs/card-dynamic-scraper.svg">⚡ dynamic-scraper · 51 个工具</a></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/card-api-collector.svg" alt="api-collector 卡片"/><br><sub><a href="docs/card-api-collector.svg">🔌 api-collector · 49 个工具</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-agent-skill.svg" alt="agent-skill 卡片"/><br><sub><a href="docs/card-agent-skill.svg">🤖 agent-skill · 45 个工具</a></sub></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/card-dataset.svg" alt="dataset 卡片"/><br><sub><a href="docs/card-dataset.svg">📚 dataset · 32 个工具</a></sub></td>
  </tr>
</table>

## 🚀 用法

唤起该技能后,自然语言即可:

| 你说 | 会发生什么 |
|------|-----------|
| `抓小红书笔记` / `抖音评论` / `微博热搜` | 快速通道:平台定向 shortlist + 合规门 → 抓取 |
| `refresh` / `discover` / `刷新` | 运行 `scripts/discover_repos.py`,更新编目 |
| `我想抓 X` / `抓 X 数据` | 渐进式披露 → 类目菜单 → 卡片 → 抓取 |
| `browse` / `看看编目` | 只读的类目/卡片视图 |
| `schedule` / `定时` | 安装周期性刷新(cron / 任务计划程序) |

## 🛠️ 快速开始

```bash
# 1.(推荐)认证 —— 30 次/分钟 搜索请求,未认证仅 10 次/分钟
gh auth login

# 2. 首次刷新
python scripts/discover_repos.py
python scripts/build_catalog_md.py
python scripts/sync_readme_stats.py

# 3.(可选)安排每周刷新 —— 唤起技能并说 "定时刷新"
```

## 🤖 LLM 智能判级(可选)

默认情况下,设置 `LLM_API_KEY` 后,发现脚本会把整个编目(包括新候选)发送给 OpenAI 兼容端点。模型建议是否收录、所属类目及使用场景;人工策展条目受保护,具备采集特征的条目也不会因模型误判被移除。`--no-rescan` 只评估本次新增或更新的条目,`--no-llm` 在有密钥时仍可使用启发式规则。端点与密钥池设置见 [LLM 判级说明](references/llm-judging.md)。

[Discover & Catalog 工作流](.github/workflows/discover.yml)在每周一 03:17 UTC 刷新编目。在 **Settings → Secrets** 配置 `GH_PAT` 用于认证搜索和推送更新。`LLM_API_KEY` 可选,不配置时使用启发式规则。也可在 Actions 页面手动运行,通过 `categories` 指定以空格分隔的类目,或关闭 `llm`。发现成功后,[Weekly Digest](.github/workflows/weekly-digest.yml)会在最近七天有新收录条目时发布 GitHub Release。

## 🗺️ 项目结构

```
collection-skill/
├── SKILL.md                       # 路由 + 核心原则
├── workflows/
│   ├── discover-catalog.md        # 从 GitHub 刷新
│   ├── match-and-crawl.md         # 渐进式披露 → 抓取
│   ├── browse-catalog.md          # 只读视图
│   ├── schedule-refresh.md        # 安装周期性刷新
│   └── tools/                     # 单工具抓取工作流
├── references/
│   ├── tool-catalog.json          # 权威数据(在此编辑)
│   ├── tool-catalog.md            # 生成的视图(请勿手改)
│   ├── discovery-log.md           # 只追加的运行历史
│   ├── category-keywords.md       # 每类目的搜索关键词
│   ├── repo-schema.md             # 条目结构
│   ├── rate-limit-guide.md        # GitHub API 限额
│   ├── chinese-social-platforms.md # 平台别名与标签
│   └── llm-judging.md             # 可选判级与保护机制
├── templates/
│   ├── crawl-template.md          # 通用抓取工作流
│   ├── discovery-log-entry.md
│   └── run_scheduled_refresh.sh.template
├── scripts/
│   ├── discover_repos.py          # GitHub 搜索 → 编目
│   ├── build_catalog_md.py        # JSON → Markdown
│   ├── validate_catalog.py        # 写入前执行 schema 校验
│   ├── add_repo.py                # 手动添加条目
│   ├── sync_readme_stats.py       # 更新各语言 README 统计
│   ├── make_digest.py             # 生成新收录条目的摘要
│   └── offline_demo_walk.py       # 从本地文件播放离线演示
└── docs/                          # README 横幅与图示
```

## ⚖️ 设计规则

- **JSON 为本。** `tool-catalog.md` 由 `build_catalog_md.py` 重新生成 —— 切勿手改。
- **渐进式披露。** 先类目,再卡片,选定工具后才加载工作流。
- **仓库不留凭据。** 令牌来自 `$GITHUB_TOKEN` 或 `gh auth token`。
- **保留用户字段。** 重新发现时永不覆盖 `notes`、`verified`、`favorite`、`workflow_file`。
- **尊重边界。** 遵守 `robots.txt`、速率限制与服务条款;抓取新域名前先确认范围。

## 🤝 贡献一个工具

知道某个好用但还没收录的爬虫、采集器、agent skill 或数据集？30 秒即可提交：

- **开一个[工具收录 issue](../../issues/new?template=submit-tool.yml)** —— 我们会审核是否收录。
- **或直接提 PR** —— 编目规则与单工具 workflow 的写法见 [CONTRIBUTING.md](CONTRIBUTING.md)。

每一次提交都让目录对所有人更有用。🙌

## 🌍 多语言版本

| 语言 | 文件 |
|------|------|
| English | [`README.md`](README.md) |
| 简体中文 | [`README.zh-CN.md`](README.zh-CN.md) |
| 日本語 | [`README.ja.md`](README.ja.md) |
| Español | [`README.es.md`](README.es.md) |

## 📄 许可证

MIT —— 见 [LICENSE](LICENSE)。
