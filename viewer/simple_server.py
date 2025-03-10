#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serveur web simple pour le viewer HTR.
Exécutez ce script puis accédez à http://localhost:8000/htr_viewer.html
"""

import http.server
import socketserver
import webbrowser
import os

# Port sur lequel le serveur va écouter
PORT = 8000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler qui ajoute les en-têtes CORS pour permettre les requêtes cross-origin"""
    
    def end_headers(self):
        # Ajouter les en-têtes CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_GET(self):
        # Gérer les requêtes GET
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def run_server():
    """Démarrer le serveur web"""
    
    # Créer le serveur
    handler = CORSHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Serveur démarré sur le port {PORT}")
    print(f"Ouvrez votre navigateur à l'adresse : http://localhost:{PORT}/htr_viewer.html")
    
    # Ouvrir automatiquement le navigateur
    webbrowser.open(f"http://localhost:{PORT}/htr_viewer.html")
    
    try:
        # Démarrer le serveur
        httpd.serve_forever()
    except KeyboardInterrupt:
        # Arrêter le serveur proprement avec Ctrl+C
        print("\nServeur arrêté.")
        httpd.server_close()

if __name__ == "__main__":
    run_server() 