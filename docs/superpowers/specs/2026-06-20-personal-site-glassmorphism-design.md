# Personal Site Design — Adam Pratt (apremote.github.io)

**Date:** 2026-06-20
**Status:** Approved (design) — pending spec review before implementation planning
**Owner:** Adam Pratt — Cloud Architect · DevOps Engineer · Developer
**Repo:** `j00x/apremote.github.io` — a **project site** under the `j00x.github.io` user site (which owns the custom domain `learn.apnet-remote.net`). Served at `https://learn.apnet-remote.net/apremote.github.io/`, so `baseurl: "/apremote.github.io"` and **no `CNAME`** in this repo.

---

## 1. Goal

Build a fun, modern, aesthetically pleasing personal site on GitHub Pages with a
**glassmorphism / neon dark-mode** aesthetic. The site serves three purposes:

1. **Identity / landing** — who Adam is, with social links.
2. **Azure blog** — weekly Azure cloud-architecture how-to walkthroughs and lessons learned.
3. **Health** — a dedicated section that displays a **daily medical-research briefing**
   produced by an external automation, plus a dated archive of past briefings.

## 2. Constraints & context

- **Static hosting only.** GitHub Pages cannot run server-side code or a database.
  Any "dynamic" content must arrive via a commit (push) or be fetched client-side from a
  static file or public API.
- **Project site under a user site.** The custom domain `learn.apnet-remote.net` is owned
  by the `j00x.github.io` user-site repo (served at the domain root). This repo is a
  separate project site served at the `/apremote.github.io/` subpath, so `baseurl` is
  `/apremote.github.io` and this repo must **not** contain a `CNAME` file. All asset and
  internal links use `site.baseurl` (via `relative_url`) so they resolve under the subpath.
- **Existing pipeline.** `.github/workflows/jekyll-gh-pages.yml` already builds with
  `actions/jekyll-build-pages` (Jekyll in safe mode — **no custom plugins**) and deploys
  to Pages. We keep this workflow.

## 3. Chosen approach (Approach 2)

**Jekyll for the blog + structured JSON for the health briefing.**

- The **blog** uses Jekyll markdown posts — the natural fit for long technical walkthroughs.
- The **health briefing** is rendered **client-side from structured JSON** that the
  automation writes into the repo. This keeps the automation's contract trivial (emit a
  JSON file) and decouples briefing content from Jekyll's templating.

Approaches considered and rejected:
- **Approach 1 (everything markdown/Jekyll):** every briefing forces a full rebuild and the
  automation must author markdown with front matter. Heavier contract for the automation.
- **Approach 3 (GitHub Issues as CMS, fetched via API):** subject to unauthenticated API
  rate limits (60/hr per visitor IP), weaker SEO, more fragile runtime dependency.

## 4. Visual design system

- **Aesthetic:** glassmorphism / neon dark mode (reference mockups produced during
  brainstorming: hero landing + health briefing reader).
- **Tokens:**
  - Background: near-black charcoal `#0a0a14` with a subtle, slowly animated blurred
    gradient mesh (deep purple / electric cyan / magenta / teal glows).
  - Glass surfaces: translucent fills (`rgba(255,255,255,0.05–0.08)`) with
    `backdrop-filter: blur(...)`, thin glowing 1px borders, soft drop shadows, and a faint
    inner highlight.
  - Accents: neon cyan, purple, and teal (teal/green leaning for the Health section).
  - Typography: clean modern sans-serif (e.g. Inter / system UI stack) with letter-spaced
    subtitles; subtle text glow on the hero.
  - Radii: generously rounded corners on cards/panels.
- **Motion:** subtle entrance fades/slide-ins, gentle animated background mesh, glow on
  hover. **Must respect `prefers-reduced-motion`.**
- **Responsive:** phone-first, since the daily briefing is meant to be read on a phone in
  bed. Verified down to ~375px width.
- **Accessibility:** sufficient contrast for body text over glass, focus states on
  interactive elements, semantic HTML.

## 5. Site structure & navigation

Frosted-glass sticky top nav: **Home · Azure · Health · About**

- **Home** — hero (name "Adam Pratt" + title "Cloud Architect · DevOps Engineer · Developer"),
  a "Latest Azure post" card, a "Today's Briefing" card, and social links
  (GitHub, LinkedIn, etc.).
- **Azure** — blog index (cards) + individual post pages. Holds both `how-to` and
  `lessons-learned` posts. (Nav label is "Azure"; content includes how-tos and lessons learned.)
- **Health** — latest briefing reader + dated archive. `noindex` (not search-indexed) but
  reachable by direct link.
- **About** — bio, skills, contact.

## 6. Blog (Azure)

- Standard Jekyll posts at `_posts/YYYY-MM-DD-title.md`.
- Front matter: `title`, `date`, `tags`, `category` (`how-to` | `lessons-learned`),
  `summary`, optional `hero` image.
- Code blocks: syntax highlighting themed for the dark glass aesthetic.
- Index page renders posts as glass cards (title, date, summary, tags); post pages render
  full markdown with a styled reading layout.

## 7. Health briefing — automation contract

The automation produces a **medical-research digest** each morning with one section per
research topic and source citations. Topics (from the automation's spec):

- Anti-Aging (supplements, devices, topicals, procedures, regimens)
- HIIT workouts for women
- Pelvic floor exercises
- Alternative treatments for cancers (e.g. Breast Cancer HER2+, P53 gene)
- Sleep — studies, best practices, and supplements for restless/disjointed sleep

### Files the automation writes

- **`/health/briefings/YYYY-MM-DD.json`** — one file per day (the briefing).
- **`/health/index.json`** — an archive manifest; the automation **prepends** a new entry
  each day so the newest is first.

### Briefing JSON shape

Section bodies are **markdown** so the agent can write rich prose with inline links;
sources are structured so they render as citation chips.

```json
{
  "date": "2026-06-20",
  "title": "Daily Health Briefing",
  "intro": "optional short summary",
  "sections": [
    {
      "topic": "Anti-Aging",
      "body": "markdown text of findings…",
      "sources": [
        { "title": "Study title", "publisher": "PubMed", "url": "https://…", "date": "2026-06-18" }
      ]
    },
    { "topic": "HIIT Workouts for Women", "body": "…", "sources": [] },
    { "topic": "Pelvic Floor Exercises", "body": "…", "sources": [] },
    { "topic": "Alternative Cancer Treatments", "body": "…", "sources": [] },
    { "topic": "Sleep — Studies & Best Practices", "body": "…", "sources": [] }
  ]
}
```

### index.json shape

```json
{
  "briefings": [
    { "date": "2026-06-20", "title": "Daily Health Briefing" },
    { "date": "2026-06-19", "title": "Daily Health Briefing" }
  ]
}
```

### Rendering behavior

- On load, the Health page fetches `index.json`, builds the archive list, and loads the
  most recent briefing (or a date selected from the archive).
- Each section renders into a glass panel: topic heading + small glowing icon, the body
  (markdown → HTML via a tiny client-side renderer), and a row of pill-shaped **citation
  chips** linking to each source (publisher label + link icon).
- A **date picker / archive sidebar** lets the reader open any past day.
- Graceful empty/error states (e.g. "No briefing yet for today").

### Deliverables to support the automation

- A **sample briefing JSON** + matching `index.json` committed as seed/demo data.
- A short **README** in `/health/` documenting the exact JSON contract so the automation
  can target it precisely.

## 8. Safety & privacy decisions

- **Medical disclaimer:** the Health section displays a tasteful disclaimer
  ("Informational only — not medical advice; consult a qualified professional").
- **Search indexing:** the Health section is `noindex` (e.g. `<meta name="robots"
  content="noindex">` and/or robots rules) so it is not surfaced by search engines, while
  remaining reachable by direct link. (Default decision — can be changed to fully public.)

## 9. Build & deploy

- Keep the existing `jekyll-gh-pages.yml` workflow (push to `main` → build → deploy).
- Configure `_config.yml` with `baseurl: "/apremote.github.io"` and `url:
  "https://learn.apnet-remote.net"`. Do not add a `CNAME` (the domain is owned by the
  `j00x.github.io` user site).
- JSON files under `/health/` are served as static assets (copied as-is by the Jekyll build)
  and fetched client-side.

## 10. Testing plan

- Build the Jekyll site locally and serve it.
- **Manual GUI testing** (screenshots + a demo video) covering:
  - Home hero + cards + social links.
  - A sample Azure post (index card → full post page).
  - The Health briefing reader loading the latest sample day and switching to an archived day.
- Verify on **desktop and a phone-width viewport (~375px)**.
- Verify `prefers-reduced-motion` disables non-essential motion.
- Confirm links/assets resolve under the `/apremote.github.io/` subpath.

## 11. Out of scope (YAGNI)

- No comments system, analytics, or newsletter signup (can be added later).
- No authentication / private content (site is public; Health is `noindex` only).
- The automation itself is **not** built here — only the JSON contract + sample data + reader.
