# 533yes ("See-yes")

![Status: Completed](https://img.shields.io/badge/Status-Completed-success)
![Models: 23](https://img.shields.io/badge/Models-23-informational)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

533yes est un benchmark rapide pour comparer la performance des systèmes d'IA multimodaux sur la tâche HTR (Handwritten Text Recognition) avec des approches plus anciennes (apprentissage machine) sur un échantillon de documents manuscrits d'Emmanuel-Joseph Sieyès. C'est une petite étape sur la voie d'un projet plus large, *IAg Révolution*. L'objectif n'est pas d'obtenir une transcription complète, mais de restituer la plus grande partie possible du contenu sémantique des documents pour les rendre accessible à un moteur de recherche.

## Résultats principaux

Les résultats complets de notre benchmark sont disponibles dans ce dépôt. Voici les points clés :

- **23 modèles évalués** : Incluant des modèles propriétaires (OpenAI, Google, X-AI, Amazon) et libres (Mistral, Meta-Llama, Qwen, Kraken)
- **15 images de test** : Documents manuscrits d'Emmanuel-Joseph Sieyès et le concernant (XVIIIe siècle) 
- **Meilleure performance** : Les modèles les plus performants sont `google/gemini-2.0-flash-thinking-exp` (WER médian: 0.600) et `openai/o1` (WER médian: 0.722)
- **Rapport coût/performance** : Les modèles libres comme `FoNDUE-GD_v2_fr` offrent un excellent rapport qualité/prix

Pour explorer les résultats en détail :
- Consultez [resultats_summary.md](resultats_summary.md) pour un aperçu global des performances
- Explorez [rapports/performance_par_page.md](rapports/performance_par_page.md) pour les performances détaillées par page
- Utilisez le visualiseur interactif [viewer/htr_viewer.html](viewer/htr_viewer.html) pour comparer les transcriptions
- Lisez l'analyse détaillée dans [rapports/analyse_modeles.md](rapports/analyse_modeles.md)

## Structure du projet

- Les images source sont dans le dossier `/images`
- Les transcriptions de référence sont dans le dossier `/transcriptions_de_référence`
- Les transcriptions des divers systèmes sont dans le dossier `/résultats`
- Les résultats produits par les différents modèles sont dans des fichiers au format `nomimage_fournisseur_modele.md`

## Composants du projet

- `benchmark_htr.ipynb` : Notebook principal pour l'exécution des tests
- `benchmark_kraken.py` : Script pour les tests avec Kraken
- `transkribus_api.py` : Interface avec l'API Transkribus
- `utils.py` : Fonctions utilitaires
- `requirements.txt` : Dépendances du projet
- `viewer/htr_viewer.html` : Interface web pour visualiser et comparer les transcriptions
- `scripts/generate_performance_table.py` : Script pour générer les tableaux de performance

## Objectif

Ce benchmark vise à évaluer et comparer l'efficacité des différentes approches de reconnaissance de texte manuscrit sur des documents historiques.

### Limites de la démarche

- **Uniformité des paramètres** : Pour garantir une comparaison standardisée, le même prompt et la même température sont utilisés pour l'ensemble des modèles. Or, ces paramètres fixes peuvent ne pas être adaptés à la spécificité de chaque modèle, limitant ainsi la possibilité d'optimiser leurs performances individuelles.
- **Taille de l'échantillon** : Le benchmark est limité à 15 images, ce qui peut ne pas être représentatif de tous les types de documents manuscrits.

## Métrique d'évaluation : WER (Word Error Rate)

Le WER (Taux d'Erreur par Mot) est la métrique principale utilisée pour évaluer la performance des systèmes HTR. Il est calculé comme suit :

WER = (S + D + I) / N

Où :
- S = nombre de substitutions (mots incorrectement reconnus)
- D = nombre de suppressions (mots manquants)
- I = nombre d'insertions (mots ajoutés)
- N = nombre total de mots dans la référence

Plus le WER est bas, meilleure est la performance du système. Un WER de 0 signifie une reconnaissance parfaite, tandis qu'un WER de 1 (ou 100%) indique une reconnaissance totalement incorrecte.

## Comment utiliser ce dépôt

1. **Explorer les résultats** : Consultez les fichiers de résultats dans le dossier `/rapports`
2. **Visualiser les comparaisons** : Ouvrez `viewer/htr_viewer.html` dans un navigateur pour une expérience interactive
3. **Reproduire les tests** : Suivez les instructions dans `benchmark_htr.ipynb` pour exécuter vos propres tests

## Licence

Ce projet est sous licence [MIT](LICENSE.md).

