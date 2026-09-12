# 04 Common Reference

## URL building

`common.build_url("<service>/v1/<rest>")` maps service paths to the API-key hosts:

| Prefix | Result host |
|---|---|
| `meta/v1/...` | `https://meta.bizyair.ai` |
| `finance/v1/...` | `https://api.bizyair.ai` |
| `v1/...` | `https://api.bizyair.ai` |

Examples: `meta/v1/user/info`, `finance/v1/wallet`, `v1/webapp/task/openapi/create`,
`v1/modelzoo/tasks/openapi/{endpoint}`.

## Headers

- `Authorization: Bearer <api_key>`
- `lang: en` (locale from `config.json` -> `client.locale`)
- `User-Agent`: a desktop browser UA (the site's Cloudflare bans `Python-urllib` with error 1010)
- async task create adds `X-BizyAir-Task-Async: enable`

Public calls (catalog) omit `Authorization` so a missing key does not cause 401.

## Response shape

Wrapped: `{"code":20000,"message":"Ok","status":true,"data":{...}}`. Success codes:
`20000` (Ok), `20002` (Accepted). `common.unwrap_data` pulls `.data`. Async create returns
HTTP 202 with a bare `{"request_id":"..."}` (no wrapper) -> returned as-is.

Bad API keys return `{"code":"20052","message":"无效的API密钥"}` (HTTP 401) or a plain
text unauthorized response.

## Pagination

`current` (1-based), `page_size` (10/20/50). Returns `{list, total, current, page_size}`
(note: `list`, not `records`).

## Task status enum (terminal in bold)

`Queuing` / `Preparing` / `Running` / **`Success`** / **`Failed`** / **`Canceled`**.

## Error codes (retryable vs client)

Retryable (may recover with a wait or a different key): `20049/20050/20051` balance,
`30039` queue full, `30040` max parallelism, `30015/30016/30018` no node, `50600-50604`
rate limit, HTTP 429/402/503.

Client (won't fix by retry): `20015` invalid param, `20021` moderation, `20052/20093/20094`
bad/expired/exhausted API key, `20224` web app not found, `30008` please login,
`30009` task not found, `40025` empty input_values.

Friendly hints are in `config/error_codes.json`.

## Output URLs

- OSS hosts: `storage.bizyair.ai`; some channel editions use third-party temp storage.
- AI app outputs carry `expired_at` (~15 days). Download promptly; don't assume permanence.

## Field types -> payload (ModelZoo input_params)

| field_type | payload |
|---|---|
| customtext | string |
| combo | one of `field_options.values` |
| boolean | bool |
| number / slider / slides | number |
| seed | number (-1 = random) |
| images | list[str] (URLs after upload) |
| audios / videos | string URL |

`field_options` is already a dict (no extra parse needed).
