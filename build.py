#!/usr/bin/env python3
"""Generate README.md from places.yml.

Every place lists the sections it belongs to under `tags`, so a place can
appear in several sections. Edit places.yml, then run:

    python3 build.py
"""
from pathlib import Path
from urllib.parse import quote_plus

import yaml

ROOT = Path(__file__).parent
data = yaml.safe_load((ROOT / "places.yml").read_text(encoding="utf-8"))
sections = data["sections"]
places = data["places"]
by_key = {s["key"]: s for s in sections}

# Sanity check: every tag must be a known section.
for p in places:
    for t in p["tags"]:
        if t not in by_key:
            raise SystemExit(f"Unknown tag '{t}' on {p['name']}")


def short_title(s):
    """Section title without the leading emoji."""
    return s["title"].split(" ", 1)[1]


def map_link(p):
    q = quote_plus(p.get("map") or p["name"])
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def render_place(p, current):
    name = f"[{p['name']}]({p['url']})" if p.get("url") else p["name"]
    head = f"#### {name}"
    meta = []
    if p.get("area"):
        meta.append(f"📍 {p['area']}")
    meta.append(f"[🗺️ Map]({map_link(p)})")
    lines = [head, "", " · ".join(meta), ""]
    lines += [f"- {n}" for n in p["notes"]]
    if p.get("tip"):
        lines.append(f"- 💬 **Tip:** {p['tip']}")
    others = [t for t in p["tags"] if t != current]
    if others:
        links = ", ".join(f"[{short_title(by_key[t])}](#{t})" for t in others)
        lines += ["", f"<sub>Also in: {links}</sub>"]
    lines.append("")
    return "\n".join(lines)


out = []
out.append("# Rachel's Guide to Williamsburg, VA 🇺🇸\n")
out.append(
    "My personal tips for visiting Williamsburg and Virginia's Historic Triangle: "
    "where to eat, what to see, and who to say hi to. Many places appear in more "
    "than one section, so jump to whatever you're in the mood for.\n"
)
out.append(
    "> 💬 Look for the **Tip** lines. Some of my friends will take extra good care of you "
    "if you tell them you're my student!\n"
)

# Table of contents
out.append("## Sections\n")
for s in sections:
    n = sum(1 for p in places if s["key"] in p["tags"])
    out.append(f"- [{s['title']}](#{s['key']}) ({n})")
out.append("- [📋 All places A–Z](#all-places)\n")

# Sections
for s in sections:
    members = [p for p in places if s["key"] in p["tags"]]
    if not members:
        continue
    out.append(f'<a id="{s["key"]}"></a>\n')
    out.append(f"## {s['title']}\n")
    if s.get("intro"):
        out.append(f"{s['intro']}\n")
    for p in members:
        out.append(render_place(p, s["key"]))
    out.append("[↑ Back to sections](#sections)\n")

# A–Z index
out.append('<a id="all-places"></a>\n')
out.append("## 📋 All places A–Z\n")
out.append("| Place | Where | Sections |")
out.append("|---|---|---|")
for p in sorted(places, key=lambda p: p["name"].lower().removeprefix("the ")):
    name = f"[{p['name']}]({p['url']})" if p.get("url") else p["name"]
    secs = ", ".join(f"[{short_title(by_key[t])}](#{t})" for t in p["tags"])
    out.append(f"| {name} | {p.get('area', '')} · [map]({map_link(p)}) | {secs} |")
out.append("")
out.append("---\n")
out.append(
    "<sub>Hours, seasons and schedules change, so check each website before you go. "
    "To add or edit a place, update `places.yml` and run `python3 build.py`.</sub>\n"
)

(ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")
print(f"Wrote README.md: {len(places)} places in {len(sections)} sections")
