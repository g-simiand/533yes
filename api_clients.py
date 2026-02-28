"""Clients API pour OpenRouter et Transkribus."""

import os
import base64
import requests
import io
import math
from PIL import Image
from transkribus_api import query_transkribus
from config import VALID_OPENROUTER_MODELS, VALID_TRANSKRIBUS_MODELS, system_prompt


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
    OPENROUTER_PRICING = {}


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