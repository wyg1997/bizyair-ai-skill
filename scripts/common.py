"""common.py -- config loader, URL resolver and HTTP client for BizyAir.ai.

Authentication uses an API key (BizyAir Settings -> API Keys) sent as
`Authorization: Bearer <api_key>` against the documented hosts:
  /meta/v1/user/info             -> https://meta.bizyair.ai/v1/user/info
  /finance/v1/wallet             -> https://api.bizyair.ai/v1/wallet
  /v1/webapp/task/openapi/create -> https://api.bizyair.ai/v1/webapp/task/openapi/create

Public endpoints (modelzoo list/detail/price) can be called with auth=False so a
missing API key does not turn them into 401s.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_ROOT / "config.json"
DEFAULT_TIMEOUT = 120
_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
_PATH_RE = re.compile(r"^\/?(?:api\/)?(?:([a-z][a-z0-9-]*)\/)?(v\d+)(?=\/|\?|#|$)(.*)", re.I)


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def client_cfg() -> dict:
    return load_config().get("client", {})


def credentials() -> dict:
    return load_config().get("credentials", {})


def locale() -> str:
    return str(client_cfg().get("locale", "en"))


def api_key() -> str | None:
    return os.environ.get("BIZYAIR_API_KEY") or credentials().get("api_key") or None


_SERVICE_HOST = {"meta": "meta_host", "api": "api_host", "finance": "api_host"}


def build_url(path: str) -> str:
    """Build the absolute URL for the API-key hosts."""
    if re.match(r"^[a-z][a-z\d+\-.]*://", path, re.I):
        return path
    m = _PATH_RE.match(path)
    service = (m.group(1) or "api").lower() if m else "api"
    version = m.group(2) if m else "v1"
    rest = (m.group(3) or "") if m else path
    host = client_cfg().get(_SERVICE_HOST.get(service, "api_host"), "https://api.bizyair.ai")
    return f"{host}/{version}{rest}"


class ApiError(Exception):
    def __init__(self, message: str, *, http_code: int = 0, biz_code: str = "", raw: Any = None):
        super().__init__(message)
        self.http_code = http_code
        self.biz_code = biz_code
        self.raw = raw


def _headers(*, content_type: bool, async_task: bool = False, auth: bool = True) -> dict:
    h: dict = {"Accept": "application/json, text/plain, */*", "User-Agent": _UA, "Accept-Language": "en-US,en;q=0.9"}
    h["lang"] = locale()
    if auth:
        tok = api_key()
        if tok:
            h["Authorization"] = f"Bearer {tok}"
    if content_type:
        h["Content-Type"] = "application/json"
    if async_task:
        h["X-BizyAir-Task-Async"] = "enable"
    return h


def request(method, path, *, json_body=None, params=None, auth=True, async_task=False, timeout=None):
    """HTTP request -> parsed JSON. Raises ApiError on 4xx/5xx or non-20000 codes.

    Pass auth=False for public endpoints so a missing API key does not produce 401s.
    The async task-create response (HTTP 202, bare {"request_id": ...}) is returned as-is.
    """
    url = build_url(path)
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{qs}" if qs else url
    body = None
    ct = False
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        ct = True
    headers = _headers(content_type=ct, async_task=async_task, auth=auth)
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout or DEFAULT_TIMEOUT) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return _handle_error(e.read().decode("utf-8", "replace"), e.code)
    except urllib.error.URLError as e:
        raise ApiError(f"network error: {e.reason}", http_code=0) from e
    return _parse_response(raw, status)


def _parse_response(raw: str, status: int):
    text = raw.strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        if status >= 400:
            raise ApiError(text or f"HTTP {status}", http_code=status, raw=text)
        return text
    if status == 202 and isinstance(data, dict) and "request_id" in data:
        return data
    if isinstance(data, dict) and ("code" in data or "status" in data):
        code_raw = data.get("code")
        ok = code_raw in (20000, 20002, "20000", "20002", True)
        if not ok and code_raw is not None:
            biz = "" if code_raw is True else str(code_raw)
            raise ApiError(data.get("message") or "request failed", http_code=status, biz_code=biz, raw=data)
        return data
    return data


def _handle_error(raw: str, status: int):
    text = raw.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        msg = text or f"HTTP {status}"
        if status == 401:
            msg = f"unauthorized ({text or 'api key rejected'})"
        raise ApiError(msg, http_code=status, raw=raw)
    if isinstance(data, dict) and "code" in data:
        raise ApiError(data.get("message") or "request failed", http_code=status, biz_code=str(data.get("code")), raw=data)
    raise ApiError(text or f"HTTP {status}", http_code=status, raw=raw)


def unwrap_data(result: Any) -> Any:
    """Pull data out of a wrapped {code,message,data} response."""
    if isinstance(result, dict):
        if "data" in result and ("code" in result or "status" in result):
            return result.get("data")
        if "request_id" in result:
            return result
    return result


def is_ok(result: Any) -> bool:
    if isinstance(result, dict):
        c = result.get("code")
        return c in (20000, 20002, "20000", "20002") or result.get("status") is True
    return bool(result)


def biz_code_of(result: Any) -> str:
    if isinstance(result, dict) and "code" in result:
        c = result.get("code")
        return "" if c is True else str(c)
    return ""


def out(value: Any, *, indent: int = 2) -> None:
    if isinstance(value, (dict, list)):
        print(json.dumps(value, ensure_ascii=False, indent=indent))
    else:
        print(value)


def cfg_display_path() -> str:
    return str(CONFIG_PATH)


def poll_until_done(query_fn, request_id: str, *, interval: int = 5, max_seconds: int = 900):
    """Poll a task status function until terminal status or timeout.

    query_fn should take a request_id and return a dict with a 'status' key.
    Terminal statuses: Success, Failed, Canceled.
    """
    import time
    deadline = time.time() + max_seconds
    last = None
    while time.time() < deadline:
        last = query_fn(request_id)
        status = (last.get("status") if isinstance(last, dict) else None) or ""
        if status in ("Success", "Failed", "Canceled"):
            return last
        time.sleep(interval)
    return last
