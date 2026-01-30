"""
Ollama Provider Implementation
Uses locally-hosted Ollama models for free AI-generated scouting reports.
"""
import os
import re
import json
from typing import Dict, Any
import requests

from . import AIProvider


class OllamaProvider(AIProvider):
    """Ollama local LLM provider for AI-generated scouting reports."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider.
        
        Args:
            config: Configuration dictionary with base URL and model
        """
        super().__init__(config)
        self.base_url = config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = config.get('OLLAMA_MODEL', 'llama2')
    
    def generate_report(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a scouting report using Ollama.
        
        Args:
            prompt: The prompt to send to Ollama
            temperature: Sampling temperature
            
        Returns:
            Generated scouting report
        """
        try:
            full_prompt = f"You are an expert hockey scout specializing in player movement analysis.\n\nUser: {prompt}\n\nAssistant:"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f"Error: Ollama returned status code {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure Ollama is running locally."
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def generate_score(self, prompt: str) -> int:
        """
        Generate a numeric score (0-100) using Ollama.
        
        Args:
            prompt: The prompt describing the player's performance
            
        Returns:
            Score between 0 and 100
        """
        scoring_prompt = f"You are a hockey scout providing numeric scores.\n\nUser: {prompt}\n\nBased on the above analysis, provide ONLY a numeric score from 0-100 (integer only, no explanation):\n\nAssistant:"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": scoring_prompt,
                    "temperature": 0.3,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                score_text = result.get('response', '').strip()
                
                # Extract first number found
                match = re.search(r'\d+', score_text)
                if match:
                    score = int(match.group())
                    return max(0, min(100, score))  # Clamp to 0-100
                return 50  # Default score if parsing fails
            else:
                print(f"Error: Ollama returned status code {response.status_code}")
                return 50
                
        except Exception as e:
            print(f"Error generating score: {str(e)}")
            return 50
