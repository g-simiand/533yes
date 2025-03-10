# Analyse des forces et faiblesses des modèles HTR

Ce document présente une analyse détaillée des performances des différents types de modèles testés dans le cadre du projet 533yes, en mettant en évidence leurs forces et faiblesses spécifiques.

## Résumé des performances par type de modèle

### Modèles propriétaires multimodaux récents

| Modèle | WER médian | Forces | Faiblesses |
|--------|------------|--------|------------|
| google/gemini-2.0-flash-thinking-exp | 0.600 | Excellente performance générale, gratuit (version expérimentale) | Disponibilité limitée (expérimental) |
| google/gemini-2.0-flash-001 | 0.711 | Très bonne performance, coût très faible (0.000473$/image) | Moins performant sur les documents complexes |
| openai/o1 | 0.722 | Performance constante sur tous les types de documents | Coût très élevé (0.305001$/image) |
| openai/gpt-4o-2024-11-20 | 0.834 | Bonne performance générale | Performance très variable (WER max: 41.203) |

### Modèles libres multimodaux

| Modèle | WER médian | Forces | Faiblesses |
|--------|------------|--------|------------|
| mistralai/pixtral-large-2411 | 0.928 | Bonne performance, stabilité | Testé sur seulement 5 images |
| meta-llama/llama-3.2-90b-vision-instruct | 0.980 | Performance stable (WER max: 1.310) | Coût modéré, performances légèrement inférieures |
| mistralai/pixtral-12b | 1.000 | Coût très faible, capable de parfaite reconnaissance sur certaines images | Performance moyenne |

### Modèles spécialisés HTR (Kraken)

| Modèle | WER médian | Forces | Faiblesses |
|--------|------------|--------|------------|
| FoNDUE-GD_v2_fr | 0.953 | Gratuit, spécialisé pour documents français | Moins performant sur certains styles d'écriture |
| McCATMuS_nfd_nofix_V1 | 0.969 | Gratuit, bonne performance sur documents spécifiques | Performance variable selon le type de document |
| catmus-print-fondue-large | 1.000 | Gratuit, parfait sur certains documents | Moins polyvalent que les modèles multimodaux |

## Analyse par cas d'usage

### Documents avec écriture claire et régulière

Les modèles les plus performants sur les documents avec une écriture claire et régulière sont:

1. **google/gemini-2.0-flash-thinking-exp** (WER: 0.194-0.600)
2. **openai/o1** (WER: 0.074-0.722)
3. **FoNDUE-GD_v2_fr** (WER: 0.411-0.667)

Ces modèles excellent particulièrement sur les documents comme "AN-284AP-4-doss 10_page_30" et "AN-284AP-4-doss 13-Declar Volont Sieyes Condorcet-juin 1791-x4 correct_page_16".

### Documents avec écriture dense ou difficile

Pour les documents avec une écriture dense, des ratures ou une mise en page complexe:

1. **openai/o1** maintient une performance constante (WER: 0.787-1.299)
2. **mistralai/pixtral-large-2411** offre une bonne stabilité (WER: 0.928-1.028)
3. **google/gemini-2.0-flash-001** a des performances variables (WER: 0.354-3.024)

Les modèles spécialisés Kraken montrent des faiblesses significatives sur ces documents complexes, avec des WER dépassant souvent 2.0.

### Pages blanches ou presque vides

Presque tous les modèles identifient correctement les pages blanches (WER: 0.000), à l'exception de certains modèles comme:
- **meta-llama/llama-3.2-90b-vision-instruct** (WER: 1.000)
- **openai/gpt-4o-2024-11-20** (WER: 1.000)
- **x-ai/grok-vision-beta** (WER: 1.000)

### Rapport coût/performance

En termes de rapport coût/performance:

1. **google/gemini-2.0-flash-thinking-exp** offre le meilleur rapport (gratuit, WER médian: 0.600)
2. **FoNDUE-GD_v2_fr** et autres modèles Kraken (gratuits, WER médian: 0.953-1.044)
3. **google/gemini-2.0-flash-001** (0.000473$/image, WER médian: 0.711)

Le modèle **openai/o1**, bien que très performant, présente un coût prohibitif (0.305001$/image) qui limite son utilisation à grande échelle.

## Cas particuliers notables

### Excellentes performances

- **openai/o1** sur "AN-284AP-4-doss 13-Declar Volont Sieyes Condorcet-juin 1791-x4 correct_page_16" (WER: 0.074)
- **google/gemini-2.0-flash-thinking-exp** sur "AN-284AP-4-doss 10_page_30" (WER: 0.194)

### Échecs notables

- **x-ai/grok-2-vision-1212** sur "AN-284AP-4-doss 11_page_12" (WER: 89.687)
- **openai/gpt-4o-mini** sur "AN-284AP-4-doss 10_page_20" (WER: 55.512)
- **x-ai/grok-vision-beta** sur "AN-284AP-4-doss 11_page_12" (WER: 51.358)

## Conclusion

Les résultats de ce benchmark montrent une claire supériorité des modèles multimodaux récents (Gemini, O1) sur les approches traditionnelles pour la tâche HTR. Cependant, les modèles spécialisés comme FoNDUE-GD_v2_fr offrent un excellent compromis coût/performance pour des applications à grande échelle.

La variabilité des performances selon le type de document suggère qu'une approche hybride, combinant différents modèles selon les caractéristiques du document, pourrait offrir les meilleurs résultats pour des applications réelles.

Pour les projets avec des contraintes budgétaires, les modèles libres comme FoNDUE-GD_v2_fr ou google/gemini-2.0-flash-thinking-exp (tant qu'il reste gratuit) représentent les meilleures options. 