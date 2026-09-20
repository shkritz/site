#!/usr/bin/env python3
"""
Builds a static publications site from publications.json.
Run:  python3 build.py
Then commit the generated files.
"""

import json, os, html, shutil

# ---------------------------------------------------------------- CONFIG
NAME    = "Shai Kritz"
DOMAIN  = "shaikritz.com"          # <-- change if you register a different domain
EMAIL   = "shkritz@gmail.com"     # <-- change
LINKEDIN = "https://www.linkedin.com/in/YOUR-HANDLE"   # <-- change
ORCID    = "https://orcid.org/0000-0000-0000-0000"     # <-- change
POSITIONING = ("I build measurement and risk frameworks for systems nobody controls "
               "&mdash; first in decentralised finance, now in enterprise AI.")
ABOUT = [
    "I work on risk and governance for AI systems that act on their own. The problem is "
    "concrete: measure what an autonomous system is actually doing, set the bounds it has "
    "to operate inside, and be able to demonstrate afterwards that it stayed there. "
    "Enterprises are deploying these systems faster than they can answer any of those "
    "three questions.",
    "At Chaos Labs I lead the research behind Cortex, where those three questions are the "
    "product: attributing AI work to the outcomes it produced, evaluating which models and "
    "workflows are worth running, and enforcing the mandate an agent operates under.",
    "The four years before that were the same problem in a different market. I led the "
    "research practice at Chaos Labs' decentralised finance risk business, the category "
    "leader in its field, and the papers below are its output &mdash; frameworks for "
    "setting parameters on systems with no operating history, stress tests of protocols "
    "whose failure modes had never been observed, and methodologies built to be applied "
    "again rather than once.",
    "The through-line is a single question asked of two substrates. You are handed a "
    "system you do not control, driven by participants or by models whose behaviour you "
    "cannot dictate, and asked how far it can be pushed before it stops doing what it was "
    "designed to do. Answering that takes measurement you can defend, bounds you can "
    "justify, and the discipline to state plainly what your model does not cover. "
    "Financial protocols and autonomous agents differ in mechanism, not in what the "
    "question demands.",
]
# ------------------------------------------------------------ END CONFIG

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_PUB = os.path.join(ROOT, "publications")

CSS = """/* ---- tokens ---- */
:root{
  --bg:#fbfaf8; --fg:#1a1a18; --muted:#6b6b63; --rule:#e2ddd4;
  --accent:#8a5a2b; --card:#ffffff;
  --serif: "Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans: -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#131311; --fg:#eceae4; --muted:#9a968c; --rule:#2d2c28;
    --accent:#c99a63; --card:#1a1a17;
  }
}
:root[data-theme="dark"]{
  --bg:#131311; --fg:#eceae4; --muted:#9a968c; --rule:#2d2c28;
  --accent:#c99a63; --card:#1a1a17;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--fg);
  font-family:var(--serif); font-size:18px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:720px; margin:0 auto; padding:0 16px}
a{color:inherit; text-decoration:none; border-bottom:1px solid var(--rule)}
a:hover{border-bottom-color:var(--accent); color:var(--accent)}

/* ---- header ---- */
header{padding:72px 0 40px; border-bottom:1px solid var(--rule)}
h1{font-size:34px; line-height:1.15; margin:0 0 14px; letter-spacing:-.01em; font-weight:600}
.positioning{font-size:20px; color:var(--muted); margin:0; max-width:36em}

/* ---- sections ---- */
section{padding:44px 0; border-bottom:1px solid var(--rule)}
section:last-of-type{border-bottom:none}
h2{
  font-family:var(--sans); font-size:12px; font-weight:600; letter-spacing:.11em;
  text-transform:uppercase; color:var(--muted); margin:0 0 22px;
}
p{margin:0 0 16px}
p:last-child{margin-bottom:0}

/* ---- publication list ---- */
ol.pubs{list-style:none; margin:0; padding:0}
ol.pubs li{padding:18px 0; border-bottom:1px solid var(--rule)}
ol.pubs li:last-child{border-bottom:none}
.pub-title{font-size:19px; font-weight:600; line-height:1.35; display:block; border:none}
.pub-title:hover{color:var(--accent)}
.pub-meta{
  font-family:var(--sans); font-size:12.5px; color:var(--muted);
  letter-spacing:.02em; margin-top:6px;
}
.pub-sum{font-size:16.5px; color:var(--muted); margin-top:8px; max-width:40em}

/* ---- paper page ---- */
.back{
  font-family:var(--sans); font-size:12.5px; letter-spacing:.05em;
  text-transform:uppercase; color:var(--muted); border:none;
}
.back:hover{color:var(--accent)}
article h1{font-size:28px; margin:22px 0 18px}
.meta-block{
  font-family:var(--sans); font-size:14px; color:var(--muted);
  border-left:2px solid var(--rule); padding-left:16px; margin:0 0 28px;
}
.meta-block div{margin-bottom:5px}
.meta-block div:last-child{margin-bottom:0}
.meta-block b{color:var(--fg); font-weight:600}
.cta{
  display:inline-block; font-family:var(--sans); font-size:14.5px; font-weight:600;
  border:1px solid var(--rule); border-radius:3px; padding:11px 18px; margin-top:8px;
  background:var(--card);
}
.cta:hover{border-color:var(--accent); color:var(--accent)}
.hosted{font-family:var(--sans); font-size:12.5px; color:var(--muted); margin-top:12px}

/* ---- footer ---- */
footer{
  padding:36px 0 64px; font-family:var(--sans); font-size:14px; color:var(--muted);
}
footer a{border-bottom:1px solid var(--rule)}

@media (max-width:600px){
  body{font-size:17px}
  header{padding:48px 0 32px}
  h1{font-size:28px}
  .positioning{font-size:18px}
  article h1{font-size:24px}
}
"""

def slugify(t):
    keep = "".join(c.lower() if (c.isalnum() or c == " ") else " " for c in t)
    words, out = keep.split(), []
    for w in words:
        if out and len("-".join(out + [w])) > 70:
            break
        out.append(w)
    return "-".join(out)

def head(title, desc, url, extra="", image=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:type" content="{extra or 'website'}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{html.escape(NAME)}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{image}">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<link rel="stylesheet" href="{'../' if extra else ''}style.css">
</head>
<body>
"""

FOOTER = f"""<footer><div class="wrap">
<a href="mailto:{EMAIL}">{EMAIL}</a> &nbsp;&middot;&nbsp;
<a href="{LINKEDIN}">LinkedIn</a> &nbsp;&middot;&nbsp;
<a href="{ORCID}">ORCID</a>
</div></footer>
</body></html>
"""


# ---- social card images ----
OG_DIR = os.path.join(ROOT, "og")
# Font candidates, tried in order: Windows, macOS, Linux.
F_SERIF_B = ["georgiab.ttf", "timesbd.ttf",
             "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
             "/Library/Fonts/Georgia Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
             "DejaVuSerif-Bold.ttf"]
F_SANS    = ["segoeui.ttf", "arial.ttf",
             "/System/Library/Fonts/Supplemental/Arial.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "DejaVuSans.ttf"]
F_SANS_B  = ["segoeuib.ttf", "arialbd.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "DejaVuSans-Bold.ttf"]

def _font(candidates, size):
    from PIL import ImageFont
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    raise SystemExit(
        "No usable font found. Tried: " + ", ".join(candidates) +
        "\nEdit the F_SERIF_B / F_SANS / F_SANS_B lists in build.py "
        "to point at a .ttf file on this machine.")

def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def og_card(path, kicker, title, footer):
    """1200x630 card matching the site palette."""
    from PIL import Image, ImageDraw
    W, H, M = 1200, 630, 88
    BG, FG, MUTED, ACCENT = "#fbfaf8", "#1a1a18", "#6b6b63", "#8a5a2b"
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 10, H], fill=ACCENT)          # accent spine

    f_kick = _font(F_SANS_B, 21)
    f_foot = _font(F_SANS, 24)

    d.text((M, 78), kicker.upper(), font=f_kick, fill=MUTED)

    # shrink title until it fits in at most 5 lines
    for size in (60, 54, 48, 43, 38, 34):
        f_title = _font(F_SERIF_B, size)
        lines = _wrap(d, title, f_title, W - 2 * M)
        lh = int(size * 1.26)
        if len(lines) * lh <= 300:
            break
    top, bottom = 150, H - 150            # region between kicker and rule
    y = top + max(0, ((bottom - top) - len(lines) * lh) // 2)
    for ln in lines:
        d.text((M, y), ln, font=f_title, fill=FG)
        y += lh

    d.line([(M, H - 118), (W - M, H - 118)], fill="#e2ddd4", width=2)
    d.text((M, H - 92), footer, font=f_foot, fill=MUTED)
    img.save(path, "PNG", optimize=True)

def build():
    with open(os.path.join(ROOT, "publications.json")) as f:
        pubs = json.load(f)

    if os.path.isdir(OUT_PUB):
        shutil.rmtree(OUT_PUB)
    os.makedirs(OUT_PUB)
    if os.path.isdir(OG_DIR):
        shutil.rmtree(OG_DIR)
    os.makedirs(OG_DIR)
    og_card(os.path.join(OG_DIR, "index.png"), NAME,
            POSITIONING.replace("&mdash;", "—"), "Publications")

    with open(os.path.join(ROOT, "style.css"), "w") as f:
        f.write(CSS)

    # ---- individual paper pages ----
    for p in pubs:
        slug = slugify(p["title"])
        p["slug"] = slug
        url = f"https://{DOMAIN}/publications/{slug}.html"
        co = [c for c in p["authors"] if c != NAME]
        body = head(f'{p["title"]} — {NAME}', p["summary"], url, extra="article",
                    image=f"https://{DOMAIN}/og/{slug}.png")
        body += f"""<div class="wrap">
<article>
<p style="padding-top:40px"><a class="back" href="../index.html">&larr; {html.escape(NAME)}</a></p>
<h1>{html.escape(p["title"])}</h1>
<div class="meta-block">
  <div><b>Published</b> &nbsp;{html.escape(p["date"])} &middot; Chaos Labs</div>
  <div><b>Contribution</b> &nbsp;{html.escape(p["role"])}</div>
  <div><b>Authors</b> &nbsp;{", ".join(("<b>" + html.escape(a) + "</b>") if a == NAME else html.escape(a) for a in p["authors"])}</div>
</div>
<p>{html.escape(p["summary"])}</p>
<p><a class="cta" href="{p["url"]}" rel="noopener">Read the paper &rarr;</a></p>
<p class="hosted">Published by Chaos Labs and hosted on their site.</p>
</article>
</div>
"""
        body += FOOTER
        with open(os.path.join(OUT_PUB, f"{slug}.html"), "w") as f:
            f.write(body)
        og_card(os.path.join(OG_DIR, f"{slug}.png"),
                f'Chaos Labs · {p["date"]}', p["title"], NAME)

    # ---- index ----
    idx = head(NAME, POSITIONING.replace("&mdash;", "—"), f"https://{DOMAIN}/",
               image=f"https://{DOMAIN}/og/index.png")
    idx += f"""<div class="wrap">
<header>
  <h1>{html.escape(NAME)}</h1>
  <p class="positioning">{POSITIONING}</p>
</header>

<section>
  <h2>Publications</h2>
  <ol class="pubs">
"""
    for p in pubs:
        co = [c for c in p["authors"] if c != NAME]
        co_s = f" &middot; with {html.escape(', '.join(co))}" if co else ""
        idx += f"""    <li>
      <a class="pub-title" href="publications/{p['slug']}.html">{html.escape(p["title"])}</a>
      <div class="pub-meta">{html.escape(p["date"])} &middot; Chaos Labs{co_s}</div>
      <div class="pub-sum">{html.escape(p["summary"])}</div>
    </li>
"""
    idx += """  </ol>
</section>

<section>
  <h2>About</h2>
"""
    for para in ABOUT:
        idx += f"  <p>{para}</p>\n"
    idx += """</section>
</div>
"""
    idx += FOOTER
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(idx)

    with open(os.path.join(ROOT, "CNAME"), "w") as f:
        f.write(DOMAIN + "\n")

    print(f"Built index.html + {len(pubs)} pages in publications/ + {len(pubs)+1} cards in og/")

if __name__ == "__main__":
    build()
