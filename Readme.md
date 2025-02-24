# 533yes ("See-yes")

533yes est un petit benchmark pour comparer la performance des systèmes d'IA sur la tâche HTR (Handwritten Text Recognition) avec les approches plus anciennes (apprentissage machine, etc.) sur un échantillon de documents manuscrits d'Emmanuel-Joseph Sieyès.

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

## Objectif

Ce benchmark vise à évaluer et comparer l'efficacité des différentes approches de reconnaissance de texte manuscrit sur des documents historiques.

## Métrique d'évaluation : WER (Word Error Rate)

Le WER (Taux d'Erreur par Mot) est la métrique principale utilisée pour évaluer la performance des systèmes HTR. Il est calculé comme suit :

WER = (S + D + I) / N

Où :
- S = nombre de substitutions (mots incorrectement reconnus)
- D = nombre de suppressions (mots manquants)
- I = nombre d'insertions (mots ajoutés)
- N = nombre total de mots dans la référence

Plus le WER est bas, meilleure est la performance du système. Un WER de 0 signifie une reconnaissance parfaite, tandis qu'un WER de 1 (ou 100%) indique une reconnaissance totalement incorrecte.

