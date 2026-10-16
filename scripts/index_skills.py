"""读取每个收录仓库里的 SKILL.md，把 frontmatter 的 name / description 写入 data/skill_index.json，供网站的项目页使用。

用法：
  python3 scripts/index_skills.py                  # 全部仓库
  python3 scripts/index_skills.py --only a/b c/d   # 只更新指定仓库
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from lib import DATA, NotFound, gh_get, has_token, load_meta, load_valid

INDEX_PATH = DATA / "skill_index.json"
MAX_PER_REPO = 40   # 单个仓库最多记录这么多个 skill，其余只计数
DESC_MAX = 300


def parse_frontmatter(text: str) -> dict[str, str]:
    """只解析 name 和 description 两个字段，支持引号、> / | 块和缩进续行。"""
    text = text.lstrip("﻿")
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        km = re.match(r"^(name|description)\s*:\s*(.*)$", lines[i])
        i += 1
        if not km:
            continue
        key, value = km.group(1), km.group(2).strip()
        block = []
        while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
            block.append(lines[i].strip())
            i += 1
        if value in ("", ">", "|", ">-", "|-", ">+", "|+"):
            value = " ".join(b for b in block if b)
        elif block:
            value = " ".join([value, *(b for b in block if b)])
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[key] = re.sub(r"\s+", " ", value).strip()
    return out


def skill_paths(full_name: str, branch: str, prefixes: list[str] | None = None) -> tuple[list[str], int]:
    """返回去重后的 SKILL.md 路径（同名目录只取最短路径）和总数。prefixes 非空时只看这些目录。"""
    try:
        tree = gh_get(f"repos/{full_name}/git/trees/{branch}?recursive=1")
    except NotFound:
        return [], 0
    by_name: dict[str, str] = {}
    for item in tree.get("tree", []):
        path = item["path"]
        if prefixes and not path.startswith(tuple(prefixes)):
            continue
        if item["type"] == "blob" and path.rsplit("/", 1)[-1].lower() == "skill.md":
            parent = path.rsplit("/", 1)[0] if "/" in path else ""
            name = parent.rsplit("/", 1)[-1]
            if name not in by_name or len(path) < len(by_name[name]):
                by_name[name] = path
    paths = sorted(by_name.values())
    return paths, len(paths)


def fetch_raw(full_name: str, branch: str, path: str) -> str | None:
    """返回文件内容；文件不存在返回空串，重试后仍失败返回 None（调用方沿用上次的结果）。"""
    url = f"https://raw.githubusercontent.com/{full_name}/{branch}/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url, headers={"User-Agent": "awesome-short-drama-skills"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read(64_000).decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ""
        except OSError:
            pass
    return None


def index_repo(repo: str, meta: dict, old: dict, prefixes: list[str] | None = None) -> dict:
    full_name = meta.get("full_name", repo)
    old_skills = {k["path"]: k for k in old.get("skills", [])}
    info = gh_get(f"repos/{full_name}")
    branch = info["default_branch"]
    paths, total = skill_paths(full_name, branch, prefixes)
    skills = []
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        texts = list(pool.map(lambda p: fetch_raw(full_name, branch, p), paths[:MAX_PER_REPO]))
    for path, text in zip(paths[:MAX_PER_REPO], texts):
        if text is None and path in old_skills:
            skills.append(old_skills[path])
            continue
        fm = parse_frontmatter(text or "")
        folder = path.rsplit("/", 2)[-2] if "/" in path else full_name.split("/")[1]
        desc = fm.get("description", "")
        if len(desc) > DESC_MAX:
            desc = desc[:DESC_MAX - 1].rstrip() + "…"
        skills.append({"name": fm.get("name") or folder, "description": desc, "path": path})
    return {"branch": branch, "total": total, "skills": skills}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", metavar="OWNER/REPO", help="只更新这些仓库")
    args = ap.parse_args()

    _, skills, _, _ = load_valid()
    meta = load_meta().get("repos", {})
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8")) if INDEX_PATH.exists() else {"repos": {}}
    # 完整应用里的 SKILL.md 多是开发工具，只有在 skills.toml 写了 skill_paths 时才收录
    paths_of = {s["repo"]: s.get("skill_paths") for s in skills}
    repos = [s["repo"] for s in skills if s["format"] != "app" or s.get("skill_paths")]
    if args.only:
        wanted = {r.lower() for r in args.only}
        repos = [r for r in repos if r.lower() in wanted]
    else:
        index["repos"] = {k: v for k, v in index["repos"].items() if k in repos}

    if not has_token():
        print("提示：未检测到 GITHUB_TOKEN 或 gh 登录，匿名配额每小时 60 次。", file=sys.stderr)

    failed = []
    for repo in repos:
        if meta.get(repo, {}).get("status") == "missing":
            continue
        try:
            entry = index_repo(repo, meta.get(repo, {}), index["repos"].get(repo, {}), paths_of[repo])
        except NotFound:
            print(f"  ✗ {repo}  失效（404）")
            continue
        except Exception as exc:  # 单个仓库出错（限流、5xx、网络）不拖垮整次刷新，沿用上次的数据
            failed.append(repo)
            print(f"  ! {repo}  抓取失败，沿用上次的数据：{exc}")
            continue
        index["repos"][repo] = entry
        print(f"  ✓ {repo}  {entry['total']} 个 SKILL.md")

    index["fetched_at"] = dt.date.today().isoformat()
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\n已写入 {INDEX_PATH}")
    if failed:
        # ::warning:: 会在 GitHub Actions 的运行摘要里显示
        print(f"::warning::{len(failed)} 个仓库的 SKILL.md 没抓到，沿用上次的数据：{', '.join(failed)}")


if __name__ == "__main__":
    main()
