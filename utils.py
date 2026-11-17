"""
Fichier utils.py simplifié - maintient la compatibilité avec l'ancien code.
Les fonctionnalités ont été réorganisées dans des modules séparés.
"""

# Imports depuis les nouveaux modules
from config import system_prompt, VALID_OPENROUTER_MODELS, VALID_TRANSKRIBUS_MODELS
from metrics import calculate_wer, clean_text_for_wer
from api_clients import (
    query_model,
    query_openrouter,
    validate_model_id,
    is_transkribus_model,
    fetch_openrouter_pricing,
    resize_image_if_needed,
    OPENROUTER_PRICING
)
from reporting import generate_results_md_table

# Exports - pour maintenir la compatibilité
__all__ = [
    'system_prompt',
    'VALID_OPENROUTER_MODELS',
    'VALID_TRANSKRIBUS_MODELS',
    'calculate_wer',
    'clean_text_for_wer',
    'query_model',
    'query_openrouter',
    'validate_model_id',
    'is_transkribus_model',
    'fetch_openrouter_pricing',
    'resize_image_if_needed',
    'generate_results_md_table',
    'OPENROUTER_PRICING'
]