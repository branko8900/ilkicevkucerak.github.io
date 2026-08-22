# kucerak

Trilingual marketing site for **Ilkićev kućerak** — a private estate in Vrdnik, on the southern
slope of Fruška gora, Serbia. Two apartments, a heated saltwater pool, a wine cellar, and a hall
seating fifty, hired by one company at a time.

Static site. No framework, no build step at serve time, no runtime dependencies. 21 real pages
across Serbian, English and German.

> **Status: demo.** Domain, e‑mail and some media are unconfirmed — see [Before this goes
> public](#before-this-goes-public).

> **Note on visibility.** GitHub Pages serves a site publicly *even from a private repository*,
> and on the Free plan a private repository does not publish at all. Making the repository
> private therefore neither protects the media nor allows hosting — the media questions below
> have to be settled on their own terms.

---

## Run it

Any static server. From the repository root:

```bash
python -m http.server 4350
```

Then open <http://localhost:4350/> — the root page forwards to the visitor's language and
remembers the choice. Direct entry points:

| Language | Path |
|---|---|
| Srpski | `/sr/index.html` |
| English | `/en/index.html` |
| Deutsch | `/de/index.html` |

Opening `index.html` straight off disk mostly works, but the language gate and `fetch` are
restricted on `file://`, so use the server for an accurate preview.

---

## Layout

```
index.html          language gate -> /sr, /en, /de
sr/ en/ de/         7 pages each, localised filenames
assets/css/         the whole design system, one file
assets/js/          behaviour, vanilla, ~16 KB unminified
assets/images/      7 slots x up to 4 widths x WebP + JPEG
assets/video/       two home page clips (mp4 + poster)
sitemap.xml
robots.txt
_build/             generators — not served, not part of the site
```

Pages by key:

| key | Serbian | English | German |
|---|---|---|---|
| pocetna | `index.html` | `index.html` | `index.html` |
| kuce | `kuce.html` | `houses.html` | `haeuser.html` |
| kuca2 | `dvosobna-kuca.html` | `two-bedroom-house.html` | `zweizimmerhaus.html` |
| kuca1 | `jednosobna-kuca.html` | `one-bedroom-house.html` | `einzimmerhaus.html` |
| proslave | `proslave.html` | `celebrations.html` | `feiern.html` |
| bazen | `bazen.html` | `pool.html` | `pool.html` |
| kontakt | `kontakt.html` | `contact.html` | `kontakt.html` |

Every nav item is a real file with a real URL. Nothing is a hidden section toggled by JavaScript.
`kuce` is the dropdown parent, set by `RODITELJ`; `DROPDOWN` lists its children. The parent is a
page in its own right, so the menu opens on hover and the label still leads somewhere on click.

Apartments, Gallery, The table, Fruška gora, The estate and Restaurant were
removed at the client's request. Their copy is still in `_build/tekst.py`, so restoring any of them means putting
the key back into `SLUG`, `TOP` and `BUILDERS` and re-running the generator.

**All page copy now comes from the client** and replaced the earlier text written from
third-party sources. Four places carry text without a photograph yet: the Restaurant band on the
home page, the one-bedroom house, the pool and the kitchen. Each builder marks where the picture
goes. The square metres, fireplace, terrace and air conditioning left the site with that rewrite,
since the client's copy does not mention them; they remain in `tekst.py` under
`apartmani.a1_oznake`.

---

## Do not hand-edit the HTML

Plain HTML has no include mechanism, so the header appears in all 27 files. It is emitted from a
single template in `_build/generate.py`, which is why it cannot drift. Editing a generated file
directly works until the next run silently overwrites it.

```bash
python _build/generate.py     # copy, markup, nav, hreflang, sitemap
python _build/assets.py       # crops, responsive images, video transcode
```

All page copy lives in three dictionaries (`SR`, `EN`, `DE`) near the top of `generate.py`.

`assets.py` reads the original camera drop — HEIC, oversized JPEG, 4K HEVC — and writes
art-directed crops at 640/1024/1600/2200 px in WebP and JPEG, plus `manifest.json`, which carries
each image's intrinsic size and average colour. `SRC` at the top of that file still points at the
folder the originals were delivered in; move them somewhere permanent and update the path.

**Scale note.** At 27 pages this generator pattern is at the edge of what it should carry. Past
roughly 12 pages per language, or the moment the client wants to edit copy themselves, move to a
static site generator (11ty, Astro, Hugo) or a headless CMS. The content dictionaries are already
shaped to port over as data files.

---

## Design

Structural DNA is adapted from the Auros system: rationed colour, no drop shadows anywhere (depth
comes from the surface stack plus hairline borders), two radii only (16 px surfaces, 6 px
controls), display type at medium weight with heavy negative tracking, uppercase tracked eyebrows,
and generous section rhythm.

The palette is sampled from a photograph of the cabins at Vrdnik rather than chosen: stone path
`#e6dcc4`, sunlit grass `#c5bf74`, forest `#72753e`, shingle `#675754`, cabin wood `#493f3f`. The
canvas is the stone path, lifted enough for long reading. Nothing on the page is white — an
earlier near-white scheme glared. The hero keeps its photograph and therefore its own light ink, so page ink and hero ink are
separate token sets.

Every value is a custom property at the top of `assets/css/style.css`:

| token | value | role |
|---|---|---|
| `--podrum` | `#EAE3D1` | canvas — the stone path, lifted |
| `--hlad` | `#E0D8C2` | recessed bands, footer — the path itself |
| `--mahovina` | `#F3EFE3` | raised cards — warm paper |
| `--krec` | `#26251C` | bark, headings |
| `--magla` | `#4A4636` | body copy |
| `--tiho` | `#5C5947` | captions, meta |
| `--mesing` | `#7A4E18` | cabin wood, the single accent |
| `--mineral` | `#4A5B2A` | forest, second accent |
| `--junak-*` | light set | hero ink, which sits on a photograph |

Token names are inherited from the first, darker scheme; only the values moved.

Type is **Newsreader** (display) and **Archivo** (body/UI), both variable, both with full
Latin-Extended — which is why č ć š ž đ and ä ö ü ß all render correctly.

The home page opens with a row of five line marks under the hero: pet friendly, privacy, the
drive from Novi Sad, the garden, the parking. They are hand-written `svg` in `IKONE` in
`generate.py` on one grammar (24x24, no fill, 1.4 stroke, round joins) and sit in hairline rings
rather than filled chips, so the row reads as engraving and keeps the no-shadow rule. Each mark
is `aria-hidden` and carries its consequence in text underneath. Pet friendly, the 900 m² garden
and the forty-minute drive come from the client and are not independently verified.

**The signature** is the steam spine: the fixed rail down the left edge. Each tick carries a real
figure about the estate (PRIVATNO, 50 seats, 32 °C, 4.7, 18 monasteries) and lights as its section
reaches mid-viewport, while the rail fills with scroll progress. Below 1240 px it collapses to a
2 px bar under the header; between 1240 and 1600 px the rail runs but labels stay hidden, because
the centred container does not leave room to print them without overlapping the copy.

Motion is limited to four orchestrated moments — hero arrival, ambient steam, scroll reveals,
the spine — plus counters on the stat band. Transform and opacity only.
`prefers-reduced-motion` is honoured throughout: steam is removed, reveals resolve instantly, and
the spine keeps reporting position but stops easing.

---

## Verified

- 21/21 pages return 200; 1022 local references resolve, every `srcset` entry included, no 404s
- No horizontal overflow at 360, 375, 390, 768, 1280, 1440 or 1700 px
- Hero type over the photograph, measured by compositing the image and both scrim gradients and
  sampling the real glyph boxes: headline 8.9:1, lead 9.2:1, eyebrow 9.0:1
- Every flat surface measured against the background actually painted behind it: headings 12.0:1,
  body 7.4:1, muted 5.0:1 on the sand band, primary button 5.6:1 — all above WCAG AA
- Heading levels run with no skipped levels; one `h1` per page
- Every image has an `alt`; decorative marks carry `alt=""`
- Every form field has a real `<label for>`; inputs are 16 px so iOS does not zoom on focus
- Validation fires on blur, not on keystroke; first invalid field takes focus on submit
- Touch targets ≥ 44 px; language chips widen on coarse pointers and move into the drawer on phones
- The two home page clips carry `preload="none"`, so nothing of their 8.5 MB is fetched until
  the visitor presses play; the poster frames are 115 and 106 KB. VP9 was dropped for them
  because it encoded larger than H.264 on this footage
- Reveals carry a 2.5 s failsafe: if the observer never fires, everything is shown anyway

---

## Before this goes public

1. **The video is broadcast footage.** Both source clips carry burned-in station graphics
   (`ФРУШКОГОРСКО ЛЕТО`, `СРЦЕМ КРОЗ СРБИЈУ`) from a Serbian television feature. The graphics are
   cropped out in `assets/video/` and in four interior stills (`interior-apartment`,
   `interior-hall`, `pool-cascade`, `gate-garden`), but cropping a broadcaster's mark does not
   transfer rights. Confirm commercial use or obtain a clean master. Repository visibility does
   not help here — publishing the site publishes the footage. If the rights are not settled,
   remove `assets/video/` and those four slots before deploying.
2. **One photograph is deliberately withheld.** `IMG_8384` shows clearly identifiable guests at a
   private event and is not published anywhere on the site. The near-identical `IMG_8383` is used
   instead, at an exposure where no face is legible.
3. **There is no real menu.** Nothing resembling a published menu exists on the client's Facebook
   or Instagram. The Trpeza / Table / Tafel page is written around what is verifiable — a
   *fruškogorski fruštuk*, soup, grill, cake, menu agreed in advance by group size — with no
   invented dishes and no invented prices.
4. **No prices anywhere.** Third-party listings suggest a range, but it is unconfirmed.
5. **Domain and e-mail are unconfirmed.** `kucerak-u-sremu.rs` and `ilkic@kucerak-u-sremu.rs` come
   from a tourism-board listing. `SITE` at the top of `_build/generate.py` feeds every canonical
   URL, hreflang alternate and the sitemap — set it to the real domain and re-run before launch.
6. **The contact form has no backend.** `data-endpoint` is empty, so the form composes a
   pre-filled e-mail in the visitor's client. Point it at a Formspree/Basin/Netlify Forms URL in
   `stranica_kontakt()` to take submissions properly.
7. **Confirm the exclusivity claim.** The copy states the estate is private to one company at a
   time, following the Instagram bio (*privatan prostor za proslave i odmor · privatni bazen*).

---

## Deploying

Static folder — Netlify, Cloudflare Pages, Vercel, GitHub Pages or plain nginx.

For **GitHub Pages**: Settings → Pages → deploy from branch `main`, folder `/ (root)`.
The repository must be **public** on the Free plan, and `.nojekyll` must be present or Jekyll
drops `_build/` and renders `README.md` as the home page instead of `index.html`.

Upload with `git push`, not the browser. The web uploader caps at 100 files per batch, skips
dotfiles such as `.nojekyll`, and drops files silently on batches this size.

Serve `/assets/` with long cache lifetimes; every image filename contains its width, so the files
are safe to cache immutably.
