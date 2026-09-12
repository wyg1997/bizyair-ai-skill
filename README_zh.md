# BizyAir.ai Skill

一个用于 [BizyAir.ai](https://www.bizyair.ai/)（国际版）的智能体 Skill —— 支持图片/视频生成与模型执行。

English | [中文](README_zh.md)

该 Skill 让智能体通过自然语言与 BizyAir.ai API 交互，实现模型搜索、运行 AI 应用、查询任务结果和管理账户资产等功能。

## 安装方式

将此仓库链接提供给智能体即可：

```
https://github.com/wyg1997/bizyair-ai-skill
```

## 功能概览

 | 分类 | 功能 | CLI 命令 |
 |---|---|---|
 | **认证** | 验证 API Key / 诊断认证问题 | `cli.py check` |
 | **账户** | 查询钱包余额 | `cli.py wallet` |
 | **图片模型** | 精选图片模型菜单 | `cli.py image-menu` |
 | **视频模型** | 精选视频模型菜单 | `cli.py video-menu` |
 | **ModelZoo — 搜索** | 按关键词搜索模型端点 | `cli.py modelzoo-list ["关键词"]` |
 | **ModelZoo — 详情** | 查看端点详情 | `cli.py modelzoo-detail <endpoint>` |
 | **ModelZoo — 价格** | 查看端点定价 | `cli.py modelzoo-price <endpoint>` |
 | **ModelZoo — 选择器** | 交互式候选模型选择 | `cli.py modelzoo-pick [--video] "关键词"` |
 | **ModelZoo — 目录** | 导出 Markdown 目录 | `cli.py modelzoo-md` / `--save` |
 | **AI 应用 — 解析** | 解析 bizyair.ai 链接或 ID | `cli.py info <链接或ID>` |
 | **AI 应用 — 搜索** | 搜索社区 AI 应用 | `cli.py app-search "关键词"` |
 | **AI 应用 — 列表** | 列出所有社区 AI 应用 | `cli.py app-md` / `--save` |
 | **AI 应用 — 运行** | 异步运行 AI 应用 | `cli.py run <web_app_id> --prompt "..."` |
 | **任务 — 状态** | 查询任务状态 | `cli.py status <request_id>` |
 | **任务 — 结果** | 获取任务输出（图片/视频） | `cli.py outputs <request_id>` |

 ### 精选图片模型

 - Image B.Pro — 全能文生图，稳定且通用
 - Flux Kontext Max — 图像编辑、文字渲染、品牌设计
 - Seedream 5.0 — 海报、主视觉、营销友好
 - Nano Banana 2 — 多风格性价比之选
 - GPT Image 2 — 强指令跟随与文字渲染

 ### 精选视频模型

 - Video V.3.1.Pro — 电影质感，镜头感强
 - HappyHorse — 速度快，性价比高
 - Kling 3.0 Pro — 大动作与运动，原生 4K
 - Wan 2.7 — 中文理解强，音频同步，多镜头
 - Seedance 2.0 — 角色动作、舞蹈，一致性更强

 ## 快速开始

 ### 1. 获取 API Key

 访问 [BizyAir.ai](https://www.bizyair.ai/) → **Settings → API Keys** 创建密钥（48 位，以 `sk-` 开头）。

 ### 2. 配置

 编辑 `config.json`，替换占位符：

 ```json
 {
   "credentials": {
     "api_key": "sk-你的真实API密钥"
   }
 }
 ```

 或设置环境变量：

 ```bash
 export BIZYAIR_API_KEY="sk-你的真实API密钥"
 ```

 ### 3. 验证

 ```bash
 python3 scripts/cli.py check
 ```

 ## 项目结构

 ```
 bizyair-ai-skill/
 ├── SKILL.md              # 智能体 Skill 说明
 ├── config.json           # API 密钥与客户端配置
 ├── config/
 │   ├── menus.json        # 精选模型菜单文本
 │   └── error_codes.json  # 错误码映射
 ├── scripts/
 │   ├── cli.py            # CLI 入口
 │   ├── common.py         # 通用 HTTP/工具函数
 │   ├── modelzoo.py       # ModelZoo 目录命令
 │   ├── apps.py           # AI 应用命令
 │   ├── tasks.py          # 任务创建/查询命令
 │   └── account.py        # 账户/钱包命令
 └── references/           # API 参考文档（认证、目录、任务等）
     ├── 01-modelzoo-catalog.md
     ├── 02-account-assets.md
     ├── 03-ai-app-tasks.md
     ├── 04-common-reference.md
     └── 05-auth-and-api-key.md
 ```

 ## API 端点

 | 基础 URL | 用途 |
 |---|---|
 | `https://api.bizyair.ai` | 任务、钱包、上传 |
 | `https://meta.bizyair.ai` | 用户信息、ModelZoo 目录、应用详情 |

 ## 安全边界

 **允许：** ModelZoo 目录浏览、AI 应用任务创建/查询、账户查询。

 **禁止：** 创建/编辑/删除模型或应用、点赞/Fork/发布、编辑个人资料、API Key 管理、支付、压力测试。

 ## 开源协议

 [MIT](LICENSE)
