# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnement Sémantique](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-07

### Ajouté
- Première version officielle du benchmark 533yès
- Évaluation complète de 26 modèles HTR/OCR sur 15 manuscrits de Sieyès
- Viewer HTML interactif pour l'exploration visuelle des résultats
- Rapports détaillés d'analyse des performances par page et par modèle
- Scripts Python reproductibles pour le benchmark
- Transcriptions de référence (ground truth) des manuscrits
- Documentation complète avec README et guides d'utilisation

### Résultats clés
- TrOCR (Base Handwritten) : meilleur modèle avec WER moyen de 8.7%
- Kraken HTR United : deuxième position avec WER moyen de 14.5%
- Florence-2 Large FT : troisième position avec WER moyen de 15.1%

### Infrastructure
- Configuration GitHub Pages pour le viewer interactif
- Scripts de génération automatique des tableaux de performances
- Serveur local simple pour les tests du viewer

[1.0.0]: https://github.com/g-simiand/533yes/releases/tag/v1.0