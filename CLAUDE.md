# 533yès

## Overview
Benchmark HTR/OCR sur 15 manuscrits de Sieyès avec 26 modèles évalués (WER). Viewer HTML interactif et rapports d'analyse.

## Key Files
- `benchmark_htr.ipynb` : notebook principal du benchmark
- `utils.py` : utilitaires (717 lignes, à refactorer)
- `server.py` : serveur local pour le viewer
- `scripts/` : scripts auxiliaires
- `data/`, `transcriptions_de_référence/` : données et ground truth
- `résultats/`, `rapports/` : résultats et rapports générés
- `viewer/` : viewer HTML interactif
- `kraken_models/` : modèles Kraken testés

## Commands
```bash
pip install -r requirements.txt
python server.py
jupyter notebook benchmark_htr.ipynb
```

## Conventions
- Commits en français
- Branches par feature

## ROADMAP Maintenance
Après chaque session de travail qui complète une tâche :
1. Ouvrir `ROADMAP.md` et cocher `[x]` les tâches terminées
2. Mettre à jour la "Prochaine action (GTD)" si elle a été complétée
3. Mettre à jour la date `*Dernière mise à jour*` en bas du fichier
4. Inclure les changements ROADMAP dans le même commit
