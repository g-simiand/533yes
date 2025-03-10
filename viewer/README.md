# Visualiseur HTR - Guide d'utilisation

Le visualiseur HTR est un outil interactif qui vous permet de comparer les transcriptions générées par différents modèles pour les images du corpus 533yes.

## Comment utiliser le visualiseur

1. **Ouvrir le visualiseur** : Vous pouvez ouvrir le fichier `htr_viewer.html` directement dans votre navigateur web, ou utiliser le script `simple_server.py` pour démarrer un serveur local.

   ```bash
   python simple_server.py
   ```

   Puis accédez à `http://localhost:8000/htr_viewer.html` dans votre navigateur.

2. **Sélectionner une image** : Utilisez le menu déroulant "Sélectionner une image" pour choisir l'image manuscrite que vous souhaitez examiner.

3. **Sélectionner des modèles** : Cochez les cases correspondant aux modèles dont vous souhaitez voir les transcriptions. Vous pouvez sélectionner plusieurs modèles à la fois pour les comparer.

4. **Comparer les transcriptions** : Les transcriptions s'affichent sous l'image, avec la transcription de référence en haut. Les différences par rapport à la référence sont surlignées en rouge.

5. **Voir les statistiques** : Pour chaque modèle, le WER (Word Error Rate) est affiché à côté du nom du modèle, vous permettant d'évaluer rapidement sa performance.

## Fonctionnalités

- **Affichage côte à côte** : L'image et les transcriptions sont affichées côte à côte pour une comparaison facile.
- **Mise en évidence des différences** : Les mots qui diffèrent de la transcription de référence sont surlignés.
- **Filtrage par type de modèle** : Vous pouvez filtrer les modèles par type (propriétaire ou libre) pour faciliter la comparaison.
- **Tri des modèles** : Les modèles sont triés par performance (WER) pour identifier rapidement les meilleurs.

## Utilisation hors ligne

Le visualiseur est conçu pour fonctionner entièrement hors ligne. Toutes les données nécessaires sont chargées à partir de fichiers JSON locaux :

- `images_list.json` : Liste des images disponibles
- `models_list.json` : Liste des modèles et leurs métadonnées
- `wer_data.json` : Données de performance (WER) pour chaque combinaison modèle/image

## Dépannage

- **Images non affichées** : Vérifiez que le dossier `images` est présent et contient les fichiers d'images.
- **Transcriptions manquantes** : Vérifiez que le dossier `résultats` contient les fichiers de transcription au format attendu.
- **Erreurs JavaScript** : Ouvrez la console de votre navigateur (F12) pour voir les éventuelles erreurs.

## Version autonome

Une version autonome du visualiseur (`htr_viewer_standalone.html`) est également disponible. Cette version inclut toutes les données nécessaires directement dans le fichier HTML, ce qui la rend plus facile à partager mais plus volumineuse. 