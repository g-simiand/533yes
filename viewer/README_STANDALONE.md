# Viewer HTR Standalone

## Utilisation

Le viewer HTR peut être utilisé de deux manières :

### 1. Avec un serveur local (recommandé)

Cette méthode permet de charger dynamiquement toutes les données :

```bash
# Depuis le dossier viewer/
python simple_server.py
# Ou avec Python 3
python3 -m http.server 8000
```

Puis ouvrir http://localhost:8000/htr_viewer_standalone.html

### 2. Sans serveur (standalone)

**⚠️ Limitations importantes :**
- Les navigateurs modernes appliquent une politique CORS qui empêche le chargement de fichiers locaux via JavaScript
- L'affichage des images fonctionne, mais le chargement des transcriptions et résultats JSON peut être bloqué
- Pour contourner cette limitation sur Chrome : lancer avec `--allow-file-access-from-files`
- Sur Firefox : taper `about:config` et mettre `security.fileuri.strict_origin_policy` à false (non recommandé)

Pour ouvrir directement le fichier :
1. Ouvrir `viewer/htr_viewer_standalone.html` dans votre navigateur
2. Les images devraient s'afficher correctement
3. Les transcriptions peuvent ne pas se charger à cause des restrictions CORS

## Structure des fichiers

Le viewer attend la structure suivante :
```
projet/
├── viewer/
│   └── htr_viewer_standalone.html
├── images/                          # Images sources (PNG)
├── transcriptions_de_référence/     # Transcriptions de référence (MD)
├── résultats/                       # Résultats des modèles (JSON)
└── data/
    ├── images_list.json             # Liste des images
    └── models_list.json             # Liste des modèles
```

## Solution alternative

Pour un déploiement web sans serveur, envisager :
1. Héberger sur GitHub Pages
2. Utiliser un CDN pour les fichiers de données
3. Intégrer toutes les données directement dans le HTML (version lourde mais 100% standalone)