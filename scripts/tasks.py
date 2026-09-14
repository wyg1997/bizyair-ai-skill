"""tasks.py -- AI app task create / status / outputs / cancel.

Documented interface: https://api.bizyair.ai/v1/webapp/task/openapi/*. Async mode
(HTTP 202 -> bare {request_id}) is the default; pass async_mode=False for sync.
"""
from __future__ import annotations

import time
import common


def app_detail(web_app_id):
    """GET /meta/v1/webapp/{web_app_id}/detail -- metadata + input_nodes for prefill."""
    return common.unwrap_data(common.request("GET", f"meta/v1/webapp/{web_app_id}/detail"))


def create_task(web_app_id, input_values, *, suppress_preview_output=False, async_mode=True):
    """POST /v1/webapp/task/openapi/create."""
    body = {"web_app_id": int(web_app_id), "suppress_preview_output": suppress_preview_output, "input_values": input_values}
    return common.request("POST", "v1/webapp/task/openapi/create", json_body=body, async_task=async_mode)


def query_status(request_id: str):
    return common.unwrap_data(common.request("GET", f"v1/webapp/task/openapi/{request_id}"))


def get_outputs(request_id: str):
    return common.unwrap_data(common.request("GET", f"v1/webapp/task/openapi/{request_id}/outputs"))


def cancel(request_id: str):
    return common.request("PUT", f"v1/webapp/task/openapi/{request_id}/cancel")


def interrupt(request_id: str):
    return common.request("PUT", f"v1/webapp/task/openapi/{request_id}/interrupt")


def poll_until_done(request_id: str, *, interval: int = 5, max_seconds: int = 900):
    deadline = time.time() + max_seconds
    last = None
    while time.time() < deadline:
        last = query_status(request_id)
        status = (last.get("status") if isinstance(last, dict) else None) or ""
        if status in ("Success", "Failed", "Canceled"):
            return last
        time.sleep(interval)
    return last


def _resolve_prompt_var(web_app_id) -> str | None:
    """Find the most likely prompt input node for a generic --prompt."""
    try:
        detail = app_detail(web_app_id)
    except Exception:
        return None
    nodes = (detail.get("input_nodes") or []) if isinstance(detail, dict) else []
    for node in nodes:
        if node.get("field_type") == "customtext":
            name = (node.get("node_name") or "").lower()
            if "prompt" in name:
                return node.get("variable_name")
    return None


def run_app(web_app_id, input_values, *, async_mode=True):
    """Create (async) -> poll -> return final status + outputs."""
    # If user passed a generic "prompt", map it to the app's actual prompt node.
    if "prompt" in input_values:
        prompt_var = _resolve_prompt_var(web_app_id)
        if prompt_var and prompt_var not in input_values:
            input_values[prompt_var] = input_values.pop("prompt")
    created = create_task(web_app_id, input_values, async_mode=async_mode)
    rid = created.get("request_id") if isinstance(created, dict) else None
    if not rid:
        return {"created": created, "outputs": None}
    final = poll_until_done(rid)
    outputs = get_outputs(rid) if (final or {}).get("status") == "Success" else None
    return {"request_id": rid, "status": (final or {}).get("status"), "final": final, "outputs": outputs}


def cmd_app_detail(args):
    common.out(app_detail(args[0]))


def cmd_status(args):
    common.out(query_status(args[0]))


def cmd_outputs(args):
    common.out(get_outputs(args[0]))


def cmd_run(args):
    """cli.py run <web_app_id> --json '{input_values}'"""
    wid = args[0]
    import json
    iv = {}
    i = 1
    while i < len(args):
        if args[i] == "--json" and i + 1 < len(args):
            iv = json.loads(args[i + 1])
            i += 2
        elif args[i] == "--prompt" and i + 1 < len(args):
            iv["prompt"] = args[i + 1]
            i += 2
        else:
            i += 1
    common.out(run_app(wid, iv))
