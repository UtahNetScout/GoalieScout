"""
AI Provider Factory
Creates the appropriate AI provider based on configuration.
"""
from typing import Dict, Any

from . import AIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider


def get_ai_provider(provider_name: str, config: Dict[str, Any]) -> AIProvider:
    """
    Factory function to get the appropriate AI provider.
    
    Args:
        provider_name: Name of the provider ('openai', 'anthropic', or 'ollama')
        config: Configuration dictionary
        
    Returns:
        Instance of the requested AI provider
        
    Raises:
        ValueError: If provider_name is not recognized
    """
    provider_name = provider_name.lower()
    
    if provider_name == 'openai':
        return OpenAIProvider(config)
    elif provider_name == 'anthropic':
        return AnthropicProvider(config)
    elif provider_name == 'ollama':
        return OllamaProvider(config)
    else:
        raise ValueError(
            f"Unknown AI provider: {provider_name}. "
            f"Must be one of: 'openai', 'anthropic', 'ollama'"
        )
