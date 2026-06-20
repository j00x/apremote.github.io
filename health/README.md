# Health Briefing — Automation Contract

This folder powers the **Health** page. The page is fully static: it reads JSON files
from this folder client-side and renders them. To publish a new daily briefing, your
automation only needs to **write two files** (both via a normal git commit/push to the
`main` branch — that push triggers the GitHub Pages rebuild automatically).

## 1. Write the day's briefing

Create `health/briefings/YYYY-MM-DD.json`:

```json
{
  "date": "2026-06-20",
  "title": "Daily Health Briefing",
  "intro": "Optional one-line greeting or summary (string, optional).",
  "sections": [
    {
      "topic": "Anti-Aging",
      "icon": "sparkle",
      "body": "Markdown string. Supports **bold**, *italic*, `code`, [links](https://example.com), and - bullet / 1. numbered lists.",
      "sources": [
        { "title": "Study title", "publisher": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/...", "date": "2026-06-18" }
      ]
    }
  ]
}
```

### Field reference

| Field | Required | Notes |
|-------|----------|-------|
| `date` | yes | `YYYY-MM-DD`. Must match the filename. |
| `title` | no | Defaults to "Daily Health Briefing". |
| `intro` | no | Short greeting shown above the sections. |
| `sections[]` | yes | One entry per topic. |
| `sections[].topic` | yes | Heading text. |
| `sections[].icon` | no | One of: `sparkle`, `bolt`, `anchor`, `ribbon`, `moon`, `pulse`. Defaults to `pulse`. |
| `sections[].body` | yes | Markdown (rendered to HTML). |
| `sections[].sources[]` | no | Citation chips. |
| `sources[].title` | yes (if source present) | Tooltip / accessible label. |
| `sources[].publisher` | yes (if source present) | Chip label, e.g. `PubMed`, `JAMA`, `NIH`, `Medscape`. |
| `sources[].url` | yes (if source present) | Link target (opens in new tab). |
| `sources[].date` | no | Source date. |

## 2. Update the archive manifest

Prepend the new day to the top of `health/index.json` so it becomes the default
("latest") briefing and appears in the archive list:

```json
{
  "briefings": [
    { "date": "2026-06-20", "title": "Daily Health Briefing" },
    { "date": "2026-06-19", "title": "Daily Health Briefing" }
  ]
}
```

The first entry in `briefings` is shown by default; the rest populate the archive.

## Notes

- The body is **Markdown**, not HTML — write naturally and include source links inline
  if you like (sources also render as chips).
- All content is **public** (this is a public GitHub Pages site), though the Health page
  is marked `noindex` so search engines won't list it.
- Content is informational only and is shown with a medical disclaimer.
