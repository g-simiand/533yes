# Analyse comparative : Gemini 2.0 Flash dans le benchmark HTR

## Vue d'ensemble

**Modèle analysé** : google/gemini-2.0-flash-001

- **WER médian** : 0.711
- **WER moyen** : 1.089
- **Écart-type** : 0.920
- **Min/Max** : 0.000 / 3.024
- **Quartiles (Q1/Q3)** : 0.451 / 1.769
- **Pages évaluées** : 15

## Position dans le classement

- **Rang** : 2 / 22
- **Percentile** : Top 9.1%

## Top 5 des modèles plus performants

| Modèle | WER médian | WER moyen |
|--------|------------|-----------|
| google_gemini-2.0-flash-thinking-exp_free | 0.600 | 1.240 |

## Modèles aux performances similaires (±10%)

| Modèle | WER médian | WER moyen |
|--------|------------|-----------|
| openai_o1 | 0.722 | 0.670 |

## Analyse par catégorie

### Proprietary
- Nombre de modèles : 16
- WER médian de la catégorie : 0.990
- Meilleur : google_gemini-2.0-flash-thinking-exp_free (WER: 0.600)
- Moins bon : qwen_qvq-72b-preview (WER: 7.618)

### Kraken Models
- Nombre de modèles : 6
- WER médian de la catégorie : 1.000
- Meilleur : FoNDUE-GD_v2_fr (WER: 0.953)
- Moins bon : Gallicorpora+_best (WER: 1.273)

## Top 10 des modèles du benchmark

| Rang | Modèle | WER médian | WER moyen | Écart-type |
|------|--------|------------|-----------|------------|
| 1 | google_gemini-2.0-flash-thinking-exp_free | 0.600 | 1.240 | 1.291 |
| 2 | google_gemini-2.0-flash-001 | 0.711 | 1.089 | 0.920 |
| 3 | openai_o1 | 0.722 | 0.670 | 0.340 |
| 4 | openai_gpt-4o-2024-11-20 | 0.834 | 3.816 | 10.025 |
| 5 | qwen_qwen2.5-vl-72b-instruct_free | 0.858 | 6.472 | 12.864 |
| 6 | openai_gpt-4o-mini | 0.858 | 10.530 | 16.530 |
| 7 | mistralai_pixtral-large-2411 | 0.928 | 0.781 | 0.288 |
| 8 | FoNDUE-GD_v2_fr | 0.953 | 1.391 | 1.240 |
| 9 | McCATMuS_nfd_nofix_V1 | 0.969 | 1.523 | 1.284 |
| 10 | meta-llama_llama-3.2-90b-vision-instruct | 0.980 | 1.002 | 0.085 |

## Insights clés

1. **Position compétitive** : Gemini 2.0 Flash se positionne parmi les meilleurs modèles avec un WER médian de 0.711
2. **Performance vs propriétaires** : Surpasse la médiane des modèles propriétaires (0.990)
3. **Stabilité** : Performance plus stable que la moyenne (σ=0.920 vs moyenne=6.254)

## Recommandations d'usage

- ✅ **Adapté pour** : Transcription production avec révision minimale