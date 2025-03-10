# Analyse des forces et faiblesses des modèles HTR

Ce document présente une analyse détaillée des performances des différents types de modèles testés dans le cadre du projet 533yes, en mettant en évidence leurs forces et faiblesses spécifiques.

## Résumé des performances par type de modèle

### Modèles propriétaires multimodaux récents

| Modèle | WER médian | Forces | Faiblesses |
|--------|------------|--------|------------|
| openai/gpt-4.5-preview | 0.556 | Excellente performance générale, meilleur WER médian | Coût élevé (0.125065$/image) |
| google/gemini-2.0-flash-thinking-exp:free | 0.694 | Très bonne performance, gratuit (version expérimentale) | Disponibilité limitée (expérimental), performance variable (WER max: 5.071) |
| google/gemini-2.0-flash-exp:free | 0.695 | Très bonne performance, gratuit (version expérimentale) | Disponibilité limitée (expérimental) |
| google/gemini-2.0-flash-001 | 0.711 | Très bonne performance, coût très faible (0.000473$/image) | Moins performant sur les documents complexes |
| anthropic/claude-3.5-sonnet | 0.714 | Excellente performance, coût modéré | Non testé sur toutes les images |
| openai/o1 | 0.722 | Performance constante sur tous les types de documents (WER max: 1.299) | Coût prohibitif (0.305001$/image) |

### Modèles libres multimodaux

| Modèle | WER médian | Forces | Faiblesses |
|--------|------------|--------|------------|
| qwen/qwen2.5-vl-72b-instruct:free | 0.719 | Gratuit, excellente performance | Performance très variable (WER max: 50.303) |
| mistralai/pixtral-large-2411 | 1.116 | Bonne performance, stabilité | Testé sur seulement 13 images, coût modéré |
| qwen/qwen-2-vl-72b-instruct | 1.000 | Coût très faible (0.000401$/image) | Performance variable (WER max: 26.182) |
| qwen/qwen-2-vl-7b-instruct | 1.000 | Coût très faible (0.000178$/image) | Performance constante mais moyenne |

### Modèles spécialisés HTR (Kraken)

| Modèle | WER médian | Forces | Faiblesses |
|--------|------------|--------|------------|
| FoNDUE-GD_v2_fr | 0.953 | Gratuit, spécialisé pour documents français | Moins performant sur certains styles d'écriture |
| McCATMuS_nfd_nofix_V1 | 0.969 | Gratuit, bonne performance sur documents spécifiques | Performance variable selon le type de document |
| catmus-print-fondue-large | 1.000 | Gratuit, bonne performance sur certains documents | Moins polyvalent que les modèles multimodaux |
| ManuMcFondue | 1.000 | Gratuit, bonne performance sur certains documents | Moins polyvalent que les modèles multimodaux |

## Analyse par cas d'usage

### Documents avec écriture claire et régulière

Les modèles les plus performants sur les documents avec une écriture claire et régulière sont:

1. **openai/o1** (WER: 0.074-0.722)
2. **google/gemini-2.0-flash-thinking-exp:free** (WER: 0.194-0.694)
3. **anthropic/claude-3.7-sonnet** (WER: 0.189-0.775)

Ces modèles excellent particulièrement sur les documents comme "AN-284AP-4-doss 10_page_30" et "AN-284AP-4-doss 13-Declar Volont Sieyes Condorcet-juin 1791-x4 correct_page_16".

### Documents avec écriture dense ou difficile

Pour les documents avec une écriture dense, des ratures ou une mise en page complexe:

1. **openai/o1** maintient une performance constante (WER: 0.787-1.299)
2. **openai/gpt-4.5-preview** offre de bonnes performances (WER: 0.337-3.571)
3. **google/gemini-2.0-flash-exp:free** a des performances variables (WER: 0.387-3.381)

Les modèles spécialisés Kraken montrent des faiblesses significatives sur ces documents complexes, avec des WER dépassant souvent 2.0.

### Pages blanches ou presque vides

La plupart des modèles identifient correctement les pages blanches (WER: 0.000), à l'exception de certains modèles comme:
- **meta-llama/llama-3.2-90b-vision-instruct** (testé sur peu d'images)
- **mistralai/pixtral-12b** (performance variable)

### Rapport coût/performance

En termes de rapport coût/performance:

1. **google/gemini-2.0-flash-thinking-exp:free** et **google/gemini-2.0-flash-exp:free** offrent le meilleur rapport (gratuits, WER médian: 0.694-0.695)
2. **qwen/qwen2.5-vl-72b-instruct:free** (gratuit, WER médian: 0.719)
3. **google/gemini-2.0-flash-001** (0.000473$/image, WER médian: 0.711)

Le modèle **openai/o1**, bien que très performant, présente un coût prohibitif (0.305001$/image) qui limite son utilisation à grande échelle.

## Cas particuliers notables

### Excellentes performances

- **openai/o1** sur "AN-284AP-4-doss 13-Declar Volont Sieyes Condorcet-juin 1791-x4 correct_page_16" (WER: 0.074)
- **google/gemini-2.0-flash-thinking-exp:free** sur "AN-284AP-4-doss 10_page_30" (WER: 0.194)
- **anthropic/claude-3.7-sonnet** sur "AN-284AP-4-doss 10_page_30" (WER: 0.189)

### Échecs notables

- **x-ai/grok-2-vision-1212** sur "AN-284AP-4-doss 11_page_12" (WER: 89.687)
- **openai/gpt-4o-mini** sur "AN-284AP-4-doss 10_page_20" (WER: 55.512)
- **x-ai/grok-vision-beta** sur "AN-284AP-4-doss 11_page_12" (WER: 51.358)
- **qwen/qwen2.5-vl-72b-instruct:free** sur "AN-284AP-4-doss 11_page_17" (WER: 50.303)

## Conclusion

Les résultats de ce benchmark montrent une claire supériorité des modèles multimodaux récents (GPT-4.5-preview, Gemini, O1) sur les approches traditionnelles pour la tâche HTR. Le modèle openai/gpt-4.5-preview se distingue particulièrement avec le meilleur WER médian (0.556).

Cependant, les modèles gratuits comme google/gemini-2.0-flash-thinking-exp:free et qwen/qwen2.5-vl-72b-instruct:free offrent un excellent rapport coût/performance, avec des WER médians respectifs de 0.694 et 0.719.

La variabilité des performances selon le type de document suggère qu'une approche hybride, combinant différents modèles selon les caractéristiques du document, pourrait offrir les meilleurs résultats pour des applications réelles.

Pour les projets avec des contraintes budgétaires, les modèles libres comme FoNDUE-GD_v2_fr ou les versions gratuites des modèles propriétaires représentent les meilleures options, offrant un bon équilibre entre performance et coût. 