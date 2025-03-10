#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour générer un tableau comparatif des performances des modèles HTR par page.
Ce script analyse les résultats dans le dossier 'résultats' et génère un tableau
au format Markdown et HTML montrant le WER pour chaque modèle et chaque image.
"""

import os
import json
import re
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import sys

# Add the parent directory to sys.path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils import calculate_wer

# Chemins des dossiers
RESULTS_DIR = Path("./résultats")
REFERENCE_DIR = Path("./transcriptions_de_référence")
OUTPUT_DIR = Path("./rapports")

# Créer le dossier de sortie s'il n'existe pas
OUTPUT_DIR.mkdir(exist_ok=True)

# Dictionnaire des descriptions de pages
# Clé: nom de l'image, Valeur: description courte
PAGE_DESCRIPTIONS = {
    "AN-284AP-18-fasc ms extr Moniteur carriere Sieyes-1789-1799_page_15": "Extrait du Moniteur, carrière de Sieyès (1789-1799)",
    "AN-284AP-18-fasc ms extr Moniteur carriere Sieyes-1789-1799_page_4": "Début du document sur Sieyès, contexte révolutionnaire",
    "AN-284AP-4-doss 10_page_18": "Brouillon sans ratures",
    "AN-284AP-4-doss 10_page_20": "Brouillon sans ratures",
    "AN-284AP-4-doss 11_page_12": "Brouillon sans ratures",
    "AN-284AP-4-doss 11_page_17": "Brouillon, écriture rapide",
    "AN-284AP-4-doss 11_page_28": "Brouillon, deux colonnes, page barrée",
    "AN-284AP-4-doss 11_page_29": "Brouillon, des rayures",
    "AN-284AP-4-doss 11_page_36": "Page blanche",
    "AN-284AP-4-doss 14_page_39": "Brouillon",
    "AN-284AP-4-doss 13-Declar Volont Sieyes Condorcet-juin 1791-x4 correct_page_12": "Brouillon, barre verticale, deux § distincts",
    "AN-284AP-4-doss 13-Declar Volont Sieyes Condorcet-juin 1791-x4 correct_page_16": "Double page imprimée, annotations manuscrites en bas de page",
    "AN-284AP-4-doss 14_page_9": "Brouillon, biffure, paragraphes et titres",
    "AN-284AP-4-doss 14_page_27": "Ecriture dans le seul quart Ne, écriture rapide",
    "AN-284AP-18-fasc ms extr Moniteur carriere Sieyes-1789-1799_page_4": "Extrait du Moniteur, belle écriture, deux colonnes",
    "AN-284AP-18-fasc ms extr Moniteur carriere Sieyes-1789-1799_page_15": "Extrait du Moniteur, belle écriture, deux colonnes, un § centré",
    "AN-284AP-4-doss 10_page_30": "Lettre, écriture nette",
}

# Description par défaut pour les pages sans description spécifique
DEFAULT_PAGE_DESCRIPTION = "Document d'archives historiques"

def clean_text(text):
    """
    Nettoie le texte en supprimant les marqueurs [XXX] et les balises markdown.
    """
    # Supprimer les marqueurs [XXX]
    text = re.sub(r'\[XXX\]', '', text)
    
    # Supprimer les balises markdown au début et à la fin
    text = re.sub(r'^```.*?\n', '', text)
    text = re.sub(r'\n```$', '', text)
    
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_model_info(model_id):
    """
    Extrait les informations du modèle à partir de son ID.
    """
    # Exemple simple - dans une version complète, cela pourrait être chargé depuis un fichier de configuration
    if "amazon" in model_id:
        return {"editeur": "Amazon", "type": "propriétaire"}
    elif "openai" in model_id or "gpt" in model_id:
        return {"editeur": "OpenAI", "type": "propriétaire"}
    elif "google" in model_id or "gemini" in model_id:
        return {"editeur": "Google", "type": "propriétaire"}
    elif "anthropic" in model_id or "claude" in model_id:
        return {"editeur": "Anthropic", "type": "propriétaire"}
    elif "mistral" in model_id:
        return {"editeur": "Mistral AI", "type": "libre"}
    elif "meta" in model_id or "llama" in model_id:
        return {"editeur": "Meta", "type": "libre"}
    elif "kraken" in model_id:
        return {"editeur": "Kraken", "type": "libre"}
    else:
        return {"editeur": "Autre", "type": "libre"}

def calculate_wer_for_file(result_file, reference_dir):
    """
    Calcule le WER pour un fichier de résultat donné.
    """
    try:
        # Charger le résultat
        with open(result_file, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        
        # Extraire le nom de l'image
        image_name = Path(result_data.get('image', '')).stem
        
        # Liste des images à exclure du calcul WER (tout en les gardant dans le corpus)
        excluded_from_wer = ["AN-284AP-4-doss 11_page_36"]
        
        # Si l'image est dans la liste des exclusions, on retourne -1 comme valeur WER spéciale
        if image_name in excluded_from_wer:
            return {
                'image': image_name,
                'model': Path(result_file).stem.replace(f"{image_name}_", ""),
                'wer': -1
            }
        
        # Trouver le fichier de référence correspondant
        reference_file = reference_dir / f"{image_name}.md"
        
        if not reference_file.exists():
            print(f"Fichier de référence non trouvé pour {image_name}")
            return None
        
        # Charger la référence
        with open(reference_file, 'r', encoding='utf-8') as f:
            reference_text = f.read()
        
        # Nettoyer les textes
        clean_reference = clean_text(reference_text)
        clean_result = clean_text(result_data.get('result', ''))
        
        # Calculer le WER
        wer = calculate_wer(clean_reference, clean_result)
        
        return {
            'image': image_name,
            'model': Path(result_file).stem.replace(f"{image_name}_", ""),
            'wer': wer
        }
    
    except Exception as e:
        print(f"Erreur lors du traitement de {result_file}: {str(e)}")
        return None

def generate_performance_table():
    """
    Génère un tableau comparatif des performances des modèles par page.
    """
    # Collecter tous les fichiers de résultats
    result_files = list(RESULTS_DIR.glob("*.json"))
    
    if not result_files:
        print("Aucun fichier de résultat trouvé.")
        return
    
    # Calculer le WER pour chaque fichier
    results = []
    for result_file in result_files:
        result = calculate_wer_for_file(result_file, REFERENCE_DIR)
        if result:
            results.append(result)
    
    if not results:
        print("Aucun résultat valide trouvé.")
        return
    
    # Créer un DataFrame
    df = pd.DataFrame(results)
    
    # Pivoter le DataFrame pour avoir les modèles en colonnes et les images en lignes
    pivot_df = df.pivot(index='image', columns='model', values='wer')
    
    # Trier les colonnes par WER moyen (du meilleur au pire)
    # Exclure les valeurs -1 (images exclues du calcul WER) du calcul de la moyenne
    model_avg_wer = pivot_df.replace(-1, float('nan')).mean().sort_values()
    pivot_df = pivot_df[model_avg_wer.index]
    
    # Ajouter une ligne pour le WER moyen
    # Exclure les valeurs -1 (images exclues du calcul WER) du calcul de la moyenne
    pivot_df.loc['Moyenne'] = pivot_df.replace(-1, float('nan')).mean()
    
    # Créer un DataFrame pour les descriptions de pages
    descriptions = {}
    for image in pivot_df.index:
        if image == 'Moyenne':
            descriptions[image] = ""
        else:
            descriptions[image] = PAGE_DESCRIPTIONS.get(image, DEFAULT_PAGE_DESCRIPTION)
    
    # Formater les valeurs WER
    formatted_df = pivot_df.applymap(lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A")
    
    # Obtenir la date et l'heure actuelles
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y %H:%M:%S")
    
    # Générer le tableau markdown
    md_content = f"# Performance des modèles HTR par page (WER) - Généré le {now.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
    md_content += "Plus le WER est bas, meilleure est la performance.\n\n"
    
    # Créer le tableau markdown
    md_content += "| Image | Description |"
    for model in pivot_df.columns:
        md_content += f" {model} |"
    md_content += "\n"
    
    md_content += "|:-----|:-----------|"
    for _ in pivot_df.columns:
        md_content += "-----:|"
    md_content += "\n"
    
    # Ajouter les lignes du tableau
    for image in pivot_df.index:
        description = descriptions.get(image, "Document d'archives historiques")
        md_content += f"| {image} | {description} |"
        
        for model in pivot_df.columns:
            value = pivot_df.loc[image, model]
            if pd.isna(value):
                md_content += " N/A |"
            elif value == -1:
                md_content += " Excluded |"
            else:
                md_content += f" {value:.3f} |"
        md_content += "\n"
    
    # Écrire le tableau markdown
    with open(OUTPUT_DIR / "performance_par_page.md", 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # Générer le tableau HTML avec mise en forme conditionnelle
    html_df = pivot_df.copy()
    
    # Créer une fonction pour appliquer une couleur de fond basée sur la valeur WER
    def color_wer(val):
        """
        Applique une couleur de fond en fonction de la valeur WER.
        """
        if pd.isna(val):
            return 'background-color: #f8f8f8; color: #888888'
        
        if val == -1:
            return 'background-color: #e8e8e8; color: #888888'
            
        if val < 0.5:
            return 'background-color: #c6efce; color: #006100'
        elif val < 1.0:
            return 'background-color: #ffeb9c; color: #9c5700'
        else:
            return 'background-color: #ffc7ce; color: #9c0006'
    
    # Appliquer la mise en forme conditionnelle
    styled_df = html_df.style.map(color_wer).format(lambda x: "Excluded" if x == -1 else "{:.3f}".format(x) if not pd.isna(x) else "N/A")
    
    # Créer un DataFrame avec les descriptions
    desc_df = pd.DataFrame({"Description": descriptions}, index=pivot_df.index)
    
    # Concaténer les DataFrames
    display_df = pd.concat([desc_df, html_df], axis=1)
    styled_display_df = display_df.style.map(lambda x: color_wer(x) if not isinstance(x, str) else "", subset=html_df.columns).format("{:.3f}", subset=html_df.columns)
    
    # Générer le HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>533yes - Performance des modèles HTR par page</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ padding: 20px; }}
            .table-container {{ overflow-x: auto; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 8px; text-align: center; }}
            th {{ position: sticky; top: 0; background-color: #f8f9fa; }}
            td:nth-child(2) {{ text-align: left; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">Performance des modèles HTR par page (WER)</h1>
            <p>Généré le {date_str}</p>
            <p>Plus le WER est bas, meilleure est la performance.</p>
            
            <div class="table-container">
                {styled_display_df.to_html(classes='table table-bordered')}
            </div>
            
            <div class="mt-4">
                <h3>Légende</h3>
                <div class="d-flex flex-wrap">
                    <div class="me-4 mb-2">
                        <span style="display: inline-block; width: 20px; height: 20px; background-color: #d4edda; margin-right: 5px;"></span>
                        Très bon (WER < 0.1)
                    </div>
                    <div class="me-4 mb-2">
                        <span style="display: inline-block; width: 20px; height: 20px; background-color: #d1ecf1; margin-right: 5px;"></span>
                        Bon (WER < 0.2)
                    </div>
                    <div class="me-4 mb-2">
                        <span style="display: inline-block; width: 20px; height: 20px; background-color: #fff3cd; margin-right: 5px;"></span>
                        Moyen (WER < 0.3)
                    </div>
                    <div class="me-4 mb-2">
                        <span style="display: inline-block; width: 20px; height: 20px; background-color: #ffe5d0; margin-right: 5px;"></span>
                        Mauvais (WER < 0.5)
                    </div>
                    <div class="me-4 mb-2">
                        <span style="display: inline-block; width: 20px; height: 20px; background-color: #f8d7da; margin-right: 5px;"></span>
                        Très mauvais (WER ≥ 0.5)
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(OUTPUT_DIR / "performance_par_page.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Tableaux générés dans le dossier {OUTPUT_DIR}")
    
    # Retourner le DataFrame pour une utilisation ultérieure
    return pivot_df

if __name__ == "__main__":
    generate_performance_table() 