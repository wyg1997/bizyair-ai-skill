"""apps.py -- community AI app search and detail."""
from __future__ import annotations

import common


def search_community(keyword: str = "", *, current: int = 1, page_size: int = 25, sort: str = "Recently"):
    """Search community AI apps.

    GET /meta/v1/bizy_models/community?model_types=Application
    Returns items with versions; the first public/available version's id is the
    web_app_id that can be passed to tasks.create_task.
    """
    params = {
        "current": current,
        "page_size": page_size,
        "keyword": keyword,
        "sort": sort,
        "model_types": "Application",
    }
    return common.unwrap_data(common.request("GET", "meta/v1/bizy_models/community", params=params, auth=False))


def _pick_public_version(versions: list) -> dict | None:
    for v in versions:
        if v.get("public") and v.get("available"):
            return v
    return versions[0] if versions else None


def pick_app_candidates(query: str = "", *, limit: int = 10):
    """Search community apps and return a compact markdown-ready list."""
    data = search_community(query, page_size=max(limit, 25))
    items = (data or {}).get("list") or []
    rows = []
    for it in items[:limit]:
        v = _pick_public_version(it.get("versions") or [])
        rows.append({
            "name": it.get("name"),
            "base_model": v.get("base_model") if v else None,
            "web_app_id": str(v.get("id")) if v else None,
            "version": v.get("version") if v else None,
            "bizy_model_id": it.get("id"),
            "cover_url": (v.get("cover_urls") or [None])[0] if v else None,
        })
    return {"query": query, "total": (data or {}).get("total", len(items)), "candidates": rows}


def format_markdown_apps(items: list) -> str:
    """Format community app candidates as Markdown."""
    lines = ["# BizyAir AI Apps", ""]
    lines.append(f"_{len(items)} candidates_")
    lines.append("")
    lines.append("| Name | Base Model | web_app_id | Version |")
    lines.append("|---|---|---|---|")
    for it in items:
        name = str(it.get("name", "")).replace("|", "\|")
        bm = str(it.get("base_model", "-") or "-").replace("|", "\|")
        wid = f"`{it.get('web_app_id', '-')}`"
        ver = str(it.get("version", "-") or "-").replace("|", "\|")
        lines.append(f"| {name} | {bm} | {wid} | {ver} |")
    lines.append("")
    lines.append('Run with: `python3 scripts/cli.py run <web_app_id> --prompt "..."`')
    return "\n".join(lines)


def cmd_app_md(args):
    """cli.py app-md [--save]"""
    save = "--save" in args
    data = search_community(page_size=200)
    items = (data or {}).get("list") or []
    result = pick_app_candidates("", limit=len(items))
    md = format_markdown_apps(result.get("candidates", []))
    print(md)
    if save:
        out_path = common.SKILL_ROOT / "outputs" / "APPS.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"\nSaved to {out_path}")


def cmd_app_search(args):
    """cli.py app-search ["keyword"] [--md]"""
    md_mode = "--md" in args
    rest = [a for a in args if a != "--md"]
    query = rest[0] if rest else ""
    result = pick_app_candidates(query)
    if md_mode:
        print(format_markdown_apps(result.get("candidates", [])))
    else:
        common.out(result)
