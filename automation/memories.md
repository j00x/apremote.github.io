# Memories — Health Briefing Agent

> Long-term memory for the Daily Health Briefing automation. **Read this at the start of
> every run.** It holds who the briefing is for, the standing topics, the voice, and the
> rules learned over time. When something durable changes (a new topic, a preference, a
> correction), update the relevant section here so future runs stay consistent.

_Last updated: 2026-06-20_

## Who this is for

- **Owner / publisher:** Adam Pratt — Cloud Architect, DevOps Engineer, Developer.
- **Primary reader:** Adam's wife. She reads the briefing **first thing in the morning, on
  her phone, in bed**, after Adam leaves for work.
- **Implication for voice:** warm, calm, encouraging, and easy to skim half-awake. Lead with
  the practical takeaway. No jargon dumps, no fear-mongering.

## Mission

Each morning, scan reputable medical literature and publish a concise **Daily Health
Briefing** to the website, with one section per standing topic and real source citations.

- **Live page:** https://learn.apnet-remote.net/apremote.github.io/health/
- **How it's published:** write JSON files into the `health/` folder of repo
  `j00x/apremote.github.io` and push to `main` (auto-deploys). Full steps in
  `automation/health-briefing-agent.md`.

## Standing topics (canonical list)

Keep this list authoritative. Produce one section per topic, in this order:

1. **Anti-Aging** — supplements, devices, topicals, procedures, regimens. (icon: `sparkle`)
2. **HIIT workouts for women.** (icon: `bolt`)
3. **Pelvic floor exercises.** (icon: `anchor`)
4. **Alternative treatments for cancers** — Breast Cancer HER2+, TP53/p53, related advances.
   (icon: `ribbon`)
5. **Sleep** — studies, best practices for restless/disjointed sleep, supplements. (icon: `moon`)

> To add/remove a topic, edit this list. The agent should follow whatever is here.

## Voice & style (learned preferences)

- Warm morning greeting in the `intro` (e.g., "Good morning! Here's today's digest…").
- Short paragraphs; use **bold** for key terms; use bullet or numbered lists for takeaways.
- ~60–150 words per section. Skimmable beats exhaustive.
- State the evidence strength plainly (RCT / review / observational / preclinical).
- Encouraging and practical, never alarmist.

## Hard rules (do not break)

- **Never fabricate** a study, journal, statistic, or URL. Cite only sources you actually
  found; verify URLs resolve.
- Prefer sources from the **last 12–18 months**; flag older guidance as such.
- **Cancer / serious conditions:** present options as **evidence-based and to be discussed
  with a clinician** — never as replacements for standard care, never as personal advice.
- The page already carries a medical disclaimer and is `noindex`; don't re-add those.
- Public site: assume anything published is publicly visible.

## Repo / format facts (quick reference)

- Repo `j00x/apremote.github.io` (a **project site** under the `j00x.github.io` user site).
- Files to write each run:
  - `health/briefings/YYYY-MM-DD.json` — the day's briefing.
  - `health/index.json` — prepend `{ "date": "...", "title": "Daily Health Briefing" }`.
- `body` is **Markdown**; sources render as citation chips.
- Allowed icons: `sparkle`, `bolt`, `anchor`, `ribbon`, `moon`, `pulse`.
- Full schema + publishing steps: `automation/health-briefing-agent.md` and `health/README.md`.

## Running log (append durable notes here)

- **2026-06-20** — First real briefing published (Anti-Aging: urolithin A immune RCT &
  taurine-biomarker doubt; HIIT meta-analysis; pelvic floor PFMT meta-analysis; HER2+
  DESTINY-Breast09 / TP53 rezatapopt; sleep CBT-I vs magnesium/melatonin). Established the
  warm-morning voice and the 5-topic structure above.
<!-- Add new entries as preferences/topics evolve, e.g.:
- YYYY-MM-DD — Adam asked to add "longevity wearables" as topic 6 (icon: pulse).
- YYYY-MM-DD — Reader prefers metric units; keep summaries under 120 words.
-->
