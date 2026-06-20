# Glassmorphism Personal Site — Implementation Plan

> **For agentic workers:** Implement task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This is a static GitHub Pages site, so verification is build + serve + visual check rather than unit tests.

**Goal:** Build Adam Pratt's personal GitHub Pages site — a glassmorphism / neon dark-mode site with a Home landing, an Azure blog, an automation-fed daily Health research briefing reader, and an About page.

**Architecture:** Jekyll renders the shell + blog (markdown `_posts`); the Health section is rendered client-side from JSON written by an external automation. Deployed via the existing `jekyll-gh-pages.yml` workflow on the project-page subpath `/apremote.github.io/`.

**Tech Stack:** Jekyll (safe-mode, no custom plugins), HTML, CSS (custom design system, `backdrop-filter` glass), vanilla JS (nav, motion, a minimal markdown renderer for briefing bodies). No runtime third-party dependencies.

Spec: `docs/superpowers/specs/2026-06-20-personal-site-glassmorphism-design.md`

---

## File Structure

```
_config.yml                      # Jekyll config: title, baseurl, url, collections off
Gemfile                          # local-only: github-pages gem for `jekyll serve`
_layouts/
  default.html                   # base: head, animated bg, nav, footer
  page.html                      # simple content page wrapper
  post.html                      # blog post reading layout
_includes/
  head.html                      # meta, fonts, css; optional noindex
  nav.html                       # frosted sticky nav
  background.html                # animated gradient mesh layers
  social.html                    # social link row
assets/
  css/style.css                  # full design system + components
  js/main.js                     # nav toggle, scroll reveal, reduced-motion
  js/markdown.js                 # minimal markdown -> HTML
  js/health.js                   # fetch index.json + briefing, render reader
index.html                       # Home (hero, latest post card, today's briefing card, social)
about.md                         # About (bio, skills, contact)
azure/index.html                 # blog index (loops site.posts)
health/index.html                # briefing reader (noindex)
health/README.md                 # automation JSON contract
health/index.json                # archive manifest (seed)
health/briefings/2026-06-20.json # seed briefing (latest)
health/briefings/2026-06-19.json # seed briefing (archive)
_posts/2026-06-20-azure-landing-zones-quickstart.md   # sample how-to
_posts/2026-06-13-lessons-learned-bicep-modules.md     # sample lessons-learned
404.html                         # styled not-found
```

---

## Task 1: Jekyll config + base layout + design tokens

**Files:** Create `_config.yml`, `Gemfile`, `_includes/head.html`, `_includes/background.html`, `_includes/nav.html`, `_layouts/default.html`, `assets/css/style.css`, `assets/js/main.js`, `index.html` (placeholder hero).

- [ ] **Step 1:** Write `_config.yml` with `title`, `description`, `url: "https://j00x.github.io"`, `baseurl: "/apremote.github.io"`, `author`, social handles, and `exclude` for docs/Gemfile.
- [ ] **Step 2:** Write `Gemfile` pinning `gem "github-pages", group: :jekyll_plugins` for faithful local builds.
- [ ] **Step 3:** Build `_includes/head.html` (charset/viewport, title, description, Google Fonts Inter, link to `style.css` via `relative_url`, optional `{% if page.noindex %}<meta name="robots" content="noindex">{% endif %}`).
- [ ] **Step 4:** Build `_includes/background.html` (fixed gradient-mesh blobs) and `_includes/nav.html` (frosted sticky nav: Home/Azure/Health/About using `relative_url`, mobile hamburger).
- [ ] **Step 5:** Build `_layouts/default.html` wiring head + background + nav + `{{ content }}` + footer + scripts.
- [ ] **Step 6:** Write `assets/css/style.css` design system: CSS variables (`--bg`, glass fills, neon accents, radii), base/reset, animated mesh keyframes (gated by `prefers-reduced-motion`), nav, glass card/panel, buttons, typography.
- [ ] **Step 7:** Write `assets/js/main.js` (mobile nav toggle; IntersectionObserver scroll-reveal that no-ops under reduced-motion).
- [ ] **Step 8:** Write a minimal `index.html` (`layout: default`) with just the hero to validate the shell.
- [ ] **Step 9 (verify):** `bundle exec jekyll build` succeeds; `bundle exec jekyll serve` and load home — hero + nav + animated background render with correct subpath links.
- [ ] **Step 10:** Commit.

## Task 2: Home page

**Files:** Modify `index.html`; create `_includes/social.html`.

- [ ] **Step 1:** Build `_includes/social.html` (GitHub/LinkedIn glass icon-buttons from `_config.yml`).
- [ ] **Step 2:** Hero: "Adam Pratt" with neon glow + gradient subtitle "Cloud Architect · DevOps Engineer · Developer" + social row + CTA buttons (Read the blog / Today's briefing).
- [ ] **Step 3:** "Latest Azure post" glass card via Liquid `{% assign p = site.posts.first %}` linking to the post.
- [ ] **Step 4:** "Today's Briefing" glass card with a placeholder `<div id="home-briefing">` populated by `health.js` (latest topics teaser), link to Health.
- [ ] **Step 5 (verify):** Serve; home shows hero, social links, latest-post card (after Task 4 posts exist), briefing teaser slot.
- [ ] **Step 6:** Commit.

## Task 3: Page + post layouts, About, 404

**Files:** Create `_layouts/page.html`, `_layouts/post.html`, `about.md`, `404.html`.

- [ ] **Step 1:** `_layouts/page.html` — centered glass content container for markdown pages.
- [ ] **Step 2:** `_layouts/post.html` — post header (title, date, tags), glass reading container, dark-themed code block styling, "back to Azure" link.
- [ ] **Step 3:** `about.md` (`layout: page`) — bio, skills grid (Azure/DevOps/Dev), contact.
- [ ] **Step 4:** `404.html` — styled glass not-found with home link.
- [ ] **Step 5 (verify):** Serve; About renders; visiting a bad URL shows styled 404.
- [ ] **Step 6:** Commit.

## Task 4: Azure blog (index + sample posts)

**Files:** Create `azure/index.html`, `_posts/2026-06-20-azure-landing-zones-quickstart.md`, `_posts/2026-06-13-lessons-learned-bicep-modules.md`.

- [ ] **Step 1:** `azure/index.html` (`layout: page`) — intro + grid of post cards looping `site.posts` (title, date, category badge how-to/lessons-learned, summary, tags).
- [ ] **Step 2:** Write sample how-to post (front matter: title/date/category: how-to/tags/summary) with real Azure landing-zone content incl. a fenced code block.
- [ ] **Step 3:** Write sample lessons-learned post similarly (Bicep modules).
- [ ] **Step 4 (verify):** Serve; `/azure/` lists both posts as cards; each opens a styled post page with highlighted code.
- [ ] **Step 5:** Commit.

## Task 5: Health briefing data contract + seed data

**Files:** Create `health/README.md`, `health/index.json`, `health/briefings/2026-06-20.json`, `health/briefings/2026-06-19.json`.

- [ ] **Step 1:** Write `health/index.json` with a `briefings` array (2026-06-20 then 2026-06-19).
- [ ] **Step 2:** Write `health/briefings/2026-06-20.json` with all five topic sections (Anti-Aging, HIIT for Women, Pelvic Floor, Alternative Cancer Treatments, Sleep), each with markdown `body` and 1–2 structured `sources`.
- [ ] **Step 3:** Write `health/briefings/2026-06-19.json` (a different day) for archive testing.
- [ ] **Step 4:** Write `health/README.md` documenting the exact JSON contract + the two files the automation must write/prepend.
- [ ] **Step 5 (verify):** `python -m json.tool` validates each JSON file.
- [ ] **Step 6:** Commit.

## Task 6: Health reader (markdown renderer + fetch/render + archive)

**Files:** Create `health/index.html`, `assets/js/markdown.js`, `assets/js/health.js`.

- [ ] **Step 1:** `assets/js/markdown.js` — minimal renderer: headings, bold/italic, inline code, links (rendered with `target=_blank rel=noopener`), ordered/unordered lists, paragraphs; escape HTML first.
- [ ] **Step 2:** `health/index.html` (`layout: default`, `noindex: true`) — header (title + date pill + archive control), disclaimer banner, `#briefing-sections` container, `#archive-list` sidebar; passes `baseurl` to JS via a `data-baseurl` attribute.
- [ ] **Step 3:** `assets/js/health.js` — fetch `index.json`, build archive list, load latest (or selected date), render each section into a glass panel (topic + markdown body + citation chips), handle empty/error states; also populate `#home-briefing` teaser when present.
- [ ] **Step 4 (verify):** Serve; `/health/` loads latest briefing with five panels + citation chips + disclaimer; clicking an archive date swaps to 2026-06-19; home teaser shows topics.
- [ ] **Step 5:** Commit.

## Task 7: Polish, responsive, accessibility, final verification

**Files:** Modify `assets/css/style.css`, `assets/js/main.js` as needed.

- [ ] **Step 1:** Responsive passes at ~375px (phone) and desktop: nav collapses, panels stack, type scales.
- [ ] **Step 2:** Accessibility: focus-visible states, aria-labels on icon buttons/nav toggle, contrast check on glass text.
- [ ] **Step 3:** Confirm `prefers-reduced-motion` disables mesh animation + scroll reveal.
- [ ] **Step 4 (verify):** Full `bundle exec jekyll build`; manual GUI test (desktop + phone width) across Home, Azure index+post, Health latest+archive; capture screenshots + demo video.
- [ ] **Step 5:** Commit.

---

## Self-Review

- **Spec coverage:** §3 approach (Jekyll blog + JSON health) → Tasks 1/4/5/6; §4 design system → Task 1/7; §5 nav/structure → Tasks 1–6; §6 blog → Task 4; §7 automation contract → Task 5; §8 disclaimer + noindex → Task 6/Task 1 head; §9 build/baseurl → Task 1; §10 testing → Task 7. All covered.
- **Placeholders:** none — each task names exact files and concrete behavior.
- **Consistency:** `index.json`/`briefings/*.json` shapes match the spec; `markdown.js` + `health.js` + `health/index.html` interfaces align (`data-baseurl`, `#briefing-sections`, `#archive-list`, `#home-briefing`).
