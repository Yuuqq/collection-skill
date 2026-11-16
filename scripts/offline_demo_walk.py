#!/usr/bin/env python3
"""Offline preview of the current Xiaohongshu fast path.

Reads the local catalog and workflow files and prints the route they
specify today. It does not call a model, log in, clone MediaCrawler, or
collect anything. The sample sentence is operator input, not model output.

    python3 scripts/offline_demo_walk.py
    python3 scripts/offline_demo_walk.py --self-test
    python3 scripts/offline_demo_walk.py --play          # paced playback
    python3 scripts/offline_demo_walk.py --play --wait   # wait for /tmp/offline-demo-go

docs/demo.gif is a screen recording of --play. Every screen keeps the
OFFLINE PREVIEW label. Re-record after catalog changes; do not treat the
GIF as a live agent session.
"""

from __future__ import annotations

import json
import re
import socket
import sys
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = "我想抓小红书的笔记数据"
TARGET_FULL_NAME = "NanmiCoder/MediaCrawler"
LABEL = "OFFLINE PREVIEW · 离线预览 · 不是模型推理 · 没有采集"
GO_FILE = Path("/tmp/offline-demo-go")
DONE_FILE = Path("/tmp/offline-demo-done")

_RealSocket = socket.socket


class _BlockedSocket(_RealSocket):
    def connect(self, address):  # noqa: ANN001
        raise RuntimeError(f"network blocked: connect {address!r}")

    def connect_ex(self, address):  # noqa: ANN001
        raise RuntimeError(f"network blocked: connect {address!r}")


socket.socket = _BlockedSocket  # type: ignore[misc]


def fenced_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if lines[index].startswith("```"):
            index += 1
            buf: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                buf.append(lines[index])
                index += 1
            blocks.append("\n".join(buf))
        index += 1
    return blocks


def load() -> dict:
    catalog_path = ROOT / "references" / "tool-catalog.json"
    platforms_path = ROOT / "references" / "chinese-social-platforms.md"
    workflow_path = ROOT / "workflows" / "match-and-crawl.md"
    log_path = ROOT / "references" / "discovery-log.md"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    return {
        "catalog": catalog,
        "entries": catalog["entries"],
        "platforms": platforms_path.read_text(encoding="utf-8"),
        "workflow": workflow_path.read_text(encoding="utf-8"),
        "log": log_path.read_text(encoding="utf-8"),
    }


def aliases(platforms_md: str) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    row = re.compile(
        r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*`([^`]+)`(.*)\|\s*[^|]*\|\s*$"
    )
    for line in platforms_md.splitlines():
        match = row.match(line.strip())
        if not match:
            continue
        key, display, first, rest = (
            match.group(1), match.group(2).strip(), match.group(3), match.group(4)
        )
        for alias in [first, *re.findall(r"`([^`]+)`", rest)]:
            alias = alias.strip()
            if alias:
                found.append((key, display, alias))
    if not any(alias == "小红书" for _, _, alias in found):
        raise RuntimeError("failed to parse 小红书 from chinese-social-platforms.md")
    return found


def detect(text: str, alias_rows: list[tuple[str, str, str]]) -> tuple[str, str, str]:
    matches = [row for row in alias_rows if row[2] and row[2] in text]
    if not matches:
        raise RuntimeError(f"no platform alias matched {text!r}")
    matches.sort(key=lambda item: len(item[2]), reverse=True)
    return matches[0]


def covers_xiaohongshu(entry: dict) -> bool:
    tags = entry.get("tags") or []
    if "platform:xiaohongshu" in tags:
        return True
    blob = " ".join(
        [entry.get("one_line_description") or "", entry.get("notes") or ""]
        + list(entry.get("use_cases") or [])
    )
    return "platform:multi" in tags and "小红书" in blob


def shortlist(entries: list[dict]) -> list[dict]:
    def sort_key(entry: dict) -> tuple:
        return (-(entry.get("stars") or 0), entry.get("last_updated") or "")

    dedicated = [entry for entry in entries if "platform:xiaohongshu" in (entry.get("tags") or [])]
    dedicated.sort(key=sort_key)
    top = dedicated[:4]
    shown = {entry["repo_url"] for entry in top}
    multi = [
        entry for entry in entries
        if "platform:multi" in (entry.get("tags") or [])
        and covers_xiaohongshu(entry)
        and entry["repo_url"] not in shown
    ]
    multi.sort(key=sort_key)
    if not multi:
        raise RuntimeError("no multi-platform tool covers 小红书")
    return top + [multi[0]]


def freshness(data: dict, now: datetime | None = None) -> dict:
    last = datetime.fromisoformat(data["catalog"]["last_refreshed"])
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    delta = now - last
    log_match = re.search(r"^## (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) \(UTC\)", data["log"], re.M)
    if not log_match:
        raise RuntimeError("discovery-log.md has no run heading")
    log_dt = datetime.strptime(
        log_match.group(1) + " " + log_match.group(2), "%Y-%m-%d %H:%M"
    ).replace(tzinfo=timezone.utc)
    return {
        "now": now,
        "last": last,
        "delta": delta,
        "older_than_7_days": delta > timedelta(days=7),
        "log_dt": log_dt,
        "log_matches_json_day": log_dt.date() == last.date(),
    }


def workflow_bits(workflow: str, mediacrawler: str) -> dict:
    blocks = fenced_blocks(workflow)
    compliance = next(block for block in blocks if block.startswith("⚠️ 合规提醒"))
    gate = next(block for block in fenced_blocks(mediacrawler) if '回复 "确认"' in block)
    return {"compliance": compliance, "gate": gate}


def build_state(now: datetime | None = None) -> dict:
    data = load()
    key, display, alias = detect(REQUEST, aliases(data["platforms"]))
    ordered = shortlist(data["entries"])
    picked = ordered[-1]
    workflow_rel = picked.get("workflow_file")
    if not workflow_rel:
        raise RuntimeError(f"{picked['full_name']} has no workflow_file")
    workflow_path = ROOT / workflow_rel
    mediacrawler = workflow_path.read_text(encoding="utf-8")
    return {
        **data,
        "key": key,
        "display": display,
        "alias": alias,
        "ordered": ordered,
        "picked": picked,
        "pick": len(ordered),
        "workflow_path": workflow_path,
        "mediacrawler": mediacrawler,
        "bits": workflow_bits(data["workflow"], mediacrawler),
        "fresh": freshness(data, now),
    }


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in {"F", "W"} else 1 for ch in text)


def wrap(text: str, width: int = 92) -> str:
    breaks = set(" \t,，、;；|/)")
    out: list[str] = []
    for paragraph in text.splitlines():
        if paragraph == "":
            out.append("")
            continue
        rest = paragraph
        while rest and display_width(rest) > width:
            used = 0
            last_break = 0
            cut = 0
            for index, ch in enumerate(rest):
                ch_width = 2 if unicodedata.east_asian_width(ch) in {"F", "W"} else 1
                if used + ch_width > width:
                    cut = last_break or index
                    break
                used += ch_width
                if ch in breaks:
                    last_break = index + 1
            if cut <= 0:
                cut = max(1, last_break)
            out.append(rest[:cut].rstrip())
            rest = rest[cut:].lstrip()
        if rest:
            out.append(rest)
    return "\n".join(out)


def frame(body: str, width: int = 92) -> str:
    """Keep the offline label on the first and last line of every screen."""
    return LABEL + "\n" + wrap(body.strip("\n"), width) + "\n" + LABEL + "\n"


class Screen:
    def __init__(self, play: bool):
        self.play = play
        self.texts: list[str] = []
        self.current: list[str] = []

    def _flush_current(self) -> None:
        if self.current:
            self.texts.append("".join(self.current))
            self.current = []

    def show(self, text: str, hold: float = 0) -> None:
        self._flush_current()
        self.current.append(text)
        if self.play:
            sys.stdout.write("\033[2J\033[H")
        else:
            sys.stdout.write("\n" + ("=" * 24) + "\n")
        sys.stdout.write(text)
        sys.stdout.flush()
        self.hold(hold)

    def append(self, text: str, hold: float = 0) -> None:
        self.current.append(text)
        sys.stdout.write(text)
        sys.stdout.flush()
        self.hold(hold)

    def hold(self, seconds: float) -> None:
        if self.play and seconds > 0:
            time.sleep(seconds)

    def type_line(self, text: str, delay: float) -> None:
        self.current.append(text)
        if not self.play:
            sys.stdout.write(text)
            sys.stdout.flush()
            return
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)


def age_text(delta: timedelta) -> str:
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    return f"{delta.days} 天 {hours} 小时 {minutes} 分"


def screen_inputs(state: dict) -> str:
    fresh = state["fresh"]
    delta: timedelta = fresh["delta"]
    lines = [
        "当前 master 的小红书快速通道 · 读取本地 references/ 与 workflows/",
        "网络已禁止    采集未开始",
        "",
        f"tool-catalog.json  last_refreshed: {state['catalog']['last_refreshed']}",
        f"条目数: {len(state['entries'])}    discovery-log: {fresh['log_dt'].strftime('%Y-%m-%d %H:%M')} UTC",
        f"精确年龄: {age_text(delta)}    older than 7 days: {'是' if fresh['older_than_7_days'] else '否'}",
        "",
    ]
    if fresh["older_than_7_days"]:
        lines.extend([
            "Step 1 模板（日期来自编目与时钟，不是模型回复）:",
            f"The catalog was last refreshed on {fresh['last'].date().isoformat()} "
            f"({delta.days} days ago). I can still match,",
            "but you may want to run `/collection-skill discover` first. Proceed anyway?",
            "编目非空，按工作流默认继续。本次不运行 discover，也不访问 GitHub。",
            "",
        ])
    else:
        lines.extend([
            "Step 1: 编目未超过 7 天，直接匹配。本次不运行 discover。",
            "",
        ])
    lines.append("示例输入")
    return "\n".join(lines)


def screen_route(state: dict) -> str:
    return "\n".join([
        "Step 2  别名来自 references/chinese-social-platforms.md",
        f"命中「{state['alias']}」→ {state['display']} → key = {state['key']}",
        "路由: Step 3B 中文社媒快速通道",
        "通用五类菜单: 不展示",
        "依据 match-and-crawl.md: Skip to Step 3B. Do not show the generic category menu.",
    ])


def screen_shortlist(state: dict, width: int = 92) -> str:
    lines = [
        f"Step 3B  {state['display']} ({state['key']}) 定向名单",
        "规则: platform:xiaohongshu 按 star 取 4 个，再加 1 个覆盖该平台的 platform:multi。",
        "",
        state["bits"]["compliance"],
        "",
        "名单（字段来自 tool-catalog.json）",
    ]
    for index, entry in enumerate(state["ordered"], start=1):
        platform_tags = [tag for tag in (entry.get("tags") or []) if str(tag).startswith("platform:")]
        lines.append(f"{index}. {entry['name']}  ★{entry['stars']}  {entry['category']}")
        lines.append(
            f"   {entry['full_name']}  verified={entry.get('verified')}  workflow={entry.get('workflow_file')}"
        )
        tag_line = "   "
        for tag in platform_tags:
            addition = tag if tag_line.strip() == "" else ", " + tag
            if display_width(tag_line + addition) > width and tag_line.strip():
                lines.append(tag_line.rstrip())
                tag_line = "   " + tag
            else:
                tag_line += addition
        if tag_line.strip():
            lines.append(tag_line.rstrip())
    lines.extend([
        "",
        "选择编号。只加载该工具的工作流文件，不安装、不登录、不采集。",
    ])
    return "\n".join(lines)


def screen_card(state: dict) -> str:
    picked = state["picked"]
    usecases = "；".join((picked.get("use_cases") or [])[:3])
    caveats = "；".join(picked.get("caveats") or [])
    return "\n".join([
        f"Step 5  已选择 {picked['full_name']}",
        "category 来自编目字段，不是五类菜单里点选的。",
        f"category = {picked['category']}",
        f"workflow_file = {picked['workflow_file']}",
        f"已读取该文件（{len(state['mediacrawler'].splitlines())} 行，"
        f"{state['workflow_path'].stat().st_size} 字节），尚未执行。",
        "",
        f"### {picked['name']}  ★{picked['stars']}  {picked['last_updated']}",
        picked.get("one_line_description") or "",
        f"✅ 适合：{usecases}",
        f"⚠️ 注意：{caveats}",
        f"🔗 {picked['repo_url']}",
    ])


def screen_scope(state: dict) -> str:
    return "\n".join([
        "继续 Step 5  ·  合规门与抓取范围确认",
        "下面是 workflows/tools/mediacrawler.md Step 0 的原文。没有回复「确认」。",
        "",
        state["bits"]["gate"],
        "",
        "抓取范围确认 — 表单仍为空，到此停止",
        "- Target URL(s) or API endpoint(s): （空）",
        "- Estimated request count: （空）",
        "- Output location and format: （空）",
        "- Any auth needed: （空）",
        "- 中文平台合规再次确认: 未确认",
        "",
        "Step 6 执行采集: 未运行",
        "克隆仓库 / pip / playwright / python main.py: 未运行",
        "停止。没有登录，没有请求小红书，没有采集结果。",
    ])


def render(play: bool, wait: bool) -> list[str]:
    state = build_state()
    screen = Screen(play)
    if play and wait:
        while not GO_FILE.exists():
            time.sleep(0.05)
        time.sleep(0.15)

    pause = play
    screen.show(LABEL + "\n" + wrap(screen_inputs(state)) + "\n> ")
    screen.type_line(REQUEST + "\n", 0.08 if pause else 0)
    screen.append(wrap(screen_route(state)) + "\n" + LABEL + "\n", 4.6 if pause else 0)

    screen.show(LABEL + "\n" + wrap(screen_shortlist(state)) + "\n> ", 3.8 if pause else 0)
    screen.type_line(str(state["pick"]) + "\n", 0.16 if pause else 0)
    screen.append(LABEL + "\n", 1.6 if pause else 0)

    screen.show(frame(screen_card(state)), 4.6 if pause else 0)
    screen.show(frame(screen_scope(state)), 6.0 if pause else 0)
    screen._flush_current()
    if play:
        DONE_FILE.write_text("ok\n", encoding="utf-8")
        time.sleep(0.35)
    return screen.texts


def self_test() -> None:
    problems: list[str] = []
    state = build_state()
    if state["key"] != "xiaohongshu" or state["alias"] != "小红书":
        problems.append(f"detect {state['alias']} {state['key']}")
    if state["picked"]["full_name"] != TARGET_FULL_NAME:
        problems.append(
            "umbrella is "
            f"{state['picked']['full_name']}, expected {TARGET_FULL_NAME}"
        )
    if state["picked"]["category"] != "dynamic-scraper":
        problems.append(f"category={state['picked']['category']}")
    if state["picked"]["workflow_file"] != "workflows/tools/mediacrawler.md":
        problems.append(f"workflow={state['picked']['workflow_file']}")
    if not state["fresh"]["log_matches_json_day"]:
        problems.append("discovery-log day != catalog last_refreshed")
    if "Do not show the generic category menu" not in state["workflow"]:
        problems.append("workflow missing the fast-path skip sentence")
    if "⚠️ 合规提醒" not in state["bits"]["compliance"]:
        problems.append("compliance block missing")
    if '回复 "确认"' not in state["bits"]["gate"]:
        problems.append("mediacrawler gate missing")
    stale = timedelta(days=7, seconds=1)
    fresh = timedelta(days=7)
    if not (stale > timedelta(days=7)) or (fresh > timedelta(days=7)):
        problems.append("7-day comparison is wrong")
    try:
        _BlockedSocket().connect(("93.184.216.34", 80))
        problems.append("socket guard did not block")
    except RuntimeError:
        pass

    texts = render(play=False, wait=False)
    joined = "\n".join(texts)
    for required in (
        LABEL,
        REQUEST,
        "通用五类菜单: 不展示",
        "Step 3B",
        TARGET_FULL_NAME,
        "dynamic-scraper",
        "workflows/tools/mediacrawler.md",
        "（空）",
        "未运行",
        "没有采集结果",
    ):
        if required not in joined:
            problems.append(f"missing {required!r}")
    if joined.count(LABEL) < 8:
        problems.append(f"label count {joined.count(LABEL)} < 8")
    for banned in ("Crawled:", "items.jsonl", "✅ Crawled"):
        if banned in joined:
            problems.append(f"invented crawl marker {banned}")
    if problems:
        print("SELF-TEST FAILED")
        for item in problems:
            print(" -", item)
        sys.exit(1)
    print("SELF-TEST OK")
    print(
        f"route=Step 3B key={state['key']} pick={state['pick']} "
        f"{state['picked']['full_name']} category={state['picked']['category']}"
    )
    print(f"entries={len(state['entries'])} older_than_7_days={state['fresh']['older_than_7_days']}")
    print("network=blocked collection=not started")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--self-test" in args:
        self_test()
        return 0
    render(play="--play" in args, wait="--wait" in args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
