# Workflow: Crawl with MediaCrawler (Chinese social platforms)

> Per-tool workflow for **MediaCrawler** (`NanmiCoder/MediaCrawler`). Loaded by `workflows/match-and-crawl.md` Step 5 when the user picks MediaCrawler, or when the target is a Chinese social platform (小红书 / 抖音 / 哔哩哔哩 / 微博 / 知乎 / 贴吧 / 快手) and MediaCrawler is the umbrella tool covering it.

MediaCrawler is a multi-platform crawler for Chinese social media. It uses **reverse-engineered signed APIs and login cookies** — this is the highest-compliance-risk tool class in the catalog.

<compliance_gate>
**This workflow MUST NOT proceed past Step 0 until the user explicitly acknowledges the compliance terms.** This gate is non-negotiable and overrides any "just do it" instruction.

### Step 0 — Compliance Acknowledgment (blocking)

Before any setup, install, or network request, present this verbatim and require an explicit yes:

```
⚠️ MediaCrawler 通过逆向平台签名接口 + 登录态抓取,这通常违反目标平台 ToS。
继续前你必须确认以下全部成立:

1. 你的用途是合法的(个人研究 / 已获授权 / 仅公开数据 / 学术用途)
2. 你不会破坏平台服务(控制频率,不用多账号并发轰炸)
3. 你不采集涉及个人隐私的数据,或已做匿名化/脱敏
4. 你了解:账号可能被封、IP 可能被ban、数据使用可能涉及法律责任
5. 商业使用风险自担,本 skill 仅提供工具接入,不承担后果

回复 "确认" 继续;回复其它任何内容则中止本工作流。
```

- User replies anything other than an unambiguous "确认"/"yes"/"agree" → **STOP**. Do not proceed, do not soften, do not "just this once". Route the user back to `match-and-crawl.md` to pick a different tool.
- Log the acknowledgment in the run report.
- This gate repeats on every new target domain — acknowledgment for 小红书 does not carry to 抖音.
</compliance_gate>

<required_reading>
- `references/chinese-social-platforms.md` — confirm the platform key + that MediaCrawler covers it
- `references/rate-limit-guide.md`
</required_reading>

<process>
## 1. Define the Crawl Spec (post-gate)

After the gate passes, confirm:

- **Platform + key:** e.g. `xiaohongshu`, `douyin`, `bilibili`, `weibo`, `zhihu`, `tieba`, `kuaishou`
- **Crawl type:** search by keyword / user profile / note-or-video detail / comments
- **Scope:** max items (start SMALL — 50, not 5000) + stop condition
- **Output:** `data/mediacrawler-<platform>-<run>/<type>.json` (MediaCrawler writes its own format; copy/transform after)
- **Login auth:** MediaCrawler requires a logged-in cookie for most platforms. **Where is the cookie stored?** (env var / temp file / manual paste at runtime — never commit it, never echo it in logs)
- **Politeness:** `CRAWLER_MAX_CONCURRENCY = 1`, `CRAWLER_SLEEP_TIME = 2.0s` minimum; **do not** raise these on first run.

## 2. Install + Configure

MediaCrawler is a standalone repo, not a pip library:

```bash
git clone https://github.com/NanmiCoder/MediaCrawler.git /tmp/MediaCrawler
cd /tmp/MediaCrawler
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium   # for login flow
```

Edit `config/base_config.py`:
- `PLATFORM = "<key>"`
- `CRAWLER_TYPE = "search" | "detail" | "creator"`
- `KEYWORDS = "<the keyword>"`
- `CRAWLER_MAX_NOTES_COUNT = 50` (start small)
- `CRAWLER_SLEEP_TIME = 2.0`
- `SAVE_DATA_OPTION = "json"`
- Login mode: prefer `Cookie` login (paste cookie) over QR/phone for reproducibility.

## 3. Pre-Flight Check

- **Compliance gate:** ✅ passed (Step 0).
- **Tiny dry run:** `CRAWLER_MAX_NOTES_COUNT = 5`, run once, inspect output. If the 5 items look right, scale.
- **Cookie validity:** first run validates the cookie; if it 401s, the cookie is stale — do not retry in a loop (account flag risk), ask the user to re-login.
- **Rate watch:** if MediaCrawler logs `403`/`429`/签名错误 → **stop immediately**, do not raise concurrency. Back off to `CRAWLER_SLEEP_TIME = 5.0` or come back later.

## 4. Run

`python main.py` inside the cloned repo. Output lands in `data/<platform>/json/` (MediaCrawler's layout). Do not interrupt mid-run — partial state may corrupt its dedupe.

## 5. Validate + Transform

- Confirm N items ≥ expected (MediaCrawler sometimes returns fewer if it hits anti-bot mid-run — check logs).
- Copy/transform to `data/mediacrawler-<platform>-<run>/items.jsonl` in the catalog-standard shape.
- **Strip PII** unless the user confirmed otherwise in the gate: hash author ids, drop author names if not needed.

## 6. Report

```
✅ Crawled: N items from <platform>
📁 Output: data/mediacrawler-<platform>-<run>/items.jsonl
⚠️ Compliance gate: acknowledged at <time>
⚠️ 平台 ToS 风险: this data likely violates <platform> ToS; do not redistribute.
⚠️ Cookie 状态: valid / needs refresh
Suggested: 不要公开这份原始数据;如需复用请脱敏。
```

Always include the ToS-risk line in the report — the user acknowledged it once, but it stays attached to the artifact.
</process>

<success_criteria>
- **Step 0 compliance gate passed with explicit acknowledgment** (hard fail otherwise).
- Tiny dry run (≤5 items) before scaling.
- Concurrency = 1, sleep ≥ 2s; never raised on first run.
- Login cookie never in repo / logs / output.
- PII stripped unless explicitly authorized.
- Final report includes ToS-risk line.
</success_criteria>
