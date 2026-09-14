# Skill Maintenance & Git Workflow

The skill source lives at **https://github.com/wyg1997/bizyair-ai-skill.git**.
The local working copy is the skill directory itself (the repo root == skill root).

## Sensitive files

`config.json` contains the real BizyAir API key. It is in `.gitignore` and was
removed from git tracking (`git rm --cached config.json`). **Never commit it.**

If `config.json` shows up as modified in `git status`, restore it:
```bash
git checkout config.json   # discard local changes to tracked file
```
…or simply leave it untracked (it's in `.gitignore` now) and skip it during `git add`.

## Git identity

Set per-repo (not global) if not already configured:
```bash
git config user.name  "wyg1997"
git config user.email "wangyinggang@foxmail.com"
```

## Committing changes

```bash
cd /opt/data/skills/bizyair-ai-skill
git add -A                           # config.json is ignored automatically
git diff --cached --stat             # sanity check — no config.json
git commit -m "feat: <summary>"
```

Always verify the staged diff does **not** include `config.json` before committing.

## Pushing to GitHub

The remote is HTTPS, so push requires a **Personal Access Token** (classic, `repo` scope).
Generate at: https://github.com/settings/tokens

Push with inline token auth:
```bash
git push https://<token>@github.com/wyg1997/bizyair-ai-skill.git main
```
Or configure the remote URL once:
```bash
git remote set-url origin https://<token>@github.com/wyg1997/bizyair-ai-skill.git
git push origin main
```
After push, restore the clean remote URL to avoid leaking the token in disk state:
```bash
git remote set-url origin https://github.com/wyg1997/bizyair-ai-skill.git
```

## Commit message convention

- `feat:` new functionality (scripts, endpoints, capabilities)
- `fix:` bug fixes
- `docs:` documentation-only changes
- `chore:` maintenance (gitignore, CI, etc.)

## Reviewing what changed since last push

```bash
git log --oneline origin/main..HEAD   # commits not yet pushed
git diff origin/main..HEAD --stat     # file-level summary
```
