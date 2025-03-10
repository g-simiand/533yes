# Guide d'organisation du dépôt GitHub 533yes

Ce document décrit comment organiser le dépôt GitHub pour présenter efficacement les résultats du projet 533yes.

## Structure recommandée du dépôt

```
533yes/
├── README.md                      # Page d'accueil avec présentation et résultats principaux
├── resultats_summary.md           # Tableau récapitulatif des performances des modèles
├── rapports/
│   ├── performance_par_page.md    # Tableau détaillé des performances par page
│   ├── performance_par_page.html  # Version HTML du tableau de performances
│   └── analyse_modeles.md         # Analyse des forces et faiblesses des modèles
├── viewer/
│   ├── htr_viewer.html            # Interface de visualisation interactive
│   ├── htr_viewer_standalone.html # Version autonome du visualiseur
│   ├── README.md                  # Guide d'utilisation du visualiseur
│   └── simple_server.py           # Script pour lancer un serveur local
├── images/                        # Échantillon d'images pour démonstration
│   └── (quelques images représentatives)
├── data/                          # Données pour le visualiseur
│   ├── images_list.json
│   ├── models_list.json
│   └── wer_data.json
├── scripts/
│   ├── generate_performance_table.py
│   ├── generate_viewer_data.py
│   └── generate_summary.py
└── docs/
    ├── methodology.md             # Description détaillée de la méthodologie
    └── todo_533yes.md             # Liste des tâches (pour référence)
```

## Fichiers clés à mettre en avant

1. **README.md** - C'est la vitrine principale du projet. Il doit contenir:
   - Une description claire du projet
   - Les résultats principaux avec des liens vers les rapports détaillés
   - Des instructions pour explorer les résultats
   - Des informations sur la méthodologie

2. **resultats_summary.md** - Tableau récapitulatif des performances des modèles, facilement accessible depuis la racine.

3. **rapports/analyse_modeles.md** - Analyse détaillée des forces et faiblesses des différents types de modèles.

4. **viewer/htr_viewer.html** - Interface interactive pour explorer les résultats.

## Optimisations pour GitHub

1. **Badges** - Ajouter des badges au README pour indiquer l'état du projet:
   ```markdown
   ![Status: Completed](https://img.shields.io/badge/Status-Completed-success)
   ![Models: 23](https://img.shields.io/badge/Models-23-informational)
   ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
   ```

2. **GitHub Pages** - Activer GitHub Pages pour héberger le visualiseur HTML:
   - Aller dans Settings > Pages
   - Sélectionner la branche main et le dossier /docs ou /
   - Cela permettra d'accéder au visualiseur via une URL publique

3. **Releases** - Créer une release officielle avec une version (v1.0):
   - Inclure un résumé des résultats
   - Joindre une version PDF des rapports principaux

4. **Fichier .gitattributes** - Pour améliorer l'affichage des fichiers Markdown:
   ```
   *.md linguist-detectable=true
   *.md linguist-documentation=false
   ```

## Préparation des fichiers pour GitHub

1. **Vérifier les chemins relatifs** - S'assurer que tous les liens dans les fichiers Markdown utilisent des chemins relatifs compatibles avec GitHub.

2. **Optimiser les images** - Compresser les images pour réduire la taille du dépôt.

3. **Nettoyer les fichiers temporaires** - Supprimer les fichiers de cache, les résultats intermédiaires et autres fichiers non nécessaires.

4. **Ajouter des licences** - Inclure un fichier LICENSE.md à la racine du projet.

## Étapes finales

1. **Vérifier le README** - S'assurer qu'il est complet, bien formaté et contient toutes les informations essentielles.

2. **Tester les liens** - Vérifier que tous les liens internes fonctionnent correctement.

3. **Créer un fichier CITATION.cff** - Pour faciliter la citation du projet:
   ```yaml
   cff-version: 1.2.0
   message: "Si vous utilisez ce logiciel, veuillez le citer comme suit."
   authors:
   - family-names: "Votre Nom"
     given-names: "Votre Prénom"
   title: "533yes: Benchmark HTR pour documents manuscrits historiques"
   version: 1.0.0
   date-released: 2025-03-06
   url: "https://github.com/votre-compte/533yes"
   ```

4. **Ajouter des mots-clés** - Dans la description et les topics GitHub pour améliorer la découvrabilité. 