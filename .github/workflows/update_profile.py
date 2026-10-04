#!/usr/bin/env python3
"""Refreshes the profile README: moodboard project cards, recent activity,
a daily note and a 'last synced' stamp. Runs inside GitHub Actions."""

import datetime as dt
import html
import json
import os
import pathlib
import re
import sys
import textwrap
import urllib.request

USER = "Pooja27-web"
ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CARDS = ROOT / "assets" / "cards"
TOKEN = os.environ.get("GITHUB_TOKEN")

# ---------------------------------------------------------------------------
# EDIT ME
# (keyword that appears in the repo name, title on the card, short description)
# Cards show up in this order. If a keyword matches no repo, it's skipped.
# ---------------------------------------------------------------------------
FEATURED = [
    ("gigsetu", "GigSetu", "My Smart India Hackathon 2026 project. Still in progress."),
    ("retail", "Retail Data Analysis", "Digging into retail data to find sales patterns and insights."),
    ("electric", "EV Population Data", "Power BI dashboard turning electric vehicle data into clear visuals."),
    ("warlens", "WarLens", "An NLP project."),
    ("campuscart", "CampusCart", "Full-stack campus marketplace for student buying and selling."),
]

QUOTES = [
    "every dataset has a love letter hiding in it.",
    "slow mornings, sharp queries.",
    "tea cooling, tabs open, curiosity on.",
    "soft heart, strong joins.",
    "write the code gently, debug it kindly.",
    "plot twist: the outliers were the story.",
    "good insights, like good chai, take their time.",
    "dear data, tell me what you're hiding.",
    "bloom where your notebook is open.",
    "progress looks a lot like quiet evenings and one more chart.",
    "a little more learning, a little less rushing.",
    "keep going, your future self is already proud.",
    "small pages, steady pen, a whole story by the end.",
    "messy data, calm mind, pretty chart.",
]

# (card background, ink colour)
PALETTE = [
    ("#F9E1E4", "#7A4A55"),  # blush
    ("#E6DDF2", "#5E4B7A"),  # lavender
    ("#DCEBDD", "#4F6B53"),  # sage
    ("#FBEBCB", "#7A6030"),  # butter
    ("#DCEAF2", "#46657A"),  # sky
    ("#F5DCCB", "#7A5238"),  # peach
]

SERIF = "Georgia, 'Times New Roman', serif"
SANS = "'Segoe UI', Helvetica, Arial, sans-serif"


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-refresh"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def parse_time(value):
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def ago(value):
    delta = dt.datetime.now(dt.timezone.utc) - parse_time(value)
    mins = int(delta.total_seconds() // 60)
    if mins < 60:
        return "just now"
    if mins < 60 * 24:
        return f"{mins // 60}h ago"
    days = delta.days
    if days < 2:
        return "yesterday"
    if days < 60:
        return f"{days}d ago"
    return f"{days // 30}mo ago"


def norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def card_svg(title, desc, lang, stars, updated, idx):
    bg, ink = PALETTE[idx % len(PALETTE)]
    t_lines = textwrap.wrap(title, 22)[:2] or [title]
    d_lines = textwrap.wrap(desc, 36)
    if len(d_lines) > 4:
        d_lines = d_lines[:4]
        d_lines[-1] = d_lines[-1].rstrip(".,") + "…"

    title_y = 86
    desc_y = title_y + 30 * (len(t_lines) - 1) + 36
    foot_y = desc_y + 22 * (len(d_lines) - 1) + 46
    height = foot_y + 28

    pill_text = html.escape(lang or "project")
    pill_w = 18 + int(7.4 * len(lang or "project"))

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{height}" viewBox="0 0 400 {height}">',
        f'<rect x="1" y="1" width="398" height="{height - 2}" rx="24" fill="{bg}" stroke="{ink}" stroke-opacity="0.18"/>',
        f'<circle cx="354" cy="42" r="46" fill="{ink}" opacity="0.07"/>',
        f'<circle cx="380" cy="98" r="18" fill="{ink}" opacity="0.06"/>',
        f'<rect x="24" y="24" width="{pill_w}" height="26" rx="13" fill="{ink}" opacity="0.13"/>',
        f'<text x="{24 + pill_w / 2}" y="42" text-anchor="middle" font-family="{SANS}" '
        f'font-size="12" font-weight="600" fill="{ink}">{pill_text}</text>',
    ]
    for i, line in enumerate(t_lines):
        out.append(
            f'<text x="24" y="{title_y + 30 * i}" font-family="{SERIF}" font-size="25" '
            f'font-weight="bold" fill="{ink}">{html.escape(line)}</text>'
        )
    for i, line in enumerate(d_lines):
        out.append(
            f'<text x="24" y="{desc_y + 22 * i}" font-family="{SERIF}" font-size="15" '
            f'font-style="italic" fill="{ink}" opacity="0.88">{html.escape(line)}</text>'
        )
    out.append(
        f'<line x1="24" x2="376" y1="{foot_y - 24}" y2="{foot_y - 24}" stroke="{ink}" '
        f'stroke-opacity="0.25" stroke-dasharray="3 5"/>'
    )
    out.append(
        f'<text x="24" y="{foot_y}" font-family="{SANS}" font-size="13" fill="{ink}" opacity="0.8">'
        f'★ {stars}   ·   updated {html.escape(updated)}</text>'
    )
    out.append("</svg>")
    return "\n".join(out), height


def build_projects(repos):
    CARDS.mkdir(parents=True, exist_ok=True)
    for old in CARDS.glob("*.svg"):
        old.unlink()

    items, used = [], set()
    for kw, title, desc in FEATURED:
        for repo in repos:
            if repo["name"] in used or kw not in norm(repo["name"]):
                continue
            used.add(repo["name"])
            items.append((repo, title, desc))
            break

    cols, heights = [[], []], [0, 0]
    for idx, (repo, title, desc) in enumerate(items):
        svg, h = card_svg(
            title, desc, repo.get("language"), repo.get("stargazers_count", 0),
            ago(repo["pushed_at"]), idx,
        )
        name = f"{slug(repo['name'])}.svg"
        (CARDS / name).write_text(svg, encoding="utf-8")
        target = 0 if heights[0] <= heights[1] else 1
        heights[target] += h + 16
        cols[target].append(
            f'<a href="{repo["html_url"]}"><img src="assets/cards/{name}" width="100%" alt="{html.escape(title)}"/></a>'
        )

    if not items:
        return "_projects loading, check back soon_ 🌸"
    cells = "\n".join(
        f'<td width="50%" valign="top">\n' + "\n<br/>\n".join(c) + "\n</td>" for c in cols
    )
    return f'<table width="100%">\n<tr>\n{cells}\n</tr>\n</table>'


def build_activity():
    try:
        events = api(f"/users/{USER}/events/public?per_page=50")
    except Exception:
        events = []
    seen, lines = set(), []
    for ev in events:
        if ev.get("type") != "PushEvent":
            continue
        name = ev["repo"]["name"].split("/")[-1]
        if name == USER or name in seen:
            continue
        seen.add(name)
        lines.append(f"- 🌸 pushed to [**{name}**](https://github.com/{USER}/{name}) · {ago(ev['created_at'])}")
        if len(lines) == 5:
            break
    return "\n".join(lines) or "- quiet week, writing in my head ✏️"


def build_quote():
    return f"> ✉️ *{QUOTES[dt.date.today().toordinal() % len(QUOTES)]}*"


def replace_section(text, name, content):
    pattern = re.compile(rf"(<!--START_SECTION:{name}-->)(.*?)(<!--END_SECTION:{name}-->)", re.S)
    if not pattern.search(text):
        print(f"warning: markers for '{name}' not found in README", file=sys.stderr)
        return text
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


def main():
    try:
        repos = api(f"/users/{USER}/repos?per_page=100&sort=pushed&type=owner")
    except Exception as exc:
        print(f"could not reach the GitHub API: {exc}", file=sys.stderr)
        sys.exit(1)

    text = README.read_text(encoding="utf-8")
    text = replace_section(text, "projects", build_projects(repos))
    text = replace_section(text, "activity", build_activity())
    text = replace_section(text, "quote", build_quote())
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    text = replace_section(text, "updated", f"<sub>last synced {stamp}</sub>")
    README.write_text(text, encoding="utf-8")
    print("README refreshed")


if __name__ == "__main__":
    main()
