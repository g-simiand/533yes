| Modèle | Éditeur | Type de modèle | Nombre d'images | Coût total ($) | Coût moyen ($) | WER min | WER médian | WER max |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| gpt-4o-mini | inconnu | inconnu | 1 | 0.000225 | 0.000225 | 0.878 | 0.878 | 0.878 |
| gpt-4o | inconnu | inconnu | 1 | 0.008162 | 0.008162 | 0.297 | 0.297 | 0.297 |


Le taux d'erreur de mots (WER, Word Error Rate) est calculé en comparant la transcription générée à la transcription de référence. Pour ce faire, nous déterminons le nombre minimal d'opérations (substitutions, insertions, suppressions) nécessaires pour transformer la transcription générée en transcription de référence, puis nous divisons ce nombre par le nombre de mots de la transcription de référence. Ainsi, un WER de 0 indique une correspondance parfaite, tandis qu'un WER de 1 signifie que l'ensemble des mots diffère.

Les colonnes 'Éditeur' et 'Type de modèle' indiquent respectivement l'entité ayant développé le modèle et si le modèle est libre (open source) ou propriétaire.

Remarque : Si les coûts affichés sont nuls, vérifiez que vos fichiers de résultats incluent une clé 'cost' correcte. Le calcul des coûts repose sur la donnée renvoyée par les API et peut nécessiter un ajustement pour refléter les valeurs attendues.