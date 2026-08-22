# -*- coding: utf-8 -*-
"""
Tihi lokalni server za pregled sajta.

Pokrece se preko pythonw.exe, dakle bez konzolnog prozora. Standardni
`python -m http.server` u tom rezimu ne radi: on za svaki zahtev pise red u
stderr, a pod pythonw stderr ne postoji, pa upis pukne i veza se prekine.
Zato ovde log ide u prazno.

Upotreba:  pythonw serve.pyw [port]
"""
import http.server
import os
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4360
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Tihi(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *args):
        pass          # bez ovoga pythonw pukne na prvom zahtevu

    def end_headers(self):
        # Pregled treba uvek da pokaze zadnju verziju, ne kes.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def zapisi_gresku(greska):
    """Pod pythonw nema ni konzole ni stderr, pa bi pad prosao nemo. Ovako
    ostane red u serve-greska.log, pa se sledeci put zna zasto je stalo."""
    import datetime, traceback
    put = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serve-greska.log")
    try:
        with open(put, "a", encoding="utf-8") as fh:
            fh.write("\n%s  port %d\n%s\n" % (
                datetime.datetime.now().isoformat(timespec="seconds"),
                PORT, traceback.format_exc() if greska else ""))
    except Exception:
        pass


if __name__ == "__main__":
    try:
        with Server(("127.0.0.1", PORT), Tihi) as s:
            s.serve_forever()
    except OSError:
        # Port je zauzet, dakle server vec radi. Nije greska, samo izadji.
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        zapisi_gresku(True)
        sys.exit(1)
