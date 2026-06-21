# Cursor automation prefill payloads

These JSON files are **prefillWorkflowData** payloads for the Cursor Automations editor
(`open_automation` / Agents window → Automations → New automation).

They are not used by GitHub Actions. Import them when creating the two scheduled cloud agents
described in `automation/README.md` → Option C.

| File | Schedule | Purpose |
|------|----------|---------|
| `azure-weekly.json` | `0 13 * * 1` (Mon 13:00 UTC) | Weekly Azure blog post → review PR |
| `health-daily.json` | `0 10 * * *` (daily 10:00 UTC) | Daily Health briefing → review PR |

## How to import

1. Open the **Agents** window in Cursor (or go to [cursor.com/automations](https://cursor.com/automations)).
2. Create a **New automation**.
3. If your session supports it, ask the agent to run `/automate` and paste the contents of
   one JSON file as `prefillWorkflowData`, or copy fields manually:
   - **Name / description** from the JSON root
   - **Trigger** → cron from `workflow.triggers[0].cron.cron`
   - **Repository** → `workflow.gitConfig.repo` + `workflow.gitConfig.branch`
   - **Instructions** → `workflow.prompts[0]`
   - **Memories** → off (`memoryEnabled: false` in the prefill)
4. Save the automation, then **Run now** once to validate the draft PR flow before relying on
   the schedule.

Both automations target **`j00x/apremote.github.io`** on branch **`main`**.
