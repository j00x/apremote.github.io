# Automation

Version-controlled "brains" and runners for the site's content automations. This folder is
**excluded from the published site** (see `exclude:` in `_config.yml`).

## Contents

| File | Purpose |
|------|---------|
| `health-briefing-agent.md` | Instruction set / system prompt for the daily **Health** briefing agent. |
| `memories.md` | Long-term memory for the **Health** agent. |
| `azure-blog-agent.md` | Instruction set / system prompt for the weekly **Azure** blog agent. |
| `azure-memories.md` | Long-term memory + topic backlog for the **Azure** agent. |
| `scripts/generate_azure_post.py` | Python generator: Azure OpenAI -> `_posts/*.md` (used by the Azure GitHub Action). |
| `scripts/generate_health_briefing.py` | Python generator: Azure OpenAI -> `health/briefings/*.json` + updates `health/index.json` (used by the Health GitHub Action). |
| `scripts/requirements.txt` | Python deps for both generators. |
| `runbooks/Publish-AzureBlogPost.ps1` | Azure Automation runbook: generate the Azure post + open a PR via the GitHub API. |
| `runbooks/Publish-HealthBriefing.ps1` | Azure Automation runbook: generate the Health briefing + open a PR via the GitHub API. |
| `../.github/workflows/publish-azure-post.yml` | GitHub Actions workflow: weekly Azure post -> review PR. |
| `../.github/workflows/publish-health-briefing.yml` | GitHub Actions workflow: daily Health briefing -> review PR. |

Both content streams have the **same shape**: an agent instruction file + a memories file +
a Python generator + a GitHub Actions workflow + an Azure runbook. They **open a pull request
for review** rather than publishing straight to `main`, so you can tweak before it goes live.
Switch to direct-publish only if you want fully hands-off posting (see below).

---

## Secrets & variables (one set powers everything)

Both workflows (`publish-azure-post.yml` and `publish-health-briefing.yml`) read the **same**
configuration, so you only set it once. Add it under **Settings -> Secrets and variables ->
Actions**:

**Secrets** (tab: _Secrets_) — sensitive, never printed:

| Name | Example | Notes |
|------|---------|-------|
| `AZURE_OPENAI_ENDPOINT` | `https://my-aoai.openai.azure.com` | Your Azure OpenAI resource endpoint. |
| `AZURE_OPENAI_API_KEY` | `­­­­­­­­­…` | Key from the Azure OpenAI resource (or use OIDC + AAD instead). |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o` | The **chat model deployment** name (not the model name). |

**Variables** (tab: _Variables_) — non-sensitive config:

| Name | Default | Notes |
|------|---------|-------|
| `AZURE_OPENAI_API_VERSION` | `2024-10-21` | Optional; omit to use the default. |

Also enable PR creation once: **Settings -> Actions -> General -> Workflow permissions ->**
"Read and write permissions" + "Allow GitHub Actions to create and approve pull requests".

> **Until these secrets exist, the scheduled runs are safe no-ops.** Each workflow's first
> step (`Preflight`) checks for `AZURE_OPENAI_API_KEY`; if it's missing it logs a warning and
> skips the rest, so the cron schedule never produces red/failing runs.

For the **Azure Automation runbooks**, the same values live in **Key Vault** instead
(`aoai-api-key`, plus the `gh-pat-blog` GitHub PAT) with endpoint/deployment as Automation
variables — see Option B.

### Switching a stream to direct-publish (no review PR)

The daily Health briefing is the most likely candidate for hands-off posting. To publish
straight to `main` instead of opening a PR, replace the "Open pull request" step in
`publish-health-briefing.yml` with a commit/push of the generated files, e.g.:

```yaml
      - name: Commit and push
        if: steps.preflight.outputs.skip != 'true'
        run: |
          git config user.name  "health-briefing-bot"
          git config user.email "actions@github.com"
          git add health/briefings/ health/index.json
          git commit -m "health: add briefing for ${{ steps.gen.outputs.date }}"
          git push
```

(The default `GITHUB_TOKEN` with `contents: write` — already granted — can push to `main`.)

---

## Option A — GitHub Actions (simplest; repo already on GitHub)

Two workflows, same shape — each runs its generator, then opens a **draft PR** with the
result. Add the [secrets & variables](#secrets--variables-one-set-powers-everything) once and
both work.

| Workflow | Generator | Cadence | Output |
|----------|-----------|---------|--------|
| **Publish Azure Blog Post** (`publish-azure-post.yml`) | `generate_azure_post.py` | weekly (`0 13 * * 1`) + manual | `_posts/YYYY-MM-DD-<slug>.md` |
| **Publish Health Briefing** (`publish-health-briefing.yml`) | `generate_health_briefing.py` | daily (`0 10 * * *`) + manual | `health/briefings/YYYY-MM-DD.json` + `health/index.json` |

**Run manually:** Actions tab → pick the workflow → **Run workflow**. The Azure one takes an
optional category/topic; the Health one takes an optional date (blank = today, UTC). Adjust a
`cron` line in the workflow to change the schedule.

**Local test (no model / no secrets):**

```bash
pip install -r automation/scripts/requirements.txt

# Azure post
python automation/scripts/generate_azure_post.py --dry-run        # writes a stub post
bundle exec jekyll build                                          # confirm it builds
git checkout -- _posts automation/azure-memories.md               # discard the stub
rm -f _posts/*-dry-run-sample-post.md

# Health briefing
python automation/scripts/generate_health_briefing.py --dry-run   # writes a stub briefing + index entry
bundle exec jekyll build                                          # confirm it builds
git checkout -- health/index.json                                 # discard the manifest change
rm -f health/briefings/$(date +%F).json                           # discard the stub briefing
```

---

## Option B — Azure Automation runbook (Azure-native)

`runbooks/Publish-AzureBlogPost.ps1` and `runbooks/Publish-HealthBriefing.ps1` generate their
content and open a PR via the GitHub API. Both share the same Automation setup.

**Setup**

1. **Automation account** with a **system-assigned managed identity**; import Az modules
   `Az.Accounts` and `Az.KeyVault`.
2. **Key Vault** secrets (grant the identity *get* on secrets):
   - `gh-pat-blog` — fine-grained GitHub PAT scoped to this repo with
     **Contents: read/write** and **Pull requests: read/write**.
   - `aoai-api-key` — Azure OpenAI key.
3. **Automation variables:** `KeyVaultName`, `AoaiEndpoint`, `AoaiDeployment`
   (owner/repo default to `j00x/apremote.github.io`).
4. Import each `.ps1` as a **PowerShell runbook**, publish it, and attach a **schedule**
   (weekly for the Azure post, daily for the Health briefing).
