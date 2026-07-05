# Workflow: Browse Catalog (Read-Only)

<required_reading>
Load this reference:
1. `references/tool-catalog.json`
</required_reading>

<process>
## Step 1: Read the Catalog

Load `references/tool-catalog.json`. Group entries by `category`. Do not make any network calls — this is a pure read view.

## Step 2: Show a Summary

```
📚 Catalog 总览（{total} 个工具，{verified_count} 已验证，更新于 {last_refresh}）

| 类别 | 数量 | 平均 star | 最近更新 |
|------|------|-----------|----------|
| 🕸️  web-scraper       | N | ⭐ avg | YYYY-MM |
| ⚡  dynamic-scraper   | N | ⭐ avg | YYYY-MM |
| 🔌  api-collector     | N | ⭐ avg | YYYY-MM |
| 🤖  agent-skill       | N | ⭐ avg | YYYY-MM |
| 📚  dataset           | N | ⭐ avg | YYYY-MM |
```

## Step 3: Offer Drill-Down

Ask which category to expand, or accept a specific filter:
- By category: show all entries as cards (see Step 4 of `match-and-crawl.md` for card format).
- By tag/keyword: filter on the `tags` array.
- By `favorite: true`: only show starred tools.
- By `verified: true`: only show validated tools.

## Step 4: Card Display (when drilled in)

For each matching entry, show:
```
### 🔧 {name}  ★{stars}  {last_updated}  {verified✓?}
{one_line_description}
🏷️  tags: {tags}
✅ 适合：{use_cases}
🔗 {repo_url}
📝 notes: {user_notes (if any)}
```

## Step 5: Surface Actions

After showing results, offer:
- "要标记某个工具为常用吗？" → set `favorite: true` in JSON, regenerate MD.
- "某个工具信息过时了？" → trigger `discover-catalog.md` for that repo (single refresh).
- "想用某个工具去抓数据？" → route to `match-and-crawl.md` Step 5.
</process>

<success_criteria>
- No network calls made.
- User saw a summary table first, then drill-down on request.
- Any edits (favorite toggle) went to JSON, then MD was regenerated.
</success_criteria>
