# Ilkićev kućerak, predaja projekta

Sve što treba preneti u novi chat. Zalepi ovaj fajl kao prvu poruku, ili ga samo priloži.

---

## 1. Šta je projekat

Trojezični statični sajt (srpski, engleski, nemački) za **Ilkićev kućerak**, imanje u Vrdniku
na Fruškoj gori koje se izdaje jednom društvu u isto vreme.

Nema frameworka, nema build koraka pri serviranju, nema zavisnosti u pregledaču. Čist HTML,
jedan CSS fajl, jedan JS fajl, sve generisano Python skriptom.

**Mapa projekta:** `C:\Users\Branko\Desktop\Claude Code\kucerak`

---

## 2. Kako se pokreće i gleda

Server se **sam diže pri paljenju računara**, nevidljivo:

- prečica `Kucerak server.lnk` u Startup folderu pokreće `pythonw.exe _build\serve.pyw 4360`
- na Desktopu je `Kucerak sajt.lnk`, dvoklik otvara sajt

Desktop prečica **ne vodi pravo na adresu**, nego pokreće `_build\otvori.pyw`. Ta skripta prvo
proveri da li neko sluša na portu, pa ako ne sluša, digne server, sačeka da se javi i tek onda
otvori pregledač. Ranije je na Desktopu stajao običan `.url`, pa je klik posle pada servera
završavao na poruci da se stranica ne može otvoriti. Drugi klik ne pravi drugi server, samo
otvori još jedan tab.

Adrese: `http://localhost:4360/sr/index.html`, `/en/`, `/de/`

Ako server ne radi, pokrenuti ručno:

```
"C:\Users\Branko\AppData\Local\Programs\Python\Python312\pythonw.exe" "C:\Users\Branko\Desktop\Claude Code\kucerak\_build\serve.pyw" 4360
```

**Zašto ne običan `python -m http.server`:** pod `pythonw` (bez konzole) standardni modul puca,
jer za svaki zahtev piše red u stderr koji ne postoji, pa se veza prekida. `serve.pyw` ne loguje
i šalje `Cache-Control: no-store` da pregled uvek pokaže poslednju verziju.

**Ako server ipak padne**, upisuje razlog u `_build\serve-greska.log`. Pod `pythonw` nema ni
konzole ni stderr, pa bi bez toga pad prošao nemo, što se već jednom desilo. Ako je port zauzet,
druga instanca tiho izadje umesto da pukne.

---

## 3. Struktura

```
index.html            jezička kapija, preusmerava na /sr, /en ili /de
sr/ en/ de/           po 7 strana
assets/css/style.css  ceo dizajn sistem, jedan fajl
assets/js/script.js   ponašanje, vanilla, bez biblioteka
assets/images/        7 slotova, do 4 širine, WebP + JPEG, 57 fajlova
assets/video/         dva klipa na naslovnoj (`kapija`, `kaskada`) plus stari `estate-loop`
                      koji se nigde ne koristi
_build/               generatori, ne serviraju se
sitemap.xml robots.txt .nojekyll
```

### Strane

| ključ | srpski | engleski | nemački |
|---|---|---|---|
| pocetna | `index.html` | `index.html` | `index.html` |
| kuce | `kuce.html` | `houses.html` | `haeuser.html` |
| kuca2 | `dvosobna-kuca.html` | `two-bedroom-house.html` | `zweizimmerhaus.html` |
| kuca1 | `jednosobna-kuca.html` | `one-bedroom-house.html` | `einzimmerhaus.html` |
| proslave | `proslave.html` | `celebrations.html` | `feiern.html` |
| bazen | `bazen.html` | `pool.html` | `pool.html` |
| kontakt | `kontakt.html` | `contact.html` | `kontakt.html` |

Navigacija: Početna, Kuće, Proslave, Bazen, Kontakt.

**Kuće nose padajući meni.** Na prelazak mišem otvara se Dvosobna kuća i Jednosobna kuća,
na dodir se otvara klikom, a sama stavka je prava strana sa pregledom obe kuće. Roditelj se
zadaje sa `RODITELJ` u `generate.py`, deca sa `DROPDOWN`. Podstrane nose mrvice nazad na Kuće.

Naslovna ide: hero, red ikonica, Ukratko, Jedini gosti tog dana ste vi, utisak gosta,
poziv na rezervaciju.

**Red ikonica** pod herojem nosi pet stvari koje posetilac proverava pre nego što počne da
čita: pet friendly, privatnost, 40 minuta od Novog Sada, vrt od 900 m², besplatan parking.
Crteži su ručno pisani `svg` u `IKONE` u `generate.py`, 24x24, bez popune, debljina linije
1.4. Boju daje prsten, pa svaki znak nasleđuje `currentColor`. Sam znak je `aria-hidden`,
jer ispod njega stoji tekst. Tekst je u `home.odlike` u `tekst.py`, kao lista trojki
`(ključ ikonice, ime, posledica)`.

---

## 4. Kako se menja

**Nikada ne dirati generisane `.html` fajlove.** Sledeće pokretanje generatora ih prepiše.

```
cd "C:\Users\Branko\Desktop\Claude Code\kucerak"
python _build\generate.py      # tekst, markup, navigacija, hreflang, sitemap
python _build\assets.py        # isecanje slika, sve širine, prekodiranje videa
python _build\shot_mobile.py 375 812   # snimci na pravoj mobilnoj širini
```

| fajl | šta radi |
|---|---|
| `_build/tekst.py` | **sav tekst sajta, sva tri jezika.** Ovde se menja copy |
| `_build/generate.py` | šabloni, navigacija, raspored sekcija, `SLUG`, `TOP`, `BUILDERS` |
| `_build/assets.py` | obrada fotografija iz originala, `SLOTS` definiše isecanja |
| `_build/serve.pyw` | tihi lokalni server |
| `_build/otvori.pyw` | pokreće server ako ne radi, pa otvori sajt. Na njega gleda Desktop prečica |
| `_build/shot_mobile.py` | snimci preko DevTools protokola |

### Dodavanje ili vraćanje strane

Tekst uklonjenih strana **nije obrisan** iz `tekst.py`. Vraćanje bilo koje od njih znači vratiti
njen ključ u `SLUG`, `TOP` i `BUILDERS` u `generate.py` i pokrenuti generator.

Uklonjeno na zahtev klijenta: `apartmani`, `galerija`, `trpeza`, `fruska`, `imanje`, `restoran`.

**Slike uklonjenih strana su obrisane sa diska.** Posle svih rezova sajt poziva samo 7 slotova, a
12 ih je ostalo bez ijedne reference: `celebrations-night`, `celebrations-square`,
`celebrations-tall`, `cellar-glass`, `cellar-glass-square`, `estate-arch-night`, `estate-dusk`,
`gate-garden`, `interior-hall`, `pool-cascade`, `table-setting`, `table-setting-tall`. Njihovih
70 fajlova i 12 MB je obrisano, kao i stari `estate-loop` koji se nigde nije prikazivao. Razlog:
GitHub-ov veb otpremanje uzima najviše 100 fajlova po turi, a projekat je bio na 166.

Vraćaju se u dva koraka, isecanja su i dalje opisana u `SLOTS` u `assets.py`:

```
python _build/assets.py          # ponovo iseca iz originala u Downloads
```

ili `git checkout <commit> -- assets/images` iz istorije. Isti slotovi su izbačeni i iz
`manifest.json`, pa ako neko vrati staru stranu a ne pokrene `assets.py`, generator pukne sa
`KeyError` umesto da ispiše putanju do fajla kog nema.

Sa Dvosobne kuće je sklonjena traka **Za veće grupe**, a sa Jednosobne **obe** trake. Nijedan
tekst nije obrisan, sve stoji dalje u `tekst.py` pod `kuca2.napomena_*` odnosno pod celim
ključem `kuca1`, a u oba graditelja je ostavljen komentar gde se vraća.

Sa Proslava su sklonjene rečenice ispod naslova u karticama i dve trake, **Kako to izgleda u
praksi** i **Termin**, a sa Terminom i fotografija dekoracije uveče. Tekst stoji dalje pod
`proslave.sta`, `kako_h`, `kako`, `napomena_h` i `napomena_p`. Pet kartica koje su ostale nose
samo naslov, pa idu kroz `.resetka--kratka` da svih pet stane u jedan red. Strana sada ima jednu
traku i poziv.

Sa Bazena su sklonjene obe trake, **Zbog vode se u Vrdnik dolazi i zimi** i **Veče ne mora da
se prekida**, a sa njima i fotografije `pool-tall` i `celebrations-night`. Tekst stoji dalje pod
ključem `bazen`.

> **Jednosobna kuća i Bazen su trenutno prazne strane.** Obe nose samo naslov, uvodnu rečenicu
> i poziv na rezervaciju. Obe stoje u meniju i u podnožju, pa ih vredi ili popuniti, ili
> privremeno izbaciti iz `SLUG`, `TOP` odnosno `DROPDOWN`, i `BUILDERS` dok ne budu imale
> sadržaj. Ako izadje i Bazen, u meniju ostaju Početna, Kuće, Proslave i Kontakt.

---

## 5. Dizajn

Struktura je preuzeta iz Auros sistema: štedljiva upotreba boje, nigde senki (dubina se pravi
slojevima površina i tankim linijama), samo dva radijusa (16px površine, 6px kontrole), veliki
naslovi srednje debljine sa jakim negativnim razmakom, verzalni natpisi iznad naslova.

**Paleta je uzorkovana iz fotografije brvnara u Vrdniku, nije birana odoka:**
staza `#e6dcc4`, osunčana trava `#c5bf74`, šuma `#72753e`, šindra `#675754`, drvo `#493f3f`.

Podloga je kamena staza, podignuta da izdrži duže čitanje. **Nigde nema bele** jer je ranija
verzija bila skoro bela i blještala je.

| token | vrednost | uloga |
|---|---|---|
| `--podrum` | `#EAE3D1` | podloga |
| `--hlad` | `#E0D8C2` | uvučene trake, podnožje |
| `--mahovina` | `#F3EFE3` | izdignute kartice |
| `--krec` | `#26251C` | naslovi |
| `--magla` | `#4A4636` | telo teksta |
| `--tiho` | `#5C5947` | prigušeni tekst |
| `--mesing` | `#7A4E18` | jedini akcenat |
| `--mineral` | `#4A5B2A` | drugi akcenat |
| `--junak-*` | svetli set | tekst u heroju, jer stoji na fotografiji |

Imena tokena su nasleđena iz prve, tamne verzije. Samo su vrednosti promenjene.

**Pisma:** Newsreader (naslovi) i Archivo (telo), oba varijabilna, oba sa punim Latin-Extended,
zbog č ć š ž đ i ä ö ü ß.

**Potpis dizajna** je leva vertikalna traka koja prati skrol. Svaka tačka nosi stvarni podatak
(`VRDNIK`, `PRIVATNO`, `4.7`). Ispod 1240px se pretvara u traku od 2px ispod zaglavlja, između
1240 i 1600px traka radi ali su natpisi sakriveni jer nema mesta da se ispišu bez preklapanja.

**Pokret** je ograničen na ulazak heroja, ambijentalne mrlje, otkrivanje pri skrolu i traku.
Samo `transform` i `opacity`. `prefers-reduced-motion` se poštuje u potpunosti.

---

## 6. Pravila za pisanje teksta

Zapisana su i na vrhu `tekst.py`:

1. Naslov prodaje razlog dolaska, ne opisuje prostor. Ne „trpezarija za pedeset" nego šta gost
   time dobija.
2. Uz svaki podatak ide i zašto je gostu bitan. Broj bez posledice je prazan.
3. **Bez dugih crta.** Rečenica se prelama tačkom ili zarezom. Provereno, trenutno ih ima nula.
4. Bez praznih fraza: dobrodošli, oaza, savršeno mesto, nezaboravno.

---

## 7. Provereno stanje

- 21/21 strana vraća 200, 1022 lokalne reference se razrešavaju, uključujući svaki `srcset` unos,
  postere i snimke. Nijedan 404
- Bez horizontalnog skrola na 360, 375, 390, 768, 1280, 1440 i 1700px
- Tekst u heroju preko fotografije, mereno kompozitom slike i oba gradijenta: naslov 8.9:1,
  uvod 9.2:1, natpis 9.0:1
- Ravne površine, mereno prema podlozi koja je zaista iscrtana ispod: naslovi 12.0:1,
  telo 7.4:1, prigušeno 5.0:1 na peščanoj traci, glavno dugme 5.6:1. Sve iznad WCAG AA
- Nivoi naslova bez preskakanja, jedan `h1` po strani
- Svaka slika ima `alt`
- Svako polje obrasca ima pravi `<label for>`, unos je 16px da iOS ne zumira
- Dodirna polja ≥ 44px
- Nula dugih crta

---

## 8. Šta čeka, po prioritetu

### Odmah

1. **Fotografije za nove sekcije.** Tekst je stigao od klijenta i ceo je ugrađen, ali četiri
   mesta stoje bez slike: Restoran na naslovnoj, Jednosobna kuća, Bazen i kuhinja. Kada slike
   stignu, obraditi ih kroz `assets.py` (dodati slot u `SLOTS`) pa ih ubaciti u odgovarajuće
   graditelje. U svakom od njih stoji komentar gde slika ide.
3. **Objaviti izmene.** Remote je podešen, čeka 16 commita i sve izmene iz ove sesije:
   ```
   cd "C:\Users\Branko\Desktop\Claude Code\kucerak"
   git push -u origin main --force
   ```
   Online je i dalje **stara, tamna verzija** sa starim tekstom.
   `--force` je potreban jer je ono gore stiglo preko web uploadera i nema zajedničku istoriju.

### Pre nego što sajt ode na pravi domen

4. **`SITE` u `generate.py`** stoji na `https://kucerak-u-sremu.rs`. Hrani sve `canonical`,
   `hreflang` i `sitemap.xml`. Postaviti pravi domen i pokrenuti generator.
5. **Domen i e-pošta nisu potvrđeni.** `kucerak-u-sremu.rs` i `ilkic@kucerak-u-sremu.rs` uzeti
   sa liste Turističke organizacije Vojvodine.
6. **Obrazac nema pozadinu.** `data-endpoint` je prazan, pa se poruka sastavlja u mejl klijentu
   posetioca. Za pravo primanje upita staviti Formspree ili Basin adresu u `stranica_kontakt()`.
7. **Nema cena nigde.** Trećestrani izvori pominju raspon, ali nije potvrđen.

### Otvorena pitanja o materijalu

8. **Video je iz TV priloga, i od 22. avgusta 2026. stoji na naslovnoj.** Oba snimka nose
   ugašenu grafiku stanice, `ФРУШКОГОРСКО ЛЕТО` dole levo i `СРЦЕМ КРОЗ СРБИЈУ` dole
   desno. Klijent je poslao ta ista dva fajla i tražio da idu na sajt, pa sada stoje kao
   `kapija` i `kaskada` u `assets/video/`, u traci ispod reda ikonica. Grafika je odsečena
   istim receptom kao ranije (`BUG_CROP`, donjih 23 %), **ali isecanje ne prenosi prava.** Iz
   istog izvora su i četiri slike enterijera (`interior-apartment`, `interior-hall`,
   `pool-cascade`, `gate-garden`), od kojih se sada koristi samo `interior-apartment`.

   **Rešiti pre nego što sajt ode na pravi domen.** Objaviti sajt znači objaviti i snimak.
   Pitati domaćina da li ima pisanu dozvolu stanice ili čist master bez grafike. Ako nema,
   izbaciti `klipovi` iz `stranica_pocetna()` i obrisati `assets/video/`.
9. **Jedna fotografija je namerno izostavljena.** `IMG_8384` prikazuje prepoznatljive goste na
   zatvorenoj proslavi. Umesto nje se koristi `IMG_8383`, ista scena pri ekspoziciji na kojoj se
   nijedno lice ne razaznaje.
10. ~~**Nema pravog jelovnika.**~~ Rešeno. Klijent je potvrdio da jelovnika **namerno** nema:
   nema ni plana obroka, sve se dogovara sa gostom. To sada stoji kao sekcija Restoran na
   naslovnoj. Nijedno jelo nije izmišljeno ni ranije.

### Pitanja za domaćina koja bi tekst najviše podigla

Ovo su stvari koje niko osim njih ne zna, a upravo one dele živ tekst od pristojnog:

- Ko su domaćini i kako se zovu? U tekstu trenutno nema nijednog imena.
- Otkad je kuća u porodici i šta je bila pre?
- Ko kuva i po čijim receptima?
- Šta gosti najčešće traže, a nemaju? Iskren odgovor diže poverenje više od pohvale.
- Koje je doba godine najlepše, a koje najgore?
- Jedna stvar u dvorištu koja ima priču.

---

## 9. Provereni podaci o objektu

Sve što je na sajtu, sa izvorom:

| podatak | vrednost | izvor |
|---|---|---|
| Adresa | Mirka Laćarca 9, 22408 Vrdnik | Google, Facebook |
| Telefon | +381 65 288 0781 | klijent, 22. avgusta 2026. Raniji broj sa Facebooka, +381 63 76 89 070, vise se ne koristi |
| Ocena | 4,7 od 5, 303 utiska | Google |
| Preporuka | 98%, 55 recenzija | Facebook |
| Veći smeštaj | 70 m², 2 spavaće sobe | trip.com |
| Sala | 50 mesta | tourism listing |
| Bazen | grejan, slana voda, kaskada | fotografije, snimak |
| Termalni izvor Vrdnika | 32 °C | više izvora |
| Manastiri na Fruškoj gori | 18, od toga 8 u iriškoj opštini | turistički izvori |
| Novi Sad / Beograd / Ruma | 23 / 70 / 15 km | trip.com |
| Instagram | @ilkicev_kucerak | direktno |
| Facebook | /ilkicevkucerak, 2,5K pratilaca | direktno |

### Podaci koje je dao klijent, bez nezavisne provere

**Ceo tekst sajta od 22. avgusta 2026. dolazi od naručioca**, u fajlu `kucerak copy (1).txt`.
Zamenio je raniji tekst pisan po trećim izvorima. Ako neko kasnije traži odakle je nešto, za
sve dole navedeno odgovor je: od naručioca.

| podatak | gde stoji |
|---|---|
| Pet friendly | red ikonica |
| Vrt od 900 m² | red ikonica |
| 40 minuta od Novog Sada | red ikonica, hero, opis |
| Sremska kuća iz 19. veka, zidana peć, drvene grede | Ukratko |
| Vinski podrum ispod kuće | hero, Ukratko |
| Dve spavaće sobe, bračni + 2 kreveta, kuhinja, kupatilo | Dvosobna kuća |
| Dva kreveta, opremljena kuhinja, kupatilo | Jednosobna kuća |
| Hidromasažna kada, grejanje, slana voda po izboru | Bazen |
| Nema jelovnika, sve se dogovara sa gostom | Restoran na naslovnoj |
| Dogovori za proslave idu telefonom | Proslave |

**Izašlo sa sajta:** kvadratura od 70 m², kamin, terasa, klima i pogled na goru. To je dolazilo
sa trip.com i iz starijeg teksta, a klijentov tekst ih ne pominje. Ostalo je u `tekst.py` pod
`apartmani.a1_oznake` ako se pokaže da važi.

Rastojanje od 23 km do Novog Sada stoji u tekstu Ukratko i dolazi sa trip.com. Nije u sukobu sa
40 minuta, jedno je kilometraža a drugo vreme vožnje, ali vredi da domaćin potvrdi oboje.

**Nije potvrđeno i ne sme se tvrditi bez provere:** cene, vreme prijave i odjave (jedini izvor
navodi 07:30 do 13:30 za oboje, što je očigledno greška u podacima), da bazen nema ogradu
(zaključeno sa fotografija), koliko unapred se zauzimaju vikendi.

---

## 10. Poznate zamke u ovom okruženju

Da se ne troši vreme na ponovno otkrivanje:

- **Headless Chrome ne poštuje `--window-size`** za širinu prikaza. Traži se 375, stranica se
  raspoređuje na 482px i slika se samo iseče. Stari headless režim je uklonjen iz Chrome-a.
  Rešenje je `_build/shot_mobile.py`, koji preko DevTools protokola postavlja pravu širinu.
- **Snimci hvataju stranicu usred ulazne animacije.** Za pouzdan snimak privremeno dodati
  override na kraj `style.css` koji gasi `transition` i `animation`, pa ga ukloniti.
- **Windows Defender briše `.vbs`** iz Startup foldera bez poruke. Zato je autostart obična
  prečica na `pythonw.exe`, bez skripte.
- **GitHub web uploader tiho ispušta fajlove** i preskače imena sa tačkom. Na 169 fajlova je
  otpremio 109 i ništa nije prijavio. Koristiti `git push`.
- **GitHub Pages iz privatnog repoa** radi samo na plaćenom planu, a objavljeni sajt je javan i
  kada je repo privatan. Privatnost repoa ne štiti materijal.

---

## 11. Ako premestiš mapu

Mapa `kucerak` je samodovoljna. Nosi sve: strane, slike, video, generatore, tekst, ovaj fajl i
celu git istoriju. Kopiraj je bilo gde i sajt radi.

Generator, tekst i server računaju putanje **relativno u odnosu na sam fajl**, pa se ne diraju.

Posle premeštanja pucaju samo dve stvari, i to samo za određene poslove:

1. **Obe prečice.** `Kucerak server.lnk` u Startup folderu i `Kucerak sajt.lnk` na Desktopu
   pokazuju na staru putanju.
   Otvori Startup (`Win+R`, ukucaj `shell:startup`), desni klik na prečicu, Properties, i u polju
   Target ispravi putanju do `pythonw.exe` i do novog `_build\serve.pyw`.
   Ili je obriši i napravi novu.

2. **`SRC` u `_build/assets.py`** pokazuje na mapu sa originalnim fotografijama u Downloads.
   Treba samo ako se slike ponovo obrađuju iz originala. Obrađene slike su već u projektu, pa
   sajt radi i bez toga. Skripta se sama zaustavi sa porukom ako mapu ne nađe.

Putanje pomenute u ovom fajlu su takođe stare posle premeštanja, ali to je samo tekst.

**Ako kopiraš na drugi računar**, treba i Python (testirano na 3.12). Za obradu slika i videa
dodatno `pillow`, `pillow-heif` i `imageio-ffmpeg`, a za mobilne snimke `websocket-client`.
Za samo gledanje i menjanje sajta ništa od toga ne treba, dovoljan je Python.

**Veličina:** 21 MB bez `.git`, od čega 12 MB slike i 8,5 MB snimci. `.git` je još oko 30 MB, jer
nosi i slike koje su u međuvremenu obrisane. Istoriju vredi poneti, jer poruke commita
objašnjavaju zašto je nešto urađeno. Ako ti treba samo sajt za postavljanje, kopiraj bez `.git`
i bez `_build`.

---

## 12. Git

14 commita, grana `main`, radno stablo čisto.
Remote: `https://github.com/branko8900/ilkicevkucerak.github.io.git`

Poruke commita objašnjavaju **zašto**, ne šta. Ako treba razumeti neku odluku, `git log` je
najbrži put.
