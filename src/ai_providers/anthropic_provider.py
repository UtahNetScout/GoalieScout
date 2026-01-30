"""
Anthropic Claude Provider Implementation
Uses Anthropic's Claude models for scouting report generation.
"""
import os
import re
from typing import Dict, Any
from anthropic import Anthropic

from . import AIProvider


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider for AI-generated scouting reports."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Anthropic provider.
        
        Args:
            config: Configuration dictionary with API key and model
        """
        super().__init__(config)
        self.api_key = config.get('ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))
        self.model = config.get('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        
        if not self.api_key:
            raise ValueError("Anthropic API key not found in config or environment")
        
        self.client = Anthropic(api_key=self.api_key)
    
    def generate_report(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a scouting report using Anthropic Claude.
        
        Args:
            prompt: The prompt to send to Claude
            temperature: Sampling temperature
            
        Returns:
            Generated scouting report
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=temperature,
                system="You are an expert hockey scout specializing in player movement analysis.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def generate_score(self, prompt: str) -> int:
        """
        Generate a numeric score (0-100) using Anthropic Claude.
        
        Args:
            prompt: The prompt describing the player's performance
            
        Returns:
            Score between 0 and 100
        """
        scoring_prompt = f"{prompt}\n\nBased on the above analysis, provide ONLY a numeric score from 0-100 (integer only, no explanation):"
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                temperature=0.3,
                system="You are a hockey scout providing numeric scores. Return only the integer score.",
                messages=[
                    {"role": "user", "content": scoring_prompt}
                ]
            )
            
            score_text = message.content[0].text.strip()
            # Extract first number found
            match = re.search(r'\d+', score_text)
            if match:
                score = int(match.group())
                return max(0, min(100, score))  # Clamp to 0-100
            return 50  # Default score if parsing fails
            
        except Exception as e:
            print(f"Error generating score: {str(e)}")
            return 50
