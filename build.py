#!/usr/bin/env python3
"""DecorWall LA site v2 generator: city x service matrix (~520 pages)."""
import hashlib, html, json, os, random, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_cities import CITIES
from data_services import SERVICES
from data_styles import STYLES
from detail_variants import DETAIL_ALT, STEPS_B
from faq_variants import FAQ_ALT

BASE = "https://decorwallla.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
PHONE = "(213) 913-5312"
PHONE_TEL = "+12139135312"
EMAIL = "hello@decorwallla.com"
# Form endpoint: wired to the CRM form handler in the form step; every form posts here.
FORM_ACTION = "https://formsubmit.co/hello@decorwallla.com"

CSS = """
:root{--bg:#FBF9F6;--sand:#F3EDE4;--panel:#F3EDE4;--panel2:#FFFFFF;--line:#E7DFD3;--text:#211D16;--muted:#6E6455;--bronze:#9A6B3F;--bronze2:#7E5630;--amber:#9A6B3F;--amber2:#7E5630;--walnut:#8a5a33}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:Georgia,'Times New Roman',serif;line-height:1.65;padding-bottom:80px}
a{color:var(--amber);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header{position:sticky;top:0;background:rgba(251,249,246,.96);border-bottom:1px solid var(--line);z-index:50;backdrop-filter:blur(6px)}
.hbar{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;max-width:1120px;margin:0 auto}
.logo{display:flex;align-items:center;gap:10px;color:var(--text);font-size:20px;letter-spacing:.04em}
.logo img{width:38px;height:38px;border-radius:9px}
nav a{color:var(--muted);margin-left:18px;font-size:15px}
nav a:hover{color:var(--amber);text-decoration:none}
.cta-btn{display:inline-block;background:linear-gradient(180deg,var(--bronze),var(--bronze2));color:#fff;padding:13px 26px;border-radius:8px;font-weight:bold;font-size:16px;border:0;cursor:pointer}
.cta-btn:hover{text-decoration:none;background:var(--bronze2)}
.hero{padding:64px 0 46px;background:radial-gradient(900px 420px at 70% -10%,rgba(154,107,63,.13),transparent),linear-gradient(180deg,#F3EDE4,#FBF9F6)}
.hero h1{font-size:42px;line-height:1.15;font-weight:normal;max-width:820px}
.hero p.lede{color:var(--muted);font-size:19px;max-width:720px;margin:18px 0 26px}
.price-line{color:var(--amber);font-size:17px;margin-bottom:22px}
.slats{height:10px;background:repeating-linear-gradient(90deg,var(--walnut) 0 26px,#6B4423 26px 32px);opacity:.85;border-radius:3px;margin:26px 0 0}
section{padding:44px 0}
h2{font-size:29px;font-weight:normal;margin-bottom:16px}
h3{font-size:20px;font-weight:normal;margin:20px 0 8px;color:var(--text)}
p{margin-bottom:14px;color:#3B352B}
.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin:18px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px}
.card a{font-size:17px}
.card p{font-size:14.5px;color:var(--muted);margin:6px 0 0}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:26px}
@media(max-width:760px){.cols{grid-template-columns:1fr}.hero h1{font-size:31px}nav{display:none}}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;counter-reset:step}
.step{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:18px}
.step b{color:var(--amber);display:block;margin-bottom:6px;font-size:15px;letter-spacing:.06em}
table{width:100%;border-collapse:collapse;margin:16px 0;background:var(--panel)}
th,td{border:1px solid var(--line);padding:11px 13px;text-align:left;font-size:15.5px}
th{color:var(--amber);font-weight:normal;letter-spacing:.03em}
.faq{border-top:1px solid var(--line)}
.faq details{border-bottom:1px solid var(--line);padding:13px 2px}
.faq summary{cursor:pointer;font-size:17px;color:var(--text)}
.faq p{margin-top:8px;color:var(--muted);font-size:15.5px}
.formbox{background:var(--panel);border:1px solid var(--amber2);border-radius:12px;padding:26px;margin:10px 0}
.formbox h2{margin-bottom:6px}
.frow{display:grid;grid-template-columns:1fr 1fr;gap:13px}
@media(max-width:760px){.frow{grid-template-columns:1fr}}
label{display:block;font-size:14px;color:var(--muted);margin:10px 0 4px}
input,select,textarea{width:100%;background:#fff;border:1px solid var(--line);border-radius:7px;color:var(--text);padding:11px;font-size:15.5px;font-family:inherit}
textarea{min-height:90px}
.crumbs{font-size:14px;color:var(--muted);padding:16px 0 0}
.crumbs a{color:var(--muted)}
footer{border-top:1px solid var(--line);padding:38px 0 30px;margin-top:20px;background:#2A211A}
footer .cols{gap:34px}
footer h4{color:var(--amber);font-weight:normal;margin-bottom:10px;font-size:16px}
footer li{list-style:none;margin:5px 0;font-size:14.5px}
footer a{color:var(--muted)}
.small{font-size:13.5px;color:var(--muted)}
.tag{display:inline-block;border:1px solid var(--line);border-radius:20px;padding:3px 12px;font-size:13.5px;color:var(--muted);margin:0 6px 8px 0}
.hero-img{width:100%;border-radius:12px;margin-top:26px;border:1px solid var(--line);display:block}
/* ---- v3 light sales theme: overrides + shared components ---- */
.card{background:#fff;box-shadow:0 2px 10px rgba(33,29,22,.05)}
.step{box-shadow:0 2px 10px rgba(33,29,22,.05)}
.formbox{background:#fff;box-shadow:0 4px 18px rgba(33,29,22,.07)}
input,select,textarea{background:#fff}
.btn2{display:inline-block;background:#fff;color:var(--bronze);border:1.5px solid var(--bronze);padding:12px 24px;border-radius:8px;font-weight:bold;font-size:16px}
.btn2:hover{background:var(--sand);text-decoration:none}
.hbar{flex-wrap:wrap;gap:8px 14px}
.hdr-actions{display:flex;align-items:center;gap:14px}
.hdr-call{font-weight:bold;color:var(--text);font-size:16px;white-space:nowrap}
.hdr-call:hover{color:var(--bronze);text-decoration:none}
@media(max-width:760px){.hdr-call{display:none}.hdr-quote{padding:8px 13px!important;font-size:14px}}
.trust{display:flex;flex-wrap:wrap;gap:8px 24px;margin-top:24px;padding:13px 16px;background:#fff;border:1px solid var(--line);border-radius:9px;box-shadow:0 2px 8px rgba(33,29,22,.04)}
.trust span{font-size:14.5px;color:var(--text)}
.trust b{color:var(--bronze)}
.cta-band{background:linear-gradient(180deg,#F2E7D5,#EBDCC0);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:42px 0;text-align:center}
.cta-band h2{margin-bottom:8px}
.cta-band p{max-width:640px;margin:0 auto 20px;color:#4A4234}
.cta-band .row{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}
.floatbar{position:fixed;left:0;right:0;bottom:0;z-index:80;background:rgba(255,255,255,.97);border-top:1px solid var(--line);box-shadow:0 -4px 16px rgba(33,29,22,.10);display:flex;gap:10px;padding:10px 14px;justify-content:center}
.floatbar a{flex:1;max-width:230px;text-align:center;padding:11px 8px;border-radius:8px;font-weight:bold;font-size:15px;border:1.5px solid var(--bronze);color:var(--bronze);background:#fff}
.floatbar a.main{background:var(--bronze);color:#fff}
.floatbar a:hover{text-decoration:none;background:var(--sand)}
.floatbar a.main:hover{background:var(--bronze2)}
ul.checks{list-style:none;margin:8px 0 0}
ul.checks li{padding:7px 0 7px 30px;position:relative;border-bottom:1px dashed var(--line)}
ul.checks li:last-child{border-bottom:0}
ul.checks li::before{content:"\2713";position:absolute;left:2px;color:var(--bronze);font-weight:bold}
.mini-btn{display:inline-block;border:1.5px solid var(--bronze);color:var(--bronze);border-radius:7px;padding:6px 14px;font-size:14px;font-weight:bold;white-space:nowrap}
.mini-btn:hover{background:var(--bronze);color:#fff;text-decoration:none}
footer{background:#2A211A;color:#E9E1D2}
footer p{color:#D9CFBE}
footer .small{color:#B7AB93}
footer a{color:#D8C6A5}
footer h4{color:#E7BC7C}
"""

def esc(s): return html.escape(s, quote=True)

def pick(variants, *keys):
    h = hashlib.md5("|".join(keys).encode()).hexdigest()
    return variants[int(h[:6], 16) % len(variants)]

def head(title, desc, path, extra_schema=""):
    canon = BASE + path
    ld = {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "name": "DecorWall LA",
        "url": BASE + "/",
        "email": EMAIL,
        "telephone": PHONE_TEL,
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "addressLocality": "Los Angeles", "addressRegion": "CA", "addressCountry": "US"},
        "areaServed": "Los Angeles and surrounding cities within 40 miles",
    }
    schema = json.dumps(ld)
    if extra_schema:
        schema += "</script><script type=\"application/ld+json\">" + extra_schema
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
<link rel="icon" href="/assets/logo.webp">
<link rel="stylesheet" href="/assets/style.css?v=20261020b">
<script type="application/ld+json">{schema}</script>
</head>
<body>
<header><div class="hbar">
<a class="logo" href="/"><img src="/assets/logo.webp" alt="DecorWall LA logo">DecorWall&nbsp;LA</a>
<nav>
<a href="/tv-media-walls/">Media Walls</a><a href="/walnut-slat-walls/">Slat Walls</a><a href="/stone-marble-walls/">Stone</a><a href="/fireplace-walls/">Fireplace</a><a href="/styles/">Styles</a><a href="/cost/">Cost</a><a href="/service-areas/">Areas</a><a href="/estimate/">Estimate</a>
</nav>
<div class="hdr-actions"><a class="hdr-call" href="tel:{PHONE_TEL}">{PHONE}</a><a class="cta-btn hdr-quote" href="#estimate" style="padding:9px 18px">Get my free quote</a></div>
</div></header>
"""

FOOT_SERVICES = "".join(f'<li><a href="/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
TOP_CITIES = [c for c in CITIES if c[3] <= 16][:14]
FOOT_CITIES = "".join(f'<li><a href="/media-walls-{c[0]}/">Media walls in {c[1]}</a></li>' for c in TOP_CITIES)

def footer():
    return f"""
<footer><div class="wrap"><div class="cols">
<div><h4>DecorWall LA</h4>
<p class="small">Custom media walls, walnut slat walls, stone feature walls and decorative panels across Los Angeles and surrounding cities within 40 miles.</p>
<p class="small">{EMAIL}<br><a href="tel:{PHONE_TEL}">{PHONE}</a><br>Los Angeles, CA</p></div>
<div><h4>Services</h4><ul>{FOOT_SERVICES}<li><a href="/styles/">Design styles</a></li><li><a href="/cost/">Media wall cost</a></li><li><a href="/process/">Our process</a></li></ul></div>
<div><h4>Popular areas</h4><ul>{FOOT_CITIES}<li><a href="/service-areas/">All service areas</a></li></ul></div>
</div>
<p class="small" style="margin-top:24px">&copy; 2026 DecorWall LA &middot; Los Angeles, CA &middot; <a href="/privacy/">Privacy Policy</a> &middot; Design concepts shown are previews, not completed installations.</p>
</div></footer>
<div class="floatbar"><a href="tel:{PHONE_TEL}">Call</a><a href="sms:{PHONE_TEL}">Text a photo</a><a class="main" href="#estimate">Free quote</a></div>
</body></html>"""

def trust_strip():
    items = ["Free design preview", "Written fixed estimate before work starts", "Local Los Angeles crew", "Reply within 1 business day"]
    spans = "".join(f'<span><b>&#10003;</b> {t}</span>' for t in items)
    return f'<div class="trust">{spans}</div>'

def cta_band():
    return f"""
<section class="cta-band"><div class="wrap">
<h2>Get a free design preview of YOUR room</h2>
<p>Send a photo - we reply with a design concept and a written estimate within one business day.</p>
<div class="row"><a class="cta-btn" href="#estimate">Request my free preview</a><a class="btn2" href="tel:{PHONE_TEL}">Call {PHONE}</a></div>
</div></section>"""

INCLUDED_ITEMS = ["Design preview from your photo", "Written fixed estimate", "Framing and panel installation",
                  "TV mounting and concealed cables", "LED lighting setup where selected", "Paint/finish and final cleanup"]

def included_block():
    lis = "".join(f"<li>{i}</li>" for i in INCLUDED_ITEMS)
    return f'<h2>What\'s included</h2><ul class="checks">{lis}</ul>'

def price_rows():
    rows = []
    for s in SERVICES:
        rows.append(f'<tr><td>{s["name"]}</td><td>from ${s["price_from"]:,}</td><td><a class="mini-btn" href="#estimate">Get quote</a></td></tr>')
    for st in STYLES:
        pr = f'from ${st["price_from"]:,}' if st["price_from"] else "Priced by design"
        rows.append(f'<tr><td>{st["name"]} (style)</td><td>{pr}</td><td><a class="mini-btn" href="#estimate">Get this style</a></td></tr>')
    return "".join(rows)

def form_block(city=None, service=None):
    # city: dict (name/slug) or tuple (slug,name,...); service: dict
    def cname(c): return c["name"] if isinstance(c, dict) else c[1]
    def cslug(c): return c["slug"] if isinstance(c, dict) else c[0]
    city_val = esc(cname(city)) if city else ""
    svc_val = esc(service["name"]) if service else ""
    city_opts = '<option value="">Select your city</option>' + "".join(
        f'<option value="{esc(c[1])}"{" selected" if city and c[0]==cslug(city) else ""}>{c[1]}</option>' for c in CITIES)
    svc_opts = '<option value="">Select a project type</option>' + "".join(
        f'<option value="{esc(s["name"])}"{" selected" if service and s["slug"]==service["slug"] else ""}>{s["name"]}</option>' for s in SERVICES)
    return f"""
<div class="formbox" id="estimate"><h2>Get your free design preview</h2>
<p class="muted">Send a photo of your room and we reply with a design concept for your wall and a written estimate. No visit, no obligation.</p>
<form action="{FORM_ACTION}" method="post" enctype="multipart/form-data">
<div class="frow">
<div><label for="f-name">Name *</label><input id="f-name" name="name" required autocomplete="name"></div>
<div><label for="f-phone">Phone *</label><input id="f-phone" name="phone" required type="tel" autocomplete="tel" placeholder="(213) 555-0123"></div>
</div>
<div class="frow">
<div><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email"></div>
<div><label for="f-city">City</label><select id="f-city" name="city">{city_opts}</select></div>
</div>
<div class="frow">
<div><label for="f-svc">Project type</label><select id="f-svc" name="service">{svc_opts}</select></div>
<div><label for="f-size">Wall size (approx.)</label><input id="f-size" name="wall_size" placeholder="e.g. 12 ft wide x 9 ft high"></div>
</div>
<div class="frow">
<div><label for="f-budget">Budget range</label><select id="f-budget" name="budget">
<option value="">Select a range</option><option>$2,500 - $5,000</option><option>$5,000 - $8,000</option><option>$8,000 - $12,000</option><option>$12,000+</option><option>Not sure yet</option></select></div>
<div><label for="f-photos">Photos of your room (up to 5)</label><input id="f-photos" name="photos" type="file" accept="image/*" multiple></div>
</div>
<label for="f-msg">Tell us about the project</label><textarea id="f-msg" name="message" placeholder="What do you want the wall to look like? Any equipment, fireplace or storage to include?"></textarea>
<input type="hidden" name="page_city" value="{city_val}">
<input type="hidden" name="page_service" value="{svc_val}">
<input type="hidden" name="utm_source" id="utm-source"><input type="hidden" name="utm_medium" id="utm-medium"><input type="hidden" name="utm_campaign" id="utm-campaign">
<input type="hidden" name="_next" value="https://decorwallla.com/thank-you/"><input type="hidden" name="_subject" value="New DecorWall LA design preview request"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false"><input type="text" name="_honey" style="display:none">
<p style="margin-top:14px"><button class="cta-btn" type="submit">Request my free design preview</button></p>
<p class="small">By submitting you agree to be contacted about your project. Photos are used only to prepare your design preview.</p>
</form>
<p class="small" style="margin-top:12px">Prefer to talk? Call <a href="tel:{PHONE_TEL}">{PHONE}</a> or message us on Instagram <a href="https://instagram.com/decorwallla" target="_blank" rel="noopener">@decorwallla</a></p>
<script>(function(){{var p=new URLSearchParams(location.search);var m={{"utm-source":"utm_source","utm-medium":"utm_medium","utm-campaign":"utm_campaign"}};for(var id in m){{var el=document.getElementById(id);if(el)el.value=p.get(m[id])||"";}}}})();</script>
</div>"""

def crumbs(items):
    parts = ['<a href="/">Home</a>']
    for label, href in items:
        parts.append(f'<a href="{href}">{esc(label)}</a>' if href else esc(label))
    return '<div class="wrap"><p class="crumbs">' + " &raquo; ".join(parts) + "</p></div>"

def faq_html(faqs):
    out = ['<div class="faq">']
    for q, a in faqs:
        out.append(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>")
    return "\n".join(out) + "</div>"

def faq_schema(faqs):
    return json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})

def steps_html(service_name, key=""):
    steps_a = [
        ("STEP 1 - DESIGN PREVIEW", "You send a photo of your room. We design the wall around your space, screen and equipment, and send back a concept with a written estimate."),
        ("STEP 2 - MATERIALS & SCHEDULE", "You approve the design and materials. We order everything and schedule the build days - most materials are prepared before we arrive."),
        ("STEP 3 - BUILD", "Our crew builds the wall in layers: framing, finish, cabinetry, lighting and equipment. The room is protected and the site is cleaned daily."),
        ("STEP 4 - WALKTHROUGH", "We mount and connect the equipment, test lighting and remotes with you, and walk every seam and edge together before final payment."),
    ]
    steps = steps_a if pick([0, 1], "steps", key) == 0 else STEPS_B
    return '<div class="steps">' + "".join(f'<div class="step"><b>{t}</b><p class="muted" style="font-size:15px">{d}</p></div>' for t, d in steps) + "</div>"

# ---------------- matrix page text blocks (rotated per page for uniqueness) ----------------

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

def city_obj(t): return {"slug": t[0], "name": t[1], "county": t[2], "miles": t[3], "hoods": t[4], "housing": t[5], "landmark": t[6]}
CITY = {c[0]: city_obj(c) for c in CITIES}
SVC = {s["slug"]: s for s in SERVICES}
STYLE_BY_SLUG = {s["slug"]: s for s in STYLES}

# service -> style render: ONE shared image per service, reused on the service hub
# and on every city x service page for that service (no per-city images).
SERVICE_IMAGES = {
 "tv-media-walls": ("full-built-in.webp", "floor-to-ceiling built-in media wall in walnut with lit display shelving and a linear fireplace"),
 "accent-walls": ("shiplap-panels.webp", "white shiplap feature wall with a natural wood mantel beam and electric fireplace"),
 "stone-marble-walls": ("stone-marble.webp", "floor-to-ceiling black marble-look porcelain slabs with white and gold veining and a centered TV"),
 "fireplace-walls": ("fireplace-wall.webp", "fluted walnut niches flanking a wide linear fireplace with a stone surround"),
 "walnut-slat-walls": ("minimalist-tv-wall.webp", "single smooth charcoal panel TV wall with a thin linear fireplace"),
}

def svc_img(svc, city_name=None):
    fn, desc = SERVICE_IMAGES[svc["slug"]]
    loc = f' in {city_name}' if city_name else " in Los Angeles"
    return (f'<img class="hero-img" src="/assets/styles/{fn}" loading="lazy" '
            f'alt="{esc(svc["name"])}{loc} - {desc} - design concept">')

def nearest(city, n=6):
    others = [c for c in CITIES if c[0] != city["slug"]]
    others.sort(key=lambda c: abs(c[3] - city["miles"]))
    return others[:n]

def matrix_page(city, svc):
    name, short = city["name"], svc["short"]
    path = f'/{svc["slug"]}-{city["slug"]}/'
    title = f'{svc["name"]} in {name}, CA | DecorWall LA'
    desc = (f'Custom {short}s in {name}, CA - from ${svc["price_from"]:,}. Free design preview from a photo of your room, '
            f'written estimate, professional installation across {city["county"]} County.')
    intro = pick(INTRO_T, city["slug"], svc["slug"]).format(city=name, hero=svc["hero_line"], short=short)
    local = pick(LOCAL_T, svc["slug"], city["slug"]).format(city=name, housing=city["housing"], short=short,
            hoods=", ".join(city["hoods"][:3]), landmark=city["landmark"], miles=city["miles"])
    angle = pick(ANGLE_T, city["slug"], svc["slug"], "a").format(short=short)
    close = pick(CLOSE_T, city["slug"], svc["slug"], "c").format(city=name)
    detail = pick([svc["detail"]] + DETAIL_ALT.get(svc["slug"], []), city["slug"], svc["slug"], "d")
    hoods = city["hoods"]
    idea = pick(IDEA_T, city["slug"], svc["slug"], "i").format(
        city=name, short=short,
        hood1=hoods[0], hood2=hoods[1] if len(hoods) > 1 else hoods[0],
        mat=pick(svc["materials"], city["slug"], "m"), opt=pick(svc["options"], city["slug"], "o"))
    price_txt = pick(PRICE_T, city["slug"], svc["slug"], "p").format(
        svc_name=svc["name"], svc_plural=short + "s", city=name, price=f'{svc["price_from"]:,}')
    faq_set = pick([svc["faqs"], FAQ_ALT.get(svc["slug"], svc["faqs"])], city["slug"], svc["slug"], "fset")
    all_faqs = [(q.format(city=name), a.format(city=name)) for q, a in faq_set]
    drop = pick(list(range(len(all_faqs))), city["slug"], svc["slug"], "fq")
    faqs = [f for i, f in enumerate(all_faqs) if i != drop]
    faq_head = pick([f"Questions from {name} homeowners", f"What {name} clients ask us", f"{svc['name']} in {name} - common questions"], city["slug"], svc["slug"], "fh")
    rng_m = random.Random("m" + city["slug"] + svc["slug"]); mats_l = svc["materials"][:]; rng_m.shuffle(mats_l)
    rng_o = random.Random("o" + city["slug"] + svc["slug"]); opts_l = svc["options"][:]; rng_o.shuffle(opts_l)
    mats = "".join(f"<li>{m}</li>" for m in mats_l)
    opts = "".join(f"<li>{o}</li>" for o in opts_l)
    near = nearest(city)
    near_links = "".join(f'<span class="tag"><a href="/{svc["slug"]}-{c[0]}/">{svc["name"]} in {c[1]}</a></span>' for c in near)
    other_svcs = "".join(f'<span class="tag"><a href="/{s["slug"]}-{city["slug"]}/">{s["name"]} in {name}</a></span>' for s in SERVICES if s["slug"] != svc["slug"])
    schema = faq_schema(faqs)
    body = f"""
{crumbs([("Service Areas", "/service-areas/"), (name, f'/media-walls-{city["slug"]}/'), (svc["name"], None)])}
<div class="hero"><div class="wrap">
<h1>{svc["name"]} in {name}</h1>
<p class="lede">{intro}</p>
<p class="price-line">{svc["name"]} in {name} from ${svc["price_from"]:,} &middot; Free design preview &middot; Written estimate before work starts</p>
<a class="cta-btn" href="#estimate">Get my free design preview</a> <a href="tel:{PHONE_TEL}" style="margin-left:14px">Call {PHONE}</a>
<div class="slats"></div>
{svc_img(svc, name)}
{trust_strip()}
</div></div>
{cta_band()}
<section><div class="wrap">
<h2>Built for {name} homes</h2>
<p>{local}</p>
<p>{idea}</p>
<p>{angle}</p>
</div></section>
<section style="background:var(--panel)"><div class="wrap">
<h2>How we build a {short}</h2>
<p>{detail}</p>
<div class="cols"><div><h3>Materials we work with</h3><ul style="margin-left:18px">{mats}</ul></div>
<div><h3>Popular options</h3><ul style="margin-left:18px">{opts}</ul></div></div>
{included_block()}
</div></section>
<section><div class="wrap">
<h2>From photo to finished wall</h2>
{steps_html(svc["name"], city["slug"] + svc["slug"])}
<p style="margin-top:16px">{close}</p>
</div></section>
<section style="background:var(--panel)"><div class="wrap">
<h2>{svc["name"]} in {name} - pricing</h2>
<p>{price_txt}</p>
</div></section>
<section><div class="wrap">
<h2>{faq_head}</h2>
{faq_html(faqs)}
</div></section>
<section><div class="wrap">
{form_block(city, svc)}
<h3>More in {name}</h3><p>{other_svcs}</p>
<h3>{svc["name"]} nearby</h3><p>{near_links}</p>
</div></section>
"""
    return path, head(title, desc, path, schema) + body + footer()

def city_hub(city):
    name = city["name"]
    path = f'/media-walls-{city["slug"]}/'
    title = f'Media Walls & Decorative Panels in {name}, CA | DecorWall LA'
    desc = f'Custom media walls, walnut slat walls, stone feature walls and fireplace walls in {name}, CA. Free design preview, written estimates, installs across {city["county"]} County.'
    cards = "".join(f'<div class="card"><a href="/{s["slug"]}-{city["slug"]}/">{s["name"]} in {name}</a><p>From ${s["price_from"]:,} &middot; {s["hero_line"][:110]}...</p></div>' for s in SERVICES)
    faqs = [
        (f"How much does a media wall cost in {name}?", f"In {name}, TV accent walls start at $2,500, full custom media walls at $7,500 and stone and marble walls at $9,800. Every project gets a written estimate after a free design preview based on a photo of your room."),
        (f"Do you really serve {name}?", f"Yes. {name} is about {city['miles']} miles from our Los Angeles base, inside our standard service area. Design, delivery and installation run on the same schedule as our Los Angeles projects."),
        (f"What areas of {name} do you cover?", f"All of {name}, including {', '.join(city['hoods'])}. If you are near the city line, send the form anyway - we cover the surrounding area within roughly 40 miles of Los Angeles."),
        (f"How do I start a project in {name}?", f"Send a photo of your room through the estimate form. We reply with a design concept for your wall and a written estimate range - free, with no visit required."),
    ]
    near = nearest(city)
    near_links = "".join(f'<span class="tag"><a href="/media-walls-{c[0]}/">Media walls in {c[1]}</a></span>' for c in near)
    body = f"""
{crumbs([("Service Areas", "/service-areas/"), (name, None)])}
<div class="hero"><div class="wrap">
<h1>Media Walls & Decorative Panels in {name}</h1>
<p class="lede">DecorWall LA designs and builds custom TV media walls, walnut slat walls, stone feature walls and fireplace walls in {name}. {city['housing'].capitalize()} - and one well-built wall is usually what finishes them.</p>
<p class="price-line">TV accent walls from $2,500 &middot; Full media walls from $7,500 &middot; Stone & marble from $9,800</p>
<a class="cta-btn" href="#estimate">Get my free design preview</a>
<div class="slats"></div>
{trust_strip()}
</div></div>
<section><div class="wrap">
<h2>Our services in {name}</h2>
<div class="grid">{cards}</div>
<h2>Working in {name}</h2>
<p>{name} homes are {city['housing']}. Neighborhoods we serve include {', '.join(city['hoods'])} - the area around {city['landmark']}. Every project starts from a photo of your actual room, so proportions, materials and lighting are designed for your space, not copied from a showroom wall.</p>
<p>From the first concept to the final walkthrough you deal with one crew and one written estimate. No day-rate surprises, no scope creep after the build starts.</p>
</div></section>
{cta_band()}
<section style="background:var(--panel)"><div class="wrap">
<h2>How a project runs</h2>
{steps_html("media wall", city["slug"] + "hub")}
</div></section>
<section><div class="wrap">
<h2>Questions from {name} homeowners</h2>
{faq_html(faqs)}
</div></section>
<section><div class="wrap">
{form_block(city, None)}
<h3>Nearby service areas</h3><p>{near_links}</p>
</div></section>
"""
    return path, head(title, desc, path, faq_schema(faqs)) + body + footer()

def service_hub(svc):
    path = f'/{svc["slug"]}/'
    title = f'{svc["name"]} in Los Angeles | DecorWall LA'
    desc = f'{svc["name"]} in Los Angeles - from ${svc["price_from"]:,}. {svc["hero_line"]} Free design preview and written estimates.'
    city_links = "".join(f'<span class="tag"><a href="/{svc["slug"]}-{c[0]}/">{c[1]}</a></span>' for c in CITIES)
    faqs = [(q.format(city="Los Angeles"), a.format(city="Los Angeles")) for q, a in svc["faqs"][:3]]
    mats = "".join(f"<li>{m}</li>" for m in svc["materials"])
    opts = "".join(f"<li>{o}</li>" for o in svc["options"])
    body = f"""
{crumbs([(svc["name"], None)])}
<div class="hero"><div class="wrap">
<h1>{svc["name"]} in Los Angeles</h1>
<p class="lede">{svc["hero_line"]}</p>
<p class="price-line">From ${svc["price_from"]:,} &middot; Free design preview &middot; Written estimate</p>
<a class="cta-btn" href="#estimate">Get my free design preview</a>
<div class="slats"></div>
{svc_img(svc)}
{trust_strip()}
</div></div>
{cta_band()}
<section><div class="wrap">
<h2>About our {svc["short"]}s</h2>
<p>{pick([svc["detail"]] + DETAIL_ALT.get(svc["slug"], []), svc["slug"], "hub")}</p>
<div class="cols"><div><h3>Materials we work with</h3><ul style="margin-left:18px">{mats}</ul></div>
<div><h3>Popular options</h3><ul style="margin-left:18px">{opts}</ul></div></div>
{included_block()}
</div></section>
<section style="background:var(--panel)"><div class="wrap">
<h2>How it works</h2>
{steps_html(svc["name"], svc["slug"] + "hub")}
</div></section>
<section><div class="wrap">
<h2>Common questions</h2>
{faq_html(faqs)}
<h2 style="margin-top:30px">{svc["name"]} by city</h2>
<p>{city_links}</p>
{form_block(None, svc)}
</div></section>
"""
    return path, head(title, desc, path, faq_schema(faqs)) + body + footer()

def style_card(st):
    price = f'From ${st["price_from"]:,}' if st["price_from"] else "Priced by design"
    return (f'<div class="card"><a href="/styles/{st["slug"]}/"><img src="/assets/styles/{st["image"]}" '
            f'alt="{esc(st["alt"])} - design concept" loading="lazy" style="width:100%;border-radius:7px"></a>'
            f'<a href="/styles/{st["slug"]}/">{st["name"]}</a><p>{esc(st["tagline"])}</p>'
            f'<p style="color:var(--amber);margin-top:8px">{price}</p></div>')

def style_price_line(st):
    if st["price_from"]:
        return f'{st["name"]} walls from ${st["price_from"]:,} &middot; Free design preview &middot; Written estimate before work starts'
    return "Priced by design - request an estimate &middot; Free design preview &middot; Written estimate before work starts"

def styles_hub():
    path = "/styles/"
    title = "Media Wall Styles | DecorWall LA"
    desc = ("Six media wall styles by DecorWall LA: full built-in, Roman clay and fluted oak, floating cabinet, "
            "Roman clay minimalist, shiplap and panels, and minimalist TV wall. Free design preview from a photo of your room.")
    cards = "".join(style_card(st) for st in STYLES)
    body = f"""
{crumbs([("Styles", None)])}
<div class="hero"><div class="wrap">
<h1>Media Wall Styles</h1>
<p class="lede">Every DecorWall LA wall starts from one of six looks. Pick the one closest to your room - then we adapt it to your wall, your screen and your equipment in the free design preview. All images are design concepts, so you can picture the style before it is drawn for your space.</p>
<a class="cta-btn" href="#estimate">Get my free design preview</a>
<div class="slats"></div>
{trust_strip()}
</div></div>
<section><div class="wrap">
<div class="grid">{cards}</div>
<h2>Not sure which style fits?</h2>
<p>Send a photo of your room through the form. We will point the design at the style that suits your space, light and existing furniture - and show you the wall before you commit to anything. Most clients start with a style and adjust: a floating cabinet under Roman clay, shiplap with LED shelves, a built-in that borrows the minimalist panel. The styles are starting points, not packages.</p>
{form_block(None, None)}
</div></section>
"""
    return path, head(title, desc, path) + body + footer()

def style_page(st):
    path = f'/styles/{st["slug"]}/'
    title = f'{st["name"]} Media Wall Style | DecorWall LA'
    desc = f'{st["name"]} media walls in Los Angeles by DecorWall LA. {st["tagline"]} Free design preview and a written estimate.'
    paras = "".join(f"<p>{p}</p>" for p in st["paragraphs"])
    fins = "".join(f"<li>{f}</li>" for f in st["finishes"])
    dets = "".join(f"<li>{d}</li>" for d in st["details"])
    rel_svcs = "".join(f'<span class="tag"><a href="/{SVC[s]["slug"]}/">{SVC[s]["name"]}</a></span>' for s in st["services"])
    idx = STYLES.index(st)
    others = [STYLES[(idx + i) % len(STYLES)] for i in (1, 2, 3)]
    other_cards = "".join(style_card(o) for o in others)
    body = f"""
{crumbs([("Styles", "/styles/"), (st["name"], None)])}
<div class="hero"><div class="wrap">
<h1>{st["name"]}</h1>
<p class="lede">{esc(st["tagline"])}</p>
<p class="price-line">{style_price_line(st)}</p>
<a class="cta-btn" href="#estimate">Get my free design preview</a> <a href="tel:{PHONE_TEL}" style="margin-left:14px">Call {PHONE}</a>
<img class="hero-img" src="/assets/styles/{st["image"]}" alt="{esc(st["alt"])} - design concept" loading="lazy">
{trust_strip()}
</div></div>
<section><div class="wrap">
<h2>About the {st["name"]} style</h2>
{paras}
</div></section>
<section style="background:var(--panel)"><div class="wrap">
<div class="cols"><div><h3>Finishes</h3><ul style="margin-left:18px">{fins}</ul></div>
<div><h3>Details &amp; options</h3><ul style="margin-left:18px">{dets}</ul></div></div>
</div></section>
{cta_band()}
<section><div class="wrap">
<h2>Build it as a service</h2>
<p>{rel_svcs}</p>
<h2 style="margin-top:26px">More styles</h2>
<div class="grid">{other_cards}</div>
{form_block(None, None)}
</div></section>
"""
    return path, head(title, desc, path) + body + footer()

def style_pages():
    pages = [styles_hub()]
    for st in STYLES:
        pages.append(style_page(st))
    return pages

def write(path, content):
    full = os.path.join(OUT, path.strip("/"))
    if path.endswith("/") or path == "/":
        full = os.path.join(full, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f: f.write(content)

def matrix_and_hubs():
    urls = []
    # matrix
    for c in CITIES:
        city = CITY[c[0]]
        for svc in SERVICES:
            p, doc = matrix_page(city, svc); write(p, doc); urls.append(p)
        p, doc = city_hub(city); write(p, doc); urls.append(p)
    for svc in SERVICES:
        p, doc = service_hub(svc); write(p, doc); urls.append(p)
    print("matrix+hubs:", len(urls))
    return urls

# ---------------- core pages ----------------

def home_page():
    svc_cards = "".join(f'<div class="card"><a href="/{s["slug"]}/">{s["name"]}</a><p>{s["hero_line"][:120]}... From ${s["price_from"]:,}</p></div>' for s in SERVICES)
    style_cards = "".join(style_card(st) for st in STYLES)
    why = [
        ("See it before we build it", "Every project starts with a free design preview made from a photo of your room - you see the wall, the materials and the layout before anyone picks up a tool."),
        ("Fixed written estimate", "The price in your written estimate is the price you pay. The scope is itemized line by line, and the number does not change after the build starts unless you change the scope."),
        ("One crew, start to finish", "Design, build, electrical coordination and finish are handled by our own Los Angeles team - no handoffs to whoever was available that week."),
        ("Clean, fast installs", "Most walls are completed in days, not weeks. The room is protected, dust is controlled, and cleanup is included before we call a wall done."),
    ]
    why_cards = "".join(f'<div class="card"><h3 style="margin-top:0">{t}</h3><p>{d}</p></div>' for t, d in why)
    city_links = "".join(f'<span class="tag"><a href="/media-walls-{c[0]}/">{c[1]}</a></span>' for c in CITIES[:40])
    faqs = [
        ("How much does a media wall cost in Los Angeles?", "TV accent walls start at $2,500, full custom media walls at $7,500, and stone and marble feature walls at $9,800. Your exact number comes as a written estimate after a free design preview - send a photo of your room through the form and we design your wall first."),
        ("How does the free design preview work?", "Send a photo of your room through any form on this site. We design the wall for your space - layout, materials, lighting - and reply with the concept and a written estimate range. No visit, no obligation."),
        ("How long does installation take?", "Most media walls take 3 to 5 working days on site once materials are ready. Single accent walls often finish in 1 to 3 days. Design and ordering happen before the build, so your room is a work zone for days, not weeks."),
        ("Which areas do you serve?", "Los Angeles and surrounding cities within roughly 40 miles - from Malibu and Santa Monica to Pasadena, the San Gabriel Valley, Orange County and the South Bay. See the full list on the service areas page."),
    ]
    body = f"""
<div class="hero"><div class="wrap">
<h1>Custom Media Walls in Los Angeles</h1>
<p class="lede">DecorWall LA designs and builds TV media walls, walnut slat walls, stone feature walls and fireplace walls - one crew, one written estimate, and a free design preview from a photo of your room before you commit to anything.</p>
<p class="price-line">TV accent walls from $2,500 &middot; Full media walls from $7,500 &middot; Stone &amp; marble from $9,800</p>
<a class="cta-btn" href="#estimate">Get my free design preview</a> <a href="tel:{PHONE_TEL}" style="margin-left:14px">Call {PHONE}</a>
<div class="slats"></div>
{trust_strip()}
</div></div>
<section><div class="wrap">
<h2>What we build</h2>
<div class="grid">{svc_cards}</div>
</div></section>
<section><div class="wrap">
<h2>Start from a style</h2>
<p class="muted">Six looks we design from. Pick the one closest to your room and we adapt it to your wall, your screen and your budget in the free design preview.</p>
<div class="grid">{style_cards}</div>
<p><a href="/styles/">See all design styles &raquo;</a></p>
</div></section>
{cta_band()}
<section style="background:var(--panel)"><div class="wrap">
<h2>How it works</h2>
{steps_html("media wall")}
</div></section>
<section><div class="wrap">
<h2>Why homeowners pick a built wall over a bigger TV stand</h2>
<p>A media wall is designed to the inch: the screen at the right height, equipment hidden but ventilated, cables gone, and storage where you actually need it. The wall reads as furniture - the most finished surface in the room - instead of a TV sitting in front of drywall. Add walnut slats for warmth, stone for weight, or a linear fireplace for the evenings, and the room is done.</p>
<p>Every project starts the same way: your room photo, our design, a written number. <a href="/cost/">See what media walls cost</a> or <a href="/process/">how the process runs</a>.</p>
<h2 style="margin-top:26px">Service areas</h2>
<p>{city_links}</p>
<p><a href="/service-areas/">All service areas &raquo;</a></p>
</div></section>
<section><div class="wrap">
<h2>Why homeowners choose DecorWall LA</h2>
<div class="grid">{why_cards}</div>
</div></section>
<section style="background:var(--panel)"><div class="wrap">
<h2>Prices at a glance</h2>
<table><tr><th>Project</th><th>Starting price</th><th></th></tr>{price_rows()}</table>
<p class="small">Every number is a starting point for a standard wall - your written estimate is fixed before the build starts. Full breakdown on the <a href="/cost/">cost page</a>.</p>
</div></section>
<section><div class="wrap">
<h2>Common questions</h2>
{faq_html(faqs)}
</div></section>
<section><div class="wrap">
{form_block(None, None)}
</div></section>
"""
    return "/", head("Custom Media Walls in Los Angeles | DecorWall LA",
        "Custom TV media walls, walnut slat walls, stone feature walls and fireplace walls in Los Angeles. Free design preview from your room photo. Accent walls from $2,500.", "/", faq_schema(faqs)) + body + footer()

def cost_page():
    rows = [
        ("TV accent wall (panels + floating cabinet)", "from $2,500"),
        ("Walnut slat wall (TV section)", "from $2,500"),
        ("Accent wall - decorative panels, one wall", "from $2,500"),
        ("Electric fireplace wall", "from $5,900"),
        ("Full custom media wall (built-ins, lighting)", "from $7,500"),
        ("Stone & marble feature wall", "from $9,800"),
        ("Whole-home accent package", "by written quote"),
    ]
    trs = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    body = f"""
{crumbs([("Media Wall Cost", None)])}
<div class="hero"><div class="wrap"><h1>How Much Does a Media Wall Cost in Los Angeles?</h1>
<p class="lede">Real starting numbers, what moves them, and what your written estimate covers. No "call for pricing" games.</p>
<div class="slats"></div>{trust_strip()}</div></div>
<section><div class="wrap">
<h2>Starting prices</h2>
<table><tr><th>Project</th><th>Price</th></tr>{trs}</table>
<p class="small">Starting prices assume a standard wall in good condition and our standard material lines. Fireplace wall pricing is a starting estimate - the fireplace unit is quoted by size and brand in your written estimate.</p>
<h2>What drives the price</h2>
<p><b>Wall size.</b> Width and ceiling height set material quantities more than anything else. <b>Materials.</b> Painted panels are the most affordable finish; real walnut veneer, large-format porcelain and natural stone sit higher. <b>Cabinetry.</b> A floating cabinet is simpler than full-height built-ins with doors and drawers. <b>Equipment.</b> Projector lifts, motorized platforms and fireplace units are priced per model. <b>Electrical.</b> New outlets or circuits inside the wall add cost when they are needed.</p>
<h2>What your estimate covers</h2>
<p>Design preview, all materials, delivery, installation, equipment mounting and connection, lighting setup, and the final walkthrough. The estimate is written and itemized - the number does not change after the build starts unless you change the scope.</p>
{form_block(None, None)}
</div></section>
"""
    return "/cost/", head("Media Wall Cost in Los Angeles | DecorWall LA",
        "Media wall cost in Los Angeles: accent walls from $2,500, full media walls from $7,500, stone and marble from $9,800. What drives the price and what the estimate covers.", "/cost/") + body + footer()

def simple_page(path, title, desc, h1, paras, form=True):
    ps = "".join(f"<p>{p}</p>" for p in paras)
    fb = form_block(None, None) if form else ""
    body = f"""
{crumbs([(h1, None)])}
<div class="hero"><div class="wrap"><h1>{h1}</h1><div class="slats"></div></div></div>
<section><div class="wrap">{trust_strip()}{ps}{fb}</div></section>
"""
    return path, head(title, desc, path) + body + footer()

def areas_page():
    la = [c for c in CITIES if c[2] == "Los Angeles"]; oc = [c for c in CITIES if c[2] == "Orange"]; ve = [c for c in CITIES if c[2] == "Ventura"]
    def links(lst): return "".join(f'<span class="tag"><a href="/media-walls-{c[0]}/">{c[1]}</a></span>' for c in lst)
    body = f"""
{crumbs([("Service Areas", None)])}
<div class="hero"><div class="wrap"><h1>Service Areas</h1>
<p class="lede">We design and install media walls and decorative panels across Los Angeles and surrounding cities within about 40 miles. Pick your city for local pricing, services and questions.</p>
<div class="slats"></div>{trust_strip()}</div></div>
<section><div class="wrap">
<h2>Los Angeles County</h2><p>{links(la)}</p>
<h2>Orange County</h2><p>{links(oc)}</p>
<h2>Ventura County edge</h2><p>{links(ve)}</p>
<p>Near the edge of the map? Send the form anyway - if we cannot serve your address we will tell you honestly and, where we can, point you to someone who can.</p>
{form_block(None, None)}
</div></section>
"""
    return "/service-areas/", head("Service Areas - Media Walls Across Los Angeles | DecorWall LA",
        "DecorWall LA service areas: media wall and decorative panel installation across Los Angeles, Orange County and nearby cities within 40 miles.", "/service-areas/") + body + footer()

def projects_page():
    import glob
    srcs = sorted(glob.glob(os.path.expanduser("~/workspace/imagine_media/media-generation-media-wall-real-room-client-*.webp")) +
                  glob.glob(os.path.expanduser("~/workspace/imagine_media/media-generation-dark-premium-wall-final-fix-*.webp")) +
                  glob.glob(os.path.expanduser("~/workspace/imagine_media/media-generation-media-wall-angle-view-*.webp")) +
                  glob.glob(os.path.expanduser("~/workspace/imagine_media/media-generation-dark-premium-wall-hidden-door-*.webp")) +
                  glob.glob(os.path.expanduser("~/workspace/imagine_media/media-generation-dark-premium-wall-wood-backing-0-*.webp")) +
                  glob.glob(os.path.expanduser("~/workspace/imagine_media/media-generation-dark-premium-wall-no-ceiling-light-*.webp")))
    os.makedirs(os.path.join(OUT, "assets", "projects"), exist_ok=True)
    imgs = ""
    captions = ["Walnut slats, black marble and a floating cabinet - design concept",
                "Full media wall with stone column - design concept", "Angled view: panel rhythm and LED lines - design concept",
                "Hidden door inside a slat wall - design concept", "Wood backing wall with warm backlight - design concept",
                "Clean ceiling line, no crown gap - design concept"]
    for i, s in enumerate(srcs[:6]):
        dst = os.path.join(OUT, "assets", "projects", f"project-{i+1}.webp")
        shutil.copy(s, dst)
        cap = captions[i] if i < len(captions) else "Media wall - design concept"
        imgs += f'<div class="card"><img src="/assets/projects/project-{i+1}.webp" alt="{esc(cap)}" loading="lazy" style="width:100%;border-radius:7px"><p>{cap}</p></div>'
    body = f"""
{crumbs([("Projects", None)])}
<div class="hero"><div class="wrap"><h1>Projects & Design Concepts</h1>
<p class="lede">Concepts we design from client room photos before a build starts. Completed-installation photography is added as projects finish - every image here is labeled honestly.</p>
<div class="slats"></div>{trust_strip()}</div></div>
<section><div class="wrap">
<div class="grid">{imgs}</div>
<p>Want to see your room in this gallery's style? The design preview is free and starts from one photo.</p>
{form_block(None, None)}
</div></section>
"""
    return "/projects/", head("Media Wall Projects & Design Concepts | DecorWall LA",
        "Media wall design concepts by DecorWall LA: walnut slats, black marble, hidden doors and LED lighting, designed from real client rooms in Los Angeles.", "/projects/") + body + footer()

def faq_page():
    faqs = [
        ("How much does a media wall cost?", "TV accent walls start at $2,500, full custom media walls at $7,500 and stone and marble walls at $9,800. Your written estimate follows a free design preview based on your room photo."),
        ("What is a design preview?", "Our concept for your actual wall: layout, materials and lighting designed from a photo of your room, sent with an estimate range. Free, no visit, no obligation."),
        ("How long does a project take?", "Design and ordering typically take 1 to 3 weeks depending on materials. On site, a single accent wall takes 1 to 3 days and a full media wall 3 to 5 days."),
        ("Do you hide wires and equipment?", "Yes - concealed channels, ventilated equipment bays and flush access panels are standard in our designs."),
        ("Can you work with my existing TV or projector?", "Yes. We design around your equipment's exact dimensions, or size new equipment in the preview if you have not bought it yet."),
        ("Do you offer a warranty?", "We stand behind our installation work: if something we built or installed fails under normal use, tell us and we will make it right. Terms are spelled out in your written estimate."),
        ("Which areas do you serve?", "Los Angeles and surrounding cities within about 40 miles, including Orange County and the South Bay. See the service areas page for the full city list."),
        ("How do payments work?", "Payments follow the milestones in your written estimate - never a surprise lump sum. The schedule is agreed before the build starts."),
    ]
    body = f"""
{crumbs([("FAQ", None)])}
<div class="hero"><div class="wrap"><h1>Frequently Asked Questions</h1><div class="slats"></div>{trust_strip()}</div></div>
<section><div class="wrap">{faq_html(faqs)}{form_block(None, None)}</div></section>
"""
    return "/faq/", head("Media Wall FAQ | DecorWall LA",
        "Answers about media wall cost, timelines, design previews, hidden wiring and service areas - DecorWall LA, Los Angeles.", "/faq/", faq_schema(faqs)) + body + footer()

def core_pages():
    pages = []
    pages.append(home_page())
    pages.append(cost_page())
    pages.append(areas_page())
    pages.append(projects_page())
    pages.append(faq_page())
    pages.append(simple_page("/process/", "Our Process - From Photo to Finished Wall | DecorWall LA",
        "The DecorWall LA process: free design preview, written estimate, materials and schedule, clean build, final walkthrough.",
        "Our Process", [
        "<b>1. Design preview.</b> You send a photo of your room through the form. We design the wall - layout, materials, lighting, equipment fit - and send the concept with a written estimate range.",
        "<b>2. Written estimate.</b> You approve the design; we finalize materials and give you an itemized, fixed estimate and a build schedule. Nothing starts until you sign off on the number.",
        "<b>3. Build.</b> Materials are prepared before we arrive. On site we protect the room, build in layers - framing, finish, cabinetry, lighting - and clean daily. Most media walls take 3 to 5 working days.",
        "<b>4. Walkthrough.</b> Equipment mounted and connected, remotes and lighting tested with you, every seam checked together. Final payment follows the walkthrough, per your estimate."]))
    pages.append(simple_page("/materials/", "Materials & Lighting | DecorWall LA",
        "Materials DecorWall LA works with: walnut acoustic slats, large-format porcelain, marble-look tile, stone veneer, LED lighting and dimmers.",
        "Materials & Lighting", [
        "<b>Walnut slat panels.</b> Real walnut veneer over acoustic felt backing - warmth, texture and real sound dampening for open-plan rooms.",
        "<b>Large-format porcelain.</b> Marble looks without marble upkeep: 24x48 and larger slabs, thin color-matched seams, no sealing, heat and stain resistant.",
        "<b>Stone veneer.</b> Natural split-face and ledgestone for weight and shadow where a flat finish is not enough.",
        "<b>Painted panels and roman clay.</b> Matte, mineral finishes that keep a wall quiet and let furniture carry the color.",
        "<b>Lighting.</b> LED strips in channels and behind panels, on dimmers and remotes. Warm 2700-3000K light is our default - it is what makes walnut and stone look expensive at night.",
        "Every material in your design preview is named in the written estimate, so you know exactly what is being installed before the build starts."]))
    pages.append(simple_page("/about/", "About DecorWall LA | DecorWall LA",
        "DecorWall LA is a Los Angeles installation studio for custom media walls and decorative panels, built on years of hands-on construction work.",
        "About DecorWall LA", [
        "DecorWall LA is the decorative-wall studio of a Los Angeles construction team with years of hands-on remodeling work across the city - framing, finish carpentry, tile and electrical coordination under one roof.",
        "We started DecorWall LA because media walls kept being the worst-run part of otherwise good remodels: designed by a furniture store, wired by guesswork, finished by whoever was available. Our model is the opposite: one team designs the wall around your room and equipment, prices it in writing, and builds it in days.",
        f"Questions before you start? Email {EMAIL} or call {PHONE}."]))
    pages.append(simple_page("/estimate/", "Get a Free Design Preview | DecorWall LA",
        "Request a free media wall design preview: send a photo of your room, get a concept and a written estimate from DecorWall LA.",
        "Get Your Free Design Preview",
        ["Send the form below with a photo of your room. We reply with a design concept for your wall and a written estimate range - usually within one business day. Prefer to talk? Call " + PHONE + "."]))
    pages.append(simple_page("/thank-you/", "Thank You | DecorWall LA",
        "Thank you - your design preview request is in. DecorWall LA will reply with your concept and estimate.",
        "Thank you - request received",
        ["Your request is in. We will reply with your design preview and estimate range, usually within one business day. If your project is time-sensitive, call " + PHONE + " and mention your form submission."], form=False))
    pages.append(simple_page("/privacy/", "Privacy Policy | DecorWall LA",
        "DecorWall LA privacy policy: how contact details and room photos from our forms are used.",
        "Privacy Policy",
        ["Information you send through our forms - name, phone, email, project details and room photos - is used only to prepare your design preview, estimate and project communication. We do not sell your information. Photos are used for design purposes for your project. To have your information removed, email " + EMAIL + "."], form=False))
    return pages

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "style.css"), "w") as f: f.write(CSS)
    logo_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.webp")
    if os.path.exists(logo_src): shutil.copy(logo_src, os.path.join(OUT, "assets", "logo.webp"))
    styles_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "styles")
    if os.path.isdir(styles_src):
        shutil.copytree(styles_src, os.path.join(OUT, "assets", "styles"))
    urls = matrix_and_hubs()
    for p, doc in core_pages():
        write(p, doc); urls.append(p)
    for p, doc in style_pages():
        write(p, doc); urls.append(p)
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: " + BASE + "/sitemap.xml\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(set(urls)):
        if u == "/thank-you/": continue
        pr = "1.0" if u == "/" else ("0.9" if u.count("/") <= 2 and "-" not in u.strip("/") else "0.8")
        sm.append(f"<url><loc>{BASE}{u}</loc><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f: f.write("\n".join(sm))
    write("/404.html", head("Page Not Found | DecorWall LA", "Page not found.", "/404.html") +
          '<div class="wrap"><section><h1>Page not found</h1><p>The page moved or never existed. Start from the <a href="/">home page</a> or <a href="/service-areas/">pick your city</a>.</p></section></div>' + footer())
    total_files = sum(len(fs) for _, _, fs in os.walk(OUT))
    print(f"TOTAL: {len(urls)} pages, {total_files} files in dist")

if __name__ == "__main__":
    main()
