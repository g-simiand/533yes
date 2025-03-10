#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour générer les fichiers JSON nécessaires au fonctionnement du viewer HTML.
Ce script crée deux fichiers :
- images_list.json : liste des images disponibles dans le dossier 'images'
- models_list.json : liste des modèles utilisés dans les résultats
"""

import os
import json
import re
from pathlib import Path

# Chemins des dossiers
IMAGES_DIR = Path("./images")
RESULTS_DIR = Path("./résultats")

def generate_images_list():
    """
    Génère un fichier JSON contenant la liste des images disponibles.
    """
    if not IMAGES_DIR.exists():
        print(f"Le dossier {IMAGES_DIR} n'existe pas.")
        return False
    
    # Récupérer la liste des images
    images = [f.name for f in IMAGES_DIR.glob("*.png")]
    images.extend([f.name for f in IMAGES_DIR.glob("*.jpg")])
    
    # Trier les images par nom
    images.sort()
    
    # Écrire le fichier JSON
    with open("images_list.json", "w", encoding="utf-8") as f:
        json.dump(images, f, ensure_ascii=False, indent=2)
    
    print(f"Fichier images_list.json généré avec {len(images)} images.")
    return True

def get_model_type(model_id):
    """
    Détermine le type de modèle (libre ou propriétaire) en fonction de son ID.
    """
    proprietary_keywords = [
        "openai", "gpt", "anthropic", "claude", "google", "gemini", 
        "amazon", "nova", "x-ai", "grok"
    ]
    
    for keyword in proprietary_keywords:
        if keyword.lower() in model_id.lower():
            return "propriétaire"
    
    return "libre"

def get_model_name(model_id):
    """
    Génère un nom lisible pour le modèle à partir de son ID.
    """
    # Remplacer les tirets et underscores par des espaces
    name = model_id.replace("-", " ").replace("_", " ")
    
    # Capitaliser les mots
    name = " ".join(word.capitalize() for word in name.split())
    
    # Cas spéciaux
    name_mapping = {
        "openai gpt 4o": "GPT-4o",
        "openai gpt 4o mini": "GPT-4o Mini",
        "anthropic claude 3 5 sonnet": "Claude 3.5 Sonnet",
        "anthropic claude 3 7 sonnet": "Claude 3.7 Sonnet",
        "google gemini 2 0 flash": "Gemini 2.0 Flash",
        "mistralai pixtral": "Mistral Pixtral",
        "meta llama": "Meta Llama",
        "qwen vl": "Qwen VL"
    }
    
    for pattern, replacement in name_mapping.items():
        if pattern in name.lower():
            name = name.replace(pattern, replacement, 1)
    
    return name

def generate_models_list():
    """
    Génère un fichier JSON contenant la liste des modèles utilisés dans les résultats.
    """
    if not RESULTS_DIR.exists():
        print(f"Le dossier {RESULTS_DIR} n'existe pas.")
        return False
    
    # Récupérer tous les fichiers de résultats
    result_files = list(RESULTS_DIR.glob("*.json"))
    
    # Extraire les IDs de modèles uniques
    model_ids = set()
    for file in result_files:
        # Le format du nom de fichier est : image_modelid.json
        parts = file.stem.split("_")
        if len(parts) >= 2:
            # Le dernier élément est l'ID du modèle
            model_id = parts[-1]
            model_ids.add(model_id)
    
    # Créer la liste des modèles
    models = []
    for model_id in sorted(model_ids):
        model_type = get_model_type(model_id)
        model_name = get_model_name(model_id)
        
        models.append({
            "id": model_id,
            "name": model_name,
            "type": model_type
        })
    
    # Trier les modèles : d'abord par type, puis par nom
    models.sort(key=lambda m: (0 if m["type"] == "libre" else 1, m["name"]))
    
    # Écrire le fichier JSON
    with open("models_list.json", "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)
    
    print(f"Fichier models_list.json généré avec {len(models)} modèles.")
    return True

def generate_wer_data():
    """
    Génère un fichier JSON contenant les valeurs WER pour chaque combinaison image/modèle.
    Ce fichier sera utilisé pour afficher les badges WER dans le viewer.
    """
    import sys
    from pathlib import Path
    
    # Add the parent directory to sys.path to import utils
    sys.path.append(str(Path(__file__).parent.parent))
    from utils import calculate_wer
    
    # Vérifier si le dossier des transcriptions de référence existe
    reference_dir = Path("./transcriptions_de_référence")
    if not reference_dir.exists():
        print(f"Le dossier {reference_dir} n'existe pas.")
        return False
    
    # Récupérer tous les fichiers de résultats
    result_files = list(RESULTS_DIR.glob("*.json"))
    
    # Dictionnaire pour stocker les valeurs WER
    wer_data = {}
    
    # Liste des images à exclure du calcul WER (tout en les gardant dans le corpus)
    excluded_from_wer = ["AN-284AP-4-doss 11_page_36"]
    
    # Fonction pour nettoyer le texte
    def clean_text(text):
        # Supprimer les marqueurs [XXX]
        text = re.sub(r'\[XXX\]', '', text)
        
        # Supprimer les balises markdown au début et à la fin
        text = re.sub(r'^```(?:markdown)?.*?\n', '', text)
        text = re.sub(r'\n```$', '', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    # Calculer le WER pour chaque fichier de résultat
    for result_file in result_files:
        try:
            # Charger le résultat
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # Extraire le nom de l'image et l'ID du modèle
            image_name = Path(result_data.get('image', '')).stem
            model_id = result_file.stem.replace(f"{image_name}_", "")
            
            # Si l'image est dans la liste des exclusions, on l'ajoute au dictionnaire mais on ne calcule pas son WER
            if image_name in excluded_from_wer:
                if image_name not in wer_data:
                    wer_data[image_name] = {}
                # On met une valeur spéciale pour indiquer que cette image est exclue du calcul WER
                wer_data[image_name][model_id] = -1
                continue
            
            # Trouver le fichier de référence correspondant
            reference_file = reference_dir / f"{image_name}.md"
            
            if not reference_file.exists():
                print(f"Fichier de référence non trouvé pour {image_name}")
                continue
            
            # Charger la référence
            with open(reference_file, 'r', encoding='utf-8') as f:
                reference_text = f.read()
            
            # Nettoyer les textes
            clean_reference = clean_text(reference_text)
            clean_result = clean_text(result_data.get('result', ''))
            
            # Calculer le WER
            wer = calculate_wer(clean_reference, clean_result)
            
            # Stocker la valeur WER
            if image_name not in wer_data:
                wer_data[image_name] = {}
            
            wer_data[image_name][model_id] = wer
            
        except Exception as e:
            print(f"Erreur lors du traitement de {result_file}: {str(e)}")
    
    # Écrire le fichier JSON
    with open("wer_data.json", "w", encoding="utf-8") as f:
        json.dump(wer_data, f, ensure_ascii=False, indent=2)
    
    print(f"Fichier wer_data.json généré avec des données pour {len(wer_data)} images.")
    return True

if __name__ == "__main__":
    print("Génération des fichiers pour le viewer HTML...")
    
    success_images = generate_images_list()
    success_models = generate_models_list()
    
    try:
        success_wer = generate_wer_data()
    except ImportError:
        print("Impossible de générer le fichier wer_data.json : module utils non trouvé.")
        success_wer = False
    
    if success_images and success_models:
        print("\nLes fichiers ont été générés avec succès.")
        print("Pour utiliser le viewer sur GitHub Pages :")
        print("1. Ajoutez ces fichiers à votre dépôt GitHub :")
        print("   - images_list.json")
        print("   - models_list.json")
        if success_wer:
            print("   - wer_data.json")
        print("2. Activez GitHub Pages dans les paramètres de votre dépôt.")
        print("3. Le viewer sera accessible à l'adresse : https://[votre-nom-utilisateur].github.io/[nom-depot]/htr_viewer.html")
    else:
        print("\nDes erreurs se sont produites lors de la génération des fichiers.") 