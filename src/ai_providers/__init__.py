"""
AI Provider Base Class
Defines the interface for all AI providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AI provider.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        self.config = config
    
    @abstractmethod
    def generate_report(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a scouting report using the AI provider.
        
        Args:
            prompt: The prompt to send to the AI
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def generate_score(self, prompt: str) -> int:
        """
        Generate a numeric score (0-100) using the AI provider.
        
        Args:
            prompt: The prompt describing the player's performance
            
        Returns:
            Score between 0 and 100
        """
        pass
