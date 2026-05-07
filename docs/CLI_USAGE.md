# Guide d'utilisation du script CLI benchmark_cli.py

## Vue d'ensemble

Le script `benchmark_cli.py` automatise le pipeline de benchmark HTR/OCR qui était précédemment exécuté via le notebook Jupyter `benchmark_htr.ipynb`. Cette automatisation permet une exécution en ligne de commande, facilitant l'intégration dans des pipelines CI/CD et l'exécution en batch.

## Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation de base

### Exécuter le benchmark complet

```bash
python benchmark_cli.py
```

Cette commande exécute le benchmark avec les paramètres par défaut :
- Traite toutes les images dans le dossier `images/`
- Teste tous les modèles définis dans `models_to_test.json`
- Utilise 1 worker (traitement séquentiel)
- Génère automatiquement les rapports

### Options principales

#### Traitement parallèle

Pour accélérer le traitement, utilisez plusieurs workers :

```bash
python benchmark_cli.py --workers 4
```

#### Filtrer les modèles

Testez uniquement certains modèles spécifiques :

```bash
python benchmark_cli.py --models "google/gemini-2.0-flash-001" "openai/gpt-4o-2024-11-20"
```

#### Filtrer les images

Traitez uniquement certaines images :

```bash
python benchmark_cli.py --images "manuscrit_001" "manuscrit_002" 
```

#### Mode incrémental vs Force

Par défaut, le script fonctionne en mode incrémental (skip les résultats existants) :

```bash
# Mode incrémental (défaut)
python benchmark_cli.py

# Forcer le recalcul de tous les résultats
python benchmark_cli.py --force
```

#### Configuration personnalisée

Utilisez un fichier de configuration JSON ou YAML :

```bash
python benchmark_cli.py --config config_custom.json
```

Exemple de fichier de configuration JSON :

```json
{
  "results_dir": "résultats_custom",
  "images_dir": "images_test",
  "models_file": "models_subset.json",
  "force_rerun": false,
  "verbose": true
}
```

#### Contrôle des rapports

```bash
# Skip la génération automatique des rapports
python benchmark_cli.py --skip-reports

# Exporter les métriques vers un fichier CSV
python benchmark_cli.py --metrics-output metrics.csv
```

#### Mode verbose

Pour plus de détails pendant l'exécution :

```bash
python benchmark_cli.py --verbose
```

## Exemples d'utilisation avancée

### Pipeline de test rapide

Test rapide avec un sous-ensemble de modèles et d'images :

```bash
python benchmark_cli.py \
  --models "google/gemini-2.0-flash-001" \
  --images "manuscrit_001" \
  --workers 2 \
  --verbose
```

### Benchmark complet optimisé

Exécution complète avec parallélisation maximale :

```bash
python benchmark_cli.py \
  --workers 8 \
  --metrics-output benchmark_metrics.csv
```

### Mode batch avec configuration

Pour des exécutions répétées avec différentes configurations :

```bash
# Configuration développement
python benchmark_cli.py --config configs/dev.json

# Configuration production  
python benchmark_cli.py --config configs/prod.json --workers 16
```

## Structure du code

Le script est organisé en classe `HTRBenchmark` avec les méthodes principales :

- `__init__()` : Initialisation et chargement de la configuration
- `run_benchmark()` : Exécution du benchmark principal
- `process_image()` : Traitement d'une image avec un modèle
- `generate_reports()` : Génération des rapports et tables
- `analyze_metrics()` : Analyse des métriques de performance

## Sorties générées

Le script génère les mêmes sorties que le notebook original :

1. **Fichiers JSON individuels** : Un fichier par combinaison image/modèle dans `résultats/`
2. **Table de résultats** : Générée via `generate_results_md_table()`
3. **Table de performance** : Via `scripts/generate_performance_table.py`
4. **Données du viewer** : Via `scripts/generate_viewer_data.py`
5. **Métriques CSV** : Si spécifié avec `--metrics-output`

## Migration depuis le notebook

Pour migrer depuis le notebook vers le CLI :

1. **Exécution simple** : Remplacez l'exécution du notebook par `python benchmark_cli.py`
2. **Paramètres** : Les variables du notebook peuvent être passées via arguments CLI ou fichier de config
3. **Résultats** : Les sorties sont identiques et compatibles avec le viewer existant

## Intégration CI/CD

Exemple d'intégration dans un pipeline CI/CD :

```yaml
# .github/workflows/benchmark.yml
name: HTR Benchmark
on:
  schedule:
    - cron: '0 2 * * *'  # Exécution quotidienne

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run benchmark
        run: python benchmark_cli.py --workers 4 --metrics-output metrics.csv
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: |
            résultats/
            metrics.csv
```

## Troubleshooting

### Erreur "No images found"

Vérifiez que le dossier `images/` contient des fichiers `.jpg` ou `.png`.

### Erreur de mémoire

Réduisez le nombre de workers :

```bash
python benchmark_cli.py --workers 1
```

### Résultats manquants

Vérifiez les logs en mode verbose pour identifier les erreurs :

```bash
python benchmark_cli.py --verbose --images "image_problematique"
```

## Support

Pour toute question ou problème, consultez :
- Le README principal du projet
- Les issues GitHub du projet
- La documentation dans `CLAUDE.md`