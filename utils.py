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
import re
import datetime
import math
from transkribus_api import query_transkribus

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

# Define a list of known valid model IDs for OpenRouter
VALID_OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-001",
    "qwen/qwen-vl-plus:free",
    "qwen/qwen2.5-vl-72b-instruct:free",
    "google/gemini-2.0-flash-thinking-exp:free",
    "google/gemini-2.0-flash-exp:free",
    "qwen/qvq-72b-preview",
    "openai/o1",
    "x-ai/grok-2-vision-1212",
    "amazon/nova-lite-v1",
    "openai/gpt-4o-2024-11-20",
    "mistralai/pixtral-large-2411",
    "x-ai/grok-vision-beta",
    "anthropic/claude-3.5-sonnet",
    "meta-llama/llama-3.2-90b-vision-instruct",
    "qwen/qwen-2-vl-72b-instruct",
    "mistralai/pixtral-12b",
    "qwen/qwen-2-vl-7b-instruct",
    "openai/gpt-4o-mini",
    "openai/gpt-4-vision",
    "openai/gpt-4.5-preview",
    "anthropic/claude-3.7-sonnet",
    # Add more valid models as needed
]

# Define a list of known valid model IDs for Transkribus
VALID_TRANSKRIBUS_MODELS = [
    "transkribus/CITlab_HTR+",
    "transkribus/PyLaia",
    "transkribus/French_18th_Century",
    # Add more valid Transkribus models as needed
]

def validate_model_id(model_id):
    """
    Validate if a model ID is known to be valid for OpenRouter or Transkribus.
    
    Args:
        model_id: The model ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if model_id.startswith("transkribus/"):
        return model_id in VALID_TRANSKRIBUS_MODELS
    else:
        return model_id in VALID_OPENROUTER_MODELS

def is_transkribus_model(model_id):
    """
    Check if a model ID is a Transkribus model.
    
    Args:
        model_id: The model ID to check
        
    Returns:
        bool: True if it's a Transkribus model, False otherwise
    """
    return model_id.startswith("transkribus/")

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

def resize_image_if_needed(image_path, max_size_bytes=5*1024*1024, max_dimension=None):
    """
    Resize an image if it exceeds the maximum size limit or dimension limit.
    
    Args:
        image_path: Path to the image file
        max_size_bytes: Maximum size in bytes (default: 5MB)
        max_dimension: Maximum allowed dimension in pixels (width or height)
        
    Returns:
        base64_image: Base64 encoded image data
        was_resized: Boolean indicating if the image was resized
    """
    # Check file size
    file_size = os.path.getsize(image_path)
    
    # Always process the image to ensure correct format
    try:
        # Set a higher PIL limit for large images
        Image.MAX_IMAGE_PIXELS = 200000000  # Increase limit to handle very large images
        
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_width, original_height = img.size
            needs_resize = False
            
            # Check if dimensions exceed max_dimension
            if max_dimension and (original_width > max_dimension or original_height > max_dimension):
                needs_resize = True
                # Calculate scaling factor based on the larger dimension
                scale_factor = max_dimension / max(original_width, original_height)
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            else:
                new_width, new_height = original_width, original_height
            
            # Start with high quality
            quality = 95
            buffer = io.BytesIO()
            
            # If file is likely to be too large, start with a lower quality
            if file_size > max_size_bytes * 0.8:
                quality = 85
            
            # Iteratively reduce quality until file size is under the limit
            while True:
                buffer.seek(0)
                buffer.truncate(0)
                img.save(buffer, format='JPEG', quality=quality)
                buffer_size = buffer.tell()
                
                # If size is under the limit, we're done
                if buffer_size <= max_size_bytes * 0.95:  # 5% safety margin
                    break
                
                # If we've already reduced quality significantly and still too large
                if quality <= 30:
                    # Need to resize the image further
                    scale_factor = math.sqrt(max_size_bytes * 0.9 / buffer_size)
                    new_width = int(new_width * scale_factor)
                    new_height = int(new_height * scale_factor)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    quality = 70  # Reset quality after resize
                else:
                    # Reduce quality and try again
                    quality -= 10
                
                needs_resize = True
            
            return base64.b64encode(buffer.getvalue()).decode('utf-8'), needs_resize
    except Exception as e:
        raise Exception(f"Error processing image {image_path}: {str(e)}")

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
    # Validate model ID
    if not validate_model_id(model):
        raise Exception(f"Invalid model ID: {model}. Please check models_to_test.json for valid model IDs.")
    
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
    
    # Process and resize image if needed
    try:
        # Set model-specific limits
        if "mistralai" in model:
            max_size_bytes = 2*1024*1024  # 2MB for Mistral models
            max_dimension = None  # No specific dimension limit
        elif "anthropic" in model or "claude" in model:
            max_size_bytes = 4*1024*1024  # 4MB for Claude models (reduced from 5MB for safety)
            max_dimension = 7500  # Claude has 8000 pixel limit, use 7500 for extra safety
        elif "llama" in model.lower() or "pixtral" in model.lower():
            # More conservative limits for Llama and Pixtral models
            max_size_bytes = 3*1024*1024  # 3MB for Llama/Pixtral
            max_dimension = 6000  # Lower dimension limit
        else:
            max_size_bytes = 5*1024*1024  # 5MB for other models
            max_dimension = None  # No specific dimension limit
            
        base64_image, was_resized = resize_image_if_needed(image_path, max_size_bytes, max_dimension)
        
        # Double-check file size for Claude models to ensure it's under the limit
        if ("anthropic" in model or "claude" in model):
            # Decode base64 to get actual bytes
            image_bytes = base64.b64decode(base64_image)
            actual_size = len(image_bytes)
            
            # If still too large, force another resize with even stricter limits
            if actual_size > 4.9*1024*1024:  # If over 4.9MB
                print(f"Warning: Image {os.path.basename(image_path)} still too large ({actual_size/1024/1024:.2f}MB). Forcing stricter resize.")
                max_size_bytes = 4*1024*1024  # 4MB hard limit
                max_dimension = 6000  # Even smaller dimension
                base64_image, _ = resize_image_if_needed(image_path, max_size_bytes, max_dimension)
        
        if was_resized:
            resize_info = f"{max_size_bytes/1024/1024}MB"
            if max_dimension:
                resize_info += f" and {max_dimension}px max dimension"
            print(f"Image {os.path.basename(image_path)} was resized to fit within {resize_info}")
    except Exception as e:
        raise Exception(f"Error processing image {image_path}: {str(e)}")
    
    messages = []
    if system_message:
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    # Special handling for Llama and Pixtral models
    if "llama" in model.lower() or "pixtral" in model.lower():
        # For these models, try a different message format with explicit instruction
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please transcribe the text in this historical French manuscript image. Transcribe exactly what you see, preserving original spelling, punctuation, and line breaks."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })
    else:
        # Standard format for other models
        messages.append({
            "role": "user",
            "content": [{
                "type": "image_url",
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

def clean_text_for_wer(text):
    """
    Nettoie le texte pour le calcul du WER en supprimant les marqueurs [XXX],
    les balises markdown au début et à la fin, et tout texte de réflexion avant la transcription.
    Gère plusieurs cas de formatage markdown.
    """
    # Supprimer les marqueurs [XXX]
    text = re.sub(r'\[XXX\]', '', text)
    
    # Cas 1: Bloc markdown complet avec ```markdown ... ```
    if re.search(r'```markdown.*?```', text, re.DOTALL):
        match = re.search(r'```markdown(.*?)```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    
    # Cas 2: Bloc markdown sans spécifier "markdown" - ```...```
    elif re.search(r'```.*?```', text, re.DOTALL):
        match = re.search(r'```(.*?)```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    
    # Cas 3: Texte qui commence par ```markdown mais sans fermeture
    elif text.strip().startswith('```markdown'):
        text = re.sub(r'^```markdown\s*', '', text).strip()
    
    # Cas 4: Texte qui commence par ``` mais sans fermeture
    elif text.strip().startswith('```'):
        text = re.sub(r'^```\s*', '', text).strip()
    
    # Cas 5: Texte qui se termine par ``` mais sans ouverture
    elif text.strip().endswith('```'):
        text = re.sub(r'\s*```$', '', text).strip()
    
    # Cas 6: Si le mot "markdown" apparaît seul au début
    elif text.strip().startswith('markdown'):
        text = re.sub(r'^markdown\s*', '', text).strip()
    
    # Cas 7: Si le modèle a réfléchi avant de donner sa réponse
    # Chercher des indicateurs de fin de réflexion
    reflection_markers = [
        r'Voici la transcription\s*:', 
        r'Transcription\s*:', 
        r'Voici le texte\s*:',
        r'Le texte transcrit\s*:',
        r'Ma transcription\s*:',
        r'Voici ma transcription\s*:',
        r'Texte transcrit\s*:',
        r'Contenu du document\s*:'
    ]
    
    for marker in reflection_markers:
        match = re.search(marker, text)
        if match:
            # Ne garder que ce qui suit le marqueur
            text = text[match.end():].strip()
            break
    
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Calculate Word Error Rate (WER) between reference and hypothesis texts.
    
    Args:
        reference: The reference text (ground truth)
        hypothesis: The hypothesis text (prediction)
        
    Returns:
        float: WER score (0.0 = perfect match, 1.0 = all words wrong)
    """
    # Nettoyer les textes avant le calcul
    reference = clean_text_for_wer(reference)
    hypothesis = clean_text_for_wer(hypothesis)
    
    # Diviser en mots
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    # Si la référence est vide, retourner 1.0 si l'hypothèse n'est pas vide, sinon 0.0
    if len(ref_words) == 0:
        return 1.0 if len(hyp_words) > 0 else 0.0
    
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
    return edit_distance / len(ref_words)


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
    import os
    import json
    import re
    import datetime

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

def query_model(image_path, model, system_message=system_prompt):
    """
    Query the appropriate API based on the model ID
    
    Args:
        image_path: Path to the image file
        model: Model ID (e.g., "openai/gpt-4-vision" or "transkribus/CITlab_HTR+")
        system_message: Optional system message to prepend
        
    Returns:
        tuple: (response_data, cost)
    """
    # Determine which API to use based on the model ID
    if is_transkribus_model(model):
        # Extract the actual model ID without the "transkribus/" prefix
        transkribus_model_id = model.replace("transkribus/", "")
        return query_transkribus(image_path, transkribus_model_id)
    else:
        return query_openrouter(image_path, model, system_message)