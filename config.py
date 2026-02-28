"""Configuration et constantes du projet."""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# System prompt pour HTR
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