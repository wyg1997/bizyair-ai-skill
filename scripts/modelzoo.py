"""modelzoo.py -- ModelZoo catalog search, detail, price and tasks.

Public endpoints (list / detail / price_table) work without a credential. Task
creation/status use /v1/modelzoo/tasks/openapi/<endpoint> on api.bizyair.ai.
"""
from __future__ import annotations

import time
import common


def list_endpoints(keyword: str = "", *, current: int = 1, page_size: int = 20, sort: str = "Auto"):
    body = {"tags": [], "categories": [], "show_deprecated": False}
    if keyword:
        body["keyword"] = keyword
    params = {"current": current, "page_size": page_size, "sort": sort}
    return common.unwrap_data(common.request("POST", "meta/v1/modelzoo/list", json_body=body, params=params, auth=False))


def get_detail(endpoint: str):
    return common.unwrap_data(common.request("GET", f"meta/v1/modelzoo/detail/{endpoint}", auth=False))


def get_price(endpoint: str):
    return common.unwrap_data(common.request("GET", f"meta/v1/modelzoo/price_table/{endpoint}", auth=False))


def get_filters():
    return common.unwrap_data(common.request("GET", "meta/v1/modelzoo/filters", auth=False))


def build_payload(detail: dict, params: dict) -> dict:
    """Turn detail.input_params + caller params into a create-task payload.

    field_type -> payload type mapping (see references/04). Media types (images/
    audios/videos) must be uploaded separately; here we only pass scalar/URL values.
    """
    payload: dict = {}
    for f in detail.get("input_params") or []:
        name = f.get("field_name")
        if not name:
            continue
        if name in params:
            payload[name] = _coerce(f.get("field_type"), params[name])
        elif f.get("required") and f.get("field_value") is not None:
            payload[name] = f.get("field_value")
    return payload


def _coerce(field_type: str, value):
    ft = (field_type or "").lower()
    if ft in ("number", "slider", "slides", "seed"):
        try:
            return int(value)
        except (TypeError, ValueError):
            try:
                return float(value)
            except (TypeError, ValueError):
                return value
    if ft == "boolean":
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)
    if ft == "images" and isinstance(value, str):
        return [value]
    return value


def encode_local_image(path: str) -> str:
    """Read a local image file and return a base64 data URL."""
    import base64
    import os
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "bmp": "bmp"}.get(ext, "jpeg")
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return f"data:image/{mime};base64,{b64}"


def create_task(endpoint: str, payload: dict):
    """POST /v1/modelzoo/tasks/openapi/<endpoint> -- async, returns {request_id}."""
    return common.request("POST", f"v1/modelzoo/tasks/openapi/{endpoint}", json_body=payload)


def query_task(request_id: str):
    return common.unwrap_data(common.request("GET", f"v1/modelzoo/tasks/openapi/{request_id}"))


def poll_until_done(request_id: str, *, interval: int = 5, max_seconds: int = 900):
    deadline = time.time() + max_seconds
    last = None
    while time.time() < deadline:
        last = query_task(request_id)
        status = (last.get("status") if isinstance(last, dict) else None) or ""
        if status in ("Success", "Failed", "Canceled"):
            return last
        time.sleep(interval)
    return last


def pick_candidates(query: str, *, modality: str = "image", limit: int = 10):
    """Search ModelZoo and return a compact candidate list (markdown-ready)."""
    data = list_endpoints(query, page_size=max(limit, 20))
    items = (data or {}).get("list") or []
    rows = []
    for it in items[:limit]:
        ep = it.get("endpoint", "")
        cat = it.get("category", "")
        name = it.get("display_name", "")
        price = it.get("min_credits")
        rows.append({"endpoint": ep, "name": name, "category": cat, "min_credits": price, "link": f"https://www.bizyair.ai/modelzoo/{ep}"})
    return {"query": query, "modality": modality, "total": (data or {}).get("total", len(items)), "candidates": rows}


def cmd_list(args):
    kw = args[0] if args and not args[0].startswith("--") else ""
    data = list_endpoints(kw)
    items = (data or {}).get("list") or []
    common.out({"total": (data or {}).get("total", len(items)), "items": [_short(i) for i in items]})


def _short(it: dict) -> dict:
    return {k: it.get(k) for k in ("endpoint", "display_name", "category", "sub_category", "min_credits", "edition", "status")}


def cmd_detail(args):
    common.out(get_detail(args[0]))


def cmd_price(args):
    data = get_price(args[0])
    tables = (data or {}).get("price_tables") or []
    simple = "; ".join(f"{t.get('pricing_name')} {','.join(t.get('pricing_values') or [])} {t.get('unit_name')}" for t in tables)
    benefit = (data or {}).get("benefit") or {}
    common.out({"simple_price": simple or "no price info", "benefit": benefit, "raw": data})


def cmd_pick(args):
    mod = "image"
    rest = list(args)
    if rest and rest[0] == "--video":
        mod = "video"
        rest = rest[1:]
    query = rest[0] if rest else ""
    common.out(pick_candidates(query, modality=mod))


def _md_escape(text: str) -> str:
    return str(text).replace("|", "\\|")


def format_markdown_menu(items: list):
    """Build a grouped Markdown reference from ModelZoo endpoint items."""
    lines = ["# BizyAir ModelZoo Endpoints", ""]
    lines.append(f"_Generated {time.strftime('%Y-%m-%d %H:%M')} \u00b7 {len(items)} endpoints in total_")
    lines.append("")

    groups = {}
    for it in items:
        cat = it.get("category", "Other") or "Other"
        groups.setdefault(cat, []).append(it)

    for cat in sorted(groups.keys()):
        lines.append(f"## {cat}")
        lines.append("")
        lines.append("| Endpoint | Name | Credits | Edition |")
        lines.append("|---|---|---:|---|")
        for it in sorted(groups[cat], key=lambda x: x.get("endpoint", "")):
            ep = _md_escape(it.get("endpoint", ""))
            name = _md_escape(it.get("display_name", ""))
            price = it.get("min_credits", "-") or "-"
            edition = it.get("edition", "-") or "-"
            lines.append(f"| `{ep}` | {name} | {price} | {edition} |")
        lines.append("")

    return "\n".join(lines)


def cmd_md(args):
    """cli.py modelzoo-md [--save]"""
    save = "--save" in args
    data = list_endpoints(page_size=200)
    items = (data or {}).get("list") or []
    md = format_markdown_menu(items)
    print(md)
    if save:
        out_path = common.SKILL_ROOT / "outputs" / "MODELS.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"\nSaved to {out_path}")
