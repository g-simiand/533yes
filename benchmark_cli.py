#!/usr/bin/env python3
"""
Script CLI pour automatiser le benchmark HTR/OCR.
Remplace le notebook Jupyter benchmark_htr.ipynb.
"""

import os
import json
import random
import argparse
import concurrent.futures
from datetime import datetime
from pathlib import Path
from functools import partial
from typing import List, Dict, Tuple, Optional, Any

import pandas as pd
from tqdm import tqdm

from api_clients import query_model
from config import system_prompt
from reporting import generate_results_md_table


class HTRBenchmark:
    """Classe principale pour le benchmark HTR/OCR."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le benchmark HTR.
        
        Args:
            config_path: Chemin vers un fichier de configuration optionnel
        """
        self.config = self._load_config(config_path) if config_path else {}
        self._setup_directories()
        self.models = self._load_models()
        self.image_files = self._get_image_files()
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge un fichier de configuration JSON/YAML."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        if path.suffix == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        elif path.suffix in ['.yaml', '.yml']:
            try:
                import yaml
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML required for YAML config. Install with: pip install pyyaml")
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")
    
    def _setup_directories(self) -> None:
        """Crée les répertoires nécessaires."""
        self.results_dir = Path(self.config.get('results_dir', 'résultats'))
        self.reference_dir = Path(self.config.get('reference_dir', 'transcriptions_de_référence'))
        self.images_dir = Path(self.config.get('images_dir', 'images'))
        
        self.results_dir.mkdir(exist_ok=True)
        self.reference_dir.mkdir(exist_ok=True)
        
    def _load_models(self) -> List[Tuple[str, str]]:
        """Charge la configuration des modèles à tester."""
        models_file = self.config.get('models_file', 'models_to_test.json')
        with open(models_file, "r") as f:
            return json.load(f)
            
    def _get_image_files(self) -> List[Path]:
        """Récupère la liste des images à traiter."""
        images = list(self.images_dir.glob("*.jpg")) + list(self.images_dir.glob("*.png"))
        if not images:
            raise ValueError(f"No images found in {self.images_dir}")
        return images
        
    def get_model_metadata(self, model_id: str, model_type: str) -> Dict[str, str]:
        """
        Extrait les métadonnées d'un modèle.
        
        Args:
            model_id: ID du modèle
            model_type: Type du modèle ('open' ou 'proprietary')
            
        Returns:
            Dict avec editeur et modele_type
        """
        parts = model_id.split("/")
        editor = parts[0]
        model_type_fr = "libre" if model_type == "open" else "propriétaire"
        
        return {
            "editeur": editor,
            "modele_type": model_type_fr
        }
        
    def process_image(self, img_path: Path, model_info: Tuple[str, str]) -> Optional[Dict]:
        """
        Traite une image avec un modèle donné.
        
        Args:
            img_path: Chemin vers l'image
            model_info: Tuple (model_id, model_type)
            
        Returns:
            Dict avec les résultats ou None si déjà traité ou erreur
        """
        model_meta = self.get_model_metadata(model_info[0], model_info[1])
        model, _ = model_info
        
        # Créer un nom de fichier valide
        safe_model_name = model.replace('/', '_').replace('\\', '_').replace(':', '_')
        result_file = self.results_dir / f"{img_path.stem}_{safe_model_name}.json"
        
        # Vérifier si le résultat existe déjà (mode incrémental)
        if not self.config.get('force_rerun', False) and result_file.exists():
            if self.config.get('verbose', False):
                print(f"Skipping {img_path.name} with {model} (result exists)")
            return None
            
        try:
            # Query the model
            response_data, cost = query_model(str(img_path), model)

            # Extract the transcription from the response based on format
            if 'choices' in response_data and response_data['choices']:
                transcription = response_data['choices'][0]['message']['content']
            elif 'result' in response_data:
                # This is for Transkribus API format
                transcription = response_data['result']
            else:
                raise Exception(f"Unexpected response format: {response_data}")
            
            # Get usage data with defaults if missing
            usage_data = response_data.get('usage', {})
            if not usage_data or not isinstance(usage_data, dict):
                usage_data = {
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0
                }

            # Prepare result data
            result_data = {
                "model": model,
                "editeur": model_meta["editeur"],
                "modele_type": model_meta["modele_type"],
                "image": str(img_path),
                "result": transcription,
                "timestamp": datetime.now().isoformat(),
                "model_info": response_data.get('model_info', {}),
                "usage": usage_data,
                "latency": response_data.get('created') - response_data.get('started', 0) if 'created' in response_data else None
            }
            
            # Save result to file
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
            return result_data
            
        except Exception as e:
            print(f"Error processing {img_path} with {model}: {str(e)}")
            return None
            
    def run_benchmark(self, 
                      max_workers: int = 1,
                      models_filter: Optional[List[str]] = None,
                      images_filter: Optional[List[str]] = None,
                      shuffle_models: bool = True) -> None:
        """
        Exécute le benchmark HTR.
        
        Args:
            max_workers: Nombre de workers pour le traitement parallèle
            models_filter: Liste optionnelle de modèles à tester (filtre)
            images_filter: Liste optionnelle d'images à traiter (filtre)  
            shuffle_models: Mélanger l'ordre des modèles
        """
        # Filtrer les modèles si nécessaire
        models_to_test = self.models
        if models_filter:
            models_to_test = [m for m in self.models if m[0] in models_filter]
            if not models_to_test:
                raise ValueError(f"No models found matching filter: {models_filter}")
                
        # Filtrer les images si nécessaire  
        images_to_process = self.image_files
        if images_filter:
            images_to_process = [img for img in self.image_files 
                                if img.stem in images_filter or img.name in images_filter]
            if not images_to_process:
                raise ValueError(f"No images found matching filter: {images_filter}")
                
        # Mélanger les modèles pour éviter les biais
        if shuffle_models:
            random.shuffle(models_to_test)
            
        print(f"Traitement de {len(images_to_process)} images avec {len(models_to_test)} modèles")
        print(f"Nombre de workers: {max_workers}")
        
        # Process models in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for model_info in tqdm(models_to_test, desc="Processing models"):
                # Create partial function with fixed model_info
                process_fn = partial(self.process_image, model_info=model_info)
                
                # Submit all images for this model to process in parallel
                future_to_img = {executor.submit(process_fn, img_path): img_path 
                                for img_path in images_to_process}
                
                # Process results as they complete
                for future in tqdm(concurrent.futures.as_completed(future_to_img), 
                                 total=len(future_to_img),
                                 desc=f"Processing images with {model_info[0]}", 
                                 leave=False):
                    result = future.result()
                    if result is not None:
                        self.results.append(result)
                        
        print(f"Traitement terminé : {len(self.results)} résultats obtenus")
        
    def generate_reports(self) -> None:
        """Génère les rapports et tables de résultats."""
        print("Génération de la table de résultats...")
        generate_results_md_table()
        print("Table de résultats générée avec succès")
        
        # Génération de la table de performance
        if Path("scripts/generate_performance_table.py").exists():
            print("Génération de la table de performance...")
            os.system("python scripts/generate_performance_table.py")
            
        # Génération des données pour le viewer interactif
        if Path("scripts/generate_viewer_data.py").exists():
            print("Génération des données pour le viewer...")
            os.system("python scripts/generate_viewer_data.py")
            
    def analyze_metrics(self, output_file: Optional[str] = None) -> pd.DataFrame:
        """
        Analyse les métriques de performance.
        
        Args:
            output_file: Fichier optionnel pour sauvegarder les métriques
            
        Returns:
            DataFrame avec les métriques consolidées
        """
        if not self.results:
            print("Aucun résultat disponible pour l'analyse")
            return pd.DataFrame()
            
        # Create a DataFrame for analysis
        df_results = pd.DataFrame(self.results)
        
        # Add columns for latency and token usage analysis
        df_summary = df_results.groupby('model').agg({
            'latency': ['mean', 'min', 'max'],
            'usage': lambda x: pd.Series([d.get('total_tokens', 0) for d in x]).mean()
        }).round(2)
        
        df_summary.columns = ['Avg Latency (s)', 'Min Latency (s)', 'Max Latency (s)', 'Avg Tokens']
        
        # Save to file if requested
        if output_file:
            df_summary.to_csv(output_file)
            print(f"Métriques sauvegardées dans {output_file}")
            
        return df_summary


def main():
    """Fonction principale du CLI."""
    parser = argparse.ArgumentParser(
        description="Benchmark HTR/OCR pour manuscrits de Sieyès",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Exécuter le benchmark complet
  python benchmark_cli.py
  
  # Exécuter avec 4 workers parallèles  
  python benchmark_cli.py --workers 4
  
  # Tester uniquement certains modèles
  python benchmark_cli.py --models "google/gemini-2.0-flash-001" "openai/gpt-4o-2024-11-20"
  
  # Traiter uniquement certaines images
  python benchmark_cli.py --images "manuscrit_001" "manuscrit_002"
  
  # Utiliser un fichier de configuration
  python benchmark_cli.py --config config_custom.json
  
  # Forcer le recalcul même si les résultats existent
  python benchmark_cli.py --force
  
  # Mode verbose avec plus de détails
  python benchmark_cli.py --verbose
        """
    )
    
    parser.add_argument(
        '--config',
        help='Chemin vers un fichier de configuration (JSON ou YAML)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Nombre de workers pour le traitement parallèle (défaut: 1)'
    )
    
    parser.add_argument(
        '--models',
        nargs='+',
        help='Liste des modèles à tester (filtre sur les IDs)'
    )
    
    parser.add_argument(
        '--images',
        nargs='+',
        help='Liste des images à traiter (nom de fichier ou stem)'
    )
    
    parser.add_argument(
        '--no-shuffle',
        action='store_true',
        help='Ne pas mélanger l\'ordre des modèles'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Forcer le recalcul même si les résultats existent déjà'
    )
    
    parser.add_argument(
        '--skip-reports',
        action='store_true',
        help='Ne pas générer les rapports après le benchmark'
    )
    
    parser.add_argument(
        '--metrics-output',
        help='Fichier de sortie pour les métriques (CSV)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbose avec plus de détails'
    )
    
    args = parser.parse_args()
    
    # Créer une configuration à partir des arguments
    config = {}
    if args.force:
        config['force_rerun'] = True
    if args.verbose:
        config['verbose'] = True
        
    # Initialiser le benchmark
    try:
        benchmark = HTRBenchmark(config_path=args.config)
        
        # Fusionner la config CLI
        benchmark.config.update(config)
        
        # Exécuter le benchmark
        benchmark.run_benchmark(
            max_workers=args.workers,
            models_filter=args.models,
            images_filter=args.images,
            shuffle_models=not args.no_shuffle
        )
        
        # Générer les rapports
        if not args.skip_reports:
            benchmark.generate_reports()
            
        # Analyser les métriques
        metrics_df = benchmark.analyze_metrics(output_file=args.metrics_output)
        if not metrics_df.empty:
            print("\n=== Métriques de performance ===")
            print(metrics_df.to_string())
            
    except Exception as e:
        print(f"Erreur: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())