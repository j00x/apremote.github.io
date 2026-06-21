# AGENTS.md

## Cursor Cloud specific instructions

This repo is the **`apremote.github.io`** Jekyll site (a GitHub Pages *project* site served at
`/apremote.github.io/`). It is a personal site for "Adam Pratt" with weekly Azure blog posts
(`_posts/`), a client-side Health briefing page (`health/`), and content-generation automation
(`automation/`). Production builds run via GitHub Actions (`.github/workflows/jekyll-gh-pages.yml`);
local dev uses Jekyll directly.

### Services / how to run

- **Jekyll site (local dev):** `bundle exec jekyll serve --host 0.0.0.0 --port 4000 --livereload`
  - Because `baseurl: "/apremote.github.io"`, the site is served at
    **`http://localhost:4000/apremote.github.io/`** (not the bare `/`). The bare root returns 404 —
    this is expected; always include the baseurl path.
  - `--livereload`/`--watch` auto-regenerates on file changes (including new `_posts/*.md`).
- **Build only:** `bundle exec jekyll build` (output in `_site/`, gitignored).
- **Azure post generator (`automation/scripts/generate_azure_post.py`):** real runs need
  `AZURE_OPENAI_*` env vars, but `--dry-run` writes a stub post offline with no model/secrets —
  use it to exercise the publish pipeline locally. It mutates `_posts/` and appends to
  `automation/azure-memories.md`; revert with `git checkout -- _posts automation/azure-memories.md`
  and delete any new stub file under `_posts/`.

### Non-obvious notes

- Ruby (3.2), Bundler, and the Jekyll gems are baked into the VM snapshot; the startup update
  script runs `bundle install` (into `vendor/bundle`, gitignored) and `pip install` for the
  automation deps. There is no committed `Gemfile.lock` (gitignored), so `bundle install` resolves
  fresh.
- The **Health page is fully static**: JS in `assets/js/health.js` fetches JSON from `health/` at
  runtime. To publish a briefing, add `health/briefings/YYYY-MM-DD.json` and prepend it to
  `health/index.json` (see `health/README.md`). No rebuild logic beyond Jekyll copying the files.
- There is **no automated test suite or linter**; "verification" = a clean `bundle exec jekyll build`
  plus loading pages from the dev server.
- The custom domain `learn.apnet-remote.net` belongs to the sibling **`j00x.github.io`** user-site
  repo. Do **not** add a `CNAME` here.
