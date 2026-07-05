<p align="center">
  <img src="docs/banner.svg" alt="collection-skill バナー" width="100%"/>
</p>

<h3 align="center">
  発見 · カタログ化 · 選定 · クロール
</h3>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="https://github.com/Yuuqq/collection-skill/blob/main/README.ja.md">日本語</a> ·
  <a href="README.es.md">Español</a>
</p>

<p align="center">
  <img alt="状態" src="https://img.shields.io/badge/状態-稼働中-22c55e?style=flat-square">
  <img alt="ライセンス" src="https://img.shields.io/badge/ライセンス-MIT-blue?style=flat-square">
  <img alt="カタログ数" src="https://img.shields.io/badge/収録ツール-183-8b5cf6?style=flat-square">
  <img alt="主要言語" src="https://img.shields.io/badge/主要言語-Python-3776AB?style=flat-square">
  <img alt="プラットフォーム" src="https://img.shields.io/badge/プラットフォーム-クロスプラットフォーム-475569?style=flat-square">
</p>

---

> GitHub 上の**収集・スクレイピング系スキルとリポジトリを発見・カタログ化**し、データを取得したいときに**最適なツールを段階的に提案してクロールを開始**するスキル。

## ✨ 主な特徴

| | |
|:--|:--|
| 🗂️ **厳選カタログ** | GitHub リポジトリを**5つの標準カテゴリ**に自動分類、重複排除とスコアリング付き。 |
| 🧭 **段階的開示** | カタログを一括表示しない —— カテゴリメニュー → ツールカード → ワークフロー → クロール。 |
| 🗃️ **JSON が正** | `tool-catalog.json` が唯一の信頼源、Markdown ビューは自動生成。 |
| 🔐 **デフォルトで安全** | トークンは `gh` キーリング / 環境変数から —— リポジトリに資格情報は置かない。 |
| ⏱️ **スケジュール対応** | cron / タスクスケジューラで定期更新をインストール可能。 |

## 📦 何をするか

**1つのナレッジベース**を共有する2つの機能:

<p align="center">
  <img src="docs/flow.svg" alt="collection-skill の仕組み" width="92%"/>
</p>

### ① 発見 & カタログ化
定期的に GitHub を走査し、*収集系*リポジトリを5カテゴリに分類:

| タグ | 意味 | 例 |
|-----|------|-----|
| 🕸️ `web-scraper` | 静的 HTML / 単純な HTTP 取得 | BeautifulSoup、httpx、Selectolax、Scrapy |
| ⚡ `dynamic-scraper` | JS レンダリング、SPA | Playwright、Selenium、Crawl4AI |
| 🔌 `api-collector` | REST/GraphQL、SDK 取得、ETL | SDK 駆動コレクター、パイプライン |
| 🤖 `agent-skill` | Claude/GPT スキル、MCP サーバー | ツール使用フレームワーク |
| 📚 `dataset` | 公開データセット、awesome リスト | 厳選リソースリポジトリ |

### ② 選定 & クロール
「*X をスクレイプしたい*」と言うと、短いファネルを進みます:

```
カテゴリメニュー  →  ツールカード  →  ワークフロー読込  →  範囲確認  →  クロール
```

## 📊 カタログ概況

> `tool-catalog.json` から自動生成 · 最終更新 `2026-07-05`

| カテゴリ | 件数 | | 主要言語 |
|----------|----:|---|----------|
| 🕸️ web-scraper | 42 | | Python · Go · JS |
| 🔌 api-collector | 41 | | Python · TypeScript |
| ⚡ dynamic-scraper | 39 | | Python · TypeScript |
| 🤖 agent-skill | 31 | | JavaScript · Python |
| 📚 dataset | 30 | | HTML · Markdown |
| **合計** | **183** | | **Python(89)** が最多 |

## 🚀 使い方

スキルを呼び出したら、自然な言葉で指示:

| 言うこと | 何が起きるか |
|---------|--------------|
| `refresh` / `discover` / `更新` | `scripts/discover_repos.py` を実行、カタログを更新 |
| `X をスクレイプしたい` / `抓 X 数据` | 段階的開示 → カテゴリ → カード → クロール |
| `browse` / `カタログを見せて` | 読み取り専用のカテゴリ/カード表示 |
| `schedule` / `定期実行` | 定期更新をインストール(cron / タスクスケジューラ) |

## 🛠️ クイックスタート

```bash
# 1.(推奨)認証 —— 認証済みなら検索 30 req/分、未認証は 10 req/分
gh auth login

# 2. 初回更新
python scripts/discover_repos.py
python scripts/build_catalog_md.py

# 3.(任意)毎週の更新を予約 —— スキルを呼び出して「定期更新」と発話
```

## 🗺️ プロジェクト構成

```
collection-skill/
├── SKILL.md                       # ルーター + 基本原則
├── workflows/
│   ├── discover-catalog.md        # GitHub から更新
│   ├── match-and-crawl.md         # 段階的開示 → クロール
│   ├── browse-catalog.md          # 読み取り専用ビュー
│   └── schedule-refresh.md        # 定期更新のインストール
├── references/
│   ├── tool-catalog.json          # 正データ(ここを編集)
│   ├── tool-catalog.md            # 生成ビュー(編集不可)
│   ├── discovery-log.md           # 追記型の実行履歴
│   ├── category-keywords.md       # カテゴリ別の検索キーワード
│   ├── repo-schema.md             # エントリのスキーマ
│   └── rate-limit-guide.md        # GitHub API の制限
├── templates/
│   ├── crawl-template.md          # 汎用クロールワークフロー
│   ├── discovery-log-entry.md
│   └── run_scheduled_refresh.sh.template
├── scripts/
│   ├── discover_repos.py          # GitHub 検索 → カタログ
│   ├── build_catalog_md.py        # JSON → Markdown
│   └── add_repo.py                # 手動でエントリを追加
└── docs/                          # README のバナーと図
```

## ⚖️ 設計ルール

- **JSON が正。** `tool-catalog.md` は `build_catalog_md.py` で再生成されます —— 手動編集禁止。
- **段階的開示。** まずカテゴリ、次にカード、ツール決定後にワークフローを読み込む。
- **資格情報は置かない。** トークンは `$GITHUB_TOKEN` または `gh auth token` から取得。
- **ユーザーフィールドは保持。** 再発見時にも `notes`、`verified`、`favorite`、`workflow_file` は上書きしない。
- **境界を尊重。** `robots.txt`、レート制限、利用規約を遵守。新ドメインのクロール前に範囲を確認。

## 🌍 多言語版

| 言語 | ファイル |
|------|---------|
| English | [`README.md`](README.md) |
| 简体中文 | [`README.zh-CN.md`](README.zh-CN.md) |
| 日本語 | [`README.ja.md`](README.ja.md) |
| Español | [`README.es.md`](README.es.md) |

## 📄 ライセンス

MIT
