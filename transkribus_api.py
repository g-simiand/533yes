import os
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Tuple, Optional

# Load environment variables
load_dotenv()

class TranskribusAPI:
    """
    Wrapper for Transkribus API interactions
    """
    def __init__(self):
        self.base_url = "https://transkribus.eu/TrpServer/rest"
        self.auth_token = os.getenv("TRANSKRIBUS_TOKEN")
        if not self.auth_token:
            raise ValueError("TRANSKRIBUS_TOKEN environment variable not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def get_session_id(self) -> str:
        """Get a session ID from Transkribus"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get session ID: {response.text}")
        return response.json().get("sessionId")

    def transcribe_image(self, 
                        image_path: str, 
                        model_id: Optional[str] = None) -> Tuple[Dict, float]:
        """
        Send an image to Transkribus for transcription
        
        Args:
            image_path: Path to the image file
            model_id: Optional HTR model ID to use (defaults to best available)
            
        Returns:
            tuple: (response_data, cost)
            - response_data contains the transcription and metadata
            - cost is the API usage cost (if applicable)
        """
        # Get session ID first
        session_id = self.get_session_id()
        
        # Prepare the image
        with open(image_path, "rb") as image_file:
            files = {
                'img': (Path(image_path).name, image_file, 'image/jpeg')
            }
        
        # Add session ID to headers
        headers = self.headers.copy()
        headers["JSESSIONID"] = session_id
        
        # Prepare model parameters if specified
        params = {}
        if model_id:
            params["modelId"] = model_id
        
        # Send request to Transkribus
        response = requests.post(
            f"{self.base_url}/recognition/text",
            headers=headers,
            files=files,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error from Transkribus API: {response.text}")
        
        response_data = response.json()
        
        # Format response to match existing code structure
        formatted_response = {
            "result": response_data.get("text", ""),
            "model_info": {
                "id": model_id or "transkribus_default",
                "pricing": (0, 0),  # Transkribus uses different pricing model
                "total_cost": 0  # Cost tracking would need to be implemented differently
            },
            "usage": {
                "prompt_tokens": 0,  # Not applicable for Transkribus
                "completion_tokens": 0
            },
            "editeur": "Transkribus",
            "modele_type": "propriétaire"
        }
        
        # For now, return 0 cost since Transkribus uses credits/subscription
        # This could be modified to track credit usage if needed
        return formatted_response, 0.0

def query_transkribus(image_path: str, model_id: Optional[str] = None) -> Tuple[Dict, float]:
    """
    Convenience function to query Transkribus API
    
    Args:
        image_path: Path to the image file
        model_id: Optional HTR model ID to use
        
    Returns:
        tuple: (response_data, cost)
    """
    api = TranskribusAPI()
    return api.transcribe_image(image_path, model_id) 