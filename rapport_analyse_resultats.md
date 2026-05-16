# Rapport d'analyse des résultats JSON - Benchmark HTR/OCR 533yès

## Vue d'ensemble du benchmark

- **26 modèles** évalués (14 libres, 12 propriétaires)
- **15 manuscrits** de Sieyès testés avec **14 pages** valides
- **372 fichiers** de résultats JSON analysés
- Métrique principale : **WER** (Word Error Rate)

## Manuscrits testés

1. AN-284AP-18-fasc ms extr Moniteur carriere Sieyes-1789-1799 (2 pages)
2. AN-284AP-4-doss 10 (3 pages) 
3. AN-284AP-4-doss 11 (4 pages)
4. AN-284AP-4-doss 13-Declar Volont Sieyes Condorcet-juin 1791-x4 correct (2 pages)
5. AN-284AP-4-doss 14 (2 pages)

## Classement des modèles par performance (WER médian)

### Top 10 des meilleurs modèles

1. **openai/gpt-4.5-preview** [propriétaire/openai]
   - WER médian: **0.572**
   - WER: min=0.223 | max=3.571 | moy=1.111
   - Coût: $1.876 total | $0.125 moy
   - Pages testées: 15 | WER valides: 14

2. **anthropic/claude-3.5-sonnet** [propriétaire/anthropic]
   - WER médian: **0.694**
   - WER: min=0.269 | max=3.667 | moy=1.262
   - Coût: $0.140 total | $0.010 moy
   - Pages testées: 14 | WER valides: 13

3. **google/gemini-2.0-flash-001** [propriétaire/google]
   - WER médian: **0.711**
   - WER: min=0.257 | max=3.024 | moy=1.167
   - Coût: $0.007 total | $0.0005 moy
   - Pages testées: 15 | WER valides: 14

4. **google/gemini-2.0-flash-thinking-exp:free** [propriétaire/google]
   - WER médian: **0.711**
   - WER: min=0.194 | max=5.071 | moy=1.339
   - Coût: Gratuit
   - Pages testées: 15 | WER valides: 14

5. **anthropic/claude-3.7-sonnet** [propriétaire/anthropic]
   - WER médian: **0.715**
   - WER: min=0.189 | max=2.952 | moy=1.129
   - Coût: $0.137 total | $0.010 moy
   - Pages testées: 14 | WER valides: 13

6. **google/gemini-2.0-flash-exp:free** [propriétaire/google]
   - WER médian: **0.729**
   - WER: min=0.257 | max=3.381 | moy=1.196
   - Coût: Gratuit
   - Pages testées: 15 | WER valides: 14

7. **openai/o1** [propriétaire/openai]
   - WER médian: **0.736**
   - WER: min=0.074 | max=1.299 | moy=0.718
   - Coût: $4.575 total | $0.305 moy (le plus cher)
   - Pages testées: 15 | WER valides: 14

8. **qwen/qwen2.5-vl-72b-instruct:free** [libre/qwen]
   - WER médian: **0.788**
   - WER: min=0.309 | max=50.303 | moy=6.863
   - Coût: Gratuit
   - Pages testées: 15 | WER valides: 14

9. **openai/gpt-4o-2024-11-20** [propriétaire/openai]
   - WER médian: **0.817**
   - WER: min=0.191 | max=41.203 | moy=4.017
   - Coût: $0.076 total | $0.005 moy
   - Pages testées: 15 | WER valides: 14

10. **FoNDUE-GD_v2_fr** [libre/kraken]
    - WER médian: **0.970**
    - WER: min=0.411 | max=4.952 | moy=1.491
    - Coût: Gratuit
    - Pages testées: 15 | WER valides: 14

### Modèles HTR spécialisés (Kraken)

11. **qwen/qwen-2-vl-7b-instruct** [libre/qwen] - WER médian: 1.000
12. **qwen/qwen-2-vl-72b-instruct** [libre/qwen] - WER médian: 1.000  
13. **McCATMuS_nfd_nofix_V1** [libre/kraken] - WER médian: 1.012
14. **catmus-print-fondue-large** [libre/kraken] - WER médian: 1.026
15. **ManuMcFondue** [libre/kraken] - WER médian: 1.030
16. **lectaurep_base** [libre/kraken] - WER médian: 1.070
17. **Gallicorpora+_best** [libre/kraken] - WER médian: 1.316

## Analyse comparative

### Modèles propriétaires vs libres
- **Propriétaires** (12 modèles): WER médian moyen = **1.066**
- **Libres** (14 modèles): WER médian moyen = **9.061**

Les modèles propriétaires dominent largement le classement, occupant 9 des 10 premières places.

### Coûts par éditeur
1. **OpenAI**: $6.527 total (3 modèles) - Performance excellente mais coûteux
2. **X-AI**: $0.888 total (2 modèles) - Performance variable
3. **Anthropic**: $0.277 total (2 modèles) - Excellent rapport qualité/prix
4. **Mistral**: $0.135 total (2 modèles) - Performance moyenne
5. **Meta**: $0.073 total (1 modèle) - Performance très faible
6. **Qwen**: $0.014 total (4 modèles) - Très économique
7. **Google**: $0.007 total (3 modèles) - Excellent rapport qualité/prix
8. **Amazon**: $0.006 total (1 modèle) - Performance correcte, très économique

### Modèles gratuits performants
1. **google/gemini-2.0-flash-thinking-exp:free** - WER: 0.711
2. **google/gemini-2.0-flash-exp:free** - WER: 0.729
3. **qwen/qwen2.5-vl-72b-instruct:free** - WER: 0.788

## Recommandations

### Pour la précision maximale
1. **openai/gpt-4.5-preview** (coûteux)
2. **anthropic/claude-3.5-sonnet** (bon compromis)
3. **google/gemini-2.0-flash-001** (très économique)

### Pour l'usage gratuit
1. **google/gemini-2.0-flash-thinking-exp:free**
2. **google/gemini-2.0-flash-exp:free**
3. **qwen/qwen2.5-vl-72b-instruct:free**

### Pour l'HTR spécialisé (open source)
1. **FoNDUE-GD_v2_fr**
2. **McCATMuS_nfd_nofix_V1**
3. **catmus-print-fondue-large**

## Métadonnées techniques

### Structure des fichiers JSON
Chaque résultat contient :
- `model`: nom du modèle
- `editeur`: fournisseur (anthropic, openai, google, etc.)
- `modele_type`: "propriétaire" ou "libre"
- `result`: transcription produite
- `model_info`: informations de coût et usage
- `timestamp`: horodatage

### Correspondance WER
Les données WER sont stockées dans `wer_data.json` avec une normalisation des noms de modèles (remplacement de "/" par "_" et ":" par "_").

## Données sources
- **Fichiers JSON**: 372 résultats dans `/résultats/`
- **Données WER**: `wer_data.json`
- **Transcriptions de référence**: `/transcriptions_de_référence/` (14 fichiers .md)
- **Images**: `/images/` (14 fichiers .png)