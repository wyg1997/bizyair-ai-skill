# 03 AI App & ModelZoo Tasks

## AI apps

Unified task interface: `https://api.bizyair.ai/v1/webapp/task/openapi/*`. Three call
modes, switched by header, body unchanged:

| Mode | Header | Behavior |
|---|---|---|
| sync | none | holds connection, returns result directly (read timeout >= 60s) |
| async | `X-BizyAir-Task-Async: enable` | HTTP 202 -> bare `{"request_id": "..."}`, then poll |
| webhook | `X-BizyAir-Task-WebHook-Url: <url>` | 202 + request_id, server POSTs result on done |

The CLI uses **async** by default.

### Flow

1. `GET /meta/v1/webapp/{web_app_id}/detail` -> metadata + input_nodes (`cli.py app-detail`)
2. build `input_values` = `{ "nodeId:NodeName.field": value }` (at least one field; usually the prompt)
3. `POST /v1/webapp/task/openapi/create` with `{web_app_id, suppress_preview_output:false, input_values}` + async header
4. poll `GET /v1/webapp/task/openapi/{request_id}` until `status` is terminal
5. `GET /v1/webapp/task/openapi/{request_id}/outputs` -> `outputs[].object_url`

```bash
python3 scripts/cli.py app-detail 57302
python3 scripts/cli.py run 57302 --prompt "a futuristic cityscape at sunset"
python3 scripts/cli.py status <request_id>
python3 scripts/cli.py outputs <request_id>
```

`run` does create(async) -> poll -> fetch outputs in one shot.

### Task status

`Queuing` / `Preparing` / `Running` (non-terminal) -> `Success` / `Failed` / `Canceled`.


### Outputs

- `outputs[].object_url` are temporary (~15 day expiry) -> download promptly.
- Images render as `![result](url)`; video as a bare URL line.
- `suppress_preview_output: true` makes outputs return null -> do not set it.

## ModelZoo tasks

The standard-model API runs a ModelZoo endpoint directly:

- `POST /v1/modelzoo/tasks/openapi/{endpoint}` with the `input_params` payload
- `GET  /v1/modelzoo/tasks/openapi/{request_id}` for status

Both are served from `https://api.bizyair.ai`.

Build the payload from `modelzoo-detail` -> `input_params`. Media inputs (images/audios/videos) can be passed as URLs after uploading to OSS
(`GET /v1/upload/token` -> commit), OR directly as base64 data URLs
(`data:image/jpeg;base64,...`) — no upload needed.

```bash
python3 scripts/cli.py modelzoo-run <endpoint> --json '{"prompt":"a cat","image_size":"1024x1024"}'
python3 scripts/cli.py modelzoo-status <request_id>
```

The catalog (list/detail/price) is public and reliable.

## Execution permission

- "default / you decide / recommended" only authorizes a prefilled card, NOT execution.
- Only "go / run it / confirm execution" authorizes real submission (which spends balance).
