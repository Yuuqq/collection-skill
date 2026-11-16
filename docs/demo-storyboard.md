# Demo recording

`docs/demo.gif` is an **offline preview** of the current Xiaohongshu fast path. It is a screen recording of `scripts/offline_demo_walk.py`, which only reads local catalog and workflow files. It is not a live model session and it does not collect anything.

Issue #1's original shot list (five-category menu, then a live crawl) predates the fast path. Current `workflows/match-and-crawl.md` routes 小红书 to Step 3B and does not show that menu. Do not change the product route to match the old list, and do not record a crawl.

## Shot list

| # | On screen | ~s |
|---|-----------|---|
| 1 | `我想抓小红书的笔记数据`, alias → `xiaohongshu`, Step 3B, five-category menu not shown | 6 |
| 2 | Compliance reminder and the real shortlist; choose MediaCrawler | 6 |
| 3 | Catalog card: `dynamic-scraper`, `workflows/tools/mediacrawler.md` loaded, not executed | 5 |
| 4 | Step 0 compliance gate and an empty scope form. Stop. Step 6 does not run | 7 |

Every screen keeps this label on the first and last line:

`OFFLINE PREVIEW · 离线预览 · 不是模型推理 · 没有采集`

## Rebuild

```bash
python3 scripts/offline_demo_walk.py --self-test
python3 scripts/offline_demo_walk.py --play
```

Record the terminal. Export a looping GIF about 1200px wide, 10–15 fps, 15–30s, under 5MB, to `docs/demo.gif`.

## Embed

Under the banner in each README, with a localized caption that says this is an offline preview and that no collection runs. The English hero is:

```html
<p align="center">
  <img src="docs/demo.gif" alt="Offline preview: Xiaohongshu fast path, stop before collection" width="92%"/>
  <br/>
  <sub>Offline preview of the current Xiaohongshu fast path, read from local files. Not live inference, and no collection.</sub>
</p>
```
