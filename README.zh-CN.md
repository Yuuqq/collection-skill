<p align="center">
  <img src="docs/banner.svg" alt="collection-skill 横幅" width="100%"/>
</p>

<h3 align="center">
  发现 · 编目 · 匹配 · 抓取
</h3>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="https://github.com/Yuuqq/collection-skill/blob/main/README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.es.md">Español</a>
</p>

<p align="center">
  <img alt="状态" src="https://img.shields.io/badge/状态-运行中-22c55e?style=flat-square">
  <img alt="许可证" src="https://img.shields.io/badge/许可证-MIT-blue?style=flat-square">
  <img alt="编目工具" src="https://img.shields.io/badge/已编目工具-183-8b5cf6?style=flat-square">
  <img alt="主要语言" src="https://img.shields.io/badge/主要语言-Python-3776AB?style=flat-square">
  <img alt="平台" src="https://img.shields.io/badge/平台-跨平台-475569?style=flat-square">
</p>

---

> 一个**发现并编目 GitHub 上采集 / 爬虫类 skill 与仓库**的技能,在你需要抓取数据时**渐进式推荐合适工具并开始抓取**。

## ✨ 特性一览

| | |
|:--|:--|
| 🗂️ **精选编目** | 自动发现 GitHub 仓库,归入**五大标准类目**,自动去重并打分排序。 |
| 🧭 **渐进式披露** | 绝不一股脑倾倒整个编目 —— 类目菜单 → 工具卡片 → 工作流 → 抓取。 |
| 🗃️ **JSON 为本** | `tool-catalog.json` 是唯一权威数据源,Markdown 视图由脚本生成。 |
| 🔐 **默认安全** | 令牌从 `gh` 密钥环 / 环境变量读取 —— 仓库内不留任何凭据。 |
| ⏱️ **可定时** | 通过 cron / 任务计划程序安装周期性刷新。 |

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
当你说*"我想抓 X"* 时,它会走一条短漏斗:

```
类目菜单  →  工具卡片  →  加载工作流  →  确认范围  →  抓取
```

## 📊 编目概览

> 由 `tool-catalog.json` 自动生成 · 最近刷新 `2026-07-13`

| 类目 | 数量 | | 主要语言 |
|------|----:|---|----------|
| 🕸️ web-scraper | 37 | | Python · Java · TypeScript |
| 🔌 api-collector | 31 | | Python · TypeScript · Java |
| ⚡ dynamic-scraper | 42 | | Python · TypeScript · HTML |
| 🤖 agent-skill | 16 | | Python · TypeScript · JavaScript |
| 📚 dataset | 28 | | Python · HTML · JavaScript |
| **合计** | **154** | | **Python(80)** 居首 |

## 🎴 类目卡片

<table>
  <tr>
    <td width="50%" align="center"><img src="docs/card-web-scraper.svg" alt="web-scraper 卡片"/><br><sub><a href="docs/card-web-scraper.svg">🕸️ web-scraper · 37 个工具</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-dynamic-scraper.svg" alt="dynamic-scraper 卡片"/><br><sub><a href="docs/card-dynamic-scraper.svg">⚡ dynamic-scraper · 42 个工具</a></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/card-api-collector.svg" alt="api-collector 卡片"/><br><sub><a href="docs/card-api-collector.svg">🔌 api-collector · 31 个工具</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-agent-skill.svg" alt="agent-skill 卡片"/><br><sub><a href="docs/card-agent-skill.svg">🤖 agent-skill · 16 个工具</a></sub></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/card-dataset.svg" alt="dataset 卡片"/><br><sub><a href="docs/card-dataset.svg">📚 dataset · 28 个工具</a></sub></td>
  </tr>
</table>

## 🚀 用法

唤起该技能后,自然语言即可:

| 你说 | 会发生什么 |
|------|-----------|
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

# 3.(可选)安排每周刷新 —— 唤起技能并说 "定时刷新"
```

## 🗺️ 项目结构

```
collection-skill/
├── SKILL.md                       # 路由 + 核心原则
├── workflows/
│   ├── discover-catalog.md        # 从 GitHub 刷新
│   ├── match-and-crawl.md         # 渐进式披露 → 抓取
│   ├── browse-catalog.md          # 只读视图
│   └── schedule-refresh.md        # 安装周期性刷新
├── references/
│   ├── tool-catalog.json          # 权威数据(在此编辑)
│   ├── tool-catalog.md            # 生成的视图(请勿手改)
│   ├── discovery-log.md           # 只追加的运行历史
│   ├── category-keywords.md       # 每类目的搜索关键词
│   ├── repo-schema.md             # 条目结构
│   └── rate-limit-guide.md        # GitHub API 限额
├── templates/
│   ├── crawl-template.md          # 通用抓取工作流
│   ├── discovery-log-entry.md
│   └── run_scheduled_refresh.sh.template
├── scripts/
│   ├── discover_repos.py          # GitHub 搜索 → 编目
│   ├── build_catalog_md.py        # JSON → Markdown
│   └── add_repo.py                # 手动添加条目
└── docs/                          # README 横幅与图示
```

## ⚖️ 设计规则

- **JSON 为本。** `tool-catalog.md` 由 `build_catalog_md.py` 重新生成 —— 切勿手改。
- **渐进式披露。** 先类目,再卡片,选定工具后才加载工作流。
- **仓库不留凭据。** 令牌来自 `$GITHUB_TOKEN` 或 `gh auth token`。
- **保留用户字段。** 重新发现时永不覆盖 `notes`、`verified`、`favorite`、`workflow_file`。
- **尊重边界。** 遵守 `robots.txt`、速率限制与服务条款;抓取新域名前先确认范围。

## 🌍 多语言版本

| 语言 | 文件 |
|------|------|
| English | [`README.md`](README.md) |
| 简体中文 | [`README.zh-CN.md`](README.zh-CN.md) |
| 日本語 | [`README.ja.md`](README.ja.md) |
| Español | [`README.es.md`](README.es.md) |

## 📄 许可证

MIT
