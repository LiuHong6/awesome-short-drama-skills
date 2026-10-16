"""列出本次刷新里新增或改动的第三方文字（GitHub 仓库简介、SKILL.md 说明），供人工过目。

网站项目页直接展示这些文字，它们每周自动刷新、不经人工审核。这里对比 git HEAD 和工作区，
被 lib.third_party_text 拦下（网站上不展示）的条目单独列出。

用法：
  python3 scripts/text_changes.py               # 打印到终端
  python3 scripts/text_changes.py --out FILE    # 有变化时写入 FILE，没有变化不生成文件
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from lib import DATA, META_PATH, ROOT, third_party_text

INDEX_PATH = DATA / "skill_index.json"
SITE = "https://shortdramaskills.com"
BODY_MAX = 60_000  # GitHub issue 正文上限是 65536 字符


def at_head(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 else {}


def in_tree(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def texts(meta: dict, index: dict) -> dict[tuple[str, str], str]:
    """(仓库, 位置) → 文字。位置是「仓库简介」或 SKILL.md 路径。"""
    out = {}
    for repo, m in meta.get("repos", {}).items():
        if (m.get("description") or "").strip():
            out[(repo, "仓库简介")] = m["description"].strip()
    for repo, entry in index.get("repos", {}).items():
        for k in entry.get("skills", []):
            if k.get("description"):
                out[(repo, k["path"])] = k["description"]
    return out


def section(title: str, rows: list[tuple[tuple[str, str], str]]) -> list[str]:
    if not rows:
        return []
    lines = [f"## {title}（{len(rows)}）", ""]
    by_repo: dict[str, list[tuple[str, str]]] = {}
    for (repo, where), text in rows:
        by_repo.setdefault(repo, []).append((where, text))
    for repo, items in by_repo.items():
        lines += [f"**{repo}** · [网站页面]({SITE}/skills/{repo.lower()}/) · [GitHub](https://github.com/{repo})", "",
                  "```text"]
        # 放进代码块：第三方文字里的 @提及、链接、图片都不会在 issue 里生效
        lines += [f"{where}: {text.replace('```', "'''")}" for where, text in items]
        lines += ["```", ""]
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="有变化时写入这个文件")
    args = ap.parse_args()

    old = texts(at_head(META_PATH), at_head(INDEX_PATH))
    new = texts(in_tree(META_PATH), in_tree(INDEX_PATH))
    changed = [(key, new[key]) for key in sorted(new) if old.get(key) != new[key]]
    if not changed:
        print("第三方文字没有变化")
        return

    blocked = [(key, text) for key, text in changed if not third_party_text(text)]
    shown = [(key, text) for key, text in changed if third_party_text(text)]
    lines = [
        "网站项目页会直接展示仓库简介和 SKILL.md 说明。下面是本次自动刷新里新增或改动的条目，扫一眼有没有广告、"
        "引流或写给 AI 的指令。有问题的话，在 `data/ignore.toml` 里撤下整个项目，"
        "或者在 `scripts/lib.py` 的 `THIRD_PARTY_BLOCK` 里加一条规则。",
        "",
        *section("已拦下，网站上不展示", blocked),
        *section("新增或改动，已在网站上展示", shown),
    ]
    body = "\n".join(lines)
    if len(body) > BODY_MAX:
        body = body[:BODY_MAX].rsplit("\n", 1)[0]
        if body.count("```") % 2:
            body += "\n```"
        body += "\n\n（内容太长，后面的省略了，完整差异见本次提交里的 data/ 改动。）\n"

    print(f"第三方文字：{len(shown)} 条新增或改动，{len(blocked)} 条被拦下")
    if args.out:
        args.out.write_text(body, encoding="utf-8")
    else:
        print(body)


if __name__ == "__main__":
    main()
