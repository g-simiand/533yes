# Viewer HTR Standalone

## Versions disponibles

Le projet propose **trois versions du viewer** pour différents cas d'usage :

1. **`htr_viewer.html`** - Version originale nécessitant un serveur
2. **`htr_viewer_standalone.html`** - Version avec fallback pour mode standalone 
3. **`htr_viewer_fully_standalone.html`** - Version 100% autonome avec données intégrées ✨

## Utilisation

### Option 1 : Version 100% Standalone (RECOMMANDÉ pour usage sans serveur)

Ouvrez directement **`htr_viewer_fully_standalone.html`** dans votre navigateur :
- ✅ Fonctionne sans aucun serveur
- ✅ Toutes les données sont intégrées dans le HTML
- ✅ Aucune restriction CORS
- ℹ️ Les transcriptions sont simulées pour la démonstration

### Option 2 : Avec un serveur local (pour données réelles)

Cette méthode permet de charger dynamiquement toutes les données réelles :

```bash
# Depuis le dossier viewer/
python simple_server.py
# Ou avec Python 3
python3 -m http.server 8000
```

Puis ouvrir http://localhost:8000/htr_viewer_standalone.html

### Option 3 : Mode standalone avec contournement CORS

**⚠️ Limitations importantes :**
- Les navigateurs modernes appliquent une politique CORS qui empêche le chargement de fichiers locaux via JavaScript
- L'affichage des images fonctionne, mais le chargement des transcriptions et résultats JSON peut être bloqué

Pour contourner ces limitations :
- **Chrome** : lancer avec `--allow-file-access-from-files`
- **Firefox** : dans `about:config`, mettre `security.fileuri.strict_origin_policy` à false (non recommandé)

## Test de compatibilité

Ouvrez **`test_standalone_validation.html`** pour vérifier la compatibilité de votre navigateur avec le mode standalone.

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