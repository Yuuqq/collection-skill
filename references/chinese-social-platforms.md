# Chinese Social Media Platforms — Mapping Table

This file is the **canonical reference** for Chinese social media collection.
The skill uses it to:
1. Recognize a platform name in the user's request (`references/chinese-social-platforms.md`).
2. Tag catalog entries with the right `platform` sub-tag.
3. Group entries in the catalog's 🇨🇳 aggregation block.

## ⚠️ Compliance (read first)

Most tools in this space are community reverse-engineered and violate the platforms' Terms of Service. This skill catalogs them with the risk surfaced, not hidden:

- The compliance reminder in `match-and-crawl.md` Step 3B is **mandatory** before any tool selection, and intent is re-confirmed before the first network request (Step 5).
- The skill **never** assists with evading anti-bot / risk-control systems.
- Default posture: research / authorized use, low request rates, public data, anonymized personal data.

## Tag Convention

Every Chinese-social catalog entry gets:
- `tags: ["chinese-social", "platform:<key>"]`
- `platform` is one of the keys below (e.g. `platform:xiaohongshu`).

This is a **soft tag** — entries keep their primary `category` (usually `dynamic-scraper` or `api-collector`) and additionally carry the chinese-social tag for cross-category aggregation.

---

## Platform Registry

### 主流七大 (Main Big Seven)

| key | 平台 | 别名/搜索词 | 抓取特点 |
|-----|------|-------------|----------|
| `xiaohongshu` | 小红书 | `小红书`, `xiaohongshu`, `xhs`, `red note`, `小红书笔记`, `小红书评论` | 风控强，需登录态/cookie，笔记+评论一体 |
| `douyin` | 抖音 | `抖音`, `douyin`, `tiktok 抖音`, `抖音视频`, `抖音评论` | 逆向 sign 参数，视频+评论+用户 |
| `bilibili` | 哔哩哔哩 | `bilibili`, `b站`, `哔哩哔哩`, `bilibili视频`, `bilibili评论`, `BV号` | API 相对开放，有官方/半官方 SDK |
| `weibo` | 微博 | `微博`, `weibo`, `sina weibo`, `微博帖子`, `微博热搜`, `微博话题` | 老牌，工具最多，反爬中等 |
| `zhihu` | 知乎 | `知乎`, `zhihu`, `知乎问答`, `知乎专栏`, `知乎文章` | API 较规范，问答+文章+评论 |
| `tieba` | 百度贴吧 | `贴吧`, `tieba`, `baidu tieba`, `贴吧帖子`, `贴吧回复` | 老社区，帖子+回复+楼中楼 |
| `kuaishou` | 快手 | `快手`, `kuaishou`, `快手视频`, `快手直播` | 视频+直播，逆向维护频繁 |

### 微信生态 (WeChat Ecosystem)

| key | 平台 | 别名/搜索词 | 抓取特点 |
|-----|------|-------------|----------|
| `wechat-oa` | 微信公众号 | `微信公众号`, `wechat official account`, `公众号文章`, `mp.weixin`, `wechat oa` | 反爬最强之一，需登录+抓草稿/搜狗入口 |
| `wechat-channels` | 视频号 | `视频号`, `wechat channels`, `shipinhao` | 新平台，工具较少，多为视频元数据 |
| `wechat-search` | 搜一搜 | `微信搜一搜`, `wechat search` | 搜索结果聚合，工具少 |

### 电商评论 (E-commerce Reviews)

| key | 平台 | 别名/搜索词 | 抓取特点 |
|-----|------|-------------|----------|
| `taobao` | 淘宝/天猫 | `淘宝`, `taobao`, `tmall`, `天猫`, `淘宝评论`, `商品评论` | 风控极强，评论需逆向 |
| `jd` | 京东 | `京东`, `jd`, `jd.com`, `京东评价`, `京东评论` | 评价 API 可逆向 |
| `pdd` | 拼多多 | `拼多多`, `pdd`, `pinduoduo`, `拼多多评价` | App 端为主，Web 工具少 |

### 垂直社区 (Vertical Communities)

| key | 平台 | 别名/搜索词 | 抓取特点 |
|-----|------|-------------|----------|
| `douban` | 豆瓣 | `豆瓣`, `douban`, `豆瓣小组`, `豆瓣书影音`, `豆瓣评论`, `豆瓣电影` | 书影音/小组，API 较友好 |
| `jike` | 即刻 | `即刻`, `jike`, `即刻app` | 年轻社区，工具少 |
| `xueqiu` | 雪球 | `雪球`, `xueqiu`, `雪球财经`, `雪球讨论`, `股票评论` | 金融数据，API 逆向 |
| `juejin` | 掘金 | `掘金`, `juejin`, `掘金文章` | 技术社区，API 较开放 |
| `v2ex` | V2EX | `v2ex`, `v2ex 节点`, `v2ex 帖子` | 技术社区，API 开放 |
| `xiaohongshu-variant` | 啡呵/得物等 | `得物`, `dewu`, `闲鱼`, `xianyu` | 二级电商/社区 |

---

## Usage in `match-and-crawl.md`

When the user's request contains any "别名/搜索词" from the table above, route **directly** to the chinese-social aggregation, skip the generic category menu. Show only `chinese-social`-tagged entries filtered by that platform key.

If the platform has 0 entries in the catalog yet, fall back to:
1. Show MediaCrawler (the umbrella tool, covers most platforms).
2. Trigger a targeted discovery with the platform's search词.

---

## Maintenance

- Adding a new platform → add a row to the right group, then re-run discovery.
- If a platform dies (e.g., 贴吧 closes API), don't delete the row — mark it with a `status: deprecated` note in the entry's `caveats`.
- Tool counts per platform are auto-computed by `build_catalog_md.py`.
