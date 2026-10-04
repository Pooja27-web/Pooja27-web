#!/usr/bin/env python3
"""Rebuilds the profile: animated banners, live stat cards, moodboard project
cards, recent activity and a daily note. Runs inside GitHub Actions."""

import collections
import datetime as dt
import html
import json
import math
import os
import pathlib
import re
import sys
import textwrap
import urllib.request

USER = "Pooja27-web"
ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
ASSETS = ROOT / "assets"
CARDS = ASSETS / "cards"
TOKEN = os.environ.get("GITHUB_TOKEN")

# ---------------------------------------------------------------------------
# EDIT ME
# ---------------------------------------------------------------------------
# (keyword in repo name, title on card, short description). Order = card order.
FEATURED = [
    ("gigsetu", "GigSetu", "My Smart India Hackathon 2026 project. Still in progress."),
    ("retail", "Retail Data Analysis", "Digging into retail data to find sales patterns and insights."),
    ("electric", "EV Population Data", "Power BI dashboard turning electric vehicle data into clear visuals."),
    ("warlens", "WarLens", "An NLP project."),
    ("campuscart", "CampusCart", "Full-stack campus marketplace for student buying and selling."),
]

SKILLS = ["Python", "Pandas", "Power BI", "Data Analysis", "Data Visualization",
          "Jupyter", "Java", "JavaScript", "HTML/CSS", "Git", "MongoDB"]

# (label, title, subtitle)
TIMELINE = [
    ("2024", "Started BCA Data Science", "Alliance University"),
    ("2025", "1M1B internship", "AI-based Carbon Footprinter"),
    ("2026", "Smart India Hackathon", "GigSetu, in progress"),
    ("now", "Power BI projects", "aiming for data analyst"),
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

# (background, ink)
PALETTE = [
    ("#F9E1E4", "#7A4A55"), ("#E6DDF2", "#5E4B7A"), ("#DCEBDD", "#4F6B53"),
    ("#FBEBCB", "#7A6030"), ("#DCEAF2", "#46657A"), ("#F5DCCB", "#7A5238"),
]
INK = "#6B4A5A"
MAUVE = "#B07A94"
CREAM = "#FFF8F3"
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "'Segoe UI', Helvetica, Arial, sans-serif"


# ----------------------------------------------------------------- helpers --
def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-refresh"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def esc(text):
    return html.escape(str(text), quote=True)


def parse_time(value):
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def ago(value):
    delta = dt.datetime.now(dt.timezone.utc) - parse_time(value)
    mins = int(delta.total_seconds() // 60)
    if mins < 60:
        return "just now"
    if mins < 60 * 24:
        return f"{mins // 60}h ago"
    if delta.days < 2:
        return "yesterday"
    if delta.days < 60:
        return f"{delta.days}d ago"
    return f"{delta.days // 30}mo ago"


def norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def save(name, content):
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / name).write_text(content, encoding="utf-8")


def svg(w, h, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<style>{style}</style>{body}</svg>')


# ------------------------------------------------------------ animated art --
def hero_svg():
    style = (".p{animation:fl 6s ease-in-out infinite}"
             "@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}"
             ".s{animation:tw 3s ease-in-out infinite}"
             "@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}"
             ".st{opacity:0;animation:sm 3.4s ease-in-out infinite}"
             "@keyframes sm{0%{transform:translateY(12px);opacity:0}40%{opacity:.55}100%{transform:translateY(-18px);opacity:0}}")
    colors = ["#F4C6CC", "#E6DDF2", "#CFE3D0", "#FBEBCB"]
    petals = [(600, 60, 14, 0.0, 25), (690, 36, 10, 1.2, -30), (790, 84, 16, 2.1, 50),
              (850, 40, 9, 0.6, 10), (560, 220, 11, 1.8, -20), (846, 236, 13, 2.8, 35),
              (760, 268, 8, 0.3, 70), (520, 120, 9, 2.4, 15)]
    parts = [
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#FBE3E6"/><stop offset="0.55" stop-color="#EBE2F5"/>'
        '<stop offset="1" stop-color="#DCEBDD"/></linearGradient></defs>',
        '<rect width="900" height="300" rx="30" fill="url(#g)"/>',
        '<rect x="8" y="8" width="884" height="284" rx="24" fill="none" stroke="#B07A94" '
        'stroke-opacity="0.35" stroke-dasharray="4 7"/>',
    ]
    for i, (x, y, r, d, a) in enumerate(petals):
        parts.append(f'<g transform="translate({x} {y}) rotate({a})"><ellipse class="p" rx="{r}" ry="{r * 0.6:.1f}" '
                     f'fill="{colors[i % 4]}" opacity="0.9" style="animation-delay:{d}s"/></g>')
    for i, (x, y) in enumerate([(470, 50), (640, 150), (880, 150), (520, 260), (60, 40), (480, 262)]):
        parts.append(f'<path class="s" transform="translate({x} {y})" fill="#B07A94" style="animation-delay:{i * 0.5}s" '
                     'd="M0 -9 L2.5 -2.5 L9 0 L2.5 2.5 L0 9 L-2.5 2.5 L-9 0 L-2.5 -2.5Z"/>')
    # chai cup
    parts += [
        '<ellipse cx="700" cy="236" rx="82" ry="11" fill="#E6DDF2" stroke="#B07A94" stroke-opacity="0.5"/>',
        '<path d="M770 168 q40 0 40 30 q0 30 -36 30" fill="none" stroke="#B07A94" stroke-width="7" stroke-linecap="round"/>',
        '<path d="M630 152 H770 V182 Q770 234 700 234 Q630 234 630 182 Z" fill="#FFF8F3" stroke="#B07A94" stroke-width="3"/>',
        '<ellipse cx="700" cy="152" rx="70" ry="10" fill="#D9A98C" stroke="#B07A94" stroke-width="2"/>',
        '<path d="M700 214 c-16 -11 -22 -24 -11 -30 c6 -3 11 0 11 5 c0 -5 5 -8 11 -5 c11 6 5 19 -11 30z" fill="#F4C6CC"/>',
    ]
    for i, x in enumerate([675, 700, 725]):
        parts.append(f'<path class="st" d="M{x} 140 c-9 -13 9 -22 0 -36" fill="none" stroke="#B07A94" stroke-width="4" '
                     f'stroke-linecap="round" style="animation-delay:{i * 0.9}s"/>')
    parts += [
        f'<text x="56" y="132" font-family="{SERIF}" font-size="68" font-weight="bold" fill="{INK}">Poojashree</text>',
        f'<text x="58" y="178" font-family="{SERIF}" font-size="23" font-style="italic" fill="#8E6B86">dear data, let me tell your story</text>',
        f'<text x="58" y="216" font-family="{SANS}" font-size="15" letter-spacing="1.5" fill="{INK}" opacity="0.8">BCA DATA SCIENCE  ·  ALLIANCE UNIVERSITY</text>',
        '<rect x="58" y="238" width="190" height="32" rx="16" fill="#B07A94" opacity="0.18"/>',
        f'<text x="153" y="259" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="600" fill="{INK}">aspiring data analyst</text>',
    ]
    return svg(900, 300, "".join(parts), style)


def divider_svg():
    style = (".w{stroke-dasharray:6 8;animation:d 2s linear infinite}"
             "@keyframes d{to{stroke-dashoffset:-28}}"
             ".f{transform-box:fill-box;transform-origin:center;animation:b 3s ease-in-out infinite}"
             "@keyframes b{50%{transform:scale(1.25)}}")
    flower = "".join(
        f'<circle cx="{450 + 6 * math.cos(math.radians(a)):.1f}" cy="{14 + 6 * math.sin(math.radians(a)):.1f}" r="4" fill="{c}"/>'
        for a, c in zip(range(0, 360, 72), ["#F4C6CC", "#E6DDF2", "#CFE3D0", "#FBEBCB", "#F4C6CC"]))
    body = ('<path class="w" d="M20 14 Q60 2 100 14 T180 14 T260 14 T340 14 T420 14" fill="none" stroke="#B07A94" stroke-opacity="0.55" stroke-width="2" stroke-linecap="round"/>'
            '<path class="w" d="M480 14 Q520 2 560 14 T640 14 T720 14 T800 14 T880 14" fill="none" stroke="#B07A94" stroke-opacity="0.55" stroke-width="2" stroke-linecap="round"/>'
            f'<g class="f">{flower}<circle cx="450" cy="14" r="3.2" fill="#B07A94"/></g>')
    return svg(900, 28, body, style)


def quote_svg():
    text = QUOTES[dt.date.today().toordinal() % len(QUOTES)]
    style = (".q{animation:in 1.6s ease-out both}@keyframes in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
             ".h{animation:pu 3s ease-in-out infinite}@keyframes pu{50%{opacity:.35}}")
    body = (f'<rect x="2" y="2" width="896" height="106" rx="26" fill="{CREAM}" stroke="#E8A0B0" stroke-width="2" stroke-dasharray="5 7"/>'
            f'<text x="44" y="78" font-family="{SERIF}" font-size="80" fill="#F4C6CC">“</text>'
            f'<text class="q" x="450" y="66" text-anchor="middle" font-family="{SERIF}" font-size="25" font-style="italic" fill="{INK}">{esc(text)}</text>'
            f'<text x="450" y="92" text-anchor="middle" font-family="{SANS}" font-size="11" letter-spacing="3" fill="{MAUVE}">NOTE FOR TODAY</text>'
            '<path class="h" transform="translate(846 38)" d="M0 12 c-12 -9 -17 -19 -8 -24 c5 -3 8 0 8 4 c0 -4 3 -7 8 -4 c9 5 4 15 -8 24z" fill="#E8A0B0"/>')
    return svg(900, 110, body, style)


def skills_svg():
    chips, x = [], 0
    for i, name in enumerate(SKILLS):
        w = 30 + int(8.2 * len(name))
        bg, ink = PALETTE[i % len(PALETTE)]
        chips.append((x, w, name, bg, ink))
        x += w + 14
    total = x

    def row(offset):
        return "".join(
            f'<g transform="translate({cx + offset} 12)"><rect width="{w}" height="38" rx="19" fill="{bg}" stroke="{ink}" stroke-opacity="0.25"/>'
            f'<text x="{w / 2}" y="24" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="600" fill="{ink}">{esc(name)}</text></g>'
            for cx, w, name, bg, ink in chips)

    style = f".m{{animation:sc {max(18, total // 40)}s linear infinite}}@keyframes sc{{to{{transform:translateX(-{total}px)}}}}"
    body = (f'<defs><clipPath id="c"><rect width="900" height="62" rx="20"/></clipPath></defs>'
            f'<g clip-path="url(#c)"><g class="m">{row(0)}{row(total)}{row(total * 2)}</g></g>')
    return svg(900, 62, body, style)


def now_svg(title, when):
    style = ".d{animation:pl 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}@keyframes pl{0%{transform:scale(1);opacity:.7}100%{transform:scale(3);opacity:0}}"
    body = (f'<rect x="2" y="2" width="896" height="116" rx="28" fill="{CREAM}" stroke="#B9D4BC" stroke-width="2"/>'
            '<circle cx="56" cy="60" r="9" fill="#7FB38A"/><circle class="d" cx="56" cy="60" r="9" fill="#7FB38A"/>'
            f'<text x="92" y="46" font-family="{SANS}" font-size="12" letter-spacing="3" fill="#6E9A78">CURRENTLY ON MY DESK</text>'
            f'<text x="92" y="88" font-family="{SERIF}" font-size="34" font-weight="bold" fill="{INK}">{esc(title)}</text>'
            f'<text x="858" y="68" text-anchor="end" font-family="{SERIF}" font-size="17" font-style="italic" fill="#8E6B86">last push · {esc(when)}</text>')
    return svg(900, 120, body, style)


def timeline_svg():
    n = len(TIMELINE)
    step = 660 / (n - 1)
    style = ".n{animation:pp 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}@keyframes pp{50%{transform:scale(1.3)}}"
    parts = [f'<rect x="2" y="2" width="896" height="196" rx="28" fill="{CREAM}" stroke="#E6DDF2" stroke-width="2"/>',
             '<line x1="120" x2="780" y1="90" y2="90" stroke="#B07A94" stroke-opacity="0.5" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>']
    for i, (label, title, sub) in enumerate(TIMELINE):
        cx = 120 + step * i
        bg, ink = PALETTE[i % len(PALETTE)]
        parts.append(f'<text x="{cx}" y="60" text-anchor="middle" font-family="{SERIF}" font-size="24" font-weight="bold" fill="{ink}">{esc(label)}</text>')
        parts.append(f'<circle class="n" cx="{cx}" cy="90" r="11" fill="{bg}" stroke="{ink}" stroke-width="3" style="animation-delay:{i * 0.6}s"/>')
        parts.append(f'<text x="{cx}" y="128" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="600" fill="{INK}">{esc(title)}</text>')
        for j, line in enumerate(textwrap.wrap(sub, 22)[:2]):
            parts.append(f'<text x="{cx}" y="{150 + 18 * j}" text-anchor="middle" font-family="{SERIF}" font-size="14" font-style="italic" fill="#8E6B86">{esc(line)}</text>')
    return svg(900, 200, "".join(parts), style)


def stats_svg(user, repos):
    own = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in own)
    langs = collections.Counter(r["language"] for r in own if r.get("language")).most_common(5)
    tiles = [("public repos", user.get("public_repos", len(own))), ("followers", user.get("followers", 0)),
             ("stars earned", stars), ("languages", len(collections.Counter(r["language"] for r in own if r.get("language"))))]
    style = (".b{transform-box:fill-box;transform-origin:left center;animation:gr 1.4s ease-out both}"
             "@keyframes gr{from{transform:scaleX(0)}}")
    parts = []
    for i, (label, value) in enumerate(tiles):
        bg, ink = PALETTE[i]
        x = 20 + i * 220
        parts.append(f'<rect x="{x}" y="20" width="200" height="86" rx="22" fill="{bg}" stroke="{ink}" stroke-opacity="0.2"/>'
                     f'<text x="{x + 100}" y="66" text-anchor="middle" font-family="{SERIF}" font-size="38" font-weight="bold" fill="{ink}">{value}</text>'
                     f'<text x="{x + 100}" y="90" text-anchor="middle" font-family="{SANS}" font-size="12" letter-spacing="2" fill="{ink}" opacity="0.8">{label.upper()}</text>')
    y = 142
    top = langs[0][1] if langs else 1
    for i, (lang, count) in enumerate(langs):
        bg, ink = PALETTE[(i + 1) % len(PALETTE)]
        width = max(24, int(560 * count / top))
        parts.append(f'<text x="30" y="{y + 16}" font-family="{SANS}" font-size="14" font-weight="600" fill="{INK}">{esc(lang)}</text>'
                     f'<rect x="200" y="{y}" width="640" height="22" rx="11" fill="{CREAM}" stroke="{ink}" stroke-opacity="0.2"/>'
                     f'<rect class="b" x="200" y="{y}" width="{width}" height="22" rx="11" fill="{bg}" stroke="{ink}" stroke-opacity="0.5" style="animation-delay:{i * 0.15}s"/>'
                     f'<text x="{200 + width + 10}" y="{y + 16}" font-family="{SANS}" font-size="12" fill="{INK}">{count} repo{"s" if count != 1 else ""}</text>')
        y += 32
    h = max(y + 10, 150)
    back = f'<rect x="2" y="2" width="896" height="{h - 4}" rx="28" fill="{CREAM}" stroke="#E6DDF2" stroke-width="2"/>'
    return svg(900, h, back + "".join(parts), style)


# ---------------------------------------------------------- project cards --
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
    pill = lang or "project"
    pill_w = 18 + int(7.4 * len(pill))
    out = [
        f'<rect x="1" y="1" width="398" height="{height - 2}" rx="24" fill="{bg}" stroke="{ink}" stroke-opacity="0.18"/>',
        f'<circle cx="354" cy="42" r="46" fill="{ink}" opacity="0.07"/><circle cx="380" cy="98" r="18" fill="{ink}" opacity="0.06"/>',
        f'<rect x="24" y="24" width="{pill_w}" height="26" rx="13" fill="{ink}" opacity="0.13"/>',
        f'<text x="{24 + pill_w / 2}" y="42" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="600" fill="{ink}">{esc(pill)}</text>',
    ]
    for i, line in enumerate(t_lines):
        out.append(f'<text x="24" y="{title_y + 30 * i}" font-family="{SERIF}" font-size="25" font-weight="bold" fill="{ink}">{esc(line)}</text>')
    for i, line in enumerate(d_lines):
        out.append(f'<text x="24" y="{desc_y + 22 * i}" font-family="{SERIF}" font-size="15" font-style="italic" fill="{ink}" opacity="0.88">{esc(line)}</text>')
    out.append(f'<line x1="24" x2="376" y1="{foot_y - 24}" y2="{foot_y - 24}" stroke="{ink}" stroke-opacity="0.25" stroke-dasharray="3 5"/>')
    out.append(f'<text x="24" y="{foot_y}" font-family="{SANS}" font-size="13" fill="{ink}" opacity="0.8">★ {stars}   ·   updated {esc(updated)}</text>')
    return svg(400, height, "".join(out)), height


def match_featured(repos):
    items, used = [], set()
    for kw, title, desc in FEATURED:
        for repo in repos:
            if repo["name"] not in used and kw in norm(repo["name"]):
                used.add(repo["name"])
                items.append((repo, title, desc))
                break
    return items


def build_projects(items):
    CARDS.mkdir(parents=True, exist_ok=True)
    for old in CARDS.glob("*.svg"):
        old.unlink()
    cols, heights = [[], []], [0, 0]
    for idx, (repo, title, desc) in enumerate(items):
        card, h = card_svg(title, desc, repo.get("language"), repo.get("stargazers_count", 0), ago(repo["pushed_at"]), idx)
        name = f"{slug(repo['name'])}.svg"
        (CARDS / name).write_text(card, encoding="utf-8")
        t = 0 if heights[0] <= heights[1] else 1
        heights[t] += h + 16
        cols[t].append(f'<a href="{repo["html_url"]}"><img src="assets/cards/{name}" width="100%" alt="{esc(title)}"/></a>')
    if not items:
        return "_projects loading, check back soon_ 🌸"
    cells = "\n".join('<td width="50%" valign="top">\n' + "\n<br/>\n".join(c) + "\n</td>" for c in cols)
    return f'<table width="100%">\n<tr>\n{cells}\n</tr>\n</table>'


# ---------------------------------------------------------------- activity --
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
    try:
        user = api(f"/users/{USER}")
    except Exception:
        user = {}

    items = match_featured(repos)
    recent = [r for r in repos if r["name"] != USER and not r.get("fork")]
    if recent:
        latest = recent[0]
        title = next((t for r, t, _ in items if r["name"] == latest["name"]), latest["name"])
        save("now.svg", now_svg(title, ago(latest["pushed_at"])))

    save("hero.svg", hero_svg())
    save("divider.svg", divider_svg())
    save("quote.svg", quote_svg())
    save("skills.svg", skills_svg())
    save("timeline.svg", timeline_svg())
    save("stats.svg", stats_svg(user, repos))

    text = README.read_text(encoding="utf-8")
    text = replace_section(text, "projects", build_projects(items))
    text = replace_section(text, "activity", build_activity())
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    text = replace_section(text, "updated", f"<sub>last synced {stamp}</sub>")
    README.write_text(text, encoding="utf-8")
    print("profile refreshed")


if __name__ == "__main__":
    main()
