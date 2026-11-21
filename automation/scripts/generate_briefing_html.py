#!/usr/bin/env python3
"""Render a Daily Health Briefing JSON into a self-contained, designed HTML page.

The live Health page (`/health/`) renders the briefing JSON client-side. This tool
produces a standalone, portable `.html` twin of a given day's briefing, reusing the
site's glassmorphism design language (see `assets/css/style.css`) inlined so the file
opens anywhere with no build step. It faithfully mirrors the MiniMarkdown renderer in
`assets/js/markdown.js` so the standalone page matches what the live page shows.

Usage:
  python3 automation/scripts/generate_briefing_html.py --date YYYY-MM-DD
  python3 automation/scripts/generate_briefing_html.py --in path.json --out path.html
"""
from __future__ import annotations

import argparse
import datetime
import html as htmllib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
BRIEFINGS_DIR = ROOT / "health" / "briefings"

ICONS = {
    "sparkle": "\u2726", "bolt": "\u26a1", "anchor": "\u2693",
    "ribbon": "\U0001f397", "moon": "\U0001f319", "pulse": "\u2764",
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

LINK_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/>'
            '<path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>')


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text: str) -> str:
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+|mailto:[^\s)]+)\)",
        lambda m: '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>'
        % (m.group(2), m.group(1)),
        text,
    )
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(^|[^*])\*([^*]+)\*", r"\1<em>\2</em>", text)
    return text


def render_markdown(md: str) -> str:
    if not md:
        return ""
    lines = escape_html(str(md)).split("\n")
    out: list[str] = []
    list_type: str | None = None

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append("</%s>" % list_type)
            list_type = None

    for raw in lines:
        trimmed = raw.strip()
        if trimmed == "":
            close_list()
            continue
        h = re.match(r"^(#{1,4})\s+(.*)$", trimmed)
        if h:
            close_list()
            level = min(len(h.group(1)) + 1, 4)
            out.append("<h%d>%s</h%d>" % (level, inline(h.group(2)), level))
            continue
        ol = re.match(r"^\d+\.\s+(.*)$", trimmed)
        if ol:
            if list_type != "ol":
                close_list()
                out.append("<ol>")
                list_type = "ol"
            out.append("<li>%s</li>" % inline(ol.group(1)))
            continue
        ul = re.match(r"^[-*]\s+(.*)$", trimmed)
        if ul:
            if list_type != "ul":
                close_list()
                out.append("<ul>")
                list_type = "ul"
            out.append("<li>%s</li>" % inline(ul.group(1)))
            continue
        close_list()
        out.append("<p>%s</p>" % inline(trimmed))
    close_list()
    return "\n".join(out)


def fmt_date(iso: str) -> str:
    y, m, d = (int(x) for x in iso.split("-"))
    return "%s %d, %d" % (MONTHS[m - 1], d, y)


def render_sources(sources: list[dict]) -> str:
    if not sources:
        return ""
    chips = []
    for s in sources:
        label = s.get("publisher") or s.get("title") or "Source"
        title = htmllib.escape(s.get("title") or label, quote=True)
        url = htmllib.escape(s.get("url") or "#", quote=True)
        chips.append(
            '<a class="source-chip" href="%s" target="_blank" rel="noopener noreferrer" title="%s">%s<span>%s</span></a>'
            % (url, title, LINK_SVG, htmllib.escape(label))
        )
    return '<div class="sources">%s</div>' % "".join(chips)


def render_section(sec: dict) -> str:
    icon = ICONS.get(sec.get("icon"), ICONS["pulse"])
    return (
        '<article class="briefing-section glass reveal">'
        '<div class="briefing-section__head">'
        '<span class="briefing-section__icon" aria-hidden="true">%s</span>'
        "<h2>%s</h2></div>"
        '<div class="briefing-body">%s</div>%s</article>'
    ) % (icon, htmllib.escape(sec.get("topic", "")),
         render_markdown(sec.get("body", "")), render_sources(sec.get("sources")))


STYLE = """
:root{--bg:#0a0a14;--bg-2:#0d0d1c;--ink:#eef1ff;--ink-soft:#b8bdd6;--ink-dim:#8a8fb0;
--glass:rgba(255,255,255,.055);--glass-strong:rgba(255,255,255,.09);--glass-border:rgba(255,255,255,.14);
--glass-border-soft:rgba(255,255,255,.08);--cyan:#38e1ff;--purple:#9b6bff;--magenta:#ff5ccb;--teal:#2ff5c8;
--radius:20px;--radius-sm:12px;--blur:18px;--shadow:0 18px 50px -20px rgba(0,0,0,.75);
--glow-cyan:0 0 22px rgba(56,225,255,.45);--glow-teal:0 0 22px rgba(47,245,200,.4);--maxw:900px;
--ease:cubic-bezier(.22,.61,.36,1)}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
color:var(--ink);background:var(--bg);line-height:1.65;-webkit-font-smoothing:antialiased;overflow-x:hidden;
padding:2.5rem 0 1rem}
a{color:var(--cyan);text-decoration:none;transition:color .2s var(--ease)}
a:hover{color:#9ff0ff}
h1,h2,h3,h4{line-height:1.15;margin:0 0 .5em;font-weight:700;letter-spacing:-.02em}
p{margin:0 0 1em;color:var(--ink-soft)}
:focus-visible{outline:2px solid var(--cyan);outline-offset:3px;border-radius:6px}
.wrap{width:min(100% - 2.4rem,var(--maxw));margin-inline:auto}
.bg-mesh{position:fixed;inset:0;z-index:-2;overflow:hidden;
background:radial-gradient(1200px 800px at 50% -10%,rgba(58,141,255,.10),transparent 60%),linear-gradient(180deg,var(--bg-2),var(--bg) 60%)}
.blob{position:absolute;width:46vmax;height:46vmax;border-radius:50%;filter:blur(90px);opacity:.5;will-change:transform}
.blob--cyan{background:radial-gradient(circle,var(--cyan),transparent 65%);top:-12%;left:-8%;animation:drift1 26s var(--ease) infinite}
.blob--purple{background:radial-gradient(circle,var(--purple),transparent 65%);top:10%;right:-14%;animation:drift2 30s var(--ease) infinite}
.blob--magenta{background:radial-gradient(circle,var(--magenta),transparent 65%);bottom:-18%;left:18%;opacity:.35;animation:drift3 34s var(--ease) infinite}
.blob--teal{background:radial-gradient(circle,var(--teal),transparent 65%);bottom:-10%;right:6%;opacity:.3;animation:drift1 38s var(--ease) infinite reverse}
@keyframes drift1{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(6%,8%) scale(1.12)}}
@keyframes drift2{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-8%,6%) scale(1.08)}}
@keyframes drift3{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(5%,-7%) scale(1.15)}}
.glass{background:var(--glass);-webkit-backdrop-filter:blur(var(--blur)) saturate(140%);backdrop-filter:blur(var(--blur)) saturate(140%);
border:1px solid var(--glass-border-soft);border-radius:var(--radius);box-shadow:var(--shadow),inset 0 1px 0 rgba(255,255,255,.08)}
.briefing-head{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;padding:1.4rem 1.6rem;margin-bottom:1.1rem}
.briefing-head__title{display:flex;flex-direction:column;gap:.3rem}
.briefing-head__title .eyebrow{font-size:.74rem;letter-spacing:.18em;text-transform:uppercase;color:var(--cyan)}
.briefing-head__title h1{margin:0;font-size:clamp(1.7rem,4vw,2.4rem);color:#fff;text-shadow:0 0 30px rgba(47,245,200,.35)}
.date-pill{align-self:flex-start;padding:.35rem .9rem;border-radius:999px;font-size:.85rem;color:var(--teal);
border:1px solid rgba(47,245,200,.4);background:rgba(47,245,200,.08);box-shadow:var(--glow-teal)}
.intro{padding:0 .2rem;margin:0 0 1.1rem;color:var(--ink-soft)}
.disclaimer{display:flex;gap:.7rem;align-items:flex-start;padding:.9rem 1.1rem;margin-bottom:1.4rem;font-size:.85rem;
color:var(--ink-dim);border-left:2px solid rgba(255,200,80,.6)}
.disclaimer strong{color:#ffd57a}
.briefing-section{padding:1.5rem 1.6rem;margin-bottom:1.2rem}
.briefing-section__head{display:flex;align-items:center;gap:.7rem;margin-bottom:.8rem}
.briefing-section__icon{width:36px;height:36px;flex:none;display:grid;place-items:center;border-radius:11px;font-size:1.1rem;background:var(--glass-strong);box-shadow:var(--glow-teal)}
.briefing-section__head h2{margin:0;font-size:1.2rem;color:#fff}
.briefing-body{color:var(--ink-soft)}
.briefing-body :first-child{margin-top:0}
.briefing-body h3,.briefing-body h4{color:#fff;margin-top:1.2rem}
.briefing-body ul,.briefing-body ol{padding-left:1.3rem;color:var(--ink-soft)}
.briefing-body li{margin:.3rem 0}
.briefing-body strong{color:var(--ink)}
.briefing-body code{font-family:"JetBrains Mono",monospace;font-size:.88em;background:rgba(56,225,255,.10);color:#bdefff;padding:.15em .4em;border-radius:6px}
.briefing-body a{text-decoration:underline;text-underline-offset:2px}
.sources{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem;padding-top:.9rem;border-top:1px solid var(--glass-border-soft)}
.source-chip{display:inline-flex;align-items:center;gap:.35rem;padding:.3rem .7rem;border-radius:999px;font-size:.78rem;color:var(--cyan);
background:var(--glass);border:1px solid var(--glass-border-soft);transition:box-shadow .2s var(--ease),transform .2s var(--ease)}
.source-chip:hover{box-shadow:var(--glow-cyan);transform:translateY(-1px)}
.source-chip svg{width:13px;height:13px}
.page-footer{margin-top:1.6rem;padding:1rem 1.4rem;font-size:.82rem;color:var(--ink-dim);text-align:center}
.reveal{opacity:0;transform:translateY(18px);animation:rise .7s var(--ease) forwards}
.reveal:nth-child(2){animation-delay:.05s}.reveal:nth-child(3){animation-delay:.1s}
.reveal:nth-child(4){animation-delay:.15s}.reveal:nth-child(5){animation-delay:.2s}
@keyframes rise{to{opacity:1;transform:none}}
@media (max-width:680px){.briefing-head{padding:1.1rem 1.2rem}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important}
.blob{animation:none!important}.reveal{opacity:1!important;transform:none!important}}
"""


def build(data: dict) -> str:
    title = data.get("title", "Daily Health Briefing")
    iso = data["date"]
    sections = "\n".join(render_section(s) for s in data.get("sections", []))
    intro = htmllib.escape(data.get("intro", ""))
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>%s \u2014 %s</title>
<meta name="description" content="Daily health research briefing for %s.">
<style>%s</style>
</head>
<body>
<div class="bg-mesh" aria-hidden="true">
  <span class="blob blob--cyan"></span><span class="blob blob--purple"></span>
  <span class="blob blob--magenta"></span><span class="blob blob--teal"></span>
</div>
<main class="wrap">
  <header class="briefing-head glass">
    <div class="briefing-head__title">
      <span class="eyebrow">Health Research Digest</span>
      <h1>%s</h1>
    </div>
    <span class="date-pill">%s</span>
  </header>
  <p class="intro">%s</p>
  <div class="disclaimer glass" role="note">
    <span aria-hidden="true">\u2695\ufe0f</span>
    <span><strong>Informational only \u2014 not medical advice.</strong>
      This briefing summarizes published research and is not a substitute for professional
      diagnosis or treatment. Always consult a qualified healthcare provider.</span>
  </div>
  %s
  <footer class="page-footer">Generated %s \u00b7 Sources are linked per section \u00b7 Adam Pratt</footer>
</main>
</body>
</html>
""" % (
        htmllib.escape(title), fmt_date(iso), fmt_date(iso), STYLE,
        htmllib.escape(title), fmt_date(iso), intro, sections, fmt_date(iso),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a briefing JSON to a standalone HTML page.")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--in", dest="src", help="Input JSON (defaults to health/briefings/<date>.json)")
    parser.add_argument("--out", dest="dst", help="Output HTML (defaults to the input path with .html)")
    args = parser.parse_args()

    src = pathlib.Path(args.src) if args.src else BRIEFINGS_DIR / f"{args.date}.json"
    dst = pathlib.Path(args.dst) if args.dst else src.with_suffix(".html")

    data = json.loads(src.read_text(encoding="utf-8"))
    dst.write_text(build(data), encoding="utf-8")
    print(f"Wrote {dst.relative_to(ROOT) if dst.is_relative_to(ROOT) else dst}")


if __name__ == "__main__":
    main()
