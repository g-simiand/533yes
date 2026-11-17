# Passe HTR sur une page difficile — 7 septembre 2026

Source : `images/AN-284AP-4-doss 11_page_28.png` (numéro manuscrit : 2.). Page choisie pour son encre pâle, ses nombreuses ratures, ses ajouts interlinéaires et ses deux blocs marginaux.

- [Transcription Markdown](../résultats/AN-284AP-4-doss%2011_page_28_codex_session_2026-09-07.md)
- [Résultat JSON et provenance](../résultats/AN-284AP-4-doss%2011_page_28_codex_session_2026-09-07.json)

Lecture visuelle directe dans la session Codex, sur la page entière puis trois agrandissements. Aucun appel au pipeline API du benchmark. La transcription a été enregistrée avant consultation de la référence et n'a pas été corrigée à partir de celle-ci.

## Conventions et limites

Première passe partielle avec 44 marqueurs `[XXX]` pour les lectures incertaines ou illisibles. Les ratures lisibles sont entourées de `~~`. Les séparateurs horizontaux sont éditoriaux : ils distinguent le corps principal, la marge gauche supérieure et la marge gauche inférieure. Les ajouts interlinéaires sont placés près de leur point de lecture estimé ; leur raccordement et l'étendue exacte des ratures restent à vérifier.

La fin du corps principal permet notamment de proposer « notre exemple / influera sur le sort de l'Europe, et / par elle, sur les destinées du monde ». Ces lectures ne sont pas validées humainement.

## Comparaison avec la référence

WER brut du dépôt : **4,2143 (421,4 %)**. La référence est très lacunaire et ne contient que **42 mots après suppression des `[XXX]`**. La fonction `metrics.calculate_wer` compte donc de nombreuses lectures supplémentaires comme des insertions et conserve les marques Markdown de rature et de séparation. Un WER peut dépasser 100 % en présence d'insertions ; ici, il ne permet pas de conclure sur la justesse des passages déchiffrés.

La validation utile consiste à relire la transcription face à l'image et à compléter la référence. Les résultats historiques et la référence n'ont pas été modifiés.
