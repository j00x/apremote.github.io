#!/usr/bin/env python3
"""Generate an Azure blog post with Azure OpenAI, following the agent instructions.

Reads `automation/azure-blog-agent.md` + `automation/azure-memories.md` as the system
context, asks the model for a structured post, writes `_posts/YYYY-MM-DD-<slug>.md`, and
appends the post to the running log in `automation/azure-memories.md`.

Git / pull-request handling is done by the caller (the GitHub Actions workflow). Use
`--dry-run` to exercise the file plumbing without calling the model.

Env (non-dry-run):
  AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT
  AZURE_OPENAI_API_VERSION (optional, default 2024-10-21)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
INSTRUCTIONS = ROOT / "automation" / "azure-blog-agent.md"
MEMORIES = ROOT / "automation" / "azure-memories.md"
POSTS_DIR = ROOT / "_posts"
ALLOWED = {"how-to", "lessons-learned"}
LOG_MARKER = "## Running log (append shipped posts here)\n"


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:60] or "post"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def generate(category: str, topic: str) -> dict:
    from openai import AzureOpenAI

    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
    )
    system = (
        read(INSTRUCTIONS)
        + "\n\n---\nLONG-TERM MEMORY (authoritative for topics/voice/rules):\n"
        + read(MEMORIES)
    )
    cat_line = (
        category
        if category in ALLOWED
        else "choose 'how-to' or 'lessons-learned', alternating based on the running log"
    )
    topic_line = topic or "choose a fresh topic from the backlog that is NOT already in the running log"
    user = (
        "Write today's Azure blog post following the instructions and memory above.\n"
        f"- Category: {cat_line}\n"
        f"- Topic: {topic_line}\n\n"
        "Return ONLY a JSON object with these keys:\n"
        "  title          string\n"
        "  category       'how-to' or 'lessons-learned'\n"
        "  tags           array of lowercase strings\n"
        "  summary        one-sentence string (< 160 chars)\n"
        "  body_markdown  the full Markdown body with language-tagged fenced code blocks; "
        "do NOT include YAML front matter."
    )
    resp = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    return json.loads(resp.choices[0].message.content)


def build_post(data: dict, date: str) -> tuple[pathlib.Path, str, str, str]:
    category = str(data["category"]).strip()
    if category not in ALLOWED:
        raise SystemExit(f"Invalid category {category!r}; must be one of {sorted(ALLOWED)}")
    title = str(data["title"]).strip()
    tags = [str(t).strip() for t in data.get("tags", []) if str(t).strip()]
    summary = str(data.get("summary", "")).strip().replace('"', "'")
    body = str(data["body_markdown"]).rstrip() + "\n"

    front_matter = (
        "---\n"
        f'title: "{title.replace(chr(34), chr(39))}"\n'
        f"category: {category}\n"
        f"tags: [{', '.join(tags)}]\n"
        f'summary: "{summary}"\n'
        "---\n\n"
    )
    slug = slugify(title)
    POSTS_DIR.mkdir(exist_ok=True)
    path = POSTS_DIR / f"{date}-{slug}.md"
    path.write_text(front_matter + body, encoding="utf-8")
    return path, title, category, slug


def log_memory(date: str, category: str, title: str, path: pathlib.Path) -> None:
    if not MEMORIES.exists() or LOG_MARKER not in MEMORIES.read_text(encoding="utf-8"):
        return
    text = MEMORIES.read_text(encoding="utf-8")
    head, tail = text.split(LOG_MARKER, 1)
    entry = f'- **{date}** — `{category}`: "{title}" (`{path.relative_to(ROOT)}`).\n'
    lines = tail.splitlines(keepends=True)
    insert_at = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith("- ")), len(lines))
    lines.insert(insert_at, entry)
    MEMORIES.write_text(head + LOG_MARKER + "".join(lines), encoding="utf-8")


def emit_outputs(path: pathlib.Path, title: str, category: str, slug: str) -> None:
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if not gh_output:
        return
    with open(gh_output, "a", encoding="utf-8") as fh:
        fh.write(f"path={path.relative_to(ROOT)}\n")
        fh.write(f"title={title}\n")
        fh.write(f"category={category}\n")
        fh.write(f"slug={slug}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an Azure blog post.")
    parser.add_argument("--category", default="auto", help="how-to | lessons-learned | auto")
    parser.add_argument("--topic", default="", help="optional topic hint")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="skip the model; write a stub post")
    args = parser.parse_args()

    if args.dry_run:
        data = {
            "title": "Dry Run Sample Post",
            "category": args.category if args.category in ALLOWED else "how-to",
            "tags": ["azure", "sample"],
            "summary": "A stub post produced in dry-run mode to test the publishing pipeline.",
            "body_markdown": "## Hello\n\nThis is a dry-run stub.\n\n```bash\necho 'hello azure'\n```\n",
        }
    else:
        data = generate(args.category, args.topic)

    path, title, category, slug = build_post(data, args.date)
    log_memory(args.date, category, title, path)
    emit_outputs(path, title, category, slug)
    print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
