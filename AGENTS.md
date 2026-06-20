# AGENTS.md

## Cursor Cloud specific instructions

This repository (`apremote.github.io`) is a **Jekyll static site** deployed to GitHub Pages
via `.github/workflows/jekyll-gh-pages.yml` (`actions/jekyll-build-pages`). There is no
backend/service — the only "application" is the Jekyll site itself.

### Services / how to run

- **Dev server:** `bundle exec jekyll serve --host 0.0.0.0 --port 4000 --livereload`
  serves the site at `http://localhost:4000` with auto-regeneration on file changes.
- **Build (also the closest thing to a CI/lint check):** `bundle exec jekyll build`
  outputs the static site to `_site/`. The GitHub Actions workflow performs the equivalent
  build, so a clean `jekyll build` is the signal that a change is deploy-safe.
- There are **no automated tests** in this repo.

### Non-obvious gotchas

- Local builds use the **`github-pages` gem** (currently pins Jekyll 3.10.x) for parity with
  the GitHub Pages deploy action. Do not assume the latest standalone Jekyll behavior.
- Gems are installed **project-locally** into `vendor/bundle` (`bundle config set --local path vendor/bundle`)
  because the system gem directory (`/var/lib/gems`) is not user-writable. `vendor/` and
  `.bundle/` are git-ignored. Always run Jekyll via `bundle exec`.
- The `webrick` gem is in the `Gemfile` because it is no longer bundled with Ruby 3.x and
  `jekyll serve` needs it.
