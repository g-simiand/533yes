# ROADMAP — 533yès

## Vision

Benchmark HTR/OCR sur manuscrits de Sieyes -- evaluation systematique des modeles de reconnaissance d'ecriture manuscrite sur les brouillons de Sieyes (GTR, ajout modeles).

**Statut : ACTIF**
**Dernière mise à jour : 2026-02-16**

## V1 — Benchmark initial (TERMINÉ, mars 2025)

- [x] 26 modèles évalués sur 15 manuscrits Sieyès
- [x] Métriques WER, viewer HTML interactif
- [x] Rapports d'analyse publiés

## V1.1 — Passe qualité code (À FAIRE)

- [ ] Nettoyer `utils.py` (717 lignes) : découper en modules, supprimer code mort
- [ ] Nettoyer `benchmark_htr.ipynb` : séparer cellules config / exécution / analyse
- [ ] Vérifier que le viewer HTML fonctionne sans serveur local (standalone)
- [ ] Supprimer le dossier `backup_before_cleanup/` si plus nécessaire
- [ ] Mettre à jour `requirements.txt` (versions épinglées)
- [ ] Publier sur GitHub + release v1.0 (cf. `next_steps.md`)

## V1.2 — Benchmark Gemini 3 via OpenRouter (À FAIRE)

- [ ] Ajouter `google/gemini-3-pro` au benchmark via OpenRouter
- [ ] Ajouter `google/gemini-3-flash` au benchmark via OpenRouter
- [ ] Comparer avec les résultats Gemini 2.0 Flash existants (WER médian: 0.694)
- [ ] Mettre à jour `resultats_summary.md` et les rapports

## Backlog

- [ ] Tester d'autres modèles récents (Claude 4.5, GPT-5, Llama 4, etc.)
- [ ] Automatiser le pipeline (script CLI au lieu de notebook)
- [ ] Intégrer les résultats dans Bench_HTR (framework réutilisable sur D:)

## Prochaine action (GTD)

> Nettoyer `utils.py` (717 lignes) : découper en modules, supprimer code mort

## Skills

- python-project
- ocr-htr

*Derniere mise a jour : 2026-02-22*
