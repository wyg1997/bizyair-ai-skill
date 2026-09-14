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

Works with all tested models: Happyhorse, Seedance, Qwen Image, Nano Banana (when upstream is healthy).

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

### Field naming differs across models

Each model endpoint has different field names for the image input. **Always check
`modelzoo-detail <endpoint>` → `input_params` before constructing the payload.**

| Model | Image field name | Notes |
|---|---|---|
| Vidu Q3 Pro | `images` | Array of URLs, max 1 |
| Happyhorse 1.0 | `first_frame_url` | Array of URLs, max 1 |
| Seedance 2.0 | `ref_images` | Array of URLs (reference-to-video) |
| Kling 3.0 Pro | (FLF) uses first/last frame | Check detail for exact field |
| Wan 2.7 | (FLF) uses first/last frame | Check detail for exact field |
| Nano Banana 2 / Pro | `image_urls` | Array, max 8 |
| Qwen Image 2.0 | `image_urls` | Array, max 3 |

### Common parameters

| Parameter | Type | Notes |
|---|---|---|
| `prompt` | string | Text description of desired motion/action |
| `duration` | number (slider) | Range varies by model (e.g. 3~15, 4~16) |
| `resolution` | combo | 480p / 720p / 1080p / 4k (varies) |
| `aspect_ratio` | combo | auto/16:9/9:16/4:3/3:4/1:1/21:9 (Seedance) |
| `generate_audio` | boolean | Vidu + Seedance support this |
| `audio_type` | combo | Vidu only: all / speech_only / sound_effect_only |
| `seed` | number | -1 = random |

### Image editing models

| Model | Endpoint | Min credits | Notes |
|---|---|---|---|
| Qwen Image 2.0 | `qwen-image-2-0-official/image-to-image` | 40 | Reliable, supports Chinese prompts |
| Nano Banana 2 | `nano-banana-2-official/image-to-image` | 40 | Google Gemini 3.1 Flash Image |
| Nano Banana Pro | `nano-banana-pro-official/image-to-image` | 100 | Higher quality, may be less stable |

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

1. **Vidu API timeouts** — Vidu Q3 Pro may fail with "dial tcp ... connection timed out"
   (the call goes api.bizyair.ai → api.vidu.cn which may be temporarily unreachable).
   Retry or fall back to Seedance / Happyhorse.

2. **Nano Banana upstream failures** — Nano Banana 2 and Pro may fail with
   "empty output: no data resolved from upstream response" or "服务侧处理响应时异常".
   This is an upstream Google API issue, not a payload problem. Fall back to Qwen Image 2.0
   which is more reliable for image editing tasks.

3. **`put_object_from_file` argument** — oss2's `put_object_from_file` takes a file
   **path string**, not a file object. Passing a BufferedReader raises TypeError.

4. **Field type coercion** — `images`-type fields accept `list[str]`, but passing a
   bare string works because `_coerce()` in modelzoo.py wraps it in a list.

5. **Resolution naming** — Happyhorse uses uppercase (`720P`, `1080P`); Vidu and
   Seedance use lowercase (`720p`, `1080p`). Check `field_options.values` in detail.

6. **Cost awareness** — always check `modelzoo-price` or `min_credits` before running.
   4K generation can cost 600+ credits.

7. **Chinese prompts for Qwen** — Qwen Image 2.0 handles Chinese-language edit
   instructions well (e.g. 磨皮, 淡化黑眼圈, 提亮肤色). Use Chinese for beauty
   retouching and style-specific edits; use English for general image-to-video.

8. **oss2 install in restricted environments** — `uv pip install oss2` into a shared
   venv may fail with permission denied. Create a throwaway venv instead:
   `uv venv /tmp/bizyair_venv && uv pip install --python /tmp/bizyair_venv/bin/python oss2`
   Then run the upload script with `/tmp/bizyair_venv/bin/python`.
