# -*- coding: utf-8 -*-
"""
Asset pipeline — Ilkićev kućerak
--------------------------------
Turns the client's raw camera/phone drop (HEIC, oversized JPEG, 4K HEVC) into a
web-ready set: art-directed crops, multiple widths, WebP + JPEG, and a poster-
backed video loop.

Run:  python _build/assets.py

Every output is deterministic — re-run it after dropping new source files in and
the site picks the results up without any HTML edits, as long as the slot names
in SLOTS stay the same.
"""

import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageOps, ImageFilter

import pillow_heif
pillow_heif.register_heif_opener()

# --------------------------------------------------------------------- paths

SRC = r"C:/Users/Branko/Downloads/branja kucerak folder-20260815T170810Z-1-001/branja kucerak folder"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_OUT = os.path.join(ROOT, "assets", "images")
VID_OUT = os.path.join(ROOT, "assets", "video")

WIDTHS = [640, 1024, 1600, 2200]
JPEG_Q = 82
WEBP_Q = 78

# Source files, keyed by the short id used in SLOTS below.
RAW = {
    "banquet_indoor":  "1795.JPG – копија.jpg",
    "glassware_bw":    "1809.JPG – копија.jpg",
    "garden_rounds":   "IMG_3663.HEIC",
    "pool_rounds":     "IMG_3664.HEIC",
    "terrace_rounds":  "IMG_3665.HEIC",
    "pool_wide":       "IMG_3666.HEIC",
    "arches_dusk":     "IMG_7723.HEIC",
    "arch_night":      "IMG_8366.JPG – копија.jpg",
    "arches_night":    "IMG_8368.JPG – копија.jpg",
    "pool_night_dim":  "IMG_8383.JPG – копија.jpg",
    "pool_night_lit":  "IMG_8384.JPG – копија.jpg",   # excluded — see NOTE below
}

# NOTE ON PRIVACY: `pool_night_lit` shows clearly identifiable private guests at
# a closed event. It is deliberately NOT published to any slot. `pool_night_dim`
# is the same scene at an exposure where no face is legible, and is used instead.

# --------------------------------------------------------------- slot recipes
#
#   ratio : output aspect
#   focal : (x, y) in 0..1 — the point the crop keeps centred
#   box   : optional pre-crop (l, t, r, b) in 0..1, applied before the aspect
#           crop. Used to compose a tighter picture out of a loose original.
#   grade : optional tone treatment, see `apply_grade`
#
SLOTS = {
    # ---- the estate --------------------------------------------------------
    # Hero: blue hour, warm-lit arches, no people in frame.
    "hero-estate":        dict(src="arches_dusk",    ratio=(16, 9), focal=(.55, .46)),
    "estate-dusk":        dict(src="arches_dusk",    ratio=(4, 5),  focal=(.55, .52)),
    "estate-dusk-wide":   dict(src="arches_dusk",    ratio=(3, 2),  focal=(.55, .46)),
    "estate-arch-night":  dict(src="arch_night",     ratio=(3, 2),  focal=(.45, .45)),

    # ---- celebrations ------------------------------------------------------
    "celebrations-hero":  dict(src="pool_wide",      ratio=(16, 9), focal=(.50, .46)),
    "celebrations-tall":  dict(src="terrace_rounds", ratio=(4, 5),  focal=(.50, .55)),
    "celebrations-garden":dict(src="garden_rounds",  ratio=(4, 5),  focal=(.50, .50)),
    "celebrations-square":dict(src="terrace_rounds", ratio=(1, 1),  focal=(.55, .62)),
    "celebrations-night": dict(src="pool_night_dim", ratio=(16, 9), focal=(.50, .55)),

    # ---- pool & wellness ---------------------------------------------------
    "pool-hero":          dict(src="pool_rounds",    ratio=(16, 9), focal=(.50, .60)),
    "pool-tall":          dict(src="pool_rounds",    ratio=(4, 5),  focal=(.50, .58)),

    # ---- table & cellar ----------------------------------------------------
    # The original is a wide room shot with guests in the near foreground and
    # cigarette packs, lighters and phones along the front edge of the table.
    # These boxes compose down to the glassware, linen and sunflowers only.
    "table-setting":      dict(src="banquet_indoor", ratio=(3, 2),
                               box=(.30, .02, .74, .64), focal=(.5, .5)),
    "table-setting-tall": dict(src="banquet_indoor", ratio=(4, 5),
                               box=(.34, .00, .68, .66), focal=(.5, .48)),
    "cellar-glass":       dict(src="glassware_bw",   ratio=(4, 5),  focal=(.42, .50)),
    "cellar-glass-square":dict(src="glassware_bw",   ratio=(1, 1),  focal=(.42, .50)),
}

# Stills lifted from the broadcast footage — these are the only images of the
# apartment interiors and the brick hall. Cropped above the burned-in station
# graphics. See README: rights need clearing or a clean master.
VIDEO_STILLS = {
    "interior-apartment": dict(clip="0713.mp4",    t=6.0,  ratio=(3, 2),  focal=(.55, .45)),
    "interior-hall":      dict(clip="0713(2).mp4", t=36.0, ratio=(16, 9), focal=(.50, .48)),
    "pool-cascade":       dict(clip="0713(2).mp4", t=12.0, ratio=(3, 2),  focal=(.45, .50)),
    "gate-garden":        dict(clip="0713.mp4",    t=0.5,  ratio=(4, 5),  focal=(.55, .50)),
}

# Fraction of frame height removed from the bottom to clear the station bug.
# Measured: the lower-right station logo starts at ~78.5% of frame height and the
# lower-left programme title at ~82%. 0.23 clears both with margin.
BUG_CROP = 0.23


# ------------------------------------------------------------------ helpers

def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def load(name):
    im = Image.open(os.path.join(SRC, RAW[name]))
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


def crop_box(im, box):
    w, h = im.size
    l, t, r, b = box
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def crop_ratio(im, ratio, focal=(.5, .5)):
    """Crop to `ratio`, keeping `focal` in frame and clamped to the edges."""
    w, h = im.size
    tw, th = ratio
    target = tw / th
    current = w / h

    if current > target:                      # too wide — trim sides
        nw, nh = int(round(h * target)), h
    else:                                     # too tall — trim top/bottom
        nw, nh = w, int(round(w / target))

    cx, cy = focal[0] * w, focal[1] * h
    left = max(0, min(w - nw, int(round(cx - nw / 2))))
    top = max(0, min(h - nh, int(round(cy - nh / 2))))
    return im.crop((left, top, left + nw, top + nh))


def dominant(im):
    """Average colour, used as the frame background so images fade in from the
    right tone instead of flashing an empty surface."""
    t = im.copy()
    t.thumbnail((40, 40))
    t = t.filter(ImageFilter.GaussianBlur(6))
    px = list(t.getdata())
    n = len(px)
    r = sum(p[0] for p in px) // n
    g = sum(p[1] for p in px) // n
    b = sum(p[2] for p in px) // n
    # Pull it toward the canvas so it reads as part of the surface stack.
    r, g, b = (int(r * .55 + 14 * .45), int(g * .55 + 21 * .45), int(b * .55 + 18 * .45))
    return "#%02x%02x%02x" % (r, g, b)


def emit(im, slot, manifest):
    """Write every width in JPEG + WebP and record the slot in the manifest."""
    os.makedirs(IMG_OUT, exist_ok=True)
    w0, h0 = im.size
    made = []
    for w in WIDTHS:
        if w > w0 and made:          # never upscale past the source
            continue
        h = int(round(w * h0 / w0))
        r = im.resize((w, h), Image.LANCZOS)
        r.save(os.path.join(IMG_OUT, f"{slot}-{w}.jpg"), "JPEG",
               quality=JPEG_Q, optimize=True, progressive=True)
        r.save(os.path.join(IMG_OUT, f"{slot}-{w}.webp"), "WEBP", quality=WEBP_Q, method=5)
        made.append(w)
    manifest[slot] = dict(widths=made, w=w0, h=h0,
                          ratio=round(w0 / h0, 4), bg=dominant(im))
    print(f"  {slot:22s} {w0}x{h0}  ->  {made}")


def apply_grade(im, grade):
    return im


# --------------------------------------------------------------------- steps

def build_photos(manifest):
    print("photos")
    for slot, cfg in SLOTS.items():
        im = load(cfg["src"])
        if "box" in cfg:
            im = crop_box(im, cfg["box"])
        im = crop_ratio(im, cfg["ratio"], cfg.get("focal", (.5, .5)))
        emit(im, slot, manifest)


def build_video_stills(manifest):
    print("stills from footage (station graphics cropped)")
    exe = ffmpeg()
    tmp = os.path.join(ROOT, "_build", ".tmp")
    os.makedirs(tmp, exist_ok=True)
    for slot, cfg in VIDEO_STILLS.items():
        raw = os.path.join(tmp, f"{slot}.png")
        subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", str(cfg["t"]), "-i", os.path.join(SRC, cfg["clip"]),
                        "-frames:v", "1", raw], check=True)
        im = Image.open(raw).convert("RGB")
        w, h = im.size
        im = im.crop((0, 0, w, int(h * (1 - BUG_CROP))))       # clear the bug
        im = crop_ratio(im, cfg["ratio"], cfg.get("focal", (.5, .5)))
        emit(im, slot, manifest)
    shutil.rmtree(tmp, ignore_errors=True)


def build_video():
    """Hero loop: H.264 for reach, VP9/WebM for weight, plus a poster frame.
    Muted, no audio track at all — it is wallpaper, not media."""
    print("video")
    os.makedirs(VID_OUT, exist_ok=True)
    exe = ffmpeg()
    src = os.path.join(SRC, "0713.mp4")

    # crop=w:h:x:y — strip the station graphics, land on a 2.11:1 cinema band
    vf = f"crop=iw:ih*{1 - BUG_CROP}:0:0,scale=1600:-2"

    subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                    "-an", "-vf", vf, "-c:v", "libx264", "-profile:v", "high",
                    "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    os.path.join(VID_OUT, "estate-loop.mp4")], check=True)

    subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                    "-an", "-vf", vf, "-c:v", "libvpx-vp9", "-crf", "38",
                    "-b:v", "0", "-row-mt", "1", "-cpu-used", "3",
                    os.path.join(VID_OUT, "estate-loop.webm")], check=True)

    subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", "2.2", "-i", src, "-frames:v", "1",
                    "-vf", f"{vf},scale=1600:-2", "-q:v", "4",
                    os.path.join(VID_OUT, "estate-loop-poster.jpg")], check=True)

    for f in sorted(os.listdir(VID_OUT)):
        kb = os.path.getsize(os.path.join(VID_OUT, f)) // 1024
        print(f"  {f:28s} {kb:>6d} KB")


# Dva klipa koja je narucilac poslao 22. avgusta 2026. Isti izvor kao
# estate-loop: prilog televizije, sa urezanom grafikom stanice. Recept je zato
# isti, crop skida grafiku. Isecanje ne prenosi prava, videti PREDAJA.md.
KLIP_SRC = r"C:/Users/Branko/Downloads"
KLIPOVI = {
    "kapija":  dict(fajl="0713.mp4",      poster=4.0),
    "kaskada": dict(fajl="0713(2).mov",   poster=12.0),
}


def build_klipovi():
    """Klipovi za naslovnu. H.264 za doseg, VP9 za tezinu, plus poster.
    Bez zvucnog zapisa: na sajtu se pustaju bez tona."""
    print("klipovi")
    os.makedirs(VID_OUT, exist_ok=True)
    exe = ffmpeg()
    vf = f"crop=iw:ih*{1 - BUG_CROP}:0:0,scale=1600:-2"

    for ime, cfg in KLIPOVI.items():
        src = os.path.join(KLIP_SRC, cfg["fajl"])
        if not os.path.exists(src):
            print(f"  preskacem {ime}, nema izvora: {src}")
            continue

        subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                        "-an", "-vf", vf, "-c:v", "libx264", "-profile:v", "high",
                        "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart",
                        os.path.join(VID_OUT, f"{ime}.mp4")], check=True)

        # Bez VP9. Probano: na ovom materijalu webm ispadne veci od H.264
        # (2224 prema 1980 KB, 6962 prema 6500 KB), pa bi samo dodao tezinu.

        subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", str(cfg["poster"]), "-i", src, "-frames:v", "1",
                        "-vf", vf, "-q:v", "4",
                        os.path.join(VID_OUT, f"{ime}-poster.jpg")], check=True)
        print(f"  {ime} gotov")


def main():
    if not os.path.isdir(SRC):
        sys.exit(f"Source folder not found:\n  {SRC}")
    manifest = {}
    build_photos(manifest)
    build_video_stills(manifest)
    # build_video() namerno ne ide u redovan prolaz. Pravi estate-loop, koji
    # se nigde na sajtu ne prikazuje, a nosi 4,5 MB i tri fajla. Pozvati rucno
    # ako zatreba:  python -c "import sys;sys.path.insert(0,'_build');
    # import assets; assets.build_video()"
    build_klipovi()
    with open(os.path.join(IMG_OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print(f"\n{len(manifest)} slots -> {IMG_OUT}")


if __name__ == "__main__":
    main()
