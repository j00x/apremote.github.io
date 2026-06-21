# Cursor Agent Automation prompts

Paste-ready prompts for running the two content automations as **Cursor Agent Automations**
(scheduled cloud agents) instead of — or alongside — the GitHub Actions + Azure OpenAI
generators. See `automation/README.md` → "Option C" for why this is the recommended path and
how to set it up.

Each automation is configured in the Cursor UI (Agents window, `cursor.com/automations`, or the
`/automate` skill), **not** committed to this repo. Copy the matching prompt into the
automation's instructions, set the schedule, and scope it to the **`j00x/apremote.github.io`**
repository with base branch **`main`**.

> The heavy lifting (topics, voice, schema, safety rules, publishing steps) already lives in the
> `*-agent.md` + memory files. These prompts just point the agent at them, insist on **real,
> web-verified sources**, and ask for a **review PR**.

---

## Daily Health Briefing — schedule: daily (e.g. cron `0 10 * * *`)

```text
You are the Daily Health Briefing agent for the repo j00x/apremote.github.io.

1. Read automation/health-briefing-agent.md and automation/memories.md and follow them exactly
   (standing topics, order, icons, voice, and the JSON data contract).
2. Research the WEB for recent (prefer the last 12–18 months), reputable findings for each
   standing topic (PubMed/PMC, JAMA/NEJM/Nature/Lancet, NIH, ClinicalTrials.gov, society
   guidance, Medscape). Only cite sources you actually opened and read, and VERIFY each URL
   resolves. Never invent a title, journal, statistic, or URL.
3. Write health/briefings/<YYYY-MM-DD>.json for today (UTC) and PREPEND today's
   {date, title} entry to health/index.json, per the contract.
4. Validate: `python3 -m json.tool` both files; confirm `date` matches the filename.
5. Open a pull request titled "health: briefing for <YYYY-MM-DD>" with the two files. Do NOT
   push directly to main — this content is reviewed before publishing.

Honor every hard rule in the instructions, especially: be conservative about evidence level,
frame cancer/serious-condition options as "discuss with a clinician" (never as replacements for
standard care), and don't fabricate anything.
```

---

## Weekly Azure post — schedule: weekly (e.g. cron `0 13 * * 1`)

```text
You are the Azure Blog agent for the repo j00x/apremote.github.io.

1. Read automation/azure-blog-agent.md and automation/azure-memories.md and follow them exactly
   (post types, voice, front-matter contract, and the running log / topic backlog).
2. Pick ONE topic from the backlog that is NOT already in the running log, alternating
   how-to / lessons-learned based on the most recent shipped post. Confirm it isn't a duplicate
   by checking _posts/ and the running log.
3. Research the WEB to keep the post technically correct and current — use real Azure resource
   types, current API versions, and valid CLI/Bicep; cite Microsoft Learn / Azure Architecture
   Center where it helps and VERIFY links resolve. Never embed secrets; prefer managed identity
   + Key Vault + least privilege.
4. Write _posts/<YYYY-MM-DD>-<slug>.md with valid front matter (title, category, tags, summary)
   and a Markdown body with language-tagged, runnable code blocks and a wrap-up.
5. Validate with `bundle exec jekyll build` (must succeed). Append the post to the running log
   in automation/azure-memories.md so it isn't repeated.
6. Open a pull request titled "azure: <title>" with the post and the memories update. Do NOT
   push directly to main — posts are reviewed before publishing.
```

---

## Notes / gotchas

- **Scope the repo explicitly.** Scheduled automations default to *no repository*; attach the
  single repo + `main` so the agent can write files and open the PR.
- **Web access:** cloud agents have internet by default. If your team enforces a network
  allowlist, allowlist your research domains (pubmed, nih, nature, nejm, microsoft learn, …).
- **Review PR (not direct push):** matches this repo's convention. Merging the PR triggers the
  GitHub Pages rebuild/deploy automatically.
- **Prompt-injection awareness:** these agents ingest untrusted web pages and auto-run commands.
  Keep the repo free of secrets (it already is) and consider keeping automation "Memories" off
  or curated so a malicious page can't poison future runs.
- **Cost/timing:** automations run in Max Mode and are billed per run; scheduled runs are
  best-effort (never early, may be slightly late).
