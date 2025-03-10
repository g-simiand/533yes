# Todo List - Projet 533yes

## Correction et amélioration des évaluations

- [x] Corriger le calcul du WER pour ignorer les marqueurs `[XXX]` (mots illisibles)
- [x] Nettoyer les transcriptions des marqueurs markdown au début et à la fin des textes
- [x] Vérifier si d'autres nettoyages sont nécessaires (espaces, retours à la ligne, etc.)
- [x] Mettre à jour la fonction `calculate_wer()` dans `utils.py` avec ces corrections

## Complétion des tests

- [x] Récupérer et intégrer les résultats de Transkribus (à récupérer manuellement)
- [x] Vérifier pourquoi certains modèles n'ont pas répondu et résoudre les problèmes
- [x] Lancer l'évaluation complète avec tous les modèles maintenant que les textes de référence sont finalisés
- [x] Mettre à jour le fichier `models_to_test.json` si nécessaire (retirer les modèles problématiques ou ajouter de nouveaux)

## Visualisation et présentation des résultats

- [x] Créer un tableau comparatif des performances par page (WER pour chaque modèle et chaque image)
- [x] Développer un viewer HTML interactif avec les fonctionnalités suivantes:
  - [x] Sélection d'une image du corpus
  - [x] Sélection de différents modèles pour comparer leurs transcriptions
  - [x] Affichage côte à côte de l'image et des transcriptions
  - [x] Mise en évidence des différences avec la transcription de référence

## Documentation et analyse

- [x] Mettre à jour le README avec les résultats finaux
- [x] Retirer la mention "Work in progress" une fois l'évaluation terminée
- [x] Ajouter une analyse des forces et faiblesses de chaque type de modèle
- [x] Documenter les cas particuliers où certains modèles excellent ou échouent

## Optimisations techniques

- [x] Optimiser le code de benchmark pour réduire le temps d'exécution
- [x] Ajouter une gestion des erreurs plus robuste pour éviter les interruptions lors des tests
- [x] Mettre en place un système de cache pour éviter de refaire des requêtes coûteuses
- [x] Vérifier si les coûts sont correctement calculés pour tous les modèles

## Publication et partage

- [x] Générer des graphiques comparatifs pour visualiser les performances
- [x] Préparer une présentation des résultats
- [x] Mettre à jour le dépôt GitHub avec tous les résultats
- [x] Rédiger un article ou un billet de blog présentant la méthodologie et les résultats

## Tâches supplémentaires

- [x] Améliorer la documentation du code pour faciliter la maintenance future
- [ ] Créer une version exportable des résultats pour partage (PDF)
- [ ] Envisager l'ajout de nouveaux modèles récemment publiés pour comparaison
- [x] Optimiser le viewer HTML pour une meilleure expérience mobile 

Débugger derneirs modèles
Intégrer Transkribus
Vérifier transcriptions déjà générées