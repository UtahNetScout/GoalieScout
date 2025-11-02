"""
AI Provider Module - Supports multiple AI providers
Alternatives to OpenAI for cost reduction and flexibility
"""

import os
from typing import Optional
import requests

class AIProvider:
    """Base class for AI providers"""
    
    def generate_scouting_report(self, goalie_data: dict) -> str:
        """Generate a scouting report for a goalie"""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 provider"""
    
    def __init__(self, api_key: str):
        import openai
        self.api_key = api_key
        openai.api_key = api_key
        
    def generate_scouting_report(self, goalie_data: dict) -> str:
        import openai
        prompt = self._create_prompt(goalie_data)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[!] OpenAI error: {e}")
            return ""
    
    def _create_prompt(self, goalie_data: dict) -> str:
        return f"""
        Write a concise professional scouting report for {goalie_data['name']}, 
        a goalie from {goalie_data.get('team', 'Unknown')} in the {goalie_data.get('league', 'Unknown')} league.
        Include strengths, weaknesses, comparable NHL goalies, and tier 
        (Top Prospect / Sleeper / Watch / Red Flag). Assign a numerical score 0-100.
        """


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider - often cheaper than OpenAI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.anthropic.com/v1/messages"
        
    def generate_scouting_report(self, goalie_data: dict) -> str:
        prompt = self._create_prompt(goalie_data)
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                print(f"[!] Anthropic error: {response.status_code}")
                return ""
        except Exception as e:
            print(f"[!] Anthropic error: {e}")
            return ""
    
    def _create_prompt(self, goalie_data: dict) -> str:
        return f"""
        Write a concise professional scouting report for {goalie_data['name']}, 
        a goalie from {goalie_data.get('team', 'Unknown')} in the {goalie_data.get('league', 'Unknown')} league.
        Include strengths, weaknesses, comparable NHL goalies, and tier 
        (Top Prospect / Sleeper / Watch / Red Flag). Assign a numerical score 0-100.
        """


class OllamaProvider(AIProvider):
    """Ollama local LLM provider - FREE and private!"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        
    def generate_scouting_report(self, goalie_data: dict) -> str:
        prompt = self._create_prompt(goalie_data)
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"[!] Ollama error: {response.status_code}")
                return ""
        except Exception as e:
            print(f"[!] Ollama error: {e}")
            return ""
    
    def _create_prompt(self, goalie_data: dict) -> str:
        return f"""
        Write a concise professional scouting report for {goalie_data['name']}, 
        a goalie from {goalie_data.get('team', 'Unknown')} in the {goalie_data.get('league', 'Unknown')} league.
        Include strengths, weaknesses, comparable NHL goalies, and tier 
        (Top Prospect / Sleeper / Watch / Red Flag). Assign a numerical score 0-100.
        """


def get_ai_provider(provider_type: str = "openai") -> Optional[AIProvider]:
    """Factory function to get AI provider"""
    
    provider_type = provider_type.lower()
    
    if provider_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "YOUR_OPENAI_API_KEY":
            print("[!] OpenAI API key not set")
            return None
        return OpenAIProvider(api_key)
    
    elif provider_type == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("[!] Anthropic API key not set")
            return None
        return AnthropicProvider(api_key)
    
    elif provider_type == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")
        return OllamaProvider(base_url, model)
    
    else:
        print(f"[!] Unknown provider: {provider_type}")
        return None
