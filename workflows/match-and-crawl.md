# Workflow: Match Tool and Crawl

<required_reading>
Load these references before proceeding:
1. `references/tool-catalog.json` — the data you match against
2. `references/category-keywords.md` — to interpret the user's target
3. `references/chinese-social-platforms.md` — platform name → key map (load if Chinese platform suspected)
</required_reading>

<process>
## Step 1: Check Catalog Freshness

Read `references/discovery-log.md`. If the last successful run is older than 7 days (configurable), tell the user:

> The catalog was last refreshed on YYYY-MM-DD (N days ago). I can still match, but you may want to run `/collection-skill discover` first. Proceed anyway?

Proceed by default unless the catalog is empty — if empty, route the user to `discover-catalog.md` instead.

## Step 2: Detect Chinese-Social Target (Fast Path)

Scan the user's request for any **platform alias** from `references/chinese-social-platforms.md`. Aliases include (non-exhaustive): 小红书/抖音/B站/哔哩哔哩/微博/知乎/贴吧/快手/微信公众号/公众号/视频号/淘宝/天猫/京东/拼多多/豆瓣/雪球/掘金/V2EX/闲鱼/xhs/weibo/douyin/bilibili/zhihu etc.

**If a Chinese platform name is detected:**
- Determine the platform `key` (e.g. "小红书" → `xiaohongshu`).
- **Skip to Step 3B (Chinese-social fast path).** Do not show the generic category menu.

**If no Chinese platform detected:** continue to Step 3 (generic path).

## Step 3: Classify + Category Menu (Generic Path)

From the user's request, decide which **primary category** the target falls into. Use these signals:

| Signal in user request | → Category |
|------------------------|------------|
| "页面是静态的", "HTML", "表格", simple site, no login | `web-scraper` |
| "需要登录", "JS渲染", "动态", "滚动加载", SPA, React/Vue site | `dynamic-scraper` |
| "API", "有个接口", "GraphQL", SDK, JSON response | `api-collector` |
| "用 agent / MCP / skill 去做", tool-use framing | `agent-skill` |
| "公开数据集", "awesome", "资源汇总", curated list | `dataset` |

If genuinely ambiguous (2 categories plausible), show both.

Show the user a **category menu** (not the full tool list). Format:

```
按数据类型，我建议从这几类工具里挑：

1. 🕸️  静态网页抓取 (web-scraper) — N 个工具
    适合：静态 HTML、表格、不需要登录的页面
2. ⚡  动态页面抓取 (dynamic-scraper) — N 个工具
    适合：JS 渲染、SPA、滚动加载、需登录
3. 🔌  API 数据采集 (api-collector) — N 个工具
    适合：REST/GraphQL 接口、SDK 拉取
4. 🤖  Agent 技能 / MCP (agent-skill) — N 个工具
    适合：让 agent 自主决定如何抓
5. 📚  数据集 / 资源库 (dataset) — N 个工具
    适合：现成公开数据、awesome-list

推荐：[根据分类给出的类别] — 理由：…
```

Wait for the user to confirm or pick a different category. Do NOT proceed to Step 4 until they choose.

## Step 3B: Chinese-Social Fast Path

Detected platform: **{display_name}** (`platform:{key}`).

From `tool-catalog.json`, build a **targeted shortlist**:
1. Entries tagged `platform:{key}` (dedicated tools for this platform).
2. Entries tagged `platform:multi` (umbrella tools like MediaCrawler that cover this platform).
3. (Optional) Entries with the platform name in description, as fallback.

Combine, dedupe by `repo_url`, sort by stars desc.

**If the shortlist is empty** (no dedicated tools yet):
1. Surface MediaCrawler as the default umbrella choice (if it covers this platform — see its `use_cases`).
2. Offer to run a targeted discovery: `/collection-skill discover` with the platform's keywords from `chinese-social-platforms.md`.

**If shortlist has tools**, show them as cards (same format as Step 4) plus a **prominent compliance reminder** at the top:

```
⚠️ 合规提醒：中文社交平台采集通常违反平台 ToS，且很多工具采用逆向实现。
   抓取前请确认：
   - 你有合法的数据使用目的（个人研究 / 已授权 / 公开数据）
   - 控制请求频率，不损害平台服务
   - 不采集涉及个人隐私的数据，或做匿名化处理
   - 涉及商业使用须特别谨慎
```

Then show 1 multi-platform tool + up to 4 dedicated tools (dedicated first). Skip the generic category menu entirely.

Proceed to Step 5 once the user picks a tool.

## Step 4: Tool Cards Within Category (Generic Path)

From `tool-catalog.json`, filter entries where `category == <chosen>` AND `verified == true`. Show up to 5 as **cards**:

```
### 🔧 {name}  ★{stars}  {last_updated}
{one_line_description}
✅ 适合：{use_cases[0..2]}
⚠️ 注意：{caveats}
🔗 {repo_url}
```

Order cards by: stars desc, then last_updated desc. If more than 5, note "还有 N 个，要看全部说一声".

Ask the user which to use, or let them describe the target more precisely to narrow down.

## Step 5: Load Tool Workflow

Once the user picks a tool, **load the tool's workflow file**. Two sources:

- If the catalog entry has `workflow_file` set → load that (a per-tool workflow we already wrote).
- Otherwise → use the **generic workflow template** at `templates/crawl-template.md` and fill it in for the chosen tool + target.

Before any network request, **confirm scope with the user**:
- Target URL(s) or API endpoint(s)
- Estimated request count
- Output location and format
- Any auth needed
- **For chinese-social targets, re-confirm compliance intent** (the reminder in Step 3B must be acknowledged)

Only after explicit confirmation, execute the crawl.

## Step 6: Execute and Report

Run the crawl. Report:
- Items fetched (count)
- Output file path(s)
- Errors / skipped items
- Suggestion: "要把这个站点加入常用目标吗？可以更新 catalog 标记为常用。"

If the chosen tool performed well, consider upvoting its `notes` field in the catalog (record a successful use).
</process>

<success_criteria>
- Chinese-platform targets were detected and routed to the fast path (Step 3B), skipping the generic menu.
- Generic targets got a category menu (not a dump) in turn 1.
- User picked a tool → got scope confirmation before any network request.
- Chinese-social targets saw the compliance reminder before any tool selection.
- Crawl executed with a clear result report.
- Catalog freshness was surfaced if stale.
</success_criteria>
