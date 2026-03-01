"""Génération de rapports et tableaux de résultats."""

import os
import json
import re
import datetime
from metrics import calculate_wer, clean_text_for_wer


def compute_median(values):
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0
    else:
        return sorted_vals[mid]


def generate_results_md_table(results_dir="résultats", reference_dir="transcriptions_de_référence", output_file="resultats_summary.md"):
    """
    Itère sur les fichiers dans le dossier `results_dir` et génère un tableau markdown dans `output_file`.
    Pour chaque fichier, le WER est calculé par rapport à la transcription de référence correspondante
    dans `reference_dir`. Le tableau généré comprendra pour chaque modèle :
      - le nom du modèle,
      - l'éditeur,
      - le type de modèle (libre/propriétaire),
      - le nombre d'images prises en compte,
      - le coût total ($) (somme des coûts de chaque image),
      - le coût moyen ($),
      - le WER min, médian et max.
    En dessous du tableau, un paragraphe explique le calcul du WER ainsi que la signification des colonnes 'éditeur'
    et 'type de modèle'.
    Les modèles sont triés par WER médian croissant (meilleure performance en premier).
    La date et l'heure de génération sont ajoutées en haut du fichier.
    """
    try:
        results_files = os.listdir(results_dir)
    except FileNotFoundError:
        print(f"Le dossier '{results_dir}' n'existe pas.")
        return

    # Dictionnaire pour regrouper les données par modèle
    data_by_model = {}

    for filename in results_files:
        result_file_path = os.path.join(results_dir, filename)
        
        # Vérifier que c'est bien un fichier JSON
        if not os.path.isfile(result_file_path) or not filename.endswith('.json'):
            continue

        # Extraire le nom de base de l'image (sans le modèle et l'extension)
        # Format typique: NOM_IMAGE_page_XX_modele.json
        # On cherche à extraire NOM_IMAGE_page_XX
        
        # Utiliser une expression régulière pour extraire le nom de base
        # Recherche un motif qui correspond à "page_XX" suivi d'un underscore et d'autres caractères
        match = re.search(r'(.*?page_\d+)_', filename)
        if match:
            base_name = match.group(1)
        else:
            # Si pas de correspondance, prendre tout avant .json
            base_name = filename.split('.')[0]
        
        # Construire le chemin du fichier de référence
        ref_file_path = os.path.join(reference_dir, base_name + ".md")
        
        if not os.path.exists(ref_file_path):
            print(f"Fichier de référence pour '{filename}' introuvable: '{ref_file_path}'. Ignoré.")
            continue

        # Lecture du fichier de résultat
        with open(result_file_path, "r", encoding="utf-8") as res_file:
            res_content = res_file.read().strip()
        
        # Parsing du contenu JSON pour extraire modèle, coût, éditeur, type de modèle et transcription
        try:
            res_json = json.loads(res_content)
            hypothesis = res_json.get("result", res_content)
            # Nouveauté : si le JSON contient "model_info", on l'utilise pour récupérer le modèle et le coût.
            if "model_info" in res_json:
                model_info = res_json["model_info"]
                model = model_info.get("id", res_json.get("model", "inconnu"))
                cost = model_info.get("total_cost", 0.0)
            else:
                model = res_json.get("model", "inconnu")
                cost = res_json.get("prix", 0.0)
            try:
                cost = float(cost)
            except (ValueError, TypeError):
                cost = 0.0
            editeur = res_json.get("editeur", "inconnu")
            modele_type = res_json.get("modele_type", "inconnu")
        except json.JSONDecodeError:
            hypothesis = res_content
            model = "inconnu"
            cost = 0.0
            editeur = "inconnu"
            modele_type = "inconnu"

        # Lecture du fichier de référence
        with open(ref_file_path, "r", encoding="utf-8") as ref_file:
            ref_content = ref_file.read().strip()
            try:
                ref_json = json.loads(ref_content)
                reference = ref_json.get("result", ref_content)
            except json.JSONDecodeError:
                reference = ref_content

        # Calcul du WER via la fonction calculate_wer
        wer = calculate_wer(reference, hypothesis)

        # Cumuler les résultats par modèle (on conserve aussi l'éditeur et le type de modèle)
        if model not in data_by_model:
            data_by_model[model] = {
                "wers": [],
                "costs": [],
                "editeur": editeur,
                "modele_type": modele_type
            }
        data_by_model[model]["wers"].append(wer)
        data_by_model[model]["costs"].append(cost)

    # Calcul des statistiques pour chaque modèle et préparation des données pour le tri
    model_stats = []
    for model, data in data_by_model.items():
        n_images = len(data["wers"])
        total_cost = sum(data["costs"])
        mean_cost = total_cost / n_images if n_images > 0 else 0.0
        wer_min = min(data["wers"]) if data["wers"] else 0.0
        wer_max = max(data["wers"]) if data["wers"] else 0.0
        wer_med = compute_median(data["wers"])
        
        model_stats.append({
            "model": model,
            "editeur": data["editeur"],
            "modele_type": data["modele_type"],
            "n_images": n_images,
            "total_cost": total_cost,
            "mean_cost": mean_cost,
            "wer_min": wer_min,
            "wer_med": wer_med,
            "wer_max": wer_max
        })
    
    # Tri des modèles par WER médian croissant (meilleure performance en premier)
    model_stats.sort(key=lambda x: x["wer_med"])

    # Obtenir la date et l'heure actuelles
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y %H:%M:%S")
    
    # Création du tableau Markdown avec l'en-tête comprenant les nouvelles colonnes
    table_rows = []
    table_rows.append(f"# Résultats de transcription - Généré le {date_str}\n")
    table_rows.append("| Modèle | Éditeur | Type de modèle | Nombre d'images | Coût total ($) | Coût moyen ($) | WER min | WER médian | WER max |")
    table_rows.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")

    # Ajout des lignes du tableau triées par performance
    for stat in model_stats:
        row = (
            f"| {stat['model']} | {stat['editeur']} | {stat['modele_type']} | {stat['n_images']} | "
            f"{stat['total_cost']:.6f} | {stat['mean_cost']:.6f} | {stat['wer_min']:.3f} | {stat['wer_med']:.3f} | {stat['wer_max']:.3f} |"
        )
        table_rows.append(row)

    # Ajout d'un paragraphe explicatif en dessous du tableau
    explanation = (
        "\n\n"
        "Le taux d'erreur de mots (WER, Word Error Rate) est calculé en comparant la transcription générée "
        "à la transcription de référence. Pour ce faire, nous déterminons le nombre minimal d'opérations "
        "(substitutions, insertions, suppressions) nécessaires pour transformer la transcription générée en transcription "
        "de référence, puis nous divisons ce nombre par le nombre de mots de la transcription de référence. Ainsi, un WER de 0 indique "
        "une correspondance parfaite, tandis qu'un WER de 1 signifie que l'ensemble des mots diffère.\n\n"
        "Les colonnes 'Éditeur' et 'Type de modèle' indiquent respectivement l'entité ayant développé le modèle et si le modèle est libre "
        "(open source) ou propriétaire.\n\n"
        "Remarque : Si les coûts affichés sont nuls, vérifiez que vos fichiers de résultats incluent une clé 'cost' correcte. "
        "Le calcul des coûts repose sur la donnée renvoyée par les API et peut nécessiter un ajustement pour refléter les valeurs attendues."
    )
    table_rows.append(explanation)

    # Écriture du tableau et du paragraphe dans le fichier de sortie
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write("\n".join(table_rows))
    
    print(f"Tableau résumé généré et sauvegardé dans '{output_file}'")