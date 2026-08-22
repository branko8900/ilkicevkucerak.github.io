# -*- coding: utf-8 -*-
"""
Renders the site at a real phone viewport.

Chrome's --window-size does not control the layout viewport in the current
headless build on Windows: ask for 375 and the page still lays out at 482 and
the PNG is merely cropped. Device metrics have to be set over the DevTools
protocol instead, which is what this does.

Usage:  python _build/shot_mobile.py [width] [height] [out_dir]
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

import websocket  # websocket-client

def _nadji_chrome():
    """Trazi Chrome na uobicajenim mestima, da skripta radi i posle
    premestanja projekta ili na drugom racunaru."""
    import shutil
    kandidati = [
        os.path.join(os.environ.get("ProgramFiles", ""), "Google/Chrome/Application/chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google/Chrome/Application/chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google/Chrome/Application/chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft/Edge/Application/msedge.exe"),
    ]
    for c in kandidati:
        if c and os.path.exists(c):
            return c
    naden = shutil.which("chrome") or shutil.which("msedge")
    if naden:
        return naden
    sys.exit("Ne mogu da nadjem Chrome ni Edge. Postavi putanju rucno u CHROME.")


CHROME = _nadji_chrome()
BASE = "http://localhost:4360"

W = int(sys.argv[1]) if len(sys.argv) > 1 else 375
H = int(sys.argv[2]) if len(sys.argv) > 2 else 812
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
    os.environ["TEMP"], f"kmobil{W}x{H}")

PAGES = [
    ("1-naslovna",  "/sr/index.html",          True),
    ("2-hero",      "/sr/index.html",          False),
    ("3-proslave",  "/sr/proslave.html",       True),
    ("4-kontakt",   "/sr/kontakt.html",        True),
    ("5-meni",      "/sr/index.html",          False),   # with the drawer open
]


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    os.makedirs(OUT, exist_ok=True)
    port = free_port()
    prof = os.path.join(os.environ["TEMP"], f"kcdp{port}")
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--hide-scrollbars", f"--remote-debugging-port={port}",
         f"--user-data-dir={prof}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    ws_url = None
    for _ in range(60):
        try:
            data = json.load(urllib.request.urlopen(
                f"http://127.0.0.1:{port}/json", timeout=1))
            for t in data:
                if t.get("type") == "page":
                    ws_url = t["webSocketDebuggerUrl"]
                    break
            if ws_url:
                break
        except Exception:
            pass
        time.sleep(0.25)
    if not ws_url:
        proc.kill()
        sys.exit("Chrome se nije javio na DevTools portu")

    # Chrome rejects a WS handshake that carries an Origin it was not told
    # to allow; omitting the header entirely is cleaner than opening it up.
    ws = websocket.create_connection(ws_url, timeout=30, suppress_origin=True)
    n = [0]

    def cmd(method, params=None):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == n[0]:
                return msg.get("result", {})

    cmd("Page.enable")
    cmd("Emulation.setDeviceMetricsOverride", {
        "width": W, "height": H, "deviceScaleFactor": 2,
        "mobile": True, "screenWidth": W, "screenHeight": H})
    cmd("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})

    for name, path, full in PAGES:
        cmd("Page.navigate", {"url": BASE + path})
        time.sleep(3.2)   # let fonts, images and the entrance animation settle

        # Confirm the layout viewport really is what we asked for.
        vw = cmd("Runtime.evaluate", {
            "expression": "window.innerWidth", "returnByValue": True}
        ).get("result", {}).get("value")

        if name == "5-meni":
            cmd("Runtime.evaluate", {"expression":
                "document.querySelector('.burger').click()"})
            time.sleep(0.9)

        shot = cmd("Page.captureScreenshot", {
            "format": "png", "captureBeyondViewport": bool(full)})
        import base64
        f = os.path.join(OUT, name + ".png")
        with open(f, "wb") as fh:
            fh.write(base64.b64decode(shot["data"]))
        kb = os.path.getsize(f) // 1024
        print(f"  {name:14s} innerWidth={vw:<5} {'cela strana' if full else 'prvi ekran'}  {kb} KB")

    ws.close()
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
    shutil.rmtree(prof, ignore_errors=True)
    print(f"\nFOLDER: {OUT}")


if __name__ == "__main__":
    main()
