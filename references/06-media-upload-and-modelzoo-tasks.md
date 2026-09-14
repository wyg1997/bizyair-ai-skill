# 06 Media Upload & ModelZoo Task Execution

## Overview

ModelZoo endpoints accept media inputs (images, videos, audios) as **public URLs**
**or base64 data URLs**. For local files, prefer base64 (zero dependencies); use OSS
upload only for very large files or when a persistent public URL is needed.

## Base64 data URLs (preferred for local files)

Read the local file, base64-encode it, and pass `data:image/<ext>;base64,<...>` directly
in the image/audio/video field of the task payload. No upload step or `oss2` dependency
needed. Use `modelzoo.encode_local_image(path)` to generate the data URL.

```python
import modelzoo
data_url = modelzoo.encode_local_image("/path/to/image.jpg")
payload = {"image_urls": [data_url], "prompt": "...", ...}
modelzoo.create_task("endpoint", payload)
```

## OSS upload flow (for large files or persistent URLs)

### Prerequisites

```bash
uv pip install oss2   # or: pip install oss2
```

⚠️ If installing into a shared/restricted venv fails (permission denied), create a
throwaway venv: `uv venv /tmp/bizyair_venv && uv pip install --python /tmp/bizyair_venv/bin/python oss2`

### Using the helper script

```bash
python3 scripts/upload.py <local_path> [--content-type image/jpeg]
# Output: {"access_url": "https://storage.bizyair.ai/img/...", "local_path": "..."}
```

### Manual flow (if script unavailable)

1. **Get STS token** — `GET /v1/upload/token?file_name=<name>&content_type=<ct>` (requires API key)
   - Returns: `data.file.{object_key, access_key_id, access_key_secret, security_token}`
   - Returns: `data.storage.{endpoint, bucket, region}`
   - Returns: `data.access_url` — the public URL to use in task payloads

2. **Upload to OSS** — use `oss2.StsAuth` + `bucket.put_object_from_file(object_key, local_path)`
   - ⚠️ `put_object_from_file` takes a **file path string**, not a file object.
   - Set `Content-Type` header to match the media type.

3. **Use the access_url** — pass it in the modelzoo-run payload for image/video/audio fields.

## ModelZoo task execution

### CLI

```bash
python3 scripts/cli.py modelzoo-run <endpoint> --json '{...}'
python3 scripts/cli.py modelzoo-status <request_id>
```

### Always search dynamically — never hardcode model names

The model catalog changes over time. **Always discover endpoints at runtime:**

```bash
# Search by task type or model series
python3 scripts/cli.py modelzoo-list "text-to-video"
python3 scripts/cli.py modelzoo-list "image-to-image"
python3 scripts/cli.py modelzoo-pick "kling"

# Then inspect the endpoint's input parameters before building a payload
python3 scripts/cli.py modelzoo-detail <endpoint>
```

Never assume a specific model/endpoint still exists or has the same parameters.
**Always run `modelzoo-detail <endpoint>` → read `input_params`** to get the exact
field names, types, and allowed values for that endpoint.

### Common field patterns

Field names vary across models. Common patterns seen in the catalog:

| Pattern | Typical usage |
|---|---|
| `images` / `image_urls` | Array of image URLs or data URLs |
| `ref_images` | Reference images for image-to-video tasks |
| `first_frame_url` / `last_frame_url` | First/last frame for video generation |
| `prompt` | Text description of desired output |
| `duration` | Video length (slider, range varies by model) |
| `resolution` | 480p / 720p / 1080p / 4k (varies by model) |
| `aspect_ratio` | auto/16:9/9:16/4:3/3:4/1:1 (varies) |
| `seed` | number (-1 = random) |

These are **patterns, not guarantees** — always confirm via `modelzoo-detail`.

### Task lifecycle

1. `POST /v1/modelzoo/tasks/openapi/<endpoint>` (async) → `{request_id}`
2. Poll `GET /v1/modelzoo/tasks/openapi/<request_id>` until status is terminal
3. Terminal status: `Success` / `Failed` / `Canceled`
4. On success, `outputs.videos[]` or `outputs.images[]` contain result URLs
5. **Result URLs expire (~15 days)** — download promptly

### Polling

Videos typically take 1–3 minutes. The CLI `modelzoo-status` does a single check
(no auto-poll). Use a shell loop or the `modelzoo.poll_until_done()` function:

```bash
# Shell loop example
RID="abc-123"
while true; do
  STATUS=$(python3 scripts/cli.py modelzoo-status "$RID" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('status',''))")
  echo "Status: $STATUS"
  [ "$STATUS" = "Success" ] || [ "$STATUS" = "Failed" ] && break
  sleep 10
done
```

## Pitfalls

1. **Upstream timeouts** — Some model endpoints may fail with connection timeouts when
   the upstream provider is temporarily unreachable. Retry or use `modelzoo-list` to
   find alternative models.

2. **Upstream failures** — Some models may return "empty output" or service-side errors.
   This is an upstream issue, not a payload problem. Use `modelzoo-list` to find fallbacks.

3. **`put_object_from_file` argument** — oss2's `put_object_from_file` takes a file
   **path string**, not a file object. Passing a BufferedReader raises TypeError.

4. **Field type coercion** — `images`-type fields accept `list[str]`, but passing a
   bare string works because `_coerce()` in modelzoo.py wraps it in a list.

5. **Resolution naming** — Some models use uppercase (`720P`, `1080P`); others use
   lowercase (`720p`, `1080p`). Check `field_options.values` in detail.

6. **Cost awareness** — always check `modelzoo-price` or `min_credits` before running.
   High-resolution generation can cost hundreds of credits.

7. **oss2 install in restricted environments** — `uv pip install oss2` into a shared
   venv may fail with permission denied. Create a throwaway venv instead:
   `uv venv /tmp/bizyair_venv && uv pip install --python /tmp/bizyair_venv/bin/python oss2`
   Then run the upload script with `/tmp/bizyair_venv/bin/python`.
