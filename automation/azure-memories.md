# Memories — Azure Blog Agent

> Long-term memory for the Azure blog automation. **Read this at the start of every run.**
> It holds the audience, the post-type rotation, the topic backlog, the voice, and the rules
> learned over time. When something durable changes (a new preference, a published topic, a
> correction), update the relevant section here so future runs stay consistent.

_Last updated: 2026-06-21_

## Who this is for

- **Author / publisher:** Adam Pratt — Cloud Architect, DevOps Engineer, Developer.
- **Audience:** practitioners — cloud/DevOps engineers and architects who want practical,
  runnable Azure guidance.
- **Implication for voice:** senior-engineer, practical, lightly conversational, opinionated
  but honest about trade-offs. No marketing tone, no buzzword soup.

## Mission

Publish a focused **Azure** article on a **weekly** cadence — alternating **how-to
walkthroughs** and **lessons-learned** pieces — to the site's Azure section.

- **Live section:** https://learn.apnet-remote.net/apremote.github.io/azure/
- **How it's published:** write a Markdown post into `_posts/` of repo
  `j00x/apremote.github.io` and push to `main` (auto-deploys). Full steps in
  `automation/azure-blog-agent.md`.

## Cadence & rotation

- Target **one post per week**.
- **Alternate** post types: `how-to` one week, `lessons-learned` the next (adjust if a topic
  clearly fits one type). Keep it varied.

## Topic backlog (edit freely)

Pull from here, then move shipped items to the running log. Add new ideas any time.

- how-to: Hub-and-spoke networking with Bicep (Azure Firewall + peering)
- how-to: Policy-as-code pipeline (deploy Azure Policy via GitHub Actions / Bicep)
- how-to: Workload identity federation for GitHub Actions → Azure (no secrets)
- how-to: Private endpoints + Private DNS for PaaS (Storage / Key Vault)
- how-to: Cost guardrails — budgets, anomaly alerts, and tag policies
- lessons-learned: Bicep module registry at scale (already shipped — see log)
- lessons-learned: Landing Zone management-group design that survives reorgs
- lessons-learned: Migrating to Azure Container Apps from App Service
- lessons-learned: What changed moving to Aurora-style distributed SQL / Azure DSQL

## Voice & style (learned preferences)

- Open by framing the concrete outcome and prerequisites.
- Use `##`/`###` headings and short sections; **bold** key terms.
- Always include **language-tagged, runnable code** (`bicep`, `bash`, `powershell`, `yaml`,
  `hcl`, etc.). Prefer Bicep and Azure CLI; show Terraform when relevant.
- Security by default: managed identity, Key Vault references, least privilege; never embed
  secrets.
- Close with a short **wrap-up / next steps**.
- ~600–1,200 words is a good range; depth over padding.

## Hard rules (do not break)

- **Code must be correct and runnable.** Real resource types, current API versions, valid CLI.
- **No secrets** in code or output. Recommend managed identity + Key Vault.
- Cite **Microsoft Learn / Azure Architecture Center** where it helps.
- Be honest about cost, limits, and trade-offs.
- **No duplicate topics** — check `_posts/` and the running log first.
- `category` front-matter must be exactly `how-to` or `lessons-learned`.

## Repo / format facts (quick reference)

- Repo `j00x/apremote.github.io` (a **project site** under the `j00x.github.io` user site).
- File to write each run: `_posts/YYYY-MM-DD-<slug>.md` (front matter + Markdown). No manifest.
- Required front matter: `title`, `category` (`how-to`|`lessons-learned`), `tags`, `summary`.
- Post URL: `/apremote.github.io/azure/YYYY/MM/DD/<slug>/`.
- Full schema + publishing steps (incl. running from Azure via the GitHub Contents API):
  `automation/azure-blog-agent.md`.

## Running log (append shipped posts here)

- **2026-06-21** — `how-to`: "Dry Run Sample Post" (`_posts/2026-06-21-dry-run-sample-post.md`).
- **2026-06-20** — `how-to`: "Azure Landing Zones: A Pragmatic Quickstart"
  (`_posts/2026-06-20-azure-landing-zones-quickstart.md`).
- **2026-06-13** — `lessons-learned`: "Scaling Bicep Modules Without the Pain"
  (`_posts/2026-06-13-lessons-learned-bicep-modules.md`).
<!-- Append each new post: date — category: "title" (filename). Keeps topics from repeating. -->
