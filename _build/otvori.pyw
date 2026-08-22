# -*- coding: utf-8 -*-
"""
Otvara sajt u pregledacu, a pre toga podigne server ako ne radi.

Precica na Desktopu pokazuje ovde, ne pravo na adresu. Razlog: `.url` precica
samo otvori `http://localhost:4360` i ako server tog trenutka ne radi, u
pregledacu pise da se stranica ne moze otvoriti. Ovako se prvo proveri port,
pa ako niko ne slusa, server se pokrene i saceka se da se javi.

Upotreba:  pythonw otvori.pyw [port] [putanja]
"""
import os
import socket
import subprocess
import sys
import time
import webbrowser

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4360
PUTANJA = sys.argv[2] if len(sys.argv) > 2 else "/sr/index.html"

KOREN = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(KOREN, "serve.pyw")
URL = "http://localhost:%d%s" % (PORT, PUTANJA)

# DETACHED_PROCESS | CREATE_NO_WINDOW — server nadzivi ovu skriptu i ne
# otvara konzolni prozor.
ODVOJENO = 0x00000008 | 0x08000000


def slusa(port, cekanje=0.4):
    with socket.socket() as s:
        s.settimeout(cekanje)
        return s.connect_ex(("127.0.0.1", port)) == 0


def pythonw():
    """Pod pythonw.exe je sys.executable vec pravi, ali ako neko pokrene ovo
    obicnim python.exe, server bi dobio konzolni prozor. Zato se trazi
    pythonw pored njega."""
    exe = sys.executable
    tih = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return tih if os.path.exists(tih) else exe


def poruka(tekst):
    """Nema konzole pod pythonw, pa greska ide u prozorce."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, tekst, "Ilkićev kućerak", 0x10)
    except Exception:
        pass


def main():
    if not slusa(PORT):
        if not os.path.exists(SERVER):
            poruka("Ne mogu da nađem serve.pyw na putanji:\n\n%s\n\n"
                   "Verovatno je mapa kucerak premestena. Napravi novu prečicu "
                   "koja pokazuje na otvori.pyw u novoj mapi." % SERVER)
            return 1
        try:
            subprocess.Popen([pythonw(), SERVER, str(PORT)],
                             cwd=KOREN, creationflags=ODVOJENO,
                             stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        except Exception as e:
            poruka("Server ne može da se pokrene:\n\n%s" % e)
            return 1

        # Server se digne za koji trenutak. Ceka se do deset sekundi.
        for _ in range(40):
            if slusa(PORT):
                break
            time.sleep(0.25)
        else:
            poruka("Server se nije javio na portu %d ni posle deset sekundi.\n\n"
                   "Pogledaj %s, tu piše ako je pukao."
                   % (PORT, os.path.join(KOREN, "serve-greska.log")))
            return 1

    webbrowser.open(URL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
