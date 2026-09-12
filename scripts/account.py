"""account.py -- account, wallet and session validation."""
from __future__ import annotations

import common


def user_info():
    """GET /meta/v1/user/info -- current user metadata (requires valid API key)."""
    return common.unwrap_data(common.request("GET", "meta/v1/user/info"))


def wallet():
    """GET /finance/v1/wallet -- balance (recharge + gift + total)."""
    return common.unwrap_data(common.request("GET", "finance/v1/wallet"))


def userspace_detail():
    """GET /meta/v1/userspace/{user_id}/detail -- profile/identity counter/followed."""
    user = user_info()
    uid = user.get("id") if isinstance(user, dict) else None
    if not uid:
        return None
    return common.unwrap_data(common.request("GET", f"meta/v1/userspace/{uid}/detail"))


def check():
    """Validate the configured API key. Returns a status dict.

    status: ok | no_token | invalid | no_balance
    """
    if not common.api_key():
        return {"status": "no_token", "message": "No API key configured. Set credentials.api_key in config.json or BIZYAIR_API_KEY."}
    try:
        info = user_info()
        if isinstance(info, dict) and info.get("id"):
            return {"status": "ok", "user": info}
        return {"status": "invalid", "message": "API key was accepted but no user returned."}
    except common.ApiError as e:
        if e.http_code == 401:
            return {"status": "invalid", "message": "API key rejected by server. Check credentials.api_key or BIZYAIR_API_KEY."}
        if e.biz_code in ("20049", "20050", "20051"):
            return {"status": "no_balance", "message": "Insufficient balance."}
        return {"status": "error", "message": str(e), "biz_code": e.biz_code, "http_code": e.http_code}


def cmd_check(args):
    common.out(check())


def cmd_wallet(args):
    common.out(wallet())


def cmd_whoami(args):
    common.out(user_info())
