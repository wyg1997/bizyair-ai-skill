# BizyAir.ai Skill

An agent skill for [BizyAir.ai](https://www.bizyair.ai/) — international image/video generation and model execution platform.

[English](README.md) | [中文](README_zh.md)

This skill lets the agent interact with the BizyAir.ai API to search models, run AI apps, query task results, and manage account assets — all through natural language.

 ## Features

 | Category | Capability | CLI Command |
 |---|---|---|
 | **Auth** | Validate API key / diagnose auth issues | `cli.py check` |
 | **Account** | Check wallet balance | `cli.py wallet` |
 | **Image Models** | Curated image model menu | `cli.py image-menu` |
 | **Video Models** | Curated video model menu | `cli.py video-menu` |
 | **ModelZoo — Search** | Search model endpoints by keyword | `cli.py modelzoo-list ["keyword"]` |
 | **ModelZoo — Detail** | View endpoint details | `cli.py modelzoo-detail <endpoint>` |
 | **ModelZoo — Price** | Check endpoint pricing | `cli.py modelzoo-price <endpoint>` |
 | **ModelZoo — Pick** | Interactive candidate picker | `cli.py modelzoo-pick [--video] "<keyword>"` |
 | **ModelZoo — Catalog** | Export markdown catalog | `cli.py modelzoo-md` / `--save` |
 | **AI App — Inspect** | Parse a bizyair.ai link or ID | `cli.py info <link-or-id>` |
 | **AI App — Search** | Search community AI apps | `cli.py app-search "<keyword>"` |
 | **AI App — List** | List all community AI apps (markdown) | `cli.py app-md` / `--save` |
 | **AI App — Run** | Run an AI app asynchronously | `cli.py run <web_app_id> --prompt "..."` |
 | **Tasks — Status** | Query task status | `cli.py status <request_id>` |
 | **Tasks — Outputs** | Fetch task outputs (images/videos) | `cli.py outputs <request_id>` |

 ### Featured Image Models

 - Image B.Pro — all-round text-to-image, stable and versatile
 - Flux Kontext Max — image editing, text rendering, brand design
 - Seedream 5.0 — posters, key visuals, marketing-friendly
 - Nano Banana 2 — balanced price/performance across styles
 - GPT Image 2 — strong instruction-following and text rendering

 ### Featured Video Models

 - Video V.3.1.Pro — cinematic, strong camera presence
 - HappyHorse — fast, good price/performance
 - Kling 3.0 Pro — bold motion and action, native 4K
 - Wan 2.7 — strong Chinese understanding, audio sync, multi-shot
 - Seedance 2.0 — character motion, dance, stronger consistency

 ## Getting Started

 ### 1. Get an API Key

 Visit [BizyAir.ai](https://www.bizyair.ai/) → **Settings → API Keys** to create a key (48 characters, starts with `sk-`).

 ### 2. Configure

 Edit `config.json` and replace the placeholder:

 ```json
 {
   "credentials": {
     "api_key": "sk-your-real-api-key"
   }
 }
 ```

 Or set an environment variable:

 ```bash
 export BIZYAIR_API_KEY="sk-your-real-api-key"
 ```

 ### 3. Verify

 ```bash
 python3 scripts/cli.py check
 ```

 ## Project Structure

 ```
 bizyair-ai-skill/
 ├── SKILL.md              # Skill instructions for the agent
 ├── config.json           # API key and client config
 ├── config/
 │   ├── menus.json        # Curated model menu text
 │   └── error_codes.json  # Error code mappings
 ├── scripts/
 │   ├── cli.py            # CLI entry point
 │   ├── common.py         # Shared HTTP/utils
 │   ├── modelzoo.py       # ModelZoo catalog commands
 │   ├── apps.py           # AI App commands
 │   ├── tasks.py          # Task create/query commands
 │   └── account.py        # Account/wallet commands
 └── references/           # API reference docs (auth, catalog, tasks, etc.)
     ├── 01-modelzoo-catalog.md
     ├── 02-account-assets.md
     ├── 03-ai-app-tasks.md
     ├── 04-common-reference.md
     └── 05-auth-and-api-key.md
 ```

 ## API Endpoints

 | Base URL | Used For |
 |---|---|
 | `https://api.bizyair.ai` | Tasks, wallet, upload |
 | `https://meta.bizyair.ai` | User info, ModelZoo catalog, webapp detail |

 ## Safety Boundaries

 **Allowed:** ModelZoo catalog browsing, AI app task creation/querying, account queries.

 **Forbidden:** Creating/editing/deleting models or apps, liking/forking/publishing, profile editing, API key management, payments, stress-testing.

 ## License

 [MIT](LICENSE)
