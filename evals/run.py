#!/usr/bin/env python3
"""实测运行器：把同一个 premise 交给一个 skill，在隔离目录里用 Claude Code 无头模式跑完，保存产出和问答记录。

用法（在仓库根目录）：
  python evals/run.py 001-rebirth-revenge eternityspring/shuohao-skills --work /tmp/evals
  python evals/run.py 001-rebirth-revenge baseline --work /tmp/evals     # 不装任何 skill 的对照组
  python evals/run.py 001-rebirth-revenge <repo> --work /tmp/evals --more  # 对已有会话再发一次固定回复

参赛名单和入口 skill 写在 evals/runs/<premise>/contestants.toml。
每个 skill 用同一条开场指令和同一条固定回复，不额外加指令。
为了安全，agent 只能读写自己的工作目录，不能运行命令、不能联网、不连任何 MCP。
依赖：已登录的 claude CLI、git。只用标准库。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"

MODEL = "claude-opus-5-5"
EFFORT = "high"
MAX_TURNS = 8
TURN_TIMEOUT = 60 * 60

TASK = "请完成 premise.md 里的短剧创作需求，交付物写成文件放在当前目录。"
TASK_TOOLKIT = "请使用已安装的 skill，完成 premise.md 里的短剧创作需求，交付物写成文件放在当前目录。"
REPLY = "需求都在 premise.md 里，里面没写的你来定，不用再问我。请继续，直到 premise.md 列出的三项交付都写成文件。"

ALLOWED = ["Edit(./**)", "Write(./**)", "Skill", "TodoWrite", "Agent"]
DENIED = ["Bash", "WebFetch", "WebSearch", "Read(~/**)", "Edit(~/**)", "Write(~/**)"]
ASKING = re.compile(r"[？?]|确认|请选择|请回复|是否|要不要|哪一个|哪个方案|告诉我")


def slug(repo: str) -> str:
    return repo.replace("/", "__")


def contestant(premise: str, repo: str) -> dict:
    roster = tomllib.loads((EVALS / "runs" / premise / "contestants.toml").read_text(encoding="utf-8"))
    for c in roster["contestants"]:
        if c["repo"].lower() == repo.lower():
            return c
    sys.exit(f"{repo} 不在 evals/runs/{premise}/contestants.toml 里")


def fetch(repo: str, src_root: Path) -> tuple[Path, str]:
    """浅克隆到 src_root 下，返回目录和 commit。已克隆过就复用，保证同一轮用同一个版本。"""
    dest = src_root / slug(repo)
    if not dest.exists():
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{repo}.git", str(dest)], check=True)
    commit = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], check=True, capture_output=True,
                            text=True).stdout.strip()
    return dest, commit


def skill_dirs(src: Path) -> dict[str, Path]:
    """仓库里的 skill 目录（同名只取最短路径），和 skills CLI 的默认安装范围一致。"""
    found: dict[str, Path] = {}
    for p in sorted(src.rglob("*"), key=lambda p: len(p.parts)):
        if ".git" in p.parts or p.name.lower() != "skill.md":
            continue
        name = src.name.split("__", 1)[-1] if p.parent == src else p.parent.name
        found.setdefault(name, p.parent)
    return found


def install(src: Path, ws: Path) -> list[str]:
    target = ws / ".claude" / "skills"
    target.mkdir(parents=True)
    dirs = skill_dirs(src)
    if not dirs:  # 有的仓库把 skill 打包成 .skill（zip）
        unpacked = Path(tempfile.mkdtemp(dir=src.parent, prefix=src.name + ".unpacked."))
        for pkg in src.glob("*.skill"):
            with zipfile.ZipFile(pkg) as z:
                z.extractall(unpacked / pkg.stem)
        dirs = skill_dirs(unpacked)
    ignore = shutil.ignore_patterns(".git")
    for name, d in dirs.items():
        shutil.copytree(d, target / name, ignore=ignore)
    return sorted(dirs)


def claude(ws: Path, prompt: str, session: str, resume: bool, log: Path) -> dict:
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--model", MODEL, "--effort", EFFORT, "--setting-sources", "project",
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
           "--permission-mode", "dontAsk", "--allowedTools", *ALLOWED, "--disallowedTools", *DENIED]
    cmd += ["--resume", session] if resume else ["--session-id", session]
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    tools: dict[str, int] = {}
    result: dict = {}
    with log.open("a", encoding="utf-8") as f, subprocess.Popen(cmd, cwd=ws, env=env, stdout=subprocess.PIPE,
                                                                 stderr=subprocess.STDOUT, text=True) as proc:
        try:
            for line in proc.stdout:
                f.write(line)
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "assistant":
                    for block in ev.get("message", {}).get("content", []):
                        if block.get("type") == "tool_use":
                            name = block["name"]
                            if name == "Skill":
                                name = f"Skill({block.get('input', {}).get('skill', '?')})"
                            tools[name] = tools.get(name, 0) + 1
                elif ev.get("type") == "result":
                    result = ev
            proc.wait(timeout=TURN_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            result = {"is_error": True, "result": "（超时，进程已终止）"}
    result["tools"] = tools
    return result


def deliverables(ws: Path) -> list[Path]:
    return sorted(p for p in ws.rglob("*") if p.is_file() and ".claude" not in p.relative_to(ws).parts
                  and p.name != "premise.md")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("premise", help="evals/premises/ 下的文件名，不带 .md")
    ap.add_argument("repo", help="owner/repo，或 baseline")
    ap.add_argument("--work", required=True, type=Path, help="放克隆仓库和工作目录的地方（仓库之外）")
    ap.add_argument("--more", action="store_true", help="对已有会话再发一次固定回复")
    args = ap.parse_args()

    c = contestant(args.premise, args.repo)
    ws = args.work / "ws" / args.premise / slug(c["repo"])
    out = EVALS / "runs" / args.premise / slug(c["repo"])
    state_path = ws.parent / f"{slug(c['repo'])}.state.json"
    log = ws.parent / f"{slug(c['repo'])}.jsonl"

    if args.more:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        prompts = [REPLY]
    else:
        if ws.exists():
            sys.exit(f"{ws} 已存在；要重跑请先删掉它")
        ws.mkdir(parents=True)
        shutil.copy(EVALS / "premises" / f"{args.premise}.md", ws / "premise.md")
        state = {"repo": c["repo"], "premise": args.premise, "session": str(uuid.uuid4()), "turns": [],
                 "model": MODEL, "effort": EFFORT, "started": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                 "claude_code": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()}
        if c["repo"] == "baseline":
            state.update(commit=None, installed=[])
            first = TASK
        else:
            src, state["commit"] = fetch(c["repo"], args.work / "src")
            state["installed"] = install(src, ws)
            first = f"/{c['entry']} {TASK}" if c.get("entry") else TASK_TOOLKIT
        prompts = [first] + [REPLY] * (MAX_TURNS - 1)

    for prompt in prompts:
        resume = bool(state["turns"])
        r = claude(ws, prompt, state["session"], resume, log)
        state["turns"].append({"user": prompt, "agent": r.get("result", ""), "tools": r["tools"],
                               "denied": [d.get("tool_name") for d in r.get("permission_denials", [])],
                               "cost_usd": r.get("total_cost_usd"), "duration_s": round(r.get("duration_ms", 0) / 1000),
                               "error": r.get("is_error", False)})
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{c['repo']}] 第 {len(state['turns'])} 轮：{len(deliverables(ws))} 个文件，"
              f"{state['turns'][-1]['duration_s']}s", flush=True)
        if r.get("is_error") or not ASKING.search(r.get("result", "")[-400:]) and deliverables(ws):
            break

    state["finished"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    save(ws, out, state)


def save(ws: Path, out: Path, state: dict) -> None:
    if out.exists():
        shutil.rmtree(out)
    (out / "output").mkdir(parents=True)
    for p in deliverables(ws):
        dest = out / "output" / p.relative_to(ws)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(p, dest)
    lines = [f"# {state['repo']}", ""]
    if state["repo"] != "baseline":
        lines += [f"- 仓库：https://github.com/{state['repo']}/tree/{state['commit']}",
                  f"- 安装的 skill：{'、'.join(state['installed']) or '（无）'}"]
    else:
        lines += ["- 对照组：不安装任何 skill"]
    total = sum(t["cost_usd"] or 0 for t in state["turns"])
    lines += [f"- 环境：{state['claude_code']}，模型 {state['model']}，推理强度 {state['effort']}",
              f"- 开始：{state['started']}，结束：{state.get('finished', '—')}",
              f"- 轮数：{len(state['turns'])}，总耗时 {sum(t['duration_s'] for t in state['turns']) // 60} 分钟，"
              f"按 API 价格折算 ${total:.2f}", ""]
    for i, t in enumerate(state["turns"], 1):
        tools = "、".join(f"{k}×{v}" for k, v in sorted(t["tools"].items())) or "无"
        lines += [f"## 第 {i} 轮", "", "**用户：**", "", t["user"], "", f"**工具调用：**{tools}", ""]
        if t["denied"]:
            lines += [f"**被拒绝的工具：**{'、'.join(t['denied'])}", ""]
        lines += ["**Agent 最后的回复：**", "", t["agent"].strip() or "（空）", ""]
    (out / "transcript.md").write_text("\n".join(lines), encoding="utf-8")
    meta = {k: v for k, v in state.items() if k != "turns"} | {"turns": len(state["turns"])}
    (out / "run.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
