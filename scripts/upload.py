#!/usr/bin/env python3
"""upload.py -- upload a local media file to BizyAir OSS and print the access URL.

Usage:
  python3 scripts/upload.py <local_path> [--content-type image/jpeg]

Requires the `oss2` package:  uv pip install oss2  (or pip install oss2)

Flow:
  1. GET /v1/upload/token  -> STS credentials + OSS bucket/endpoint/object_key + access_url
  2. oss2.StsAuth + bucket.put_object_from_file(object_key, local_path)
  3. Print the access_url

The access_url is a public HTTPS URL on storage.bizyair.ai that can be passed
directly as an image/video/audio input to modelzoo-run or AI app tasks.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def upload_file(local_path: str, *, content_type: str = "image/jpeg") -> str:
    """Upload a local file to BizyAir OSS. Returns the public access URL."""
    import oss2

    file_name = os.path.basename(local_path)
    result = common.request(
        "GET",
        "v1/upload/token",
        params={"file_name": file_name, "content_type": content_type},
    )
    data = result["data"]
    f = data["file"]
    s = data["storage"]

    auth = oss2.StsAuth(
        f["access_key_id"],
        f["access_key_secret"],
        f["security_token"],
    )
    bucket = oss2.Bucket(auth, s["endpoint"], s["bucket"])
    # put_object_from_file takes a file PATH string, not a file object.
    bucket.put_object_from_file(f["object_key"], local_path, headers={"Content-Type": content_type})

    return data["access_url"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/upload.py <local_path> [--content-type image/jpeg]", file=sys.stderr)
        sys.exit(2)

    local_path = sys.argv[1]
    content_type = "image/jpeg"
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--content-type" and i + 1 < len(sys.argv):
            content_type = sys.argv[i + 1]

    if not os.path.isfile(local_path):
        print(f"File not found: {local_path}", file=sys.stderr)
        sys.exit(1)

    url = upload_file(local_path, content_type=content_type)
    print(json.dumps({"access_url": url, "local_path": local_path}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
