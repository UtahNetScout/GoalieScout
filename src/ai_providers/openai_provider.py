"""
OpenAI Provider Implementation
Uses OpenAI's GPT models for scouting report generation.
"""
import os
import re
from typing import Dict, Any
from openai import OpenAI

from . import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider for AI-generated scouting reports."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Configuration dictionary with API key and model
        """
        super().__init__(config)
        self.api_key = config.get('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
        self.model = config.get('OPENAI_MODEL', 'gpt-4')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found in config or environment")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_report(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a scouting report using OpenAI.
        
        Args:
            prompt: The prompt to send to OpenAI
            temperature: Sampling temperature
            
        Returns:
            Generated scouting report
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert hockey scout specializing in player movement analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def generate_score(self, prompt: str) -> int:
        """
        Generate a numeric score (0-100) using OpenAI.
        
        Args:
            prompt: The prompt describing the player's performance
            
        Returns:
            Score between 0 and 100
        """
        scoring_prompt = f"{prompt}\n\nBased on the above analysis, provide ONLY a numeric score from 0-100 (integer only, no explanation):"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a hockey scout providing numeric scores. Return only the integer score."},
                    {"role": "user", "content": scoring_prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extract first number found
            match = re.search(r'\d+', score_text)
            if match:
                score = int(match.group())
                return max(0, min(100, score))  # Clamp to 0-100
            return 50  # Default score if parsing fails
            
        except Exception as e:
            print(f"Error generating score: {str(e)}")
            return 50
