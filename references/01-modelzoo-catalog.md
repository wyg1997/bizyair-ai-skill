# 01 ModelZoo Catalog

ModelZoo lists the platform's low-level model endpoints (text-to-image, text-to-video,
image-to-image, etc.). Catalog calls are **public** (no session needed).

## List

```bash
python3 scripts/cli.py modelzoo-list "text-to-video"
python3 scripts/cli.py modelzoo-list            # all
```

Backed by `POST /api/meta/v1/modelzoo/list?current=1&page_size=20&sort=Auto` with body
`{"tags":[],"categories":[],"show_deprecated":false,"keyword":"<opt>"}`. Returns
`{list:[...], total, current, page_size}`. Each item: `endpoint`, `display_name`,
`category`, `sub_category`, `model_name`, `min_credits`, `edition`, `status`.

## Detail

```bash
python3 scripts/cli.py modelzoo-detail bizyair/flux-klein/image-to-image/watermarker-remover
```

`GET /api/meta/v1/modelzoo/detail/{endpoint}`. The `endpoint` contains slashes and is used
verbatim in the path.

## Price

```bash
python3 scripts/cli.py modelzoo-price "<endpoint>"
```

`GET /api/meta/v1/modelzoo/price_table/{endpoint}` -> `price_tables[]` with
`pricing_name` / `pricing_values` / `unit_name`, plus `benefit` (rpd/rph/rpm limits).
The CLI prints a `simple_price` summary (e.g. `Output 10 call`).

## Candidate picker

```bash
python3 scripts/cli.py modelzoo-pick "kling"          # image-biased
python3 scripts/cli.py modelzoo-pick --video "dance"
```

Returns `{query, modality, total, candidates:[{endpoint,name,category,min_credits,link}]}`.
The agent keeps video-relevant candidates when `--video` and drops/sinks the rest.

## Search-term rule

Translate the user's semantic need into real model/series/task words before searching
("kling", "seedance", "wan", "text-to-video", "image-to-image"). Don't feed free-form
descriptors ("cinematic", "4k") as keywords.
