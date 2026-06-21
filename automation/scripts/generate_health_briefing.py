#!/usr/bin/env python3
"""Generate a Daily Health Briefing with Azure OpenAI, following the agent instructions.

Reads `automation/health-briefing-agent.md` + `automation/memories.md` as the system
context, asks the model for a structured briefing, writes `health/briefings/YYYY-MM-DD.json`,
and prepends the day to the archive manifest `health/index.json`.

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

ROOT = pathlib.Path(__file__).resolve().parents[2]
INSTRUCTIONS = ROOT / "automation" / "health-briefing-agent.md"
MEMORIES = ROOT / "automation" / "memories.md"
BRIEFINGS_DIR = ROOT / "health" / "briefings"
INDEX = ROOT / "health" / "index.json"
ALLOWED_ICONS = {"sparkle", "bolt", "anchor", "ribbon", "moon", "pulse"}
DEFAULT_TITLE = "Daily Health Briefing"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def generate(date: str) -> dict:
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
    user = (
        "Write today's Daily Health Briefing following the instructions and memory above.\n"
        f"- Date: {date} (use this exact value for the `date` field).\n"
        "- Produce ONE section per standing topic from memory, in the canonical order.\n"
        "- Only cite real sources you actually found; never invent a title, journal, or URL.\n\n"
        "Return ONLY a JSON object with these keys:\n"
        "  date     string, YYYY-MM-DD (must equal the value above)\n"
        '  title    string (use "Daily Health Briefing")\n'
        "  intro    string, one warm morning-greeting sentence\n"
        "  sections array of objects, each with:\n"
        "             topic   string (section heading)\n"
        "             icon    one of: sparkle, bolt, anchor, ribbon, moon, pulse\n"
        "             body    Markdown string (~60-150 words; supports **bold**, lists, links)\n"
        "             sources array of { title, publisher, url, date } (1-3 real citations)\n"
    )
    resp = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return json.loads(resp.choices[0].message.content)


def _clean_source(src: dict) -> dict:
    out = {
        "title": str(src.get("title", "")).strip(),
        "publisher": str(src.get("publisher", "")).strip(),
        "url": str(src.get("url", "")).strip(),
    }
    if str(src.get("date", "")).strip():
        out["date"] = str(src["date"]).strip()
    return out


def build_briefing(data: dict, date: str) -> tuple[pathlib.Path, str, int]:
    sections_in = data.get("sections") or []
    if not sections_in:
        raise SystemExit("Model returned no sections; refusing to write an empty briefing.")

    sections = []
    for sec in sections_in:
        topic = str(sec.get("topic", "")).strip()
        body = str(sec.get("body", "")).strip()
        if not topic or not body:
            raise SystemExit(f"Section missing topic/body: {sec!r}")
        icon = str(sec.get("icon", "")).strip()
        if icon not in ALLOWED_ICONS:
            icon = "pulse"
        clean = {"topic": topic, "icon": icon, "body": body}
        sources = [_clean_source(s) for s in (sec.get("sources") or []) if s.get("url")]
        if sources:
            clean["sources"] = sources
        sections.append(clean)

    title = str(data.get("title") or DEFAULT_TITLE).strip()
    briefing = {"date": date, "title": title}
    intro = str(data.get("intro", "")).strip()
    if intro:
        briefing["intro"] = intro
    briefing["sections"] = sections

    BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    path = BRIEFINGS_DIR / f"{date}.json"
    path.write_text(json.dumps(briefing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path, title, len(sections)


def update_index(date: str, title: str) -> None:
    if INDEX.exists():
        index = json.loads(INDEX.read_text(encoding="utf-8"))
    else:
        index = {}
    briefings = [b for b in index.get("briefings", []) if b.get("date") != date]
    briefings.insert(0, {"date": date, "title": title})
    index["briefings"] = briefings
    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def emit_outputs(path: pathlib.Path, date: str, sections: int) -> None:
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if not gh_output:
        return
    with open(gh_output, "a", encoding="utf-8") as fh:
        fh.write(f"path={path.relative_to(ROOT)}\n")
        fh.write(f"date={date}\n")
        fh.write(f"sections={sections}\n")


def _dry_run_data(date: str) -> dict:
    topics = [
        ("Anti-Aging", "sparkle"),
        ("HIIT Workouts for Women", "bolt"),
        ("Pelvic Floor Exercises", "anchor"),
        ("Alternative Cancer Treatments", "ribbon"),
        ("Sleep — Studies & Best Practices", "moon"),
    ]
    return {
        "date": date,
        "title": DEFAULT_TITLE,
        "intro": "Dry-run stub briefing — placeholder content used to test the publishing pipeline.",
        "sections": [
            {
                "topic": topic,
                "icon": icon,
                "body": (
                    f"**{topic}** — this is a dry-run stub section. In a real run the agent "
                    "summarizes recent, reputable findings here with the evidence level stated.\n\n"
                    "- Placeholder takeaway one.\n- Placeholder takeaway two."
                ),
                "sources": [
                    {
                        "title": "Placeholder source (dry-run only)",
                        "publisher": "Example",
                        "url": "https://example.com/",
                        "date": date[:4],
                    }
                ],
            }
            for topic, icon in topics
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Daily Health Briefing.")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="skip the model; write a stub briefing")
    args = parser.parse_args()

    data = _dry_run_data(args.date) if args.dry_run else generate(args.date)

    path, title, sections = build_briefing(data, args.date)
    update_index(args.date, title)
    emit_outputs(path, args.date, sections)
    print(f"Wrote {path.relative_to(ROOT)} ({sections} sections) and updated {INDEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
