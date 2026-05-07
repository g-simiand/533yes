#!/usr/bin/env python3
"""
Script de comparaison détaillée des résultats Gemini 2.0 Flash avec les autres modèles.
Analyse le WER médian de 0.694 et positionne Gemini 2.0 Flash dans le benchmark.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


def load_wer_data(file_path: Path) -> Dict:
    """Charge les données WER depuis le fichier JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_model_statistics(wer_data: Dict) -> pd.DataFrame:
    """Calcule les statistiques WER pour chaque modèle."""
    models_scores = {}
    
    for page, scores in wer_data.items():
        for model, score in scores.items():
            if score >= 0:  # Ignorer les scores -1 (échecs)
                if model not in models_scores:
                    models_scores[model] = []
                models_scores[model].append(score)
    
    # Calculer les statistiques
    stats = []
    for model, scores in models_scores.items():
        if scores:
            stats.append({
                'model': model,
                'mean': np.mean(scores),
                'median': np.median(scores),
                'std': np.std(scores),
                'min': np.min(scores),
                'max': np.max(scores),
                'q25': np.percentile(scores, 25),
                'q75': np.percentile(scores, 75),
                'n_pages': len(scores)
            })
    
    df = pd.DataFrame(stats)
    df = df.sort_values('median').reset_index(drop=True)
    df['rank'] = df.index + 1
    return df


def analyze_gemini_flash(df: pd.DataFrame, target_model: str = "google_gemini-2.0-flash-001") -> Dict:
    """Analyse détaillée de Gemini 2.0 Flash."""
    if target_model not in df['model'].values:
        return {"error": f"Modèle {target_model} non trouvé dans les données"}
    
    gemini_stats = df[df['model'] == target_model].iloc[0]
    total_models = len(df)
    
    # Trouver les modèles performants similaires (±10% du WER médian)
    median_threshold = 0.1
    similar_models = df[
        (df['median'] >= gemini_stats['median'] * (1 - median_threshold)) &
        (df['median'] <= gemini_stats['median'] * (1 + median_threshold)) &
        (df['model'] != target_model)
    ]
    
    # Modèles meilleurs et moins bons
    better_models = df[df['median'] < gemini_stats['median']]
    worse_models = df[df['median'] > gemini_stats['median']]
    
    return {
        'gemini_stats': gemini_stats.to_dict(),
        'rank': int(gemini_stats['rank']),
        'total_models': total_models,
        'percentile': (1 - gemini_stats['rank'] / total_models) * 100,
        'better_models': better_models[['model', 'median', 'mean']].head(5).to_dict('records'),
        'worse_models': worse_models[['model', 'median', 'mean']].head(5).to_dict('records'),
        'similar_models': similar_models[['model', 'median', 'mean']].to_dict('records')
    }


def compare_by_category(df: pd.DataFrame) -> Dict:
    """Compare les modèles par catégorie (propriétaires vs open source, etc.)."""
    categories = {
        'proprietary': ['google_', 'openai_', 'amazon_', 'mistralai_', 'meta-llama_', 'x-ai_', 'qwen_'],
        'kraken_models': ['catmus', 'FoNDUE', 'Gallicorpora', 'lectaurep', 'ManuMcFondue', 'McCATMuS'],
    }
    
    results = {}
    for category, prefixes in categories.items():
        category_models = df[df['model'].str.contains('|'.join(prefixes), na=False)]
        if not category_models.empty:
            results[category] = {
                'count': len(category_models),
                'median_wer': category_models['median'].median(),
                'mean_wer': category_models['mean'].mean(),
                'best_model': category_models.iloc[0][['model', 'median']].to_dict(),
                'worst_model': category_models.iloc[-1][['model', 'median']].to_dict()
            }
    
    return results


def generate_comparison_report(wer_data: Dict, output_path: Path) -> None:
    """Génère un rapport de comparaison détaillé."""
    df = calculate_model_statistics(wer_data)
    gemini_analysis = analyze_gemini_flash(df)
    category_comparison = compare_by_category(df)
    
    report = []
    report.append("# Analyse comparative : Gemini 2.0 Flash dans le benchmark HTR\n")
    
    # Vue d'ensemble
    report.append("## Vue d'ensemble\n")
    stats = gemini_analysis['gemini_stats']
    report.append(f"**Modèle analysé** : google/gemini-2.0-flash-001\n")
    report.append(f"- **WER médian** : {stats['median']:.3f}")
    report.append(f"- **WER moyen** : {stats['mean']:.3f}")
    report.append(f"- **Écart-type** : {stats['std']:.3f}")
    report.append(f"- **Min/Max** : {stats['min']:.3f} / {stats['max']:.3f}")
    report.append(f"- **Quartiles (Q1/Q3)** : {stats['q25']:.3f} / {stats['q75']:.3f}")
    report.append(f"- **Pages évaluées** : {stats['n_pages']}\n")
    
    # Position dans le classement
    report.append("## Position dans le classement\n")
    report.append(f"- **Rang** : {gemini_analysis['rank']} / {gemini_analysis['total_models']}")
    report.append(f"- **Percentile** : Top {100 - gemini_analysis['percentile']:.1f}%\n")
    
    # Comparaison avec les meilleurs
    report.append("## Top 5 des modèles plus performants\n")
    report.append("| Modèle | WER médian | WER moyen |")
    report.append("|--------|------------|-----------|")
    for model in gemini_analysis['better_models']:
        report.append(f"| {model['model']} | {model['median']:.3f} | {model['mean']:.3f} |")
    report.append("")
    
    # Modèles similaires
    if gemini_analysis['similar_models']:
        report.append("## Modèles aux performances similaires (±10%)\n")
        report.append("| Modèle | WER médian | WER moyen |")
        report.append("|--------|------------|-----------|")
        for model in gemini_analysis['similar_models']:
            report.append(f"| {model['model']} | {model['median']:.3f} | {model['mean']:.3f} |")
        report.append("")
    
    # Analyse par catégorie
    report.append("## Analyse par catégorie\n")
    for category, stats in category_comparison.items():
        report.append(f"### {category.replace('_', ' ').title()}")
        report.append(f"- Nombre de modèles : {stats['count']}")
        report.append(f"- WER médian de la catégorie : {stats['median_wer']:.3f}")
        report.append(f"- Meilleur : {stats['best_model']['model']} (WER: {stats['best_model']['median']:.3f})")
        report.append(f"- Moins bon : {stats['worst_model']['model']} (WER: {stats['worst_model']['median']:.3f})\n")
    
    # Top 10 global
    report.append("## Top 10 des modèles du benchmark\n")
    report.append("| Rang | Modèle | WER médian | WER moyen | Écart-type |")
    report.append("|------|--------|------------|-----------|------------|")
    for _, row in df.head(10).iterrows():
        report.append(f"| {row['rank']} | {row['model']} | {row['median']:.3f} | {row['mean']:.3f} | {row['std']:.3f} |")
    report.append("")
    
    # Insights clés
    report.append("## Insights clés\n")
    gemini_median = gemini_analysis['gemini_stats']['median']
    
    # Calcul de la position relative
    if gemini_analysis['rank'] <= 5:
        position_desc = "parmi les meilleurs modèles"
    elif gemini_analysis['rank'] <= 10:
        position_desc = "dans le top 10"
    elif gemini_analysis['percentile'] >= 75:
        position_desc = "dans le quartile supérieur"
    elif gemini_analysis['percentile'] >= 50:
        position_desc = "au-dessus de la médiane"
    else:
        position_desc = "dans la moitié inférieure"
    
    report.append(f"1. **Position compétitive** : Gemini 2.0 Flash se positionne {position_desc} avec un WER médian de {gemini_median:.3f}")
    
    # Comparaison avec les catégories
    if 'proprietary' in category_comparison:
        prop_median = category_comparison['proprietary']['median_wer']
        if gemini_median < prop_median:
            report.append(f"2. **Performance vs propriétaires** : Surpasse la médiane des modèles propriétaires ({prop_median:.3f})")
        else:
            report.append(f"2. **Performance vs propriétaires** : Légèrement en dessous de la médiane des modèles propriétaires ({prop_median:.3f})")
    
    # Stabilité
    std_dev = gemini_analysis['gemini_stats']['std']
    avg_std = df['std'].mean()
    if std_dev < avg_std:
        report.append(f"3. **Stabilité** : Performance plus stable que la moyenne (σ={std_dev:.3f} vs moyenne={avg_std:.3f})")
    else:
        report.append(f"3. **Stabilité** : Variabilité supérieure à la moyenne (σ={std_dev:.3f} vs moyenne={avg_std:.3f})")
    
    # Cas d'usage recommandés
    report.append("\n## Recommandations d'usage\n")
    if gemini_median < 0.8:
        report.append("- ✅ **Adapté pour** : Transcription production avec révision minimale")
    elif gemini_median < 1.0:
        report.append("- ⚠️  **Adapté pour** : Transcription avec révision modérée nécessaire")
    else:
        report.append("- ❌ **Non recommandé pour** : Transcription directe sans révision importante")
    
    # Sauvegarder le rapport
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    # Sauvegarder aussi les données brutes pour analyse ultérieure
    analysis_data = {
        'model_statistics': df.to_dict('records'),
        'gemini_analysis': gemini_analysis,
        'category_comparison': category_comparison
    }
    
    json_path = output_path.parent / 'gemini_flash_analysis.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"Rapport généré : {output_path}")
    print(f"Données d'analyse : {json_path}")
    
    # Afficher un résumé
    print("\n" + "="*50)
    print("RÉSUMÉ : Gemini 2.0 Flash dans le benchmark")
    print("="*50)
    print(f"Rang : {gemini_analysis['rank']}/{gemini_analysis['total_models']}")
    print(f"WER médian : {gemini_median:.3f}")
    print(f"Position : Top {100 - gemini_analysis['percentile']:.1f}%")
    if gemini_analysis['better_models']:
        best = gemini_analysis['better_models'][0]
        print(f"Meilleur modèle : {best['model']} (WER: {best['median']:.3f})")
    print("="*50)


def generate_visual_comparison(df: pd.DataFrame, output_path: Path) -> None:
    """Génère un tableau visuel de comparaison pour les top modèles."""
    # Créer un rapport visuel simple en ASCII art
    top_models = df.head(15)
    
    report = []
    report.append("\n" + "="*70)
    report.append("TABLEAU COMPARATIF DES PERFORMANCES HTR/OCR")
    report.append("="*70)
    report.append("\nComparaison avec le WER attendu de 0.694 pour Gemini 2.0 Flash:")
    
    gemini_row = df[df['model'] == 'google_gemini-2.0-flash-001'].iloc[0]
    actual_median = gemini_row['median']
    expected_median = 0.694
    difference = actual_median - expected_median
    
    report.append(f"- WER médian RÉEL : {actual_median:.3f}")
    report.append(f"- WER médian ATTENDU : {expected_median:.3f}")
    report.append(f"- Différence : {difference:+.3f} {'(légèrement plus élevé)' if difference > 0 else '(meilleur que prévu)'}")
    
    report.append("\n" + "-"*70)
    report.append("Graphique de performance (WER médian - plus bas = meilleur)")
    report.append("-"*70)
    
    max_width = 50
    for _, row in top_models.iterrows():
        model_name = row['model'][:30].ljust(30)
        wer = row['median']
        bar_length = int(min(wer * 10, max_width))
        bar = "█" * bar_length
        
        # Marquer Gemini 2.0 Flash
        marker = " ← GEMINI 2.0 FLASH" if row['model'] == 'google_gemini-2.0-flash-001' else ""
        report.append(f"{model_name} [{wer:.3f}] {bar}{marker}")
    
    report.append("-"*70)
    
    # Sauvegarder le rapport visuel
    visual_path = output_path.parent / 'comparaison_visuelle_gemini.txt'
    with open(visual_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print('\n'.join(report))
    print(f"\nRapport visuel sauvegardé : {visual_path}")


def main():
    """Fonction principale."""
    # Chemins
    project_root = Path(__file__).parent.parent
    wer_data_path = project_root / 'data' / 'wer_data.json'
    output_path = project_root / 'rapports' / 'comparaison_gemini_flash.md'
    
    # Vérifier l'existence du fichier
    if not wer_data_path.exists():
        print(f"Erreur : Fichier {wer_data_path} introuvable")
        return
    
    # Charger et analyser
    print("Chargement des données WER...")
    wer_data = load_wer_data(wer_data_path)
    
    print("Génération du rapport de comparaison...")
    generate_comparison_report(wer_data, output_path)
    
    # Générer aussi la visualisation
    df = calculate_model_statistics(wer_data)
    generate_visual_comparison(df, output_path)


if __name__ == "__main__":
    main()