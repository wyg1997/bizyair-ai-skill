#!/usr/bin/env python3
"""cli.py -- unified CLI for the BizyAir.ai skill.

Usage:
  python3 scripts/cli.py check
  python3 scripts/cli.py wallet
  python3 scripts/cli.py whoami
  python3 scripts/cli.py image-menu | video-menu
  python3 scripts/cli.py modelzoo-list ["keyword"]
  python3 scripts/cli.py modelzoo-detail <endpoint>
  python3 scripts/cli.py modelzoo-price <endpoint>
  python3 scripts/cli.py modelzoo-pick [--video] "<keyword>"
  python3 scripts/cli.py modelzoo-run <endpoint> --json '{...}'
  python3 scripts/cli.py modelzoo-status <request_id>
  python3 scripts/cli.py modelzoo-md [--save]
  python3 scripts/cli.py app-search ["keyword"]
  python3 scripts/cli.py app-md [--save]
  python3 scripts/cli.py app-detail <web_app_id>
  python3 scripts/cli.py run <web_app_id> --prompt "..." [--json '{...}']
  python3 scripts/cli.py status <request_id>
  python3 scripts/cli.py outputs <request_id>
  python3 scripts/cli.py info <link-or-id>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import account
import apps
import common
import modelzoo
import tasks


def _menus():
    with open(Path(__file__).resolve().parent.parent / "config" / "menus.json", encoding="utf-8") as fh:
        return json.load(fh)


def cmd_image_menu(args):
    print(_menus().get("image_menu", ""))


def cmd_video_menu(args):
    print(_menus().get("video_menu", ""))


def _link_or_id(target: str) -> str:
    """Accept a bizyair.ai URL or a raw id; return the id.

    /modelzoo/<endpoint...>     -> endpoint path kept (call modelzoo-detail)
    /community/app/<id>         -> <id>
    plain digits                -> treated as web_app_id
    """
    if target.startswith("http"):
        from urllib.parse import urlparse
        path = urlparse(target).path
        if path.startswith("/modelzoo/"):
            return path[len("/modelzoo/"):]
        parts = [p for p in path.split("/") if p]
        return parts[-1] if parts else target
    return target


def cmd_info(args):
    target = _link_or_id(args[0])
    if "/" in target:
        print("# looks like a ModelZoo endpoint")
        common.out({"endpoint": target, "detail": modelzoo.get_detail(target), "price": modelzoo.get_price(target)})
    else:
        print("# looks like an AI App id")
        common.out({"web_app_id": target, "detail": tasks.app_detail(target)})


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    rest = sys.argv[2:]
    dispatch = {
        "check": account.cmd_check,
        "wallet": account.cmd_wallet,
        "whoami": account.cmd_whoami,
        "image-menu": cmd_image_menu,
        "video-menu": cmd_video_menu,
        "modelzoo-list": modelzoo.cmd_list,
        "modelzoo-detail": modelzoo.cmd_detail,
        "modelzoo-price": modelzoo.cmd_price,
        "modelzoo-pick": modelzoo.cmd_pick,
        "modelzoo-md": modelzoo.cmd_md,
        "app-search": apps.cmd_app_search,
        "app-md": apps.cmd_app_md,
        "app-detail": tasks.cmd_app_detail,
        "status": tasks.cmd_status,
        "outputs": tasks.cmd_outputs,
        "run": tasks.cmd_run,
        "info": cmd_info,
    }
    # modelzoo-run / modelzoo-status are best-effort; expose through modelzoo module
    if cmd == "modelzoo-run":
        import json as _json
        ep = rest[0]
        payload = {}
        i = 1
        while i < len(rest):
            if rest[i] == "--json" and i + 1 < len(rest):
                payload = _json.loads(rest[i + 1])
                i += 2
            elif rest[i] == "--param" and i + 1 < len(rest):
                k, v = rest[i + 1].split("=", 1)
                payload[k] = v
                i += 2
            else:
                i += 1
        common.out(modelzoo.create_task(ep, payload))
        return
    if cmd == "modelzoo-status":
        common.out(modelzoo.query_task(rest[0]))
        return
    fn = dispatch.get(cmd)
    if not fn:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)
        sys.exit(1)
    try:
        fn(rest)
    except common.ApiError as e:
        print(json.dumps({"error": str(e), "http_code": e.http_code, "biz_code": e.biz_code}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except IndexError:
        print(f"missing argument for '{cmd}'", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
