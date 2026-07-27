#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serveur web simple pour les viewers HTR.

Exécutez ce script puis accédez à :
  - http://localhost:8000/viewer/htr_viewer.html        (comparateur, lecture seule)
  - http://localhost:8000/viewer/diplomatic_editor.html (éditeur de transcription diplomatique)

En plus du service de fichiers statiques du dépôt, ce serveur expose :
  - GET  /bench/<chemin>   : fichiers du dépôt voisin Bench_HTR (images d'entrée)
  - POST /api/save-gold    : écriture disque du gold diplomatique (CSV UTF-8)
"""

import csv
import http.server
import io
import json
import os
import posixpath
import socketserver
import time
import urllib.parse
import webbrowser

# Port sur lequel le serveur va écouter
PORT = 8000

REPO = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.abspath(os.path.join(REPO, os.pardir, "Bench_HTR"))
GOLD_OUT = os.path.join(REPO, "viewer", "gold_diplomatique.csv")
GOLD_COLUMNS = ["item_name", "gold_text", "family", "image_path"]


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler statique + préfixe /bench/ + endpoint d'écriture du gold."""

    def end_headers(self):
        # Ajouter les en-têtes CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def translate_path(self, path):
        """Mappe /bench/<x> vers le dépôt Bench_HTR, le reste vers le dépôt courant."""
        parsed = urllib.parse.urlsplit(path).path
        parsed = urllib.parse.unquote(parsed, errors='surrogatepass')
        if parsed.startswith('/bench/'):
            rel = posixpath.normpath(parsed[len('/bench/'):]).lstrip('/')
            target = os.path.abspath(os.path.join(BENCH, *rel.split('/')))
            # Confinement : interdit de sortir de Bench_HTR
            if os.path.commonpath([target, BENCH]) != BENCH:
                return os.path.join(BENCH, "__interdit__")
            return target
        return super().translate_path(path)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        if urllib.parse.urlsplit(self.path).path != '/api/save-gold':
            self.send_error(404, "Endpoint inconnu")
            return
        try:
            length = int(self.headers.get('Content-Length') or 0)
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
            rows = payload.get('rows') or []
            if not isinstance(rows, list):
                raise ValueError("champ 'rows' attendu (liste)")

            os.makedirs(os.path.dirname(GOLD_OUT), exist_ok=True)
            # Sauvegarde horodatée de la version précédente (jamais d'écrasement muet)
            if os.path.exists(GOLD_OUT):
                backup = "%s.%s.bak" % (GOLD_OUT, time.strftime("%Y%m%d-%H%M%S"))
                with open(GOLD_OUT, 'rb') as src, open(backup, 'wb') as dst:
                    dst.write(src.read())

            buf = io.StringIO(newline='')
            writer = csv.DictWriter(buf, fieldnames=GOLD_COLUMNS, lineterminator='\n')
            writer.writeheader()
            for row in rows:
                writer.writerow({k: (row.get(k) or "") for k in GOLD_COLUMNS})
            with open(GOLD_OUT, 'w', encoding='utf-8', newline='') as fh:
                fh.write(buf.getvalue())

            self._json(200, {
                "ok": True, "path": GOLD_OUT, "rows": len(rows),
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as exc:  # noqa: BLE001 - l'erreur est renvoyée au client
            self._json(500, {"ok": False, "error": str(exc)})

    def _json(self, status, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def run_server(open_browser=True, page="viewer/diplomatic_editor.html"):
    """Démarrer le serveur web"""
    os.chdir(REPO)
    httpd = Server(("", PORT), CORSHTTPRequestHandler)

    print(f"Serveur démarré sur le port {PORT} (racine : {REPO})")
    print(f"  Comparateur : http://localhost:{PORT}/viewer/htr_viewer.html")
    print(f"  Éditeur     : http://localhost:{PORT}/viewer/diplomatic_editor.html")

    if open_browser:
        webbrowser.open(f"http://localhost:{PORT}/{page}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
        httpd.server_close()


if __name__ == "__main__":
    run_server(open_browser=os.environ.get("NO_BROWSER") != "1")
