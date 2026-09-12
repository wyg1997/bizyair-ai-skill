# 05 Auth & API Key

## Authentication model

This skill uses the documented BizyAir.ai API with Bearer API keys against
`api.bizyair.ai` / `meta.bizyair.ai` directly.

- Authentication header: `Authorization: Bearer <api_key>`
- Locale header: `lang: <locale>` (default `en`)

The API key is read from `config.json` -> `credentials.api_key` or the environment
variable `BIZYAIR_API_KEY`.

## Getting an API key

1. Log in to https://www.bizyair.ai.
2. Go to Settings -> API Keys.
3. Create a new key (48 characters, starts with `sk-`).
4. Paste it into `config.json`:

```json
{
  "credentials": {
    "api_key": "sk-..."
  }
}
```

5. Run `python3 scripts/cli.py check` -> expect `status: ok`.

## URL routing

`common.build_url` maps service paths to the correct host:

| Path prefix | Host |
|---|---|
| `meta/v1/...` | `https://meta.bizyair.ai` |
| `finance/v1/...` | `https://api.bizyair.ai` |
| `v1/...` (bare) | `https://api.bizyair.ai` |

Examples:
- `meta/v1/user/info` -> `https://meta.bizyair.ai/v1/user/info`
- `finance/v1/wallet` -> `https://api.bizyair.ai/v1/wallet`
- `v1/webapp/task/openapi/create` -> `https://api.bizyair.ai/v1/webapp/task/openapi/create`
- `v1/modelzoo/tasks/openapi/{endpoint}` -> `https://api.bizyair.ai/v1/modelzoo/tasks/openapi/{endpoint}`

## Public vs authenticated endpoints

| Anonymous (auth=False) | Requires API key |
|---|---|
| `POST /meta/v1/modelzoo/list` | `GET /meta/v1/user/info` |
| `GET  /meta/v1/modelzoo/detail/{endpoint}` | `GET /finance/v1/wallet` |
| `GET  /meta/v1/modelzoo/price_table/{endpoint}` | `POST /v1/webapp/task/openapi/create` |
| `GET  /meta/v1/modelzoo/filters` / `tags` | `GET  /v1/webapp/task/openapi/{id}` (+ `/outputs`, `/cancel`, `/interrupt`) |
| | `POST /v1/modelzoo/tasks/openapi/{endpoint}` |

Public endpoints are called with `auth=False` so a missing API key does not turn them
into 401s.
