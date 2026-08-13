# Demo Recording Storyboard

A 30–40s clip that proves the one thing the static cards can't: **you ask for data, it picks a tool, and it starts crawling.** Embed the result directly under the banner in `README.md` (all four locales).

## Goal

Show the match-and-crawl funnel end to end. The viewer should think *"I could be doing this in the next minute."*

## Tooling (pick one)

| Tool | When | Notes |
|------|------|-------|
| **ScreenToGif** | Windows, want a GIF | Easiest; record the terminal window, trim, export GIF. |
| **asciinema + agg** | Want a crisp, tiny, text-perfect GIF | `asciinema rec demo.cast` → `agg demo.cast docs/demo.gif`. Sharpest text. |
| **OBS** | Want MP4/video with zooms | Heavier; only if you want voiceover. |

## Terminal prep

- Clean profile, large font (18–20px), ~100×30 window, dark theme.
- Clear scrollback; a short, quiet prompt (`$ `).
- Pre-stage a target so there's no typing lag. Practice the run once first.
- Type at a steady, readable pace — or paste-and-enter to keep it tight.

## Shot list

| # | Beat | You type / do | On screen | ~s |
|---|------|----------------|-----------|---|
| 1 | Hook | `我想抓小红书的数据` (or `I want to scrape X`) | The prompt, nothing else yet | 3 |
| 2 | Category menu | invoke skill → menu appears | Five categories listed | 5 |
| 3 | Drill in | pick the matching category | Tool cards for that category | 6 |
| 4 | Pick a tool | select a card | Tool card: stars, use-cases, caveats | 6 |
| 5 | Workflow loads | confirm | The per-tool crawl workflow steps | 5 |
| 6 | Confirm scope | confirm domain/scope | The safety/scope confirmation | 4 |
| 7 | **Crawl** | run it | Live crawl output scrolling | 8 |
| 8 | Payoff | — | Clean structured result (rows/JSON) + a one-line summary | 5 |

**Total ≈ 40s.** Cut dead air between beats; keep the crawl output (beat 7) and payoff (beat 8) at full speed — that's the proof.

## Export specs

- GIF: ≤ 1200px wide, ≤ 5 MB, looping, 15–24 fps. (GitHub renders larger GIFs slowly.)
- Save as `docs/demo.gif` (or `docs/demo.cast` + a build note if using asciinema).

## Embed

Under the banner `<p align="center">…</p>` block in each README:

```html
<p align="center">
  <img src="docs/demo.gif" alt="Ask for data → get a tool → it crawls" width="92%"/>
</p>
```

> Tip: keep the clip **silent and self-explanatory** — most viewers watch muted. If a beat needs context, prefer an on-screen caption over voiceover.
