# -*- coding: utf-8 -*-
"""
Page generator — Ilkićev kućerak
--------------------------------
Plain HTML has no include mechanism, so the header must be byte-identical in
every file. It is emitted from the single template below rather than copied, so
it cannot drift. Nine pages x three languages = 27 files, plus a root redirect.

Run:  python _build/generate.py

Add a page:  add a slug to SLUG, a builder to BUILDERS, copy to each language
dict, then re-run. Never hand-edit the generated .html files — the next run
overwrites them.
"""

import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = json.load(open(os.path.join(ROOT, "assets", "images", "manifest.json"),
                          encoding="utf-8"))

SITE = "https://kucerak-u-sremu.rs"          # for canonical + hreflang tags
TEL = "+381652880781"
TEL_PRETTY = "+381 65 288 0781"
MAIL = "ilkic@kucerak-u-sremu.rs"
ADRESA = "Mirka Laćarca 9, 22408 Vrdnik"
IG = "https://www.instagram.com/ilkicev_kucerak/"
FB = "https://www.facebook.com/ilkicevkucerak/"
MAPS = "https://maps.google.com/?q=Ilki%C4%87ev+ku%C4%87erak+Mirka+La%C4%87arca+9+Vrdnik"

LANGS = ["sr", "en", "de"]

# page key -> filename per language (localised slugs, real URLs)
SLUG = {
    "pocetna":  {"sr": "index.html",            "en": "index.html",            "de": "index.html"},
    "kuce":     {"sr": "kuce.html",             "en": "houses.html",           "de": "haeuser.html"},
    "kuca2":    {"sr": "dvosobna-kuca.html",    "en": "two-bedroom-house.html","de": "zweizimmerhaus.html"},
    "kuca1":    {"sr": "jednosobna-kuca.html",  "en": "one-bedroom-house.html","de": "einzimmerhaus.html"},
    "proslave": {"sr": "proslave.html",         "en": "celebrations.html",     "de": "feiern.html"},
    "bazen":    {"sr": "bazen.html",            "en": "pool.html",             "de": "pool.html"},
    "kontakt":  {"sr": "kontakt.html",          "en": "contact.html",          "de": "kontakt.html"},
}

RODITELJ = "kuce"                                  # nosi padajuci meni
DROPDOWN = ["kuca2", "kuca1"]                      # njegove podstrane
TOP = ["pocetna", "kuce", "proslave", "bazen", "kontakt"]


# ============================================================== 1. COMPONENTS

def slika(slot, alt, sizes="100vw", lazy=True, klasa="okvir", ratio=None,
          prioritet=False, popuni=False):
    """<picture> with WebP + JPEG srcsets, an intrinsic ratio to hold layout,
    and the image's own average colour behind it so nothing flashes.

    popuni=True drops the intrinsic ratio so the figure can stretch to whatever
    box contains it — used for the hero, where the section defines the height.
    """
    m = MANIFEST[slot]
    w = m["widths"]
    webp = ", ".join("../assets/images/%s-%d.webp %dw" % (slot, x, x) for x in w)
    jpg = ", ".join("../assets/images/%s-%d.jpg %dw" % (slot, x, x) for x in w)
    biggest = w[-1]
    loading = "" if prioritet else ' loading="lazy" decoding="async"'
    fetch = ' fetchpriority="high"' if prioritet else ""
    if popuni:
        stil = "background:%s" % m["bg"]
    else:
        stil = "background:%s;aspect-ratio:%s" % (
            m["bg"], ratio or ("%d / %d" % (m["w"], m["h"])))
    return (
        '<figure class="%s" style="%s">'
        '<picture>'
        '<source type="image/webp" srcset="%s" sizes="%s">'
        '<img src="../assets/images/%s-%d.jpg" srcset="%s" sizes="%s" '
        'alt="%s" width="%d" height="%d"%s%s>'
        '</picture></figure>'
    ) % (klasa, stil, webp, sizes, slot, biggest, jpg, sizes,
         alt, m["w"], m["h"], loading, fetch)


def natpis(t):
    return '<p class="natpis">%s</p>' % t


def dugme(href, tekst, vrsta="glavno"):
    strelica = ('<svg class="strelica" width="14" height="14" viewBox="0 0 14 14" '
                'fill="none" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" '
                'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
                'stroke-linejoin="round"/></svg>')
    return '<a class="dugme dugme--%s" href="%s"><span>%s</span>%s</a>' % (
        vrsta, href, tekst, strelica)


def strelica_kvadrat():
    return ('<span class="strelica-dugme" aria-hidden="true">'
            '<svg width="13" height="13" viewBox="0 0 14 14" fill="none">'
            '<path d="M3.5 10.5l7-7M5 3.5h5.5V9" stroke="currentColor" '
            'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg></span>')


def traka(sadrzaj, klase="", podatak=None, grupa=True):
    p = ' data-podatak="%s"' % podatak if podatak else ""
    g = ' data-grupa' if grupa else ""
    return '<section class="traka %s"%s%s><div class="omot">%s</div></section>' % (
        klase, p, g, sadrzaj)


def brojevi(stavke):
    """stavke: list of (value, suffix, label). Value counts up when in view."""
    out = []
    for v, suf, lab in stavke:
        sm = '<small>%s</small>' % suf if suf else ""
        out.append(
            '<div class="otkrij"><p class="broj-vrednost">'
            '<span data-broj="%s">%s</span>%s</p>'
            '<p class="broj-oznaka">%s</p></div>' % (v, v, sm, lab))
    return '<div class="brojevi" data-grupa>%s</div>' % "".join(out)


def poziv(L, naslov, tekst, lang):
    return (
        '<section class="traka" data-grupa><div class="omot">'
        '<div class="poziv otkrij"><div class="para-polje" aria-hidden="true">'
        '<b></b><b></b><b></b></div><div class="omot-uzi">'
        '%s<h2>%s</h2><p class="uvod">%s</p>'
        '<div class="grupa-dugmadi">%s%s</div>'
        '</div></div></div></section>'
    ) % (natpis(L["c"]["poziv_natpis"]), naslov, tekst,
         dugme(SLUG["kontakt"][lang], L["c"]["upit"]),
         dugme("tel:" + TEL, TEL_PRETTY, "tiho"))


# ================================================================ 2. CONTENT

# Sav tekst zivi u _build/tekst.py, da se copy menja bez diranja generatora.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tekst import SR, EN, DE, JEZICI  # noqa: E402



# ============================================================== 3. TEMPLATES

def glava(L, kljuc, lang):
    """<head> + opening body, header and drawer. Identical in every file."""
    P = L[kljuc if kljuc in L else "home"]
    naslov = P.get("title", "Ilkićev kućerak")
    opis = P.get("desc", "")
    kanon = "%s/%s/%s" % (SITE, lang, SLUG[kljuc][lang])

    alt = "".join(
        '<link rel="alternate" hreflang="%s" href="%s/%s/%s">' % (
            JEZICI[j]["htmllang"], SITE, j, SLUG[kljuc][j]) for j in LANGS)
    alt += '<link rel="alternate" hreflang="x-default" href="%s/sr/%s">' % (SITE, SLUG[kljuc]["sr"])

    ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "name": "Ilkićev kućerak u Sremu",
        "description": opis,
        "address": {"@type": "PostalAddress", "streetAddress": "Mirka Laćarca 9",
                    "addressLocality": "Vrdnik", "postalCode": "22408",
                    "addressCountry": "RS"},
        "telephone": TEL,
        "email": MAIL,
        "url": kanon,
        "sameAs": [IG, FB],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.7",
                            "reviewCount": "303"},
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": "Heated saltwater pool", "value": True},
            {"@type": "LocationFeatureSpecification", "name": "Free parking", "value": True},
            {"@type": "LocationFeatureSpecification", "name": "Free Wi-Fi", "value": True},
        ],
    }, ensure_ascii=False)

    return """<!doctype html>
<html lang="%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
%s
<meta property="og:type" content="website">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="%s/assets/images/hero-estate-1600.jpg">
<meta property="og:locale" content="%s">
<meta name="theme-color" content="#EAE3D1">
<link rel="icon" href="../assets/grb.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,200..600;1,6..72,200..500&display=swap">
<link rel="stylesheet" href="../assets/css/style.css">
<script>document.documentElement.className+=' js';</script>
<script type="application/ld+json">%s</script>
</head>
<body>
<a class="skip" href="#sadrzaj">%s</a>
<div class="kicma-mobilna" aria-hidden="true"><i></i></div>
<div class="kicma" aria-hidden="true"><div class="kicma-sina"><span class="kicma-tok"></span></div></div>
%s
<main id="sadrzaj">
""" % (L["htmllang"], naslov, opis, kanon, alt, naslov, opis, SITE,
       L["htmllang"].replace("-", "_"), ld, L["c"]["preskoci"], zaglavlje(L, kljuc, lang))


def zaglavlje(L, kljuc, lang):
    n = L["nav"]
    u_padajucem = kljuc in DROPDOWN

    stavke = []
    for k in TOP:
        aktivan = (k == kljuc) or (k == RODITELJ and u_padajucem)
        kls = "nav-stavka" + (" aktivan" if aktivan else "")
        if k == RODITELJ and DROPDOWN:
            kls += " ima-podmeni"
            pod = "".join(
                '<li class="%s"><a class="podmeni-veza" href="%s">%s</a></li>' % (
                    "aktivan" if d == kljuc else "", SLUG[d][lang], n[d])
                for d in DROPDOWN)
            kapa = ('<svg class="nav-kapa" width="9" height="6" viewBox="0 0 9 6" fill="none" '
                    'aria-hidden="true"><path d="M1 1.5L4.5 5L8 1.5" stroke="currentColor" '
                    'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
            stavke.append(
                '<li class="%s"><a class="nav-veza" href="%s" aria-expanded="false" '
                'aria-haspopup="true">%s%s</a><ul class="podmeni">%s</ul></li>' % (
                    kls, SLUG[k][lang], n[k], kapa, pod))
        else:
            stavke.append('<li class="%s"><a class="nav-veza" href="%s">%s</a></li>' % (
                kls, SLUG[k][lang], n[k]))

    jezici = "".join(
        '<a class="jezik" href="../%s/%s" hreflang="%s"%s lang="%s">%s</a>' % (
            j, SLUG[kljuc][j], JEZICI[j]["htmllang"],
            ' aria-current="true"' if j == lang else "", JEZICI[j]["htmllang"],
            j.upper())
        for j in LANGS)

    # drawer
    fioka = []
    for k in TOP:
        aktivan = (k == kljuc) or (k == RODITELJ and u_padajucem)
        fioka.append('<li class="%s"><a class="fioka-veza" href="%s">%s</a>' % (
            "aktivan" if aktivan else "", SLUG[k][lang], n[k]))
        if k == RODITELJ and DROPDOWN:
            pod = "".join('<li class="%s"><a href="%s">%s</a></li>' % (
                "aktivan" if d == kljuc else "", SLUG[d][lang], n[d]) for d in DROPDOWN)
            fioka.append('<ul class="fioka-pod">%s</ul>' % pod)
        fioka.append("</li>")

    return """<header class="zaglavlje">
<div class="omot zaglavlje-red">
<a class="logo" href="%s" aria-label="Ilkićev kućerak, %s">
<img src="../assets/grb.svg" alt="" width="38" height="38">
<span class="logo-tekst"><span class="logo-ime">Ilkićev kućerak</span><span class="logo-mesto">%s</span></span>
</a>
<nav class="navigacija" aria-label="%s"><ul class="nav-lista">%s</ul></nav>
<div class="jezici" role="group" aria-label="%s">%s</div>
%s
<button class="burger" aria-expanded="false" aria-controls="fioka" aria-label="%s">
<span></span><span></span><span></span></button>
</div>
</header>
<div class="fioka" id="fioka">
<div class="fioka-jezici">
<p class="natpis">%s</p>
<div class="jezici" role="group" aria-label="%s">%s</div>
</div>
<ul>%s</ul>
<div class="grupa-dugmadi" style="margin-top:var(--s10)">%s</div>
</div>""" % (SLUG["pocetna"][lang], L["nav"]["pocetna"], L["c"]["mesto"],
             L["c"]["meni"], "".join(stavke), L["c"]["jezik"], jezici,
             dugme(SLUG["kontakt"][lang], L["c"]["upit"]),
             L["c"]["meni"],
             L["c"]["jezik"], L["c"]["jezik"], jezici,
             "".join(fioka),
             dugme(SLUG["kontakt"][lang], L["c"]["upit"]))


def podnozje(L, lang):
    n = L["nav"]
    kolona = lambda naslov, stavke: (
        '<div><h2>%s</h2><ul>%s</ul></div>' % (
            naslov, "".join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in stavke)))

    ig = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
          '<rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.6"/>'
          '<circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.6"/>'
          '<circle cx="17.5" cy="6.5" r="1.2" fill="currentColor"/></svg>')
    fb = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
          '<path d="M14 8.5V6.8c0-.8.3-1.3 1.4-1.3H17V2.6C16.6 2.5 15.7 2.4 14.7 2.4c-2.2 0-3.7 1.3-3.7 3.9v2.2H8.4V12H11v9h3v-9h2.5l.4-3.5H14z" '
          'fill="currentColor"/></svg>')

    return """</main>
<footer class="podnozje">
<div class="omot">
<div class="podnozje-resetka">
<div>
<a class="logo" href="%s" style="margin:0 0 var(--s5)">
<img src="../assets/grb.svg" alt="" width="38" height="38">
<span class="logo-tekst"><span class="logo-ime">Ilkićev kućerak</span><span class="logo-mesto">%s</span></span>
</a>
<p class="meta" style="max-width:34ch">%s<br>%s</p>
<ul class="drustvene" style="margin-top:var(--s6)">
<li><a href="%s" target="_blank" rel="noopener" aria-label="Instagram">%s</a></li>
<li><a href="%s" target="_blank" rel="noopener" aria-label="Facebook">%s</a></li>
</ul>
</div>
%s
%s
<div><h2>%s</h2><ul>
<li><a href="tel:%s">%s</a></li>
<li><a href="mailto:%s">%s</a></li>
<li><a href="%s" target="_blank" rel="noopener">%s</a></li>
</ul></div>
</div>
<div class="podnozje-dno">
<p>© <span id="godina">2026</span> Ilkićev kućerak u Sremu. %s</p>
<p>%s</p>
</div>
</div>
</footer>
<script src="../assets/js/script.js" defer></script>
<script>document.getElementById('godina').textContent=new Date().getFullYear();</script>
</body>
</html>""" % (
        SLUG["pocetna"][lang], L["c"]["mesto"], ADRESA, L["kontakt"]["radno_v"],
        IG, ig, FB, fb,
        kolona(L["c"]["kuca"], [(SLUG["kuce"][lang], n["kuce"]),
                                (SLUG["kuca2"][lang], n["kuca2"]),
                                (SLUG["kuca1"][lang], n["kuca1"])]),
        kolona(L["c"]["ponuda"], [(SLUG["proslave"][lang], n["proslave"]),
                                  (SLUG["bazen"][lang], n["bazen"]),
                                  (SLUG["kontakt"][lang], n["kontakt"])]),
        L["c"]["poseta"], TEL, TEL_PRETTY, MAIL, MAIL, MAPS, L["kontakt"]["mapa_l"],
        L["c"]["prava"], ADRESA)


def mrvice(L, lang, kljuc):
    """Breadcrumb for dropdown children, linking back to the parent overview."""
    if kljuc not in DROPDOWN:
        return ""
    return ('<nav aria-label="breadcrumb"><ol class="mrvice">'
            '<li><a href="%s">%s</a></li>'
            '<li><a href="%s">%s</a></li>'
            '<li aria-current="page">%s</li>'
            '</ol></nav>') % (SLUG["pocetna"][lang], L["nav"]["pocetna"],
                              SLUG[RODITELJ][lang], L["nav"][RODITELJ],
                              L["nav"][kljuc])


# Line marks for the home page row. One visual grammar throughout: 24x24,
# no fill, 1.4 stroke, round joins, drawn to read at 40 px. Colour comes from
# the ring, so every mark inherits currentColor.
IKONE = {
    "sapa": (
        '<ellipse cx="6.4" cy="10.8" rx="1.9" ry="2.4"/>'
        '<ellipse cx="10.1" cy="8.1" rx="2" ry="2.7"/>'
        '<ellipse cx="14" cy="8.1" rx="2" ry="2.7"/>'
        '<ellipse cx="17.7" cy="10.8" rx="1.9" ry="2.4"/>'
        '<path d="M12 13.4c3 0 5.3 2.2 5.3 4.4 0 1.7-1.4 2.9-3.1 2.9-1.1 0-1.5-.5-2.2-.5'
        's-1.1.5-2.2.5c-1.7 0-3.1-1.2-3.1-2.9 0-2.2 2.3-4.4 5.3-4.4z"/>'),
    "kapija": (
        '<path d="M2.6 20.6h18.8"/>'
        '<path d="M3.6 20.6v-4.8h3.8"/><path d="M20.4 20.6v-4.8h-3.8"/>'
        '<path d="M7.4 20.6v-8.6a4.6 4.6 0 0 1 9.2 0v8.6"/>'
        '<path d="M12 20.6V7.5"/>'
        '<path d="M7.4 15.8h9.2"/>'),
    "put": (
        '<path d="M12 3.4a5.1 5.1 0 0 0-5.1 5.1c0 3.7 5.1 8.6 5.1 8.6s5.1-4.9 5.1-8.6'
        'A5.1 5.1 0 0 0 12 3.4z"/>'
        '<circle cx="12" cy="8.5" r="1.9"/>'
        '<path d="M3.4 20.6c4.1-1.7 5.6.6 8.6.6s4.5-2.3 8.6-.6"/>'),
    "vrt": (
        '<circle cx="12" cy="8.2" r="4.9"/>'
        '<path d="M12 13.1v7.5"/>'
        '<path d="M2.6 20.6h18.8"/>'
        '<path d="M3.6 20.6a2.6 2.6 0 0 1 5.2 0"/>'
        '<path d="M15.6 20.6a2.4 2.4 0 0 1 4.8 0"/>'),
    "parking": (
        '<rect x="3.4" y="12.7" width="17.2" height="4.9" rx="1.7"/>'
        '<path d="M6.7 12.7l1.9-3.4c.3-.6.9-.9 1.5-.9h3.8c.6 0 1.2.3 1.5.9l1.9 3.4"/>'
        '<circle cx="8.2" cy="17.6" r="1.9"/><circle cx="15.8" cy="17.6" r="1.9"/>'
        '<path d="M2.6 19.5h18.8"/>'),
}


def odlike(L):
    """Five facts a visitor checks before reading anything: the pet, the
    privacy, the drive, the garden, the parking. Each carries its consequence
    underneath, because a mark on its own only decorates."""
    stavke = "".join(
        '<li class="odlika otkrij" style="--i:%d">'
        '<span class="odlika-znak" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
        'stroke-linecap="round" stroke-linejoin="round">%s</svg></span>'
        '<span class="odlika-ime">%s</span>'
        '<span class="odlika-opis">%s</span></li>' % (i, IKONE[k], ime, opis)
        for i, (k, ime, opis) in enumerate(L["home"]["odlike"]))
    return '<ul class="odlike">%s</ul>' % stavke


def snimak(ime, opis, poster_bg="#8d9484"):
    """Klip sa naslovne. Ne pusta se sam: preload="none" znaci da se do klika
    ne skida nijedan bajt, pa se pocetna tezina strane ne menja. Zvuka nema ni
    u fajlu. Odnos 1600x693 je ono sto ostane kad se odsece grafika stanice."""
    return (
        '<figure class="okvir snimak" style="aspect-ratio:1600 / 693;background:%s">'
        '<video controls muted playsinline preload="none" '
        'poster="../assets/video/%s-poster.jpg" aria-label="%s" '
        'width="1600" height="693">'
        '<source src="../assets/video/%s.mp4" type="video/mp4">'
        '</video></figure>') % (poster_bg, ime, opis, ime)


def zaglavlje_strane(L, lang, kljuc, P, slot=None):
    # Prazan "uvod" znaci da strana ide bez uvodne recenice, pa se ni pasus ne
    # ispisuje. Bolje nego prazan <p> koji nosi razmak bez sadrzaja.
    uvod = '<p class="uvod">%s</p>' % P["uvod"] if P.get("uvod") else ""
    return ('<section class="zaglavlje-strane">'
            '<div class="para-polje" aria-hidden="true"><b></b><b></b><b></b></div>'
            '<div class="omot">%s%s<h1>%s</h1>%s</div></section>') % (
        mrvice(L, lang, kljuc), natpis(L["c"]["mesto"]), P["h1"], uvod)


# ============================================================== 4. PAGE BODIES

def stranica_pocetna(L, lang):
    P = L["home"]
    linije = "".join('<span class="linija" style="--i:%d"><span>%s</span></span>' % (i, t)
                     for i, t in enumerate(P["h1"]))

    junak = """<section class="junak">
<div class="junak-pozadina">%s</div>
<div class="para-polje" aria-hidden="true"><b></b><b></b><b></b></div>
<div class="omot junak-omot">
<div class="pojava" style="--d:120">%s</div>
<h1 class="krupno junak-naslov">%s</h1>
<p class="junak-uvod pojava" style="--d:%d">%s</p>
<div class="grupa-dugmadi junak-akcije pojava" style="--d:%d">%s%s</div>
</div>
</section>""" % (
        slika("hero-estate", "Osvetljeni cigleni svodovi kućerka u plavom satu"
              if lang == "sr" else ("Die beleuchteten Ziegelbögen des Hauses zur blauen Stunde"
                                    if lang == "de"
                                    else "The lit brick arches of the house at blue hour"),
              sizes="100vw", klasa="junak-slika", prioritet=True, popuni=True),
        natpis(L["c"]["mesto"]), linije,
        len(P["h1"]) * 95 + 420, P["uvod"],
        len(P["h1"]) * 95 + 580,
        dugme(SLUG["kontakt"][lang], L["c"]["upit"]),
        dugme(SLUG["kuce"][lang], L["nav"]["kuce"], "tiho"))

    # Pet cinjenica koje posetilac proverava pre nego sto pocne da cita.
    znaci = traka(odlike(L), klase="traka--tesna", podatak="900 m²")

    # Dva klipa, odmah pod ikonicama. Stoje jedan uz drugi i cekaju klik.
    klipovi = traka(
        '<div class="par">'
        '<div class="otkrij">%s</div>'
        '<div class="otkrij">%s</div></div>' % (
            snimak("kapija",
                   {"sr": "Snimak ulaza u kućerak i dvorišta",
                    "en": "A clip of the entrance and the courtyard",
                    "de": "Ein Clip vom Eingang und vom Hof"}[lang]),
            snimak("kaskada",
                   {"sr": "Snimak bazena sa kaskadom",
                    "en": "A clip of the pool and its cascade",
                    "de": "Ein Clip vom Pool mit der Kaskade"}[lang])),
        klase="traka--tesna", grupa=False)

    # Orijentacija odmah posle prvog ekrana: sta je, gde je, koliko je blizu i
    # sta o tome kazu gosti. Posetilac koji je tek stigao treba to pre nego
    # sto ga posaljemo u podstranice.
    ukratko = traka(
        '<div class="par par--sirok-levo">'
        '<div class="slaganje otkrij">%s<h2>%s</h2><p>%s</p><p>%s</p></div>'
        '<div class="slaganje otkrij"><p>%s</p>%s</div></div>' % (
            natpis(P["ukratko_natpis"]), P["ukratko_h"],
            P["ukratko_p1"], P["ukratko_p2"], P["ukratko_p3"],
            dugme(SLUG["proslave"][lang], L["nav"]["proslave"], "tiho")),
        klase="traka--uvucena", podatak="VRDNIK")

    kuca = traka(
        '<div class="par par--sirok-desno">'
        '<div class="slaganje otkrij">%s<h2>%s</h2><p>%s</p>%s</div>'
        '<div class="otkrij">%s</div></div>' % (
            natpis(P["kuca_natpis"]), P["kuca_h"], P["kuca_p1"],
            dugme(SLUG["bazen"][lang], L["nav"]["bazen"], "tiho"),
            slika("celebrations-garden",
                  "Sto postavljen u dvorištu, uz bazen" if lang == "sr"
                  else "A table laid in the courtyard beside the pool",
                  sizes="(min-width:900px) 46vw, 100vw", ratio="4 / 5")),
        podatak={"sr": "PRIVATNO", "en": "PRIVATE", "de": "PRIVAT"}[lang])

    # Restoran, odmah ispod privatnosti. Nema jos fotografije kuhinje, pa
    # traka stoji na tekstu. Kad slika stigne, ide u par uz tekst.
    restoran = traka(
        '<div class="stub slaganje otkrij">%s<h2>%s</h2><p class="uvod">%s</p></div>' % (
            natpis(P["restoran_natpis"]), P["restoran_h"], P["restoran_p"]),
        klase="traka--uvucena",
        podatak={"sr": "KUHINJA", "en": "THE KITCHEN", "de": "K\u00dcCHE"}[lang])

    citat = traka(
        '<div class="stub stub--sredina otkrij" style="max-width:62ch">'
        '%s<p class="citat">„%s”</p><p class="citat-izvor">%s</p></div>' % (
            natpis(P["utisci_natpis"]), P["citat"], P["citat_izvor"]),
        klase="traka--tesna", podatak="4.7")

    return junak + znaci + klipovi + ukratko + kuca + restoran + citat + \
        poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_imanje(L, lang):
    P = L["imanje"]
    redovi = "".join('<div class="red-osobine"><dt>%s</dt><dd>%s</dd></div>' % (a, b)
                     for a, b in P["redovi"])
    detalji = "".join('<div class="red-osobine"><dt>%s</dt><dd>%s</dd></div>' % (a, b)
                      for a, b in P["detalji"])

    return zaglavlje_strane(L, lang, "imanje", P) + traka(
        '<div class="par par--sirok-desno" style="margin-bottom:var(--sekcija)">'
        '<div class="otkrij"><h2>%s</h2><dl style="margin-top:var(--s8)">%s</dl></div>'
        '<div class="otkrij">%s</div></div>'
        '<div class="par">'
        '<div class="otkrij">%s</div>'
        '<div class="otkrij"><h2>%s</h2><dl style="margin-top:var(--s8)">%s</dl></div>'
        '</div>' % (
            P["sta_h"], redovi,
            slika("estate-arch-night", "Svodovi noću" if lang == "sr" else "The arches at night",
                  sizes="(min-width:900px) 42vw, 100vw", ratio="3 / 2"),
            slika("interior-hall", "Trpezarija pod svodom" if lang == "sr" else "The vaulted dining room",
                  sizes="(min-width:900px) 46vw, 100vw", ratio="16 / 9"),
            P["detalji_h"], detalji),
        podatak="50") + poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_apartmani(L, lang):
    P = L["apartmani"]
    oz = lambda xs: '<ul class="oznake">%s</ul>' % "".join("<li>%s</li>" % x for x in xs)

    return zaglavlje_strane(L, lang, "apartmani", P) + traka(
        '<div class="par par--sirok-levo" style="margin-bottom:var(--sekcija)">'
        '<div class="slaganje otkrij"><h2>%s</h2><p>%s</p>%s</div>'
        '<div class="otkrij">%s</div></div>'
        '<div class="par par--tekst-desno">'
        '<div class="otkrij">%s</div>'
        '<div class="slaganje otkrij"><h2>%s</h2><p>%s</p>%s</div></div>'
        '<p class="uvod otkrij" style="max-width:52ch;margin-top:var(--sekcija)">%s</p>' % (
            P["a1_h"], P["a1_p"], oz(P["a1_oznake"]),
            slika("interior-apartment", "Unutrašnjost apartmana" if lang == "sr" else "Inside the apartment",
                  sizes="(min-width:900px) 46vw, 100vw", ratio="3 / 2"),
            slika("estate-dusk-wide", "Kuća u sumrak" if lang == "sr" else "The house at dusk",
                  sizes="(min-width:900px) 46vw, 100vw", ratio="3 / 2"),
            P["a2_h"], P["a2_p"], oz(P["a2_oznake"]),
            P["napomena"]),
        podatak="70 m²") + poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_bazen(L, lang):
    """Bazen. Traka sa naslovom i oznakama je sklonjena na zahtev klijenta, pa
    strana ide na fotografije: recenica pod naslovom, pa slike.

    Fotografisana su oba kadra istog ugla, siroki i uspravni, oba iz aparata i
    ostra na 3024 px. Treci ugao bazena postoji kao slot pool-cascade, sa
    kaskadom i lezaljkama, ali je kadar iz TV priloga: mekci je i nosi
    nereseno pitanje prava, pa se ne prikazuje. Vidi PREDAJA.md."""
    P = L["bazen"]
    sirok = "(min-width:900px) 46vw, 100vw"

    return zaglavlje_strane(L, lang, "bazen", P) + traka(
        '<div class="otkrij">%s</div>' % (
            slika("pool-hero",
                  {"sr": "Bazen u dvorištu, sa postavljenim stolovima uz ivicu",
                   "en": "The pool in the courtyard, tables laid along its edge",
                   "de": "Der Pool im Hof, mit gedeckten Tischen am Rand"}[lang],
                  sizes="100vw", ratio="16 / 9")),
        podatak={"sr": "SLANA VODA", "en": "SALT WATER", "de": "SALZWASSER"}[lang]) + traka(
        '<div class="par">'
        '<div class="otkrij">%s</div>'
        '<div class="otkrij">%s</div></div>' % (
            slika("pool-tall",
                  {"sr": "Bazen i kuće u dvorištu, pred veče",
                   "en": "The pool and the houses in the courtyard, towards evening",
                   "de": "Der Pool und die Häuser im Hof, gegen Abend"}[lang],
                  sizes=sirok, ratio="4 / 5"),
            slika("celebrations-garden",
                  {"sr": "Sto postavljen u dvorištu, uz bazen",
                   "en": "A table laid in the courtyard beside the pool",
                   "de": "Ein gedeckter Tisch im Hof, neben dem Pool"}[lang],
                  sizes=sirok, ratio="4 / 5")),
        klase="traka--uvucena") +         poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_galerija(L, lang):
    P = L["galerija"]
    slotovi = [
        ("hero-estate", "Svodovi kuće noću"),
        ("estate-dusk", "Kuća u plavom satu"),
        ("celebrations-hero", "Bazen i postavljeni stolovi"),
        ("celebrations-tall", "Stolovi na terasi"),
        ("pool-cascade", "Bazen sa kaskadom"),
        ("celebrations-garden", "Sto u dvorištu"),
        ("interior-hall", "Trpezarija pod ciglenim svodom"),
        ("interior-apartment", "Unutrašnjost apartmana"),
        ("estate-arch-night", "Luk od balona i svetla"),
        ("table-setting", "Postavljen sto"),
        ("cellar-glass", "Čaše"),
        ("celebrations-night", "Dvorište uveče"),
    ]
    def stavka(s, a):
        w = MANIFEST[s]["widths"]
        puna = w[-1]                                   # largest that exists
        mala = min([x for x in w if x >= 1024] or [w[-1]])   # thumbnail source
        return (
            '<a class="okvir otkrij" href="../assets/images/%s-%d.jpg" '
            'data-puna="../assets/images/%s-%d.jpg" data-opis="%s">'
            '<picture><source type="image/webp" srcset="../assets/images/%s-%d.webp">'
            '<img src="../assets/images/%s-%d.jpg" alt="%s" loading="lazy" decoding="async" '
            'width="%d" height="%d" style="width:100%%;height:100%%;object-fit:cover">'
            '</picture></a>'
        ) % (s, puna, s, puna, a, s, mala, s, w[0], a,
             MANIFEST[s]["w"], MANIFEST[s]["h"])

    stavke = "".join(stavka(s, a) for s, a in slotovi)

    return zaglavlje_strane(L, lang, "galerija", P) + traka(
        '<div class="galerija">%s</div>' % stavke) + \
        poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_proslave(L, lang):
    P = L["proslave"]
    # Samo naslov, na zahtev klijenta. Recenica ispod stoji dalje u tekst.py
    # pod proslave.sta, pa se kartica puni tako sto se ovde vrati <p>.
    sta = "".join(
        '<div class="kartica kartica--naslov otkrij"><h3>%s</h3></div>' % a
        for a, _ in P["sta"])
    # Traka "Kako to izgleda u praksi" je sklonjena na zahtev klijenta. Njen
    # tekst stoji dalje u tekst.py pod proslave.kako_h i proslave.kako, pa se
    # vraca tako sto se ovde ponovo sastavi <dl> i doda traka ispod prve.

    return zaglavlje_strane(L, lang, "proslave", P) + traka(
        '<div class="otkrij" style="margin-bottom:var(--sekcija)">%s</div>'
        '<div class="slaganje otkrij" style="max-width:48ch;margin-bottom:var(--s12)">'
        '<h2>%s</h2></div><div class="resetka resetka--kratka">%s</div>'
        '<p class="uvod otkrij" style="max-width:56ch;margin-top:var(--s12)">%s</p>' % (
            slika("celebrations-hero", "Bazen i postavljeni stolovi" if lang == "sr"
                  else "The pool and the laid tables", sizes="100vw", ratio="16 / 9"),
            P["sta_h"], sta, P["dogovor_p"]),
        podatak="50") + poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)
    # Traka "Termin" je sklonjena na zahtev klijenta, a sa njom i fotografija
    # dekoracije uvece. Tekst stoji dalje u tekst.py pod proslave.napomena_h i
    # napomena_p, pa se vraca kao traka ispod prve.


def stranica_trpeza(L, lang):
    P = L["trpeza"]
    jela = "".join(
        '<li><span class="jelo-ime">%s</span><span class="jelo-crta"></span>'
        '<span class="jelo-opis">%s</span></li>' % (a, b) for a, b in P["jela"])

    return zaglavlje_strane(L, lang, "trpeza", P) + traka(
        '<div class="par par--sirok-levo">'
        '<div class="slaganje otkrij"><h2>%s</h2><p>%s</p></div>'
        '<div class="otkrij">%s</div></div>'
        '<div class="otkrij" style="margin-top:var(--sekcija);max-width:74ch">'
        '<ul class="jelovnik">%s</ul>'
        '<p class="meta" style="margin-top:var(--s6)">%s</p></div>' % (
            P["kuhinja_h"], P["kuhinja_p"],
            slika("table-setting-tall", "Postavljen sto" if lang == "sr" else "A table laid for guests",
                  sizes="(min-width:900px) 42vw, 100vw", ratio="4 / 5"),
            jela, P["jela_napomena"]),
        podatak="4.7") + traka(
        '<div class="par par--tekst-desno">'
        '<div class="otkrij">%s</div>'
        '<div class="slaganje otkrij"><h2>%s</h2><p>%s</p>'
        '<h3 style="margin-top:var(--s8)">%s</h3><p>%s</p></div></div>' % (
            slika("cellar-glass", "Čaše" if lang == "sr" else "Glassware",
                  sizes="(min-width:900px) 46vw, 100vw", ratio="4 / 5"),
            P["podrum_h"], P["podrum_p"], P["radno_h"], P["radno_p"]),
        klase="traka--uvucena") + poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_fruska(L, lang):
    P = L["fruska"]
    mesta = "".join(
        '<div class="kartica otkrij"><h3>%s</h3><p>%s</p></div>' % (a, b) for a, b in P["mesta"])
    put = "".join(
        '<div class="red-osobine"><dt>%s</dt><dd>%s</dd></div>' % (a, b) for a, b in P["put"])

    return zaglavlje_strane(L, lang, "fruska", P) + traka(
        '<div class="slaganje otkrij" style="max-width:48ch;margin-bottom:var(--s12)">'
        '<h2>%s</h2></div><div class="resetka">%s</div>' % (P["mesta_h"], mesta),
        podatak="18") + traka(
        '<div class="par par--sirok-desno">'
        '<div class="otkrij"><h2>%s</h2><dl style="margin-top:var(--s8)">%s</dl>'
        '<p style="margin-top:var(--s8)">%s</p></div>'
        '<div class="otkrij">%s</div></div>' % (
            P["put_h"], put, P["put_p"],
            slika("estate-dusk", "Kuća u sumrak" if lang == "sr" else "The house at dusk",
                  sizes="(min-width:900px) 42vw, 100vw", ratio="4 / 5")),
        klase="traka--uvucena") + poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_kontakt(L, lang):
    P = L["kontakt"]
    F = P["polja"]
    poruke = json.dumps(P["poruke"], ensure_ascii=False).replace('"', "&quot;")

    opcije = "".join("<option>%s</option>" % o for o in F["povod_opcije"])

    def polje(ime, oznak, tip="text", obavezno=True, puno=False, extra=""):
        zvezda = '<span class="obavezno" aria-hidden="true">*</span>' if obavezno else ""
        req = " required" if obavezno else ""
        return ('<div class="polje%s"><label for="%s">%s%s</label>'
                '<input type="%s" id="%s" name="%s"%s%s>'
                '<p class="greska" role="alert"></p></div>') % (
            " polje--puno" if puno else "", ime, oznak, zvezda, tip, ime, ime, req, extra)

    forma = """<form class="obrazac" novalidate data-mail="%s" data-endpoint=""
data-subject="%s" data-poruke="%s">
%s
%s
%s
<div class="polje"><label for="povod">%s</label>
<select id="povod" name="povod">%s</select><p class="greska" role="alert"></p></div>
<div class="polje"><label for="datum">%s</label>
<input type="date" id="datum" name="datum"><p class="greska" role="alert"></p></div>
<div class="polje"><label for="gosti">%s</label>
<input type="number" id="gosti" name="gosti" min="1" max="200" inputmode="numeric">
<p class="greska" role="alert"></p></div>
<div class="polje polje--puno"><label for="poruka">%s<span class="obavezno" aria-hidden="true">*</span></label>
<textarea id="poruka" name="poruka" required placeholder="%s"></textarea>
<p class="greska" role="alert"></p></div>
<div class="polje--puno">
<button class="dugme dugme--glavno" type="submit">%s</button>
</div>
<div class="polje--puno"><div class="status-poruke" role="status" tabindex="-1" hidden></div></div>
</form>""" % (
        MAIL, P["forma_h"], poruke,
        polje("ime", F["ime"], "text", True, False, ' autocomplete="name"'),
        polje("email", F["email"], "email", True, False, ' autocomplete="email"'),
        polje("telefon", F["telefon"], "tel", False, False, ' autocomplete="tel"'),
        F["povod"], opcije, F["datum"], F["gosti"],
        F["poruka"], F["poruka_ph"], F["polja"]["posalji"] if "polja" in F else F["posalji"])

    podaci = """<ul class="kontakt-lista">
<li><span class="kontakt-oznaka">%s</span><span class="kontakt-vrednost">%s</span></li>
<li><span class="kontakt-oznaka">%s</span><a class="kontakt-vrednost" href="tel:%s">%s</a></li>
<li><span class="kontakt-oznaka">%s</span><a class="kontakt-vrednost" href="mailto:%s">%s</a></li>
<li><span class="kontakt-oznaka">%s</span><span class="kontakt-vrednost">%s</span></li>
</ul>
<div class="grupa-dugmadi" style="margin-top:var(--s8)">%s</div>""" % (
        P["adresa_l"], ADRESA, P["telefon_l"], TEL, TEL_PRETTY,
        P["epasta_l"], MAIL, MAIL, P["radno_l"], P["radno_v"],
        dugme(MAPS, P["mapa_l"], "tiho"))

    return zaglavlje_strane(L, lang, "kontakt", P) + traka(
        '<div class="par par--sirok-levo">'
        '<div class="otkrij"><h2>%s</h2><p class="uvod" style="margin:var(--s5) 0 var(--s10)">%s</p>%s</div>'
        '<div class="otkrij"><h2>%s</h2><div style="margin-top:var(--s8)">%s</div></div>'
        '</div>' % (P["forma_h"], P["forma_p"], forma, P["podaci_h"], podaci))


def stranica_kuca2(L, lang):
    """Dvosobna kuca. Tekst je privremen, slike su konacne."""
    P = L["kuca2"]
    oz = '<ul class="oznake">%s</ul>' % "".join("<li>%s</li>" % x for x in P["oznake"])

    return zaglavlje_strane(L, lang, "kuca2", P) + traka(
        '<div class="par par--sirok-levo">'
        '<div class="slaganje otkrij"><h2>%s</h2><p>%s</p><p>%s</p>%s</div>'
        '<div class="otkrij">%s</div></div>' % (
            P["a_h"], P["a_p1"], P["a_p2"], oz,
            slika("interior-apartment",
                  "Unutrašnjost kuće sa gredama i zelenim prozorima" if lang == "sr"
                  else "Inside the house, beams overhead and green window frames",
                  sizes="(min-width:900px) 42vw, 100vw", ratio="3 / 2")),
        podatak={"sr": "2 SOBE", "en": "2 ROOMS", "de": "2 ZIMMER"}[lang]) + poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)
    # Traka "Za vece grupe" je sklonjena na zahtev klijenta. Tekst stoji dalje
    # u tekst.py pod napomena_h i napomena_p, pa se vraca tako sto se ovde
    # ponovo doda traka koja ih ispisuje.


def stranica_kuce(L, lang):
    """Pregled obe kuce. Roditelj padajuceg menija, pa mora da stoji sam za
    sebe: ko dodje ovde bira izmedju dve kuce, ne cita o jednoj."""
    P = L["kuce"]
    kartice = "".join(
        '<div class="kartica otkrij"><h3>%s</h3><p>%s</p>'
        '<div class="grupa-dugmadi" style="margin-top:var(--s6)">%s</div></div>' % (
            P[h], P[t], dugme(SLUG[k][lang], L["nav"][k], "tiho"))
        for h, t, k in (("k2_h", "k2_p", "kuca2"), ("k1_h", "k1_p", "kuca1")))

    return zaglavlje_strane(L, lang, "kuce", P) + traka(
        '<div class="otkrij" style="margin-bottom:var(--sekcija)">%s</div>'
        '<div class="slaganje otkrij" style="max-width:48ch;margin-bottom:var(--s12)">'
        '<h2>%s</h2></div><div class="resetka">%s</div>' % (
            slika("estate-dusk-wide",
                  "Ku\u0107a u sumrak" if lang == "sr"
                  else ("Das Haus in der D\u00e4mmerung" if lang == "de" else "The house at dusk"),
                  sizes="100vw", ratio="16 / 9"),
            P["izbor_h"], kartice),
        podatak={"sr": "2 KUĆE", "en": "2 HOUSES", "de": "2 HÄUSER"}[lang]) + traka(
        '<div class="stub otkrij"><h2>%s</h2>'
        '<p class="uvod" style="margin-top:var(--s5)">%s</p>'
        '<div class="grupa-dugmadi" style="margin-top:var(--s8)">%s</div></div>' % (
            P["napomena_h"], P["napomena_p"],
            dugme(SLUG["kontakt"][lang], L["c"]["upit"])),
        klase="traka--uvucena traka--tesna") + \
        poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_kuca1(L, lang):
    """Jednosobna kuca, po klijentovom tekstu. Fotografije te jedinice jos
    nema, pa traka stoji na tekstu i oznakama."""
    P = L["kuca1"]
    oz = '<ul class="oznake">%s</ul>' % "".join("<li>%s</li>" % x for x in P["oznake"])

    return zaglavlje_strane(L, lang, "kuca1", P) + traka(
        '<div class="stub slaganje otkrij"><h2>%s</h2><p>%s</p>%s</div>' % (
            P["a_h"], P["a_p1"], oz),
        podatak={"sr": "2 KREVETA", "en": "2 BEDS", "de": "2 BETTEN"}[lang]) + \
        poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


def stranica_restoran(L, lang):
    """Restoran i podrum. Tekst je privremen, slike su konacne."""
    P = L["restoran"]

    return zaglavlje_strane(L, lang, "restoran", P) + traka(
        '<div class="otkrij" style="margin-bottom:var(--sekcija)">%s</div>'
        '<div class="par par--sirok-levo">'
        '<div class="slaganje otkrij"><h2>%s</h2><p>%s</p><p>%s</p></div>'
        '<div class="otkrij">%s</div></div>' % (
            slika("interior-hall",
                  "Trpezarija pod ciglenim svodom" if lang == "sr"
                  else "The dining room under its brick vault",
                  sizes="100vw", ratio="16 / 9"),
            P["sala_h"], P["sala_p1"], P["sala_p2"],
            slika("table-setting-tall",
                  "Postavljen sto" if lang == "sr" else "A table laid for guests",
                  sizes="(min-width:900px) 42vw, 100vw", ratio="4 / 5")),
        podatak="50") + traka(
        '<div class="par par--tekst-desno">'
        '<div class="otkrij">%s</div>'
        '<div class="slaganje otkrij"><h2>%s</h2><p>%s</p>'
        '<h3 style="margin-top:var(--s8)">%s</h3><p>%s</p>%s</div></div>' % (
            slika("cellar-glass",
                  "Čaše u podrumu" if lang == "sr" else "Glassware in the cellar",
                  sizes="(min-width:900px) 46vw, 100vw", ratio="4 / 5"),
            P["podrum_h"], P["podrum_p"], P["radno_h"], P["radno_p"],
            dugme(SLUG["kontakt"][lang], L["c"]["upit"], "tiho")),
        klase="traka--uvucena") + poziv(L, L["c"]["poziv_h"], L["c"]["poziv_p"], lang)


BUILDERS = {
    "pocetna": stranica_pocetna,
    "kuce": stranica_kuce,
    "kuca2": stranica_kuca2,
    "kuca1": stranica_kuca1,
    "proslave": stranica_proslave,
    "bazen": stranica_bazen,
    "kontakt": stranica_kontakt,
}


# ==================================================================== 5. EMIT

GRB = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" fill="none">
<rect width="40" height="40" rx="8" fill="#0E1512"/>
<path d="M8 20.5L20 10l12 10.5" stroke="#C8A15A" stroke-width="1.6"
stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11 19.5V30h18V19.5" stroke="#C8A15A" stroke-width="1.6"
stroke-linecap="round" stroke-linejoin="round"/>
<path d="M17 30v-6.5h6V30" stroke="#7FB8A8" stroke-width="1.6"
stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

KOREN = """<!doctype html>
<html lang="sr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ilkićev kućerak u Sremu · Vrdnik, Fruška gora</title>
<meta name="description" content="Imanje u Vrdniku na Fruškoj gori: apartmani, privatni grejani bazen, podrum i pedeset mesta za stolom.">
<link rel="icon" href="assets/grb.svg" type="image/svg+xml">
<link rel="alternate" hreflang="sr-Latn-RS" href="sr/index.html">
<link rel="alternate" hreflang="en" href="en/index.html">
<link rel="alternate" hreflang="de" href="de/index.html">
<link rel="alternate" hreflang="x-default" href="sr/index.html">
<style>
html{background:#0E1512;color:#A3B3A8;font-family:system-ui,sans-serif}
body{margin:0;min-height:100dvh;display:grid;place-items:center;padding:24px;text-align:center}
a{color:#C8A15A;font-size:18px;text-decoration:none;padding:14px 22px;border:1px solid #26362F;border-radius:6px;display:inline-block;margin:6px}
a:hover{border-color:#C8A15A}
h1{font-weight:400;letter-spacing:-.02em;color:#F2EFE6}
</style>
<script>
(function(){
  var m={sr:'sr',en:'en',de:'de'};
  var s=null;
  try{s=localStorage.getItem('kucerak:jezik');}catch(e){}
  if(!s){
    var n=(navigator.languages||[navigator.language||'sr']).join(',').toLowerCase();
    s = /\\bde/.test(n)?'de' : (/\\b(sr|hr|bs|me)/.test(n)?'sr' : (/\\ben/.test(n)?'en':'sr'));
  }
  // Over http(s) send people to the directory so the address stays clean;
  // over file:// the filename is required for the page to open at all.
  var web = location.protocol.indexOf('http') === 0;
  if(s && m[s.slice(0,2)]) location.replace(m[s.slice(0,2)] + (web ? '/' : '/index.html'));
})();
</script>
</head>
<body>
<div>
<h1>Ilkićev kućerak u Sremu</h1>
<p>Vrdnik · Fruška gora</p>
<p><a href="sr/index.html">Srpski</a><a href="en/index.html">English</a><a href="de/index.html">Deutsch</a></p>
</div>
</body>
</html>"""


def main():
    n = 0
    for lang in LANGS:
        d = os.path.join(ROOT, lang)
        os.makedirs(d, exist_ok=True)
        L = JEZICI[lang]
        for kljuc, build in BUILDERS.items():
            html = glava(L, kljuc, lang) + build(L, lang) + podnozje(L, lang)
            with open(os.path.join(d, SLUG[kljuc][lang]), "w", encoding="utf-8") as fh:
                fh.write(html)
            n += 1
        print("  %s/  %d pages" % (lang, len(BUILDERS)))

    with open(os.path.join(ROOT, "assets", "grb.svg"), "w", encoding="utf-8") as fh:
        fh.write(GRB)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(KOREN)

    # sitemap
    urls = "".join(
        "<url><loc>%s/%s/%s</loc>%s</url>" % (
            SITE, lang, SLUG[k][lang],
            "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s/%s/%s"/>' % (
                JEZICI[j]["htmllang"], SITE, j, SLUG[k][j]) for j in LANGS))
        for lang in LANGS for k in SLUG)
    sm = ('<?xml version="1.0" encoding="UTF-8"?>'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:xhtml="http://www.w3.org/1999/xhtml">%s</urlset>') % urls
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sm)
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE)

    print("\n%d pages + root redirect + sitemap" % n)


if __name__ == "__main__":
    main()
