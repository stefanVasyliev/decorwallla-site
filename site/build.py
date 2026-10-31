#!/usr/bin/env python3
"""DecorWall LA site generator.

Builds every page of decorwallla.com in the site's own design: the hand-built home page
(index.html at the repo root) plus service, style, city and core pages generated from the
content in site/data/. Data files are read as plain literals (see data_load.py).

    python3 site/build.py            -> dist/     clean URLs, for the hosting
    python3 site/build.py --preview  -> preview/  relative links, opens straight from the files
"""
import hashlib, html, json, os, random, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_load import CITIES, SERVICES, STYLES, DETAIL_ALT, STEPS_B, FAQ_ALT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = "--preview" in sys.argv
OUT = os.path.join(ROOT, "preview" if PREVIEW else "dist")

BASE = "https://decorwallla.com"
PHONE = "(213) 913-5312"
PHONE_TEL = "+12139135312"
EMAIL = "hello@decorwallla.com"
INSTAGRAM = "decorwallla"
WHATSAPP = ""  # PLACEHOLDER: WhatsApp number, digits only with country code, e.g. 12139135312
FORM_ACTION = "https://formsubmit.co/hello@decorwallla.com"
ASSET_V = "20261031"

def esc(s): return html.escape(s, quote=True)

def pick(variants, *keys):
    h = hashlib.md5("|".join(keys).encode()).hexdigest()
    return variants[int(h[:6], 16) % len(variants)]

def money(n): return f"${n:,}"

# Small slat mark from the logo; used where a link needs a visual cue (no arrows on this site).
ARROW = '<svg class="mark" viewBox="0 0 18 16" fill="currentColor" aria-hidden="true"><path d="M1 1.5l3 .9v11.2l-3 .9zM5.6 2.9l2 .6v9l-2 .6zM9.2 4l1.8.5v7l-1.8.5zM12.6 5l1.6.5v5l-1.6.5zM15.8 6l1.4.4v3.2l-1.4.4z"/></svg>'
WA_ICON = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.2a9.7 9.7 0 0 0-8.3 14.8L2.4 21.7l4.8-1.3A9.7 9.7 0 1 0 12 2.2Zm0 17.7a8 8 0 0 1-4.1-1.1l-.3-.2-2.8.8.8-2.8-.2-.3A8 8 0 1 1 12 19.9Zm4.4-6c-.2-.1-1.4-.7-1.7-.8-.2-.1-.4-.1-.5.1l-.8.9c-.1.2-.3.2-.5.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 0 0-.7.3 2.8 2.8 0 0 0-.9 2.1 5 5 0 0 0 1 2.6 11.2 11.2 0 0 0 4.3 3.8c1.6.7 2.2.7 3 .6.5-.1 1.4-.6 1.6-1.1.2-.6.2-1 .1-1.1l-.5-.2Z"/></svg>')

# WhatsApp button that sits next to every button leading to the estimate form; site.js fills in the link.
WA_BTN = f'<a class="btn-wa" data-wa href="#" target="_blank" rel="noopener">{WA_ICON}WhatsApp</a>'

CITY = {c[0]: {"slug": c[0], "name": c[1], "county": c[2], "miles": c[3], "hoods": c[4], "housing": c[5], "landmark": c[6]} for c in CITIES}
SVC = {s["slug"]: s for s in SERVICES}

# One full-resolution photo per service, shared by its hub and every city page for it.
SERVICE_IMAGES = {
    "tv-media-walls": ("full-built-in.webp", "floor-to-ceiling built-in media wall in walnut with lit display shelving and a linear fireplace"),
    "accent-walls": ("shiplap-panels.webp", "white shiplap feature wall with a natural wood mantel beam and electric fireplace"),
    "stone-marble-walls": ("stone-marble.webp", "floor-to-ceiling black marble-look porcelain slabs with white and gold veining and a centered TV"),
    "fireplace-walls": ("fireplace-wall.webp", "fluted walnut niches flanking a wide linear fireplace with a stone surround"),
    "walnut-slat-walls": ("minimalist-tv-wall.webp", "single smooth charcoal panel TV wall with a thin linear fireplace"),
}

NAV = [("Media Walls", "/tv-media-walls/"), ("Slat Walls", "/walnut-slat-walls/"), ("Stone", "/stone-marble-walls/"),
       ("Fireplace", "/fireplace-walls/"), ("Styles", "/styles/"), ("Cost", "/cost/"), ("Areas", "/service-areas/")]

# ------------------------------------------------------------------ page shell

def schema_business():
    return json.dumps({
        "@context": "https://schema.org", "@type": "HomeAndConstructionBusiness", "name": "DecorWall LA",
        "url": BASE + "/", "email": EMAIL, "telephone": PHONE_TEL, "priceRange": "$$",
        "address": {"@type": "PostalAddress", "addressLocality": "Los Angeles", "addressRegion": "CA", "addressCountry": "US"},
        "areaServed": "Los Angeles and surrounding cities within 40 miles"})

def head(title, desc, path, extra_schema=""):
    canon = BASE + path
    schema = f'<script type="application/ld+json">{schema_business()}</script>'
    if extra_schema:
        schema += f'\n<script type="application/ld+json">{extra_schema}</script>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/assets/logo.webp">
<meta name="theme-color" content="#0e0e0e">
<link rel="icon" href="/assets/logo-black.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500&family=Instrument+Serif&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={ASSET_V}">
{schema}
</head>
<body data-whatsapp="{WHATSAPP}">
{header()}
<main>
"""

def header():
    links = "".join(f'<a href="{href}">{label}</a>' for label, href in NAV)
    menu = "".join(f'<a href="{href}">{label}</a>' for label, href in NAV + [("Get estimate", "/#cost")])
    return f"""<header class="header" data-header>
  <a href="/" class="logo"><img src="/assets/logo-white.svg" alt="DecorWall LA" width="160" height="35"></a>
  <nav class="nav" aria-label="Main">{links}</nav>
  <a href="/#cost" class="cta btn-primary">Get estimate</a>
  <button type="button" class="burger" data-burger aria-label="Menu" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
</header>
<div class="menu" id="menu" data-menu hidden>{menu}</div>"""

FOOT_CITIES = [c for c in CITIES if c[3] <= 16][:8]

def footer(dock=True):
    svcs = "".join(f'<li><a href="/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    cities = "".join(f'<li><a href="/media-walls-{c[0]}/">{c[1]}</a></li>' for c in FOOT_CITIES)
    dock_html = f"""
<div class="dock" data-dock><a class="wa" data-wa href="#" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{WA_ICON}</a></div>""" if dock else ""
    return f"""</main>
<footer class="foot"><div class="wrap">
  <div class="foot-top">
    <div><p class="foot-brand"><img src="/assets/logo-white.svg" alt="DecorWall LA" width="200" height="38"></p>
      <p>Custom media walls, walnut slat walls, stone feature walls and decorative panels across Los Angeles and nearby cities.</p>
      <p><a href="tel:{PHONE_TEL}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
    <div><h4>Services</h4><ul>{svcs}</ul></div>
    <div><h4>Studio</h4><ul><li><a href="/styles/">Design styles</a></li><li><a href="/cost/">Cost</a></li><li><a href="/process/">Process</a></li><li><a href="/materials/">Materials</a></li><li><a href="/projects/">Projects</a></li><li><a href="/about/">About</a></li><li><a href="/faq/">FAQ</a></li></ul></div>
    <div><h4>Areas</h4><ul>{cities}<li><a href="/service-areas/">All service areas</a></li></ul></div>
  </div>
  <div class="foot-bottom"><span>&copy; 2026 DecorWall LA &middot; Los Angeles, CA</span><span>Design concepts shown are previews, not completed installations. <a href="/privacy/">Privacy</a></span></div>
</div></footer>{dock_html}
<script src="/assets/site.js?v={ASSET_V}"></script>
</body></html>"""

# ------------------------------------------------------------------ building blocks

PERKS = ["Free design preview", "Written fixed estimate", "Local LA crew", "Reply within 1 business day"]

def crumbs(items):
    parts = ['<a href="/">Home</a>']
    for label, href in items:
        parts.append(f'<a href="{href}">{esc(label)}</a>' if href else f'<span>{esc(label)}</span>')
    return f'<nav class="crumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>'

def page_head(crumb_items, h1, lede="", price_from=None, img=None, img_alt="", actions=True):
    from_line = f'<p class="from">from <b>{money(price_from)}</b> &middot; free design preview &middot; written estimate</p>' if price_from else ""
    act = f"""<div class="actions"><a href="#estimate" class="btn-primary">Get my free design preview</a>{WA_BTN}</div>""" if actions else ""
    figure = f'<figure class="ph-img"><img src="/assets/styles/{img}" alt="{esc(img_alt)}" width="2048" height="1152"><figcaption>Design concept</figcaption></figure>' if img else ""
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    return f"""<section class="ph{" ph-split" if img else ""}"><div class="wrap">
  <div class="ph-text">{crumbs(crumb_items)}
  <h1>{h1}</h1>{lede_html}{from_line}{act}</div>{figure}
</div></section>"""

def sec(inner, paper=False, sid=""):
    cls = "sec paper" if paper else "sec"
    idattr = f' id="{sid}"' if sid else ""
    return f'<section class="{cls}"{idattr}><div class="wrap">{inner}</div></section>'

def sec_head(title, text=""):
    p = f"<p>{text}</p>" if text else ""
    return f'<div class="sec-head"><h2 class="h2">{title}</h2>{p}</div>'

def checks(items): return '<ul class="checks">' + "".join(f"<li>{i[:1].upper() + i[1:]}</li>" for i in items) + "</ul>"

def links(items): return '<ul class="links">' + "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for t, h in items) + "</ul>"

INCLUDED_ITEMS = ["Design preview from your photo", "Written fixed estimate", "Framing and panel installation",
                  "TV mounting and concealed cables", "LED lighting setup where selected", "Paint, finish and final cleanup"]

STEPS_A = [
    ("STEP 1 - DESIGN PREVIEW", "You send a photo of your room. We design the wall around your space, screen and equipment, and send back a concept with a written estimate."),
    ("STEP 2 - MATERIALS & SCHEDULE", "You approve the design and materials. We order everything and schedule the build days - most materials are prepared before we arrive."),
    ("STEP 3 - BUILD", "Our crew builds the wall in layers: framing, finish, cabinetry, lighting and equipment. The room is protected and the site is cleaned daily."),
    ("STEP 4 - WALKTHROUGH", "We mount and connect the equipment, test lighting and remotes with you, and walk every seam and edge together before final payment."),
]

def step_title(t):
    t = t.split(" - ", 1)[-1]
    return t[:1] + t[1:].lower()

def steps(key=""):
    """The four steps as one wall changing: bare, designed, built, lit. Same on every page."""
    return slat_steps()

def samples(items):
    """Short points shown on material samples (walnut, stone, marble, clay...), lit from above."""
    return '<ul class="samples">' + "".join(f'<li class="sample s-{m} reveal"><h3>{t}</h3><p>{d}</p></li>' for t, d, m in items) + "</ul>"

def faq_html(faqs):
    return '<div class="faq">' + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs) + "</div>"

def faq_schema(faqs):
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})

def band(title="Get a free design preview of <strong>your room</strong>",
         text="Send a photo and we reply with a design concept and a written estimate, usually within one business day."):
    return f"""<section class="band paper"><div class="wrap">
  <h2 class="h2">{title}</h2><p>{text}</p>
  <div class="actions"><a href="#estimate" class="btn-primary">Request my free preview</a>{WA_BTN}</div>
</div></section>"""

BUDGETS = ["$2,500 - $5,000", "$5,000 - $8,000", "$8,000 - $12,000", "$12,000+", "Not sure yet"]
CAMERA = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<path d="M2 5.5h2.5L6 3.5h4l1.5 2H14v7H2z"/><circle cx="8" cy="9" r="2.3"/></svg>')

def chips(name, options, selected=None, kind="radio"):
    return '<div class="chips">' + "".join(
        f'<label class="chip"><input type="{kind}" name="{name}" value="{esc(o)}"{" checked" if o == selected else ""}><span>{esc(o)}</span></label>'
        for o in options) + "</div>"

def form_block(city=None, svc=None):
    """The estimate form, in the same option-and-chip language as the wall builder, kept short."""
    datalist = "".join(f'<option value="{esc(c[1])}">' for c in CITIES)
    return f"""<section class="sec" id="estimate"><div class="wrap form">
  <div class="form-intro">
    <h2 class="h2">Your free <strong>design preview</strong></h2>
    <p>Send a photo of your room. We reply with a design concept for your wall and a written estimate. No visit, no obligation.</p>
    <p class="form-built" data-form-built hidden><small>From the wall builder</small><span></span></p>
    <p class="contact"><a href="tel:{PHONE_TEL}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="https://instagram.com/{INSTAGRAM}" target="_blank" rel="noopener">@{INSTAGRAM}</a></p>
  </div>
  <form action="{FORM_ACTION}" method="post" enctype="multipart/form-data" data-form>
    <fieldset class="opt"><legend>Project</legend>{chips("service", [s["name"] for s in SERVICES] + ["Not sure yet"], svc["name"] if svc else None)}</fieldset>
    <fieldset class="opt"><legend>Budget <small>optional</small></legend>{chips("budget", BUDGETS)}</fieldset>
    <fieldset class="opt"><legend>Your room</legend>
      <label class="file" data-file><input type="file" name="photos" accept="image/*" multiple><span>{CAMERA}<span data-file-label>Add photos</span></span></label>
      <p class="opt-hint">One photo of the wall is enough for a first concept.</p>
    </fieldset>
    <div class="fields">
      <div class="field"><label for="f-name">Name *</label><input id="f-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="f-phone">Phone *</label><input id="f-phone" name="phone" required type="tel" autocomplete="tel"></div>
      <div class="field"><label for="f-city">City</label><input id="f-city" name="city" list="f-cities" autocomplete="address-level2" value="{esc(city["name"]) if city else ""}"><datalist id="f-cities">{datalist}</datalist></div>
      <div class="field wide"><label for="f-msg">Anything else <span class="muted">(optional)</span></label><textarea id="f-msg" name="message" placeholder="Wall size, equipment, a fireplace, storage..."></textarea></div>
    </div>
    <input type="hidden" name="builder" data-form-builder>
    <input type="hidden" name="page_city" value="{esc(city["name"]) if city else ""}"><input type="hidden" name="page_service" value="{esc(svc["name"]) if svc else ""}">
    <input type="hidden" name="utm_source" data-utm="utm_source"><input type="hidden" name="utm_medium" data-utm="utm_medium"><input type="hidden" name="utm_campaign" data-utm="utm_campaign">
    <input type="hidden" name="_next" value="{BASE}/thank-you/"><input type="hidden" name="_subject" value="New DecorWall LA design preview request"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false"><input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
    <div class="form-send"><button class="btn-primary" type="submit">Request my free design preview</button>{WA_BTN}<p class="small">We reply within one business day. Photos are used only for your design preview.</p></div>
  </form>
</div></section>"""

def style_card(st):
    price = f"from {money(st['price_from'])}" if st["price_from"] else "Priced by design"
    return f"""<a class="card" href="/styles/{st["slug"]}/">
  <div class="card-img"><img src="/assets/styles/{st["image"]}" alt="{esc(st["alt"])} - design concept" loading="lazy" width="2048" height="1152"></div>
  <div class="card-top"><h3 class="card-name">{st["name"]}</h3><p class="card-price">{price}</p></div>
  <p class="card-text">{esc(st["tagline"])}</p>
</a>"""

def service_card(s, city=None):
    fn, desc = SERVICE_IMAGES[s["slug"]]
    href = f'/{s["slug"]}-{city["slug"]}/' if city else f'/{s["slug"]}/'
    name = f'{s["name"]} in {city["name"]}' if city else s["name"]
    return f"""<a class="card" href="{href}">
  <div class="card-img"><img src="/assets/styles/{fn}" alt="{esc(s["name"])} - {esc(desc)} - design concept" loading="lazy" width="2048" height="1152"></div>
  <div class="card-top"><h3 class="card-name">{name}</h3><p class="card-price">from {money(s["price_from"])}</p></div>
  <p class="card-text">{esc(s["hero_line"])}</p>
</a>"""

def price_table():
    rows = "".join(f'<tr><td><a href="/{s["slug"]}/">{s["name"]}</a></td><td>from {money(s["price_from"])}</td><td><a class="btn-link" href="#estimate">Get quote{ARROW}</a></td></tr>' for s in SERVICES)
    rows += "".join(f'<tr><td><a href="/styles/{st["slug"]}/">{st["name"]}</a> <span class="muted">style</span></td><td>{"from " + money(st["price_from"]) if st["price_from"] else "Priced by design"}</td><td><a class="btn-link" href="#estimate">Get this style{ARROW}</a></td></tr>' for st in STYLES)
    return f'<table class="prices">{rows}</table>'

def nearest(city, n=8):
    others = [c for c in CITIES if c[0] != city["slug"]]
    others.sort(key=lambda c: abs(c[3] - city["miles"]))
    return others[:n]

# ------------------------------------------------------------------ city x service copy (rotated per page)

INTRO_T = [
 "Homeowners in {city} usually call us for one reason: the biggest wall in the house is doing nothing. {hero}",
 "In {city}, the living room wall behind the TV is prime real estate - and in most homes it is a blank stretch of paint. {hero}",
 "A {short} is the single upgrade that changes how a {city} living room feels every day. {hero}",
 "We build {short}s across {city} for homeowners who want the room finished, not just furnished. {hero}",
 "If your {city} home has one wall that never looks right, it is probably the one this page is about. {hero}",
]
LOCAL_T = [
 "{city} homes - {housing} - give a {short} plenty to work with. In neighborhoods like {hoods}, we design around the architecture instead of covering it up: panel proportions follow the room, materials are chosen against the floors and light you already have, and the finished wall looks like it was always part of the house. {landmark} is the local reference point our crews work from - {city} is about {miles} miles from our Los Angeles base, well inside our regular service area, so scheduling and material deliveries run on the same timeline as our in-city projects.",
 "The housing stock in {city} is {housing}. That mix matters for a {short}: ceiling heights, wall spans and light vary street by street in {hoods}, so every design starts from a photo of your actual room, not a template. We regularly work across {city} - roughly {miles} miles out from central Los Angeles - and the local landmark our clients use to describe the area is {landmark}. Your project gets the same crew, materials and written estimate as any Los Angeles job.",
 "Ask around {hoods} and you will hear the same renovation story: the room is fine, but the main wall is blank. {city} homes are {housing}, and a well-proportioned {short} is usually the missing piece. We serve {city} from our Los Angeles base ({miles} miles), design from your room photo first, and build only after you approve the concept and the written number. The area around {landmark} is typical of where we work here.",
]
ANGLE_T = [
 "The selling point of a {short} is not any single material - it is that everything on the wall finally agrees: screen, storage, light and finish in one composition.",
 "What makes a {short} work is proportion. We size panels, cabinets and screen together, so nothing looks added-on and nothing fights the room.",
 "Homeowners compare a {short} to a feature wall from a furniture store. The difference is fit: ours is designed to your wall's exact width, your ceiling height and your equipment list.",
 "A {short} also solves practical problems: cables disappear, equipment gets ventilation and access, and the TV lands at the right height for your sofa - not wherever the studs happened to be.",
]
CLOSE_T = [
 "Start with the free preview: one photo of your room is enough for a first concept and an estimate range for your {city} home.",
 "The first step costs nothing: send the room photo through the form and see your wall designed before you commit to anything.",
 "Send us the photo, get the design and the number in writing, then decide. That is how most of our {city} projects start.",
]
IDEA_T = [
 "A typical {city} pattern: in {hood1}, a {short} built around {mat} turns the wall opposite the entry into the room's focal point, while over in {hood2} clients ask for the same design language at bedroom scale. One design pass covers both when they are planned together.",
 "Recent {city} requests cluster around two ideas: {opt} for the main living wall in {hood1}, and a calmer, quieter composition for a primary bedroom in {hood2}. The materials stay consistent - the proportions do the adapting.",
 "In {hood1}, walls often want width - long, low compositions that stretch the room. In {hood2}, the same {short} tends to run taller and simpler. Starting from your room photo is what lets us tune that rhythm to your street instead of shipping a showroom layout.",
]
PRICE_T = [
 "{svc_name} projects in {city} start at <b>${price}</b>. Your written estimate itemizes design, materials and labor for your exact wall, and it is fixed before the build starts. See the <a href=\"/cost/\">full cost guide</a> for what drives the number up or down.",
 "In {city}, {svc_plural} start at <b>${price}</b>. The final number depends on wall size, materials and options - all of it itemized in a written estimate that is fixed before any work begins. The <a href=\"/cost/\">cost guide</a> breaks down what moves the price.",
 "Budgeting in {city}: {svc_plural} start at <b>${price}</b>. After the free design preview you receive an itemized written estimate for your exact wall - design, materials and labor shown separately - and that number holds unless you change the scope. See the <a href=\"/cost/\">cost page</a> for the full breakdown.",
]

# A project photo per service for the build section, so it is not the same picture as the page head.
BUILD_PHOTOS = {"tv-media-walls": "project-2.webp", "walnut-slat-walls": "project-3.webp", "stone-marble-walls": "project-1.webp",
                "fireplace-walls": "project-5.webp", "accent-walls": "project-6.webp"}

def first_sentences(text, n=2):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(parts[:n])

def build_section(svc, detail, mats, opts):
    """How we build: a project photo beside one short idea and two compact lists; what is included
    as a row of small panels."""
    photo = BUILD_PHOTOS[svc["slug"]]
    incl = "".join(f'<li>{ARROW}<span>{i}</span></li>' for i in INCLUDED_ITEMS)
    return sec(f"""{sec_head(f'How we build a <strong>{svc["short"]}</strong>')}
<div class="build">
  <figure class="build-img"><img src="/assets/projects/{photo}" alt="{esc(svc["name"])} - design concept" loading="lazy"></figure>
  <div class="build-text">
    <p class="build-lead">{first_sentences(detail)}</p>
    <div class="build-lists"><div><h3 class="h3">Materials</h3>{checks(mats[:4])}</div><div><h3 class="h3">Options</h3>{checks(opts[:4])}</div></div>
  </div>
</div>
<h3 class="h3" style="margin-top:clamp(48px,6vw,80px)">What's included</h3><ul class="incl">{incl}</ul>""")

# ------------------------------------------------------------------ pages

def matrix_page(city, svc):
    name, short = city["name"], svc["short"]
    path = f'/{svc["slug"]}-{city["slug"]}/'
    title = f'{svc["name"]} in {name}, CA | DecorWall LA'
    desc = (f'Custom {short}s in {name}, CA - from {money(svc["price_from"])}. Free design preview from a photo of your room, '
            f'written estimate, professional installation across {city["county"]} County.')
    intro = pick(INTRO_T, city["slug"], svc["slug"]).format(city=name, hero=svc["hero_line"], short=short)
    local = pick(LOCAL_T, svc["slug"], city["slug"]).format(city=name, housing=city["housing"], short=short,
            hoods=", ".join(city["hoods"][:3]), landmark=city["landmark"], miles=city["miles"])
    angle = pick(ANGLE_T, city["slug"], svc["slug"], "a").format(short=short)
    close = pick(CLOSE_T, city["slug"], svc["slug"], "c").format(city=name)
    detail = pick([svc["detail"]] + DETAIL_ALT.get(svc["slug"], []), city["slug"], svc["slug"], "d")
    hoods = city["hoods"]
    idea = pick(IDEA_T, city["slug"], svc["slug"], "i").format(
        city=name, short=short, hood1=hoods[0], hood2=hoods[1] if len(hoods) > 1 else hoods[0],
        mat=pick(svc["materials"], city["slug"], "m"), opt=pick(svc["options"], city["slug"], "o"))
    price_txt = pick(PRICE_T, city["slug"], svc["slug"], "p").format(
        svc_name=svc["name"], svc_plural=short + "s", city=name, price=f'{svc["price_from"]:,}')
    faq_set = pick([svc["faqs"], FAQ_ALT.get(svc["slug"], svc["faqs"])], city["slug"], svc["slug"], "fset")
    all_faqs = [(q.format(city=name), a.format(city=name)) for q, a in faq_set]
    drop = pick(list(range(len(all_faqs))), city["slug"], svc["slug"], "fq")
    faqs = [f for i, f in enumerate(all_faqs) if i != drop]
    faq_head = pick([f"Questions from <strong>{name}</strong> homeowners", f"What <strong>{name}</strong> clients ask us",
                     f"{svc['name']} in {name}: <strong>common questions</strong>"], city["slug"], svc["slug"], "fh")
    mats = svc["materials"][:]; random.Random("m" + city["slug"] + svc["slug"]).shuffle(mats)
    opts = svc["options"][:]; random.Random("o" + city["slug"] + svc["slug"]).shuffle(opts)
    fn, alt = SERVICE_IMAGES[svc["slug"]]
    body = "".join([
        page_head([("Service Areas", "/service-areas/"), (name, f'/media-walls-{city["slug"]}/'), (svc["name"], None)],
                  f'{svc["name"]} in <strong>{name}</strong>', intro, svc["price_from"], fn, f'{svc["name"]} in {name} - {alt} - design concept'),
        sec(sec_head(f'Built for <strong>{name}</strong> homes') + f'<div class="prose"><p>{local}</p><p>{idea}</p><p>{angle}</p></div>', paper=True),
        build_section(svc, detail, mats, opts),
        sec(sec_head("From photo to <strong>finished wall</strong>", close) + steps(city["slug"] + svc["slug"]), paper=True),
        sec(sec_head(f'{svc["name"]} in {name}: <strong>pricing</strong>') + f'<div class="prose"><p>{price_txt}</p></div>'),
        band(),
        sec(sec_head(faq_head) + faq_html(faqs)),
        form_block(city, svc),
        sec(f'<div class="two"><div><h3 class="h3">More in {name}</h3>' +
            links([(f'{s["name"]} in {name}', f'/{s["slug"]}-{city["slug"]}/') for s in SERVICES if s["slug"] != svc["slug"]]) +
            f'</div><div><h3 class="h3">{svc["name"]} nearby</h3>' +
            links([(f'{svc["name"]} in {c[1]}', f'/{svc["slug"]}-{c[0]}/') for c in nearest(city, 6)]) + '</div></div>', paper=True),
    ])
    return path, head(title, desc, path, faq_schema(faqs)) + body + footer()

def city_hub(city):
    name = city["name"]
    path = f'/media-walls-{city["slug"]}/'
    title = f'Media Walls & Decorative Panels in {name}, CA | DecorWall LA'
    desc = f'Custom media walls, walnut slat walls, stone feature walls and fireplace walls in {name}, CA. Free design preview, written estimates, installs across {city["county"]} County.'
    faqs = [
        (f"How much does a media wall cost in {name}?", f"In {name}, TV accent walls start at $2,500, full custom media walls at $7,500 and stone and marble walls at $9,800. Every project gets a written estimate after a free design preview based on a photo of your room."),
        (f"Do you really serve {name}?", f"Yes. {name} is about {city['miles']} miles from our Los Angeles base, inside our standard service area. Design, delivery and installation run on the same schedule as our Los Angeles projects."),
        (f"What areas of {name} do you cover?", f"All of {name}, including {', '.join(city['hoods'])}. If you are near the city line, send the form anyway - we cover the surrounding area within roughly 40 miles of Los Angeles."),
        (f"How do I start a project in {name}?", "Send a photo of your room through the estimate form. We reply with a design concept for your wall and a written estimate range - free, with no visit required."),
    ]
    lede = (f"DecorWall LA designs and builds custom TV media walls, walnut slat walls, stone feature walls and fireplace walls in {name}. "
            f"{city['housing'][:1].upper() + city['housing'][1:]} - and one well-built wall is usually what finishes them.")
    body = "".join([
        page_head([("Service Areas", "/service-areas/"), (name, None)], f'Media walls in <strong>{name}</strong>', lede, 2500),
        sec(sec_head(f'Our services in <strong>{name}</strong>') + '<div class="cards five">' + "".join(service_card(s, city) for s in SERVICES) + "</div>"),
        sec(sec_head(f'Working in <strong>{name}</strong>') + f"""<div class="prose"><p>{name} homes are {city['housing']}. Neighborhoods we serve include {', '.join(city['hoods'])} - the area around {city['landmark']}. Every project starts from a photo of your actual room, so proportions, materials and lighting are designed for your space, not copied from a showroom wall.</p>
<p>From the first concept to the final walkthrough you deal with one crew and one written estimate. No day-rate surprises, no scope creep after the build starts.</p></div>""", paper=True),
        sec(sec_head("How a project <strong>runs</strong>") + steps(city["slug"] + "hub")),
        band(),
        sec(sec_head(f'Questions from <strong>{name}</strong> homeowners') + faq_html(faqs)),
        form_block(city, None),
        sec('<h3 class="h3">Nearby service areas</h3>' + links([(f"Media walls in {c[1]}", f"/media-walls-{c[0]}/") for c in nearest(city)]), paper=True),
    ])
    return path, head(title, desc, path, faq_schema(faqs)) + body + footer()

def service_hub(svc):
    path = f'/{svc["slug"]}/'
    title = f'{svc["name"]} in Los Angeles | DecorWall LA'
    desc = f'{svc["name"]} in Los Angeles - from {money(svc["price_from"])}. {svc["hero_line"]} Free design preview and written estimates.'
    faqs = [(q.format(city="Los Angeles"), a.format(city="Los Angeles")) for q, a in svc["faqs"][:3]]
    fn, alt = SERVICE_IMAGES[svc["slug"]]
    detail = pick([svc["detail"]] + DETAIL_ALT.get(svc["slug"], []), svc["slug"], "hub")
    body = "".join([
        page_head([(svc["name"], None)], f'<strong>{svc["name"]}</strong> in Los Angeles', svc["hero_line"], svc["price_from"], fn, f'{svc["name"]} in Los Angeles - {alt} - design concept'),
        build_section(svc, detail, svc["materials"], svc["options"]),
        sec(sec_head("How it <strong>works</strong>") + steps(svc["slug"] + "hub"), paper=True),
        band(),
        sec(sec_head("Common <strong>questions</strong>") + faq_html(faqs)),
        form_block(None, svc),
        sec(f'<h3 class="h3">{svc["name"]} by city</h3>' + links([(c[1], f'/{svc["slug"]}-{c[0]}/') for c in CITIES]), paper=True),
    ])
    return path, head(title, desc, path, faq_schema(faqs)) + body + footer()

def styles_hub():
    path = "/styles/"
    desc = ("Six media wall styles by DecorWall LA: full built-in, Roman clay and fluted oak, floating cabinet, "
            "Roman clay minimalist, shiplap and panels, and minimalist TV wall. Free design preview from a photo of your room.")
    body = "".join([
        page_head([("Styles", None)], "Media wall <strong>styles</strong>",
                  "Every DecorWall LA wall starts from one of six looks. Pick the one closest to your room, and we adapt it to your wall, your screen and your equipment in the free design preview. All images are design concepts."),
        sec('<div class="cards">' + "".join(style_card(st) for st in STYLES) + "</div>"),
        sec(sec_head("Not sure which style <strong>fits</strong>?") + '<div class="prose"><p>Send a photo of your room through the form. We will point the design at the style that suits your space, light and existing furniture, and show you the wall before you commit to anything.</p><p>Most clients start with a style and adjust: a floating cabinet under Roman clay, shiplap with LED shelves, a built-in that borrows the minimalist panel. The styles are starting points, not packages.</p></div>', paper=True),
        form_block(),
    ])
    return path, head("Media Wall Styles | DecorWall LA", desc, path) + body + footer()

def style_page(st):
    path = f'/styles/{st["slug"]}/'
    desc = f'{st["name"]} media walls in Los Angeles by DecorWall LA. {st["tagline"]} Free design preview and a written estimate.'
    paras = "".join(f"<p>{p}</p>" for p in st["paragraphs"])
    idx = STYLES.index(st)
    others = [STYLES[(idx + i) % len(STYLES)] for i in (1, 2, 3)]
    head_html = page_head([("Styles", "/styles/"), (st["name"], None)], f'<strong>{st["name"]}</strong>', esc(st["tagline"]), st["price_from"])
    if not st["price_from"]:
        head_html = head_html.replace('<div class="actions">', '<p class="from">Priced by design &middot; free design preview &middot; written estimate</p><div class="actions">', 1)
    head_html = head_html.replace('<section class="ph">', '<section class="ph ph-split">', 1).replace("</div></section>", f'<figure class="ph-img"><img src="/assets/styles/{st["image"]}" alt="{esc(st["alt"])} - design concept" width="2048" height="1152"><figcaption>Design concept</figcaption></figure></div></section>', 1)
    body = "".join([
        head_html,
        sec(sec_head(f'About the <strong>{st["name"]}</strong> style') + f'<div class="prose">{paras}</div>', paper=True),
        sec(f'<div class="two"><div><h3 class="h3">Finishes</h3>{checks(st["finishes"])}</div><div><h3 class="h3">Details and options</h3>{checks(st["details"])}</div></div>'),
        band(),
        sec('<h3 class="h3">Build it as a service</h3>' + links([(SVC[s]["name"], f'/{s}/') for s in st["services"]])),
        sec(sec_head("More <strong>styles</strong>") + '<div class="cards">' + "".join(style_card(o) for o in others) + "</div>", paper=True),
        form_block(),
    ])
    return path, head(f'{st["name"]} Media Wall Style | DecorWall LA', desc, path) + body + footer()

def cost_page():
    rows = [("TV accent wall (panels + floating cabinet)", "from $2,500"), ("Walnut slat wall (TV section)", "from $2,500"),
            ("Accent wall - decorative panels, one wall", "from $2,500"), ("Electric fireplace wall", "from $5,900"),
            ("Full custom media wall (built-ins, lighting)", "from $7,500"), ("Stone & marble feature wall", "from $9,800"),
            ("Whole-home accent package", "by written quote")]
    trs = "".join(f'<tr><td>{a}</td><td>{b}</td><td><a class="btn-link" href="#estimate">Get quote{ARROW}</a></td></tr>' for a, b in rows)
    drivers = [("Wall size", "Width and ceiling height set material quantities more than anything else."),
               ("Materials", "Painted panels are the most affordable finish; real walnut veneer, large-format porcelain and natural stone sit higher."),
               ("Cabinetry", "A floating cabinet is simpler than full-height built-ins with doors and drawers."),
               ("Equipment and electrical", "Projector lifts, motorized platforms and fireplace units are priced per model; new outlets or circuits add cost when needed.")]
    body = "".join([
        page_head([("Cost", None)], "What a media wall <strong>costs</strong> in Los Angeles",
                  "Real starting numbers, what moves them, and what your written estimate covers. No call-for-pricing games."),
        sec(sec_head("Starting <strong>prices</strong>") + f'<table class="prices">{trs}</table><p class="small" style="margin-top:18px">Starting prices assume a standard wall in good condition and our standard material lines. Fireplace wall pricing is a starting estimate; the fireplace unit is quoted by size and brand in your written estimate.</p>'),
        sec(sec_head("What drives the <strong>price</strong>") + samples([("Wall size", "width and height", "stone"), ("Material", "paint to walnut to stone", "walnut"), ("Cabinetry", "floating or built-in", "oak"), ("Equipment", "fireplace, lifts, power", "black")]), paper=True),
        sec(sec_head("What your estimate <strong>covers</strong>", "The estimate is written and itemized; the number does not change after the build starts unless you change the scope.") +
            checks(["Design preview", "All materials and delivery", "Installation", "Equipment mounting and connection", "Lighting setup", "Final walkthrough"])),
        form_block(),
    ])
    return "/cost/", head("Media Wall Cost in Los Angeles | DecorWall LA",
        "Media wall cost in Los Angeles: accent walls from $2,500, full media walls from $7,500, stone and marble from $9,800. What drives the price and what the estimate covers.", "/cost/") + body + footer()

def areas_page():
    groups = [("Los Angeles County", "Los Angeles"), ("Orange County", "Orange"), ("Ventura County edge", "Ventura")]
    inner = "".join(f'<h3 class="h3" style="margin-top:40px">{label}</h3>' + links([(c[1], f"/media-walls-{c[0]}/") for c in CITIES if c[2] == county]) for label, county in groups)
    body = "".join([
        page_head([("Service Areas", None)], "Service <strong>areas</strong>",
                  "We design and install media walls and decorative panels across Los Angeles and surrounding cities within about 40 miles. Pick your city for local pricing, services and questions."),
        sec(inner + '<p class="small" style="margin-top:40px">Near the edge of the map? Send the form anyway. If we cannot serve your address we will tell you honestly and, where we can, point you to someone who can.</p>'),
        form_block(),
    ])
    return "/service-areas/", head("Service Areas - Media Walls Across Los Angeles | DecorWall LA",
        "DecorWall LA service areas: media wall and decorative panel installation across Los Angeles, Orange County and nearby cities within 40 miles.", "/service-areas/") + body + footer()

PROJECT_CAPTIONS = ["Walnut slats, black marble and a floating cabinet", "Full media wall with stone column",
                    "Angled view: panel rhythm and LED lines", "Hidden door inside a slat wall",
                    "Wood backing wall with warm backlight", "Clean ceiling line, no crown gap"]

def projects_page():
    cards = "".join(f"""<figure class="card" style="margin:0"><div class="card-img"><img src="/assets/projects/project-{i + 1}.webp" alt="{esc(c)} - design concept" loading="lazy"></div>
<figcaption class="card-top"><h3 class="card-name">{c}</h3><p class="card-price">Concept</p></figcaption></figure>""" for i, c in enumerate(PROJECT_CAPTIONS))
    body = "".join([
        page_head([("Projects", None)], "Projects and <strong>concepts</strong>",
                  "Concepts we design from client room photos before a build starts. Completed-installation photography is added as projects finish, and every image here is labeled honestly."),
        sec('<div class="cards">' + cards + "</div>"),
        band("See <strong>your room</strong> in this style", "The design preview is free and starts from one photo."),
        form_block(),
    ])
    return "/projects/", head("Media Wall Projects & Design Concepts | DecorWall LA",
        "Media wall design concepts by DecorWall LA: walnut slats, black marble, hidden doors and LED lighting, designed from real client rooms in Los Angeles.", "/projects/") + body + footer()

FAQS_ALL = [
    ("How much does a media wall cost?", "TV accent walls start at $2,500, full custom media walls at $7,500 and stone and marble walls at $9,800. Your written estimate follows a free design preview based on your room photo."),
    ("What is a design preview?", "Our concept for your actual wall: layout, materials and lighting designed from a photo of your room, sent with an estimate range. Free, no visit, no obligation."),
    ("How long does a project take?", "Design and ordering typically take 1 to 3 weeks depending on materials. On site, a single accent wall takes 1 to 3 days and a full media wall 3 to 5 days."),
    ("Do you hide wires and equipment?", "Yes - concealed channels, ventilated equipment bays and flush access panels are standard in our designs."),
    ("Can you work with my existing TV or projector?", "Yes. We design around your equipment's exact dimensions, or size new equipment in the preview if you have not bought it yet."),
    ("Do you offer a warranty?", "We stand behind our installation work: if something we built or installed fails under normal use, tell us and we will make it right. Terms are spelled out in your written estimate."),
    ("Which areas do you serve?", "Los Angeles and surrounding cities within about 40 miles, including Orange County and the South Bay. See the service areas page for the full city list."),
    ("How do payments work?", "Payments follow the milestones in your written estimate - never a surprise lump sum. The schedule is agreed before the build starts."),
]

def faq_page():
    body = "".join([page_head([("FAQ", None)], "Frequently asked <strong>questions</strong>"),
                    sec(faq_html(FAQS_ALL)), form_block()])
    return "/faq/", head("Media Wall FAQ | DecorWall LA",
        "Answers about media wall cost, timelines, design previews, hidden wiring and service areas - DecorWall LA, Los Angeles.", "/faq/", faq_schema(FAQS_ALL)) + body + footer()

def text_page(path, title, desc, crumb, h1, paras, form=True, lede=""):
    body = page_head([(crumb, None)], h1, lede, actions=form) + sec('<div class="prose">' + "".join(f"<p>{p}</p>" for p in paras) + "</div>", paper=True)
    if form:
        body += form_block()
    return path, head(title, desc, path) + body + footer()

def process_page():
    stages = [("Design preview", "You send a photo of your room through the form. We design the wall - layout, materials, lighting, equipment fit - and send the concept with a written estimate range."),
              ("Written estimate", "You approve the design; we finalize materials and give you an itemized, fixed estimate and a build schedule. Nothing starts until you sign off on the number."),
              ("Build", "Materials are prepared before we arrive. On site we protect the room, build in layers - framing, finish, cabinetry, lighting - and clean daily. Most media walls take 3 to 5 working days."),
              ("Walkthrough", "Equipment mounted and connected, remotes and lighting tested with you, every seam checked together. Final payment follows the walkthrough, per your estimate.")]
    body = "".join([
        page_head([("Process", None)], "From photo to <strong>finished wall</strong>", "Four steps, one crew, and a written number before anything starts."),
        sec(slat_steps()),
        band(), form_block(),
    ])
    return "/process/", head("Our Process - From Photo to Finished Wall | DecorWall LA",
        "The DecorWall LA process: free design preview, written estimate, materials and schedule, clean build, final walkthrough.", "/process/") + body + footer()

def materials_page():
    mats = [("Walnut slat panels", "Real walnut veneer over acoustic felt backing - warmth, texture and real sound dampening for open-plan rooms."),
            ("Large-format porcelain", "Marble looks without marble upkeep: 24x48 and larger slabs, thin color-matched seams, no sealing, heat and stain resistant."),
            ("Stone veneer", "Natural split-face and ledgestone for weight and shadow where a flat finish is not enough."),
            ("Painted panels and Roman clay", "Matte, mineral finishes that keep a wall quiet and let furniture carry the color."),
            ("Lighting", "LED strips in channels and behind panels, on dimmers and remotes. Warm 2700-3000K light is our default - it is what makes walnut and stone look expensive at night.")]
    body = "".join([
        page_head([("Materials", None)], "Materials and <strong>lighting</strong>",
                  "Every material in your design preview is named in the written estimate, so you know exactly what is being installed before the build starts."),
        sec(samples([("Walnut slats", "warmth, and quieter rooms", "walnut"), ("Porcelain", "the marble look, no upkeep", "marble"), ("Stone veneer", "weight and shadow", "stone"), ("Roman clay", "a quiet mineral finish", "clay")])),
        sec(sec_head(f"{mats[4][0]}") + f'<div class="prose"><p>{mats[4][1]}</p></div>', paper=True),
        form_block(),
    ])
    return "/materials/", head("Materials & Lighting | DecorWall LA",
        "Materials DecorWall LA works with: walnut acoustic slats, large-format porcelain, marble-look tile, stone veneer, LED lighting and dimmers.", "/materials/") + body + footer()

def core_pages():
    return [
        cost_page(), areas_page(), projects_page(), faq_page(), process_page(), materials_page(),
        text_page("/about/", "About DecorWall LA | DecorWall LA",
                  "DecorWall LA is a Los Angeles installation studio for custom media walls and decorative panels, built on years of hands-on construction work.",
                  "About", "About <strong>DecorWall LA</strong>", [
                  "DecorWall LA is the decorative-wall studio of a Los Angeles construction team with years of hands-on remodeling work across the city - framing, finish carpentry, tile and electrical coordination under one roof.",
                  "We started DecorWall LA because media walls kept being the worst-run part of otherwise good remodels: designed by a furniture store, wired by guesswork, finished by whoever was available. Our model is the opposite: one team designs the wall around your room and equipment, prices it in writing, and builds it in days.",
                  f'Questions before you start? Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call <a href="tel:{PHONE_TEL}">{PHONE}</a>.']),
        text_page("/estimate/", "Get a Free Design Preview | DecorWall LA",
                  "Request a free media wall design preview: send a photo of your room, get a concept and a written estimate from DecorWall LA.",
                  "Estimate", "Get your free <strong>design preview</strong>",
                  [f"Send the form below with a photo of your room. We reply with a design concept for your wall and a written estimate range, usually within one business day. Prefer to talk? Call <a href=\"tel:{PHONE_TEL}\">{PHONE}</a>."]),
        text_page("/thank-you/", "Thank You | DecorWall LA",
                  "Thank you - your design preview request is in. DecorWall LA will reply with your concept and estimate.",
                  "Thank you", "Thank you, <strong>request received</strong>",
                  [f"Your request is in. We will reply with your design preview and estimate range, usually within one business day. If your project is time-sensitive, call <a href=\"tel:{PHONE_TEL}\">{PHONE}</a> and mention your form submission."], form=False),
        text_page("/privacy/", "Privacy Policy | DecorWall LA",
                  "DecorWall LA privacy policy: how contact details and room photos from our forms are used.",
                  "Privacy", "Privacy <strong>policy</strong>",
                  [f"Information you send through our forms - name, phone, email, project details and room photos - is used only to prepare your design preview, estimate and project communication. We do not sell your information. Photos are used for design purposes for your project. To have your information removed, email <a href=\"mailto:{EMAIL}\">{EMAIL}</a>."], form=False),
    ]

# ------------------------------------------------------------------ home page

HOME_WHY = [
    ("See it before we build it", "Every project starts with a free design preview made from a photo of your room: the wall, the materials and the layout, before anyone picks up a tool."),
    ("Fixed written estimate", "The price in your written estimate is the price you pay. The scope is itemized line by line and does not change after the build starts unless you change it."),
    ("One crew, start to finish", "Design, build, electrical coordination and finish are handled by our own Los Angeles team, with no handoffs."),
    ("Clean, fast installs", "Most walls are completed in days, not weeks. The room is protected, dust is controlled, and cleanup is included."),
]
HOME_FAQS = [
    ("How much does a media wall cost in Los Angeles?", "TV accent walls start at $2,500, full custom media walls at $7,500, and stone and marble feature walls at $9,800. Your exact number comes as a written estimate after a free design preview."),
    ("How does the free design preview work?", "Send a photo of your room through any form on this site. We design the wall for your space - layout, materials, lighting - and reply with the concept and a written estimate range. No visit, no obligation."),
    ("How long does installation take?", "Most media walls take 3 to 5 working days on site once materials are ready. Single accent walls often finish in 1 to 3 days."),
    ("Which areas do you serve?", "Los Angeles and surrounding cities within roughly 40 miles - from Malibu and Santa Monica to Pasadena, the San Gabriel Valley, Orange County and the South Bay."),
]

HOME_STEPS = [("Photo", "you send one picture of the wall", "photo"), ("Design", "we design it on your photo", "design"),
              ("Build", "3 days for a simple install", "build"), ("Glow", "lights on, room done", "glow")]

def slat_steps():
    """How it works: four quiet steps in a row, no pictures. A soft warm light comes up on each
    word in turn as the row comes into view."""
    items = "".join(f'<li><span>0{i + 1}</span><b>{t}</b><em>{d}</em></li>' for i, (t, d, _) in enumerate(HOME_STEPS))
    return f'<ol class="calm reveal">{items}</ol>'

def home_how():
    return sec(sec_head("How it <strong>works</strong>") + slat_steps(), sid="how")

# What we build: one short list with no overlaps. Styles that are a version of a service are folded
# into it (Full Built-In -> Media Wall, Shiplap & Panels -> Accent Panels, both Roman clay styles -> Roman Clay).
BUILD_LIST = [
    ("Media Wall", "full-built-in.webp", "from $7,500", "/tv-media-walls/"),
    ("Slat Wall", "minimalist-tv-wall.webp", "from $2,500", "/walnut-slat-walls/"),
    ("Stone & Marble", "stone-marble.webp", "from $9,800", "/stone-marble-walls/"),
    ("Fireplace Wall", "fireplace-wall.webp", "from $5,900", "/fireplace-walls/"),
    ("Accent Panels", "shiplap-panels.webp", "from $2,500", "/accent-walls/"),
    ("Roman Clay", "roman-clay-fluted-oak.webp", "from $8,100", "/styles/roman-clay-fluted-oak/"),
    ("Floating Cabinet", "floating-cabinet.webp", "Priced by design", "/styles/floating-cabinet/"),
]

def home_build():
    """What we build: a short list; pointing at or clicking a name shows it on the right, with its
    price and a link to its page on the photo."""
    rows, pics = "", ""
    for i, (name, img, price, href) in enumerate(BUILD_LIST):
        on = ' class="is-on"' if i == 0 else ""
        # The View button sits in the row itself, so there is nothing to aim for across the page.
        rows += (f'<li class="idx-row{" is-on" if i == 0 else ""}" data-idx-row="{i}"><button type="button" data-idx-item="{i}" aria-pressed="{"true" if i == 0 else "false"}"{on}>'
                 f'<span class="idx-name">{name}</span></button><span class="idx-price">{price}</span><a class="idx-go" href="{href}">View{ARROW}</a></li>')
        pics += (f'<a class="idx-pic{" is-on" if i == 0 else ""}" href="{href}" data-idx-pic="{i}" tabindex="-1"><img src="/assets/styles/{img}" alt="{esc(name)} - design concept" loading="lazy" width="2048" height="1152"></a>')
    # Phones have no hover, so they get a plain grid of tiles instead: photo, name and price, tap to open.
    tiles = "".join(f'<li><a href="{href}"><span class="idx-m-img"><img src="/assets/styles/{img}" alt="{esc(name)} - design concept" loading="lazy" width="2048" height="1152"></span><b>{name}</b><small>{price}</small></a></li>'
                    for name, img, price, href in BUILD_LIST)
    return sec(sec_head("What we <strong>build</strong>") +
               f'<div class="idx"><ol class="idx-list">{rows}</ol><div class="idx-pics">{pics}</div></div><ul class="idx-m">{tiles}</ul>', paper=True, sid="services")

HOME_REASONS = [("See it first", "free design from your photo", "walnut"), ("One price", "fixed and in writing", "stone"),
                ("One crew", "our own LA team", "black"), ("Days, not weeks", "clean, fast installs", "oak")]

def home_why():
    """Why choose us: four material samples, like boards on a design table, each lit from above."""
    return sec(sec_head("Why homeowners choose <strong>DecorWall LA</strong>") + samples(HOME_REASONS), sid="why-us")

def home_styles():
    """Start from a style: a horizontal row of tall cards you can swipe or step through."""
    cards = "".join(f"""<a class="st-card" href="/styles/{st["slug"]}/"><div class="st-img"><img src="/assets/styles/{st["image"]}" alt="{esc(st["alt"])} - design concept" loading="lazy" width="2048" height="1152"></div>
<div class="st-meta"><span class="st-n">0{i + 1}</span><h3>{st["name"]}</h3><p>{"from " + money(st["price_from"]) if st["price_from"] else "Priced by design"}</p></div></a>""" for i, st in enumerate(STYLES))
    head = '<div class="sec-head"><h2 class="h2">Start from a <strong>style</strong></h2></div>'
    return sec(head + f'<div class="st-row" data-st-row>{cards}</div><p style="margin-top:36px"><a class="btn-link" href="/styles/">All design styles{ARROW}</a></p>', paper=True, sid="styles")

def home_areas():
    """Service areas: city names drifting past in two slow rows, each a link."""
    la = [c for c in CITIES if c[2] == "Los Angeles"][:22]; oc = [c for c in CITIES if c[2] != "Los Angeles"][:22]
    def row(lst, rev=""):
        items = "".join(f'<a href="/media-walls-{c[0]}/">{c[1]}</a>' for c in lst)
        return f'<div class="marq{rev}"><div class="marq-track">{items}{items}</div></div>'
    return f"""<section class="sec areas" id="areas"><div class="wrap">{sec_head("Service <strong>areas</strong>")}</div>
{row(la)}{row(oc, " rev")}
<div class="wrap"><p style="margin-top:40px"><a class="btn-link" href="/service-areas/">All service areas{ARROW}</a></p></div></section>"""

def home_blocks():
    return "".join([
        home_how(), home_build(), home_why(), home_areas(),
        sec(sec_head("Common <strong>questions</strong>") + faq_html(HOME_FAQS), paper=True),
        form_block(),
    ])

def home_page():
    """The hand-built home page (index.html) with the shared header, extra blocks and footer filled in."""
    src = open(os.path.join(ROOT, "index.html")).read()
    # Shared header and menu replace the home page's own.
    a = src.index('  <header class="header"'); b = src.index("  <main>")
    src = src[:a] + header().replace('href="/" class="logo"', 'href="#top" class="logo"').replace('href="/#cost"', 'href="#cost"') + "\n\n" + src[b:]
    # Head: canonical, description and schema for the home page.
    src = src.replace("<title>DecorWall LA</title>", f'<title>Custom Media Walls in Los Angeles | DecorWall LA</title>\n<link rel="canonical" href="{BASE}/">\n<link rel="icon" href="assets/logo.webp">\n'
                      f'<script type="application/ld+json">{schema_business()}</script>\n<script type="application/ld+json">{faq_schema(HOME_FAQS)}</script>', 1)
    src = src.replace("<body>", f'<body data-whatsapp="{WHATSAPP}">', 1)
    # Extra blocks and footer after the packages.
    end = src.index("  </main>")
    foot = footer(dock=False).replace("</main>\n", "", 1).replace(f'<script src="/assets/site.js?v={ASSET_V}"></script>\n</body></html>', "")
    src = src[:end] + home_blocks() + "\n  </main>\n" + foot + src[end + len("  </main>\n"):]
    src = src.replace("</body>", f'<script src="assets/site.js?v={ASSET_V}"></script>\n</body>', 1)
    return "/", src

# ------------------------------------------------------------------ output

def write(path, content):
    full = os.path.join(OUT, path.strip("/"))
    if path.endswith("/"):
        full = os.path.join(full, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)

def relativize(path, content):
    """Preview build: root-relative links become relative, and folders point at their index.html."""
    depth = path.strip("/").count("/") + (1 if path.strip("/") and path.endswith("/") else 0)
    up = "../" * depth
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith("//"):
            return m.group(0)
        target, _, frag = url[1:].partition("#")
        target, _, query = target.partition("?")
        if target == "" or target.endswith("/"):
            target += "index.html"
        new = up + target + ("?" + query if query else "") + ("#" + frag if frag else "")
        return f'{attr}="{new}"'
    return re.sub(r'(href|src)="(/[^"]*)"', fix, content)

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    shutil.copytree(os.path.join(ROOT, "images"), os.path.join(OUT, "images"))
    pages = [home_page()] + core_pages() + [styles_hub()] + [style_page(st) for st in STYLES]
    for svc in SERVICES:
        pages.append(service_hub(svc))
    for c in CITIES:
        city = CITY[c[0]]
        pages.append(city_hub(city))
        for svc in SERVICES:
            pages.append(matrix_page(city, svc))
    pages.append(("/404.html", head("Page Not Found | DecorWall LA", "Page not found.", "/404.html") +
                  page_head([("Not found", None)], "Page not <strong>found</strong>", 'The page moved or never existed. Start from the <a href="/">home page</a> or <a href="/service-areas/">pick your city</a>.', actions=False) + footer()))
    for path, doc in pages:
        write(path, relativize(path, doc) if PREVIEW else doc)
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    urls = sorted(p for p, _ in pages if p not in ("/thank-you/", "/404.html"))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pr = "1.0" if u == "/" else ("0.9" if u.count("/") <= 2 and "-" not in u.strip("/") else "0.8")
        sm.append(f"<url><loc>{BASE}{u}</loc><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write("\n".join(sm))
    print(f"{len(pages)} pages -> {os.path.relpath(OUT, ROOT)}/")

if __name__ == "__main__":
    main()
