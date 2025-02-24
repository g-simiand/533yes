import os
import base64
import requests
import shutil
import random
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import io
import json

# Load environment variables from .env file
load_dotenv()

system_prompt = """Tu es un expert en HTR (Handwritten Text Recognition) spécialisé dans les manuscrits français du XVIIIe siècle.

Voici tes instructions précises :

1. Examine attentivement l'image du manuscrit qui te sera présentée
2. Transcris le texte exactement comme il apparaît, en respectant :
   - L'orthographe d'origine
   - La ponctuation
   - Les majuscules et minuscules
   - Les sauts de ligne

3. Règles de transcription :
   - Si un mot est illisible ou incertain, remplace-le par [XXX]
   - Conserve les ratures visibles avec ~~texte barré~~
   - Maintiens les abréviations d'origine
   - Respecte la mise en page originale

4. Format de réponse :
   - Utilise uniquement le format markdown
   - Ne fournis aucun commentaire ou analyse
   - Transcris uniquement le contenu du document

Ta tâche est de produire une transcription fidèle et précise, sans interprétation ni modernisation du texte. Ne renvoie que la transcription, sans aucun commentaire ou analyse."""

def fetch_openrouter_pricing():
    """
    Fetch current model pricing from OpenRouter API
    Returns a dictionary of model pricing information
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "https://github.com/533yes",  # Updated referer
        "X-Title": "533yes HTR Benchmark",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Error fetching model pricing: {response.text}")
        
    models_data = response.json()
    pricing_dict = {}
    
    for model in models_data.get('data', []):
        model_id = model['id']
        pricing = model['pricing']
        # Convert string prices to float and store as (prompt, completion) tuple
        pricing_dict[model_id] = (
            float(pricing['prompt']),
            float(pricing['completion'])
        )
    
    return pricing_dict

# Use dynamic pricing instead of hardcoded values
try:
    OPENROUTER_PRICING = fetch_openrouter_pricing()
except Exception as e:
    print(f"Warning: Could not fetch OpenRouter pricing, using default values. Error: {e}")


def query_openrouter(image_path, model, system_message=system_prompt):
    """
    Query OpenRouter API for image analysis
    Args:
        image_path: Path to the image file
        model: Model ID from OpenRouter (e.g. "openai/gpt-4-vision-preview")
        system_message: Optional system message to prepend
    Returns:
        tuple: (response_data, cost)
    """
    # Refresh pricing data before each query to ensure we have latest prices
    try:
        current_pricing = fetch_openrouter_pricing()
    except Exception:
        current_pricing = OPENROUTER_PRICING
    
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "https://github.com/533yes",  # Updated referer
        "X-Title": "533yes HTR Benchmark",
        "Content-Type": "application/json"
    }
    
    # List of models that specifically require JPEG format
    jpeg_required_models = [
        "amazon/nova-lite-v1"
    ]
    
    # Convert to JPEG only if the model requires it
    if model in jpeg_required_models:
        with Image.open(image_path) as img:
            if img.format == 'PNG':
                # Convert to RGB mode (in case it's RGBA) and save as JPEG in memory
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as JPEG in memory
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            else:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    else:
        # For all other models, use the original image format
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    messages = []
    if system_message:
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    messages.append({
        "role": "user",
        "content": [{
            "type": 'image_url',
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }]
    })
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.1
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        raise Exception(f"Error from OpenRouter API: {response.text}")
        
    response_data = response.json()
    
    # Check if response has the expected structure
    if 'choices' not in response_data or not response_data['choices']:
        raise Exception(f"Unexpected response format - missing 'choices' field: {response_data}")
    
    # Before calculating costs, ensure usage data exists with defaults
    usage_data = response_data.get('usage', {})
    if not usage_data or not isinstance(usage_data, dict):
        usage_data = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
    response_data['usage'] = usage_data

    # Calculate cost using current pricing and usage data
    input_cost = usage_data.get('prompt_tokens', 0) * current_pricing.get(model, (0,0))[0]
    output_cost = usage_data.get('completion_tokens', 0) * current_pricing.get(model, (0,0))[1]
    total_cost = input_cost + output_cost
    
    # Add model information to response
    response_data['model_info'] = {
        'id': model,
        'pricing': current_pricing.get(model, (0,0)),
        'total_cost': total_cost
    }
    
    return response_data, round(total_cost, 12)

def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Calculate Word Error Rate (WER) between reference and hypothesis texts.
    Returns:
        float: WER score (0.0 = perfect match, 1.0 = all words wrong)
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    # Create a matrix to store the edit distances
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    
    # Initialize matrix edges
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j
    
    # Fill the matrix using Levenshtein distance algorithm
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion = d[i][j-1] + 1
                deletion = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    
    # The bottom-right cell contains the edit distance
    edit_distance = d[len(ref_words)][len(hyp_words)]
    return edit_distance / len(ref_words) if len(ref_words) > 0 else 0.0


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
    """
    import os
    import json

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

    try:
        results_files = os.listdir(results_dir)
    except FileNotFoundError:
        print(f"Le dossier '{results_dir}' n'existe pas.")
        return

    # Dictionnaire pour regrouper les données par modèle
    data_by_model = {}

    for filename in results_files:
        result_file_path = os.path.join(results_dir, filename)
        # On suppose que le fichier de référence porte le même nom (avec extension .md)
        ref_file_path = os.path.join(reference_dir, filename.split(".")[0] + ".md")
        
        # Vérifier que c'est bien un fichier
        if not os.path.isfile(result_file_path):
            continue

        if not os.path.exists(ref_file_path):
            print(f"Fichier de référence pour '{filename}' introuvable dans '{reference_dir}'. Ignoré.")
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

    # Création du tableau Markdown avec l'en-tête comprenant les nouvelles colonnes
    table_rows = []
    table_rows.append("| Modèle | Éditeur | Type de modèle | Nombre d'images | Coût total ($) | Coût moyen ($) | WER min | WER médian | WER max |")
    table_rows.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")

    # Calcul des statistiques pour chaque modèle
    for model, data in data_by_model.items():
        n_images = len(data["wers"])
        total_cost = sum(data["costs"])
        mean_cost = total_cost / n_images if n_images > 0 else 0.0
        wer_min = min(data["wers"]) if data["wers"] else 0.0
        wer_max = max(data["wers"]) if data["wers"] else 0.0
        wer_med = compute_median(data["wers"])
        row = (
            f"| {model} | {data['editeur']} | {data['modele_type']} | {n_images} | "
            f"{total_cost:.6f} | {mean_cost:.6f} | {wer_min:.3f} | {wer_med:.3f} | {wer_max:.3f} |"
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

def copy_random_images(source_dir, dest_dir, num_images=10):
    """
    Copy a random selection of images from source_dir to dest_dir
    
    Args:
        source_dir (str): Source directory containing images
        dest_dir (str): Destination directory to copy images to
        num_images (int): Number of images to copy (default: 10)
    """
    # Create destination directory if it doesn't exist
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    
    # Get list of image files
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    image_files = [f for f in os.listdir(source_dir) 
                  if os.path.isfile(os.path.join(source_dir, f))
                  and f.lower().endswith(image_extensions)]
    
    # Select random images
    num_to_copy = min(num_images, len(image_files))
    selected_images = random.sample(image_files, num_to_copy)
    
    # Copy selected images
    for image in selected_images:
        src_path = os.path.join(source_dir, image)
        dst_path = os.path.join(dest_dir, image)
        shutil.copy2(src_path, dst_path)
        print(f"Copied: {image}")
    
    print(f"\nSuccessfully copied {num_to_copy} images to {dest_dir}")