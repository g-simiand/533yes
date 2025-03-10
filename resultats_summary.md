# Résultats de transcription - Généré le 06/03/2025 18:01:15

| Modèle | Éditeur | Type de modèle | Nombre d'images | Coût total ($) | Coût moyen ($) | WER min | WER médian | WER max |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| openai/gpt-4.5-preview | openai | propriétaire | 15 | 1.875975 | 0.125065 | 0.000 | 0.556 | 3.571 |
| google/gemini-2.0-flash-thinking-exp:free | google | propriétaire | 15 | 0.000000 | 0.000000 | 0.000 | 0.600 | 5.071 |
| google/gemini-2.0-flash-exp:free | google | propriétaire | 15 | 0.000000 | 0.000000 | 0.000 | 0.695 | 3.381 |
| google/gemini-2.0-flash-001 | google | propriétaire | 15 | 0.007100 | 0.000473 | 0.000 | 0.711 | 3.024 |
| openai/o1 | openai | propriétaire | 15 | 4.575015 | 0.305001 | 0.000 | 0.722 | 1.299 |
| openai/gpt-4o-2024-11-20 | openai | propriétaire | 15 | 0.075823 | 0.005055 | 0.191 | 0.834 | 41.203 |
| openai/gpt-4o-mini | openai | propriétaire | 15 | 0.029498 | 0.001967 | 0.000 | 0.858 | 55.512 |
| qwen/qwen2.5-vl-72b-instruct:free | qwen | libre | 15 | 0.000000 | 0.000000 | 0.309 | 0.858 | 50.303 |
| FoNDUE-GD_v2_fr | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 0.953 | 4.952 |
| McCATMuS_nfd_nofix_V1 | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 0.969 | 5.238 |
| catmus-print-fondue-large | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.000 | 4.048 |
| ManuMcFondue | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.000 | 5.143 |
| qwen/qwen-2-vl-72b-instruct | qwen | libre | 15 | 0.006013 | 0.000401 | 0.229 | 1.000 | 26.182 |
| qwen/qwen-2-vl-7b-instruct | qwen | libre | 15 | 0.002665 | 0.000178 | 0.000 | 1.000 | 1.000 |
| lectaurep_base | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.044 | 5.262 |
| amazon/nova-lite-v1 | amazon | propriétaire | 15 | 0.006260 | 0.000417 | 0.000 | 1.083 | 40.881 |
| Gallicorpora+_best | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.273 | 5.810 |
| x-ai/grok-2-vision-1212 | x-ai | propriétaire | 15 | 0.307780 | 0.020519 | 0.000 | 1.416 | 89.687 |
| x-ai/grok-vision-beta | x-ai | propriétaire | 15 | 0.579645 | 0.038643 | 0.925 | 2.439 | 51.358 |
| qwen/qwen-vl-plus:free | qwen | libre | 15 | 0.000000 | 0.000000 | 0.000 | 3.015 | 31.697 |
| qwen/qvq-72b-preview | qwen | libre | 15 | 0.077495 | 0.005166 | 1.000 | 7.618 | 42.091 |


Le taux d'erreur de mots (WER, Word Error Rate) est calculé en comparant la transcription générée à la transcription de référence. Pour ce faire, nous déterminons le nombre minimal d'opérations (substitutions, insertions, suppressions) nécessaires pour transformer la transcription générée en transcription de référence, puis nous divisons ce nombre par le nombre de mots de la transcription de référence. Ainsi, un WER de 0 indique une correspondance parfaite, tandis qu'un WER de 1 signifie que l'ensemble des mots diffère.

Les colonnes 'Éditeur' et 'Type de modèle' indiquent respectivement l'entité ayant développé le modèle et si le modèle est libre (open source) ou propriétaire.

Remarque : Si les coûts affichés sont nuls, vérifiez que vos fichiers de résultats incluent une clé 'cost' correcte. Le calcul des coûts repose sur la donnée renvoyée par les API et peut nécessiter un ajustement pour refléter les valeurs attendues.