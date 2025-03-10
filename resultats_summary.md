# Résultats de transcription - Généré le 10/03/2025 13:04:16

| Modèle | Éditeur | Type de modèle | Nombre d'images | Coût total ($) | Coût moyen ($) | WER min | WER médian | WER max |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| openai/gpt-4.5-preview | openai | propriétaire | 15 | 1.875975 | 0.125065 | 0.000 | 0.556 | 3.571 |
| google/gemini-2.0-flash-thinking-exp:free | google | propriétaire | 15 | 0.000000 | 0.000000 | 0.000 | 0.694 | 5.071 |
| google/gemini-2.0-flash-exp:free | google | propriétaire | 15 | 0.000000 | 0.000000 | 0.000 | 0.695 | 3.381 |
| google/gemini-2.0-flash-001 | google | propriétaire | 15 | 0.007100 | 0.000473 | 0.000 | 0.711 | 3.024 |
| anthropic/claude-3.5-sonnet | anthropic | propriétaire | 14 | 0.140376 | 0.010027 | 0.269 | 0.714 | 3.667 |
| qwen/qwen2.5-vl-72b-instruct:free | qwen | libre | 15 | 0.000000 | 0.000000 | 0.000 | 0.719 | 50.303 |
| openai/o1 | openai | propriétaire | 15 | 4.575015 | 0.305001 | 0.000 | 0.722 | 1.299 |
| anthropic/claude-3.7-sonnet | anthropic | propriétaire | 14 | 0.136602 | 0.009757 | 0.189 | 0.775 | 2.952 |
| openai/gpt-4o-2024-11-20 | openai | propriétaire | 15 | 0.075823 | 0.005055 | 0.191 | 0.834 | 41.203 |
| openai/gpt-4o-mini | openai | propriétaire | 15 | 0.029498 | 0.001967 | 0.000 | 0.858 | 55.512 |
| FoNDUE-GD_v2_fr | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 0.953 | 4.952 |
| McCATMuS_nfd_nofix_V1 | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 0.969 | 5.238 |
| catmus-print-fondue-large | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.000 | 4.048 |
| ManuMcFondue | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.000 | 5.143 |
| qwen/qwen-2-vl-72b-instruct | qwen | libre | 15 | 0.006013 | 0.000401 | 0.229 | 1.000 | 26.182 |
| qwen/qwen-2-vl-7b-instruct | qwen | libre | 15 | 0.002665 | 0.000178 | 0.000 | 1.000 | 1.000 |
| lectaurep_base | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.044 | 5.262 |
| amazon/nova-lite-v1 | amazon | propriétaire | 15 | 0.006260 | 0.000417 | 0.000 | 1.083 | 40.881 |
| mistralai/pixtral-large-2411 | mistralai | libre | 13 | 0.129090 | 0.009930 | 0.244 | 1.116 | 8.238 |
| Gallicorpora+_best | kraken | libre | 15 | 0.000000 | 0.000000 | 0.000 | 1.273 | 5.810 |
| x-ai/grok-2-vision-1212 | x-ai | propriétaire | 15 | 0.307780 | 0.020519 | 0.000 | 1.416 | 89.687 |
| x-ai/grok-vision-beta | x-ai | propriétaire | 15 | 0.579645 | 0.038643 | 0.925 | 2.439 | 51.358 |
| qwen/qwen-vl-plus:free | qwen | libre | 15 | 0.000000 | 0.000000 | 0.000 | 3.015 | 31.697 |
| mistralai/pixtral-12b | mistralai | libre | 13 | 0.006006 | 0.000462 | 0.514 | 4.523 | 32.515 |
| qwen/qvq-72b-preview | qwen | libre | 15 | 0.077495 | 0.005166 | 0.643 | 6.280 | 42.091 |
| meta-llama/llama-3.2-90b-vision-instruct | meta-llama | libre | 3 | 0.072842 | 0.024281 | 1.017 | 100.582 | 163.241 |


Le taux d'erreur de mots (WER, Word Error Rate) est calculé en comparant la transcription générée à la transcription de référence. Pour ce faire, nous déterminons le nombre minimal d'opérations (substitutions, insertions, suppressions) nécessaires pour transformer la transcription générée en transcription de référence, puis nous divisons ce nombre par le nombre de mots de la transcription de référence. Ainsi, un WER de 0 indique une correspondance parfaite, tandis qu'un WER de 1 signifie que l'ensemble des mots diffère.

Les colonnes 'Éditeur' et 'Type de modèle' indiquent respectivement l'entité ayant développé le modèle et si le modèle est libre (open source) ou propriétaire.

Remarque : Si les coûts affichés sont nuls, vérifiez que vos fichiers de résultats incluent une clé 'cost' correcte. Le calcul des coûts repose sur la donnée renvoyée par les API et peut nécessiter un ajustement pour refléter les valeurs attendues.