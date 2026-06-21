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
| `scripts/generate_azure_post.py` | Python generator: Azure OpenAI -> `_posts/*.md` (used by the GitHub Action). |
| `scripts/requirements.txt` | Python deps for the generator. |
| `runbooks/Publish-AzureBlogPost.ps1` | Azure Automation runbook: generate + open a PR via the GitHub API. |
| `../.github/workflows/publish-azure-post.yml` | GitHub Actions workflow that runs the generator and opens a review PR. |

Both runners **open a pull request for review** rather than publishing straight to `main`,
so you can tweak before it goes live. Switch to direct-publish only if you want fully
hands-off posting.

---

## Option A — GitHub Actions (simplest; repo already on GitHub)

Runs `scripts/generate_azure_post.py`, then opens a draft PR with the new post.

**Setup**

1. In the repo: **Settings → Secrets and variables → Actions → New repository secret**, add:
   - `AZURE_OPENAI_ENDPOINT` — e.g. `https://my-aoai.openai.azure.com`
   - `AZURE_OPENAI_API_KEY` — your Azure OpenAI key
   - `AZURE_OPENAI_DEPLOYMENT` — your chat model deployment name (e.g. `gpt-4o`)
   - (optional variable) `AZURE_OPENAI_API_VERSION` — defaults to `2024-10-21`
2. Ensure Actions can open PRs: **Settings → Actions → General → Workflow permissions →**
   "Read and write permissions" + "Allow GitHub Actions to create and approve pull requests".
3. **Run it:** Actions tab → "Publish Azure Blog Post" → **Run workflow** (pick a category /
   optional topic). To run weekly, uncomment the `schedule:` block in the workflow.

**Local test (no model):**

```bash
pip install -r automation/scripts/requirements.txt
python automation/scripts/generate_azure_post.py --dry-run        # writes a stub post
bundle exec jekyll build                                          # confirm it builds
git checkout -- _posts automation/azure-memories.md               # discard the stub
```

---

## Option B — Azure Automation runbook (Azure-native)

`runbooks/Publish-AzureBlogPost.ps1` generates the post and opens a PR via the GitHub API.

**Setup**

1. **Automation account** with a **system-assigned managed identity**; import Az modules
   `Az.Accounts` and `Az.KeyVault`.
2. **Key Vault** secrets (grant the identity *get* on secrets):
   - `gh-pat-blog` — fine-grained GitHub PAT scoped to this repo with
     **Contents: read/write** and **Pull requests: read/write**.
   - `aoai-api-key` — Azure OpenAI key.
3. **Automation variables:** `KeyVaultName`, `AoaiEndpoint`, `AoaiDeployment`
   (owner/repo default to `j00x/apremote.github.io`).
4. Import the `.ps1` as a **PowerShell runbook**, publish it, and attach a **schedule**
   (e.g. weekly).

---

## Reusing for the Health briefing

The same patterns work for the daily Health briefing — point the generator/runbook at
`health-briefing-agent.md` + `memories.md` and write `health/briefings/YYYY-MM-DD.json`
plus prepend `health/index.json` (instead of a `_posts/*.md` file). Ask and this can be
cloned for health too.
