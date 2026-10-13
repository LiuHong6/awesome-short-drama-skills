"""根据 data/ 和 templates/ 生成 README.md。

用法：
  python3 scripts/build.py              # 生成 README.md
  python3 scripts/build.py --check      # README.md 与数据不一致时以退出码 1 结束（CI 用）
  python3 scripts/build.py --validate   # 只校验数据
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys

from lib import ROOT, load_meta, load_valid

README = ROOT / "README.md"
TEMPLATES = ROOT / "templates"
STALE_DAYS = 180

FORMAT_BADGE = {"prompts": "📝 提示词", "app": "🧩 应用"}
LANG_LABEL = {"zh": "中文", "en": "英文", "multi": "多语言"}


def gh_url(repo: str) -> str:
    return f"https://github.com/{repo}"


def display_name(s: dict) -> str:
    return s.get("name") or s["repo"].split("/", 1)[1]


def fmt_stars(n: int | None) -> str:
    if n is None:
        return "—"
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def sort_key(s: dict, meta: dict):
    stars = meta.get(s["repo"], {}).get("stars", -1)
    return (s.get("tier") != "featured", -stars, display_name(s).lower())


def status_mark(m: dict, ref: dt.date | None) -> str:
    if m.get("status") == "missing":
        return " ⚠️"
    if m.get("archived"):
        return " 📦"
    if ref and m.get("pushed_at") and (ref - dt.date.fromisoformat(m["pushed_at"])).days > STALE_DAYS:
        return " 💤"
    return ""


def name_cell(s: dict, m: dict) -> str:
    star = "🌟 " if s.get("tier") == "featured" else ""
    sub = []
    if s["format"] in FORMAT_BADGE:
        sub.append(FORMAT_BADGE[s["format"]])
    sub.append(LANG_LABEL[s["lang"]])
    if m.get("skill_count", 0) > 1:
        sub.append(f"{m['skill_count']}{'+' if m.get('skill_count_truncated') else ''} 个 skill")
    if m.get("license"):
        sub.append(m["license"])
    return f"{star}[{display_name(s)}]({gh_url(s['repo'])})<br><sub>{' · '.join(sub)}</sub>"


def desc_cell(s: dict, models: dict) -> str:
    text = cell(s["desc"])
    if s.get("models"):
        text += f"<br><sub>🎬 {' · '.join(models[md] for md in s['models'])}</sub>"
    if s.get("note"):
        text += f"<br><sub>💡 {cell(s['note'])}</sub>"
    return text


def install_cmd(s: dict) -> str | None:
    if s.get("install"):
        return s["install"]
    if s["format"] == "skill":
        return f"npx skills add {s['repo']}"
    return None


def by_stars(items, meta: dict) -> list[dict]:
    return sorted(items, key=lambda s: -meta.get(s["repo"], {}).get("stars", -1))


def render_packs(packs: list[dict], by_repo: dict) -> list[str]:
    out = [
        '<a id="packs"></a>',
        "## 推荐组合",
        "",
        "> 初版组合依据仓库说明搭配，尚未实测，实测后会更新。",
        "",
        "| 组合 | 适合 | 包含 | 搭配思路 |",
        "|---|---|---|---|",
    ]
    for p in packs:
        links = " → ".join(
            f"[{display_name(by_repo[r.lower()])}]({gh_url(by_repo[r.lower()]['repo'])})" for r in p["repos"]
        )
        out.append(f"| **{cell(p['name'])}** | {cell(p['goal'])} | {links} | {cell(p['why'])} |")
    return out + [""]


def render_group(key: str, group: dict, items: list[dict], meta: dict, ref: dt.date | None, taxonomy: dict) -> list[str]:
    stages = taxonomy["stages"]
    out = [f'<a id="group-{key}"></a>', f"### {group['label']}", ""]
    if group.get("intro"):
        out += [group["intro"], ""]
    out += [
        "| 项目 | 简介 | 覆盖阶段 | ★ | 最近更新 |",
        "|---|---|---|--:|---|",
    ]
    for s in items:
        m = meta.get(s["repo"], {})
        stage_text = " · ".join(st["short"] for k, st in stages.items() if k in s["stages"])
        updated = (m.get("pushed_at") or "—") + status_mark(m, ref)
        out.append(
            f"| {name_cell(s, m)} | {desc_cell(s, taxonomy['models'])} | {stage_text} "
            f"| {fmt_stars(m.get('stars'))} | {updated} |"
        )

    cmds = [(display_name(s), install_cmd(s)) for s in items if install_cmd(s)]
    if cmds:
        out += ["", "<details><summary>安装命令</summary>", "", "```bash",
                "# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准"]
        for name, cmd in cmds:
            out += [f"# {name}", cmd]
        out += ["```", "", "</details>"]
    return out + [""]


def render_index(anchor: str, title: str, intro: str, labels: dict[str, str], field: str,
                 skills: list[dict], meta: dict) -> list[str]:
    out = [f'<a id="{anchor}"></a>', f"## {title}", "", intro, ""]
    for key, label in labels.items():
        hits = by_stars((s for s in skills if key in s.get(field, [])), meta)
        if hits:
            links = " · ".join(f"[{display_name(s)}]({gh_url(s['repo'])})" for s in hits)
            out += [f"**{label}**（{len(hits)}）：{links}", ""]
    return out


def render(taxonomy: dict, skills: list[dict], packs: list[dict], meta_all: dict) -> str:
    meta = meta_all.get("repos", {})
    ref = dt.date.fromisoformat(meta_all["fetched_at"]) if meta_all.get("fetched_at") else None
    groups = taxonomy["groups"]
    by_repo = {s["repo"].lower(): s for s in skills}
    grouped = {k: sorted((s for s in skills if s["group"] == k), key=lambda s: sort_key(s, meta)) for k in groups}
    indexed = [s for s in skills if groups[s["group"]].get("indexed", True)]

    header = (TEMPLATES / "header.md").read_text(encoding="utf-8")
    header = (header.replace("{{count}}", str(len(indexed)))
                    .replace("{{platforms}}", str(len(skills) - len(indexed)))
                    .replace("{{updated}}", meta_all.get("fetched_at") or "—"))

    toc = ["## 目录", "", "- [推荐组合](#packs)", "- [按类型](#by-group)"]
    toc += [f"  - [{g['label']}](#group-{k})（{len(grouped[k])}）" for k, g in groups.items() if grouped[k]]
    toc += ["- [按创作阶段查找](#by-stage)", "- [按视频模型查找](#by-model)", "- [相关资源](#resources)", ""]

    body = ['<a id="by-group"></a>', "## 按类型", ""]
    for k, g in groups.items():
        if grouped[k]:
            body += render_group(k, g, grouped[k], meta, ref, taxonomy)

    stage_labels = {k: st["label"] for k, st in taxonomy["stages"].items()}
    parts = [
        "<!-- 本文件由 scripts/build.py 生成，请勿手改。要改内容请编辑 data/ 或 templates/ 后重新生成。 -->",
        "",
        header.rstrip(),
        "",
        *toc,
        *render_packs(packs, by_repo),
        *body,
        *render_index("by-stage", "按创作阶段查找", "卡在某一步时，从这里找能帮上忙的 skill（按星数排序）。",
                      stage_labels, "stages", indexed, meta),
        *render_index("by-model", "按视频模型查找", "仓库说明里明确提到适配的图像/视频模型（按星数排序）。",
                      taxonomy["models"], "models", indexed, meta),
        (TEMPLATES / "footer.md").read_text(encoding="utf-8").rstrip(),
        "",
    ]
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="只检查 README.md 是否最新")
    ap.add_argument("--validate", action="store_true", help="只校验数据")
    args = ap.parse_args()

    taxonomy, skills, packs, _ = load_valid()
    if args.validate:
        print(f"数据校验通过：{len(skills)} 个项目，{len(packs)} 个组合。")
        return

    meta_all = load_meta()
    unfetched = [s["repo"] for s in skills if s["repo"] not in meta_all.get("repos", {})]
    if unfetched:
        print(f"提示：{len(unfetched)} 个仓库还没有元数据，先运行 scripts/refresh.py --only {' '.join(unfetched)}",
              file=sys.stderr)

    content = render(taxonomy, skills, packs, meta_all)
    if args.check:
        if not README.exists() or README.read_text(encoding="utf-8") != content:
            sys.exit("README.md 不是最新的，请运行 python3 scripts/build.py")
        print("README.md 已是最新。")
        return
    README.write_text(content, encoding="utf-8")
    print(f"已生成 README.md：{len(skills)} 个项目。")


if __name__ == "__main__":
    main()
