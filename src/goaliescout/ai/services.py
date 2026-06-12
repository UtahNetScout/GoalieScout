"""AI service integrations for goalie analysis."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os
import logging

logger = logging.getLogger(__name__)


class AIService(ABC):
    """Abstract base class for AI services."""
    
    @abstractmethod
    def analyze_goalie(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goalie performance and generate insights.
        
        Args:
            profile_data: Dictionary containing goalie profile data
            
        Returns:
            Dictionary with AI analysis results
        """
        pass
    
    @abstractmethod
    def generate_scouting_report(self, profile_data: Dict[str, Any]) -> str:
        """Generate a detailed scouting report.
        
        Args:
            profile_data: Dictionary containing goalie profile data
            
        Returns:
            Formatted scouting report text
        """
        pass
    
    @abstractmethod
    def rank_goalies(self, goalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank multiple goalies based on performance.
        
        Args:
            goalies: List of goalie profile dictionaries
            
        Returns:
            Sorted list with rankings
        """
        pass


class OpenAIService(AIService):
    """OpenAI GPT-4 integration for premium analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OpenAI API key not provided")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        except ImportError:
            logger.error("openai package not installed")
            self.client = None
    
    def analyze_goalie(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goalie using GPT-4."""
        if not self.client:
            return self._fallback_analysis(profile_data)
        
        try:
            # Prepare analysis prompt
            prompt = self._create_analysis_prompt(profile_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert hockey goalie scout with deep knowledge of player evaluation and development."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_analysis(analysis_text)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_analysis(profile_data)
    
    def generate_scouting_report(self, profile_data: Dict[str, Any]) -> str:
        """Generate an evidence-grounded scouting report using GPT-4."""
        if not self.client:
            return self._fallback_report(profile_data)
        
        try:
            prompt = self._create_report_prompt(profile_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a hockey decision-support analyst. Use only the "
                            "supplied evidence, distinguish facts from interpretation, "
                            "and state when video or additional data is required."
                        ),
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_report(profile_data)
    
    def rank_goalies(self, goalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank goalies using AI analysis."""
        # Add AI-powered ranking logic
        for goalie in goalies:
            analysis = self.analyze_goalie(goalie)
            goalie['ai_ranking_score'] = analysis.get('overall_rating', 0)
        
        return sorted(goalies, key=lambda x: x.get('ai_ranking_score', 0), reverse=True)
    
    def _create_analysis_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Create prompt for goalie analysis including advanced metrics."""
        demographics = profile_data.get('demographics', {})
        metrics = profile_data.get('performance_metrics', [])
        advanced = profile_data.get('advanced_metrics', {})

        advanced_section = ""
        if advanced:
            advanced_section = f"""
Advanced Analytics:
- Black Ops Score: {advanced.get('black_ops_score', 'N/A')}
- GSAx (Goals Saved Above Expected): {advanced.get('gsax', 'N/A')}
- High-Danger SV%: {advanced.get('hd_sv_pct', 'N/A')}
- Rebound Control Rate: {advanced.get('controlled_rebound_rate', 'N/A')}
- Consistency Score: {advanced.get('consistency_score', 'N/A')}
- Rush Save%: {advanced.get('rush_sv_pct', 'N/A')}
"""

        prompt = f"""Analyze the following hockey goalie:

Name: {demographics.get('name', 'Unknown')}
Country: {demographics.get('country', 'Unknown')}
League: {profile_data.get('league', 'Unknown')}

Performance Metrics:
{self._format_metrics(metrics)}
{advanced_section}
Please provide:
1. Overall rating (0-100)
2. Top 3 strengths
3. Top 3 weaknesses
4. Potential rating (0-100)
5. NHL readiness assessment
6. Brief scouting notes

Format your response as JSON."""
        return prompt

    def _create_report_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Create a grounded prompt for scouting report generation."""
        demographics = profile_data.get('demographics', {})
        advanced = profile_data.get('advanced_metrics', {})
        metrics = profile_data.get('performance_metrics', [])
        achievements = profile_data.get('notable_achievements', [])
        comparisons = profile_data.get('nhl_comparisons', [])
        stored_analysis = profile_data.get('ai_analysis') or {}
        sources = profile_data.get('data_sources', [])

        advanced_section = ""
        if advanced:
            advanced_section = f"""
Key Advanced Metrics:
- Black Ops Score: {advanced.get('black_ops_score', 'N/A')} / 100
- GSAx: {advanced.get('gsax', 'N/A')} (Goals Saved Above Expected)
- High-Danger SV%: {advanced.get('hd_sv_pct', 'N/A')}
- Rebound Control: {advanced.get('controlled_rebound_rate', 'N/A')}
- Performance Consistency Score: {advanced.get('consistency_score', 'N/A')}
"""

        return f"""Create an evidence-grounded decision-support report in Markdown.

PLAYER RECORD
- Name: {demographics.get('name', 'Unknown')}
- Team: {profile_data.get('current_team', 'Unknown')}
- League: {profile_data.get('league', 'Unknown')}
- Country: {demographics.get('country', 'Unknown')}
- Date of birth: {demographics.get('date_of_birth', 'Unknown')}
- Height: {demographics.get('height', 'Unknown')}
- Weight: {demographics.get('weight', 'Unknown')}
- Catches: {demographics.get('catches', 'Unknown')}
- Dataset last updated: {profile_data.get('last_updated', 'Unknown')}

SEASON STATISTICS
{self._format_metrics(metrics)}

NOTABLE ACHIEVEMENTS
{self._format_list(achievements)}

CURATED EVALUATION CONTEXT
- Rating: {stored_analysis.get('overall_rating', 'N/A')} / 100
- Readiness: {stored_analysis.get('nhl_readiness', 'Not assessed')}
- Strengths: {self._format_list(stored_analysis.get('strengths', []))}
- Risks or limitations: {self._format_list(stored_analysis.get('weaknesses', []))}
- Notes: {stored_analysis.get('scouting_notes', 'No curated notes available')}

COMPARISON CONTEXT
{self._format_comparisons(comparisons)}
{advanced_section}

DATA SOURCES
{self._format_list(sources)}

REQUIRED OUTPUT
## Executive Summary
Give a concise assessment tied to the supplied season and career context.

## Evidence Snapshot
Use a compact Markdown table of supplied statistics and achievements.

## Evidence-Based Strengths
Explain only strengths supported by the supplied evidence. Label curated
scouting observations as interpretation, not measured fact.

## Risks and Open Questions
Identify sample-size, freshness, playoff, workload, missing-data, or validation
questions supported by the record.

## Decision Recommendation
State the likely role and the next decision a hockey organization could make.
Do not describe an established NHL player as a prospect or use a development
projection unless the supplied record supports it.

## Human Review Checklist
List claims that require video review or additional tracking data.

GROUNDING RULES
- Do not invent statistics, awards, injuries, contract facts, current-season
  results, or biographical details.
- Do not claim mental toughness, body language, anticipation, flexibility,
  rebound control, movement quality, or puck handling as observed facts unless
  those traits are explicitly supplied.
- Do not imply the dataset is current beyond its last-updated timestamp.
- When evidence is missing, say "not established by the available data."
- Keep the report under 700 words and avoid generic praise.

The report supports human review and does not replace video scouting,
medical evaluation, or professional judgment."""

    @staticmethod
    def _format_list(items: List[Any]) -> str:
        """Format values as Markdown bullets without inventing content."""
        if not items:
            return "- Not available"
        return "\n".join(f"- {item}" for item in items)

    @staticmethod
    def _format_comparisons(comparisons: List[Dict[str, Any]]) -> str:
        """Format supplied player comparisons for the report prompt."""
        if not comparisons:
            return "- Not available"
        return "\n".join(
            (
                f"- {item.get('comparable_player', 'Unknown')}: "
                f"{item.get('similarity_score', 'N/A')} similarity; "
                f"{item.get('comparison_notes', 'no notes')}"
            )
            for item in comparisons
        )
    
    def _format_metrics(self, metrics: List[Dict[str, Any]]) -> str:
        """Format performance metrics for prompt."""
        if not metrics:
            return "No metrics available"
        
        formatted = []
        for m in metrics[:3]:  # Last 3 seasons
            formatted.append(
                f"Season {m.get('season', 'N/A')}: "
                f"GP={m.get('games_played', 0)}, "
                f"SV%={m.get('save_percentage', 0):.3f}, "
                f"GAA={m.get('goals_against_average', 0):.2f}"
            )
        return "\n".join(formatted)
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse AI analysis response."""
        # Simple parsing - in production, would use structured output
        return {
            'overall_rating': 75.0,
            'strengths': ['Quick reflexes', 'Good positioning', 'Strong fundamentals'],
            'weaknesses': ['Rebound control', 'Playing the puck', 'Consistency'],
            'potential_rating': 80.0,
            'nhl_readiness': 'Developing',
            'scouting_notes': analysis_text
        }
    
    def _fallback_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when API is unavailable."""
        metrics = profile_data.get('performance_metrics', [])
        avg_sv_pct = sum(m.get('save_percentage', 0) for m in metrics) / len(metrics) if metrics else 0
        
        return {
            'overall_rating': min(avg_sv_pct * 100, 100),
            'strengths': ['Good fundamentals'],
            'weaknesses': ['Needs more data'],
            'potential_rating': 70.0,
            'nhl_readiness': 'Unknown',
            'scouting_notes': 'AI analysis unavailable - using basic metrics'
        }
    
    def _fallback_report(self, profile_data: Dict[str, Any]) -> str:
        """Build an evidence-only report when the API is unavailable."""
        demographics = profile_data.get('demographics', {})
        metrics = profile_data.get('performance_metrics', [])
        latest = metrics[-1] if metrics else {}
        achievements = profile_data.get('notable_achievements', [])
        sources = profile_data.get('data_sources', [])
        analysis = profile_data.get('ai_analysis') or {}

        return f"""## Executive Summary

{demographics.get('name', 'Unknown')} is listed as a
{analysis.get('nhl_readiness', 'goalie with an unassessed role')} for the
{profile_data.get('current_team', 'unknown team')}. This evidence-only fallback
uses the stored dataset because live AI analysis is unavailable.

## Evidence Snapshot

| Field | Available value |
| --- | --- |
| Season | {latest.get('season', 'Not available')} |
| Games played | {latest.get('games_played', 'Not available')} |
| Record | {latest.get('wins', 0)}-{latest.get('losses', 0)}-{latest.get('overtime_losses', 0)} |
| Save percentage | {latest.get('save_percentage', 'Not available')} |
| Goals-against average | {latest.get('goals_against_average', 'Not available')} |
| Dataset updated | {profile_data.get('last_updated', 'Unknown')} |

## Notable Achievements

{self._format_list(achievements)}

## Decision Recommendation

Review the supplied season record and curated evaluation context, then validate
technical and mental-game claims through video and additional tracking data.

## Human Review Checklist

- Validate movement, rebound control, and puck-handling observations on video.
- Confirm the latest available season and award information.
- Compare performance against relevant peers and playoff samples.

## Sources

{self._format_list(sources)}

_AI service unavailable. No new scouting claims were generated._
"""


class AnthropicService(AIService):
    """Anthropic Claude integration for cost-effective analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic service.
        
        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("Anthropic API key not provided")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        except ImportError:
            logger.error("anthropic package not installed")
            self.client = None
    
    def analyze_goalie(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goalie using Claude."""
        if not self.client:
            return self._fallback_analysis(profile_data)
        
        try:
            prompt = self._create_analysis_prompt(profile_data)
            
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return self._parse_analysis(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._fallback_analysis(profile_data)
    
    def generate_scouting_report(self, profile_data: Dict[str, Any]) -> str:
        """Generate scouting report using Claude."""
        if not self.client:
            return "Anthropic API unavailable"
        
        try:
            prompt = f"Generate a professional hockey goalie scouting report for: {profile_data}"
            
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return "Error generating report"
    
    def rank_goalies(self, goalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank goalies."""
        for goalie in goalies:
            analysis = self.analyze_goalie(goalie)
            goalie['ai_ranking_score'] = analysis.get('overall_rating', 0)
        
        return sorted(goalies, key=lambda x: x.get('ai_ranking_score', 0), reverse=True)
    
    def _create_analysis_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Create analysis prompt."""
        return f"Analyze this goalie and provide ratings: {profile_data}"
    
    def _parse_analysis(self, text: str) -> Dict[str, Any]:
        """Parse analysis response."""
        return {
            'overall_rating': 75.0,
            'strengths': ['Good technique'],
            'weaknesses': ['Needs improvement'],
            'potential_rating': 75.0,
            'nhl_readiness': 'Developing',
            'scouting_notes': text
        }
    
    def _fallback_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis."""
        return {
            'overall_rating': 70.0,
            'strengths': ['Basic analysis'],
            'weaknesses': ['Limited data'],
            'potential_rating': 70.0,
            'nhl_readiness': 'Unknown',
            'scouting_notes': 'Anthropic API unavailable'
        }


class OllamaService(AIService):
    """Ollama local LLM integration for zero-cost analysis."""
    
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        """Initialize Ollama service.
        
        Args:
            host: Ollama server host
            model: Model name to use
        """
        self.host = host or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama2')
        
        try:
            import ollama
            self.client = ollama
        except ImportError:
            logger.error("ollama package not installed")
            self.client = None
    
    def analyze_goalie(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goalie using local LLM."""
        if not self.client:
            return self._fallback_analysis(profile_data)
        
        try:
            prompt = f"Analyze this goalie and provide a rating: {profile_data}"
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt
            )
            
            return self._parse_analysis(response.get('response', ''))
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return self._fallback_analysis(profile_data)
    
    def generate_scouting_report(self, profile_data: Dict[str, Any]) -> str:
        """Generate scouting report using local LLM."""
        if not self.client:
            return "Ollama unavailable"
        
        try:
            prompt = f"Generate a goalie scouting report: {profile_data}"
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt
            )
            
            return response.get('response', 'No response')
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return "Error generating report"
    
    def rank_goalies(self, goalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank goalies."""
        for goalie in goalies:
            analysis = self.analyze_goalie(goalie)
            goalie['ai_ranking_score'] = analysis.get('overall_rating', 0)
        
        return sorted(goalies, key=lambda x: x.get('ai_ranking_score', 0), reverse=True)
    
    def _parse_analysis(self, text: str) -> Dict[str, Any]:
        """Parse analysis response."""
        return {
            'overall_rating': 70.0,
            'strengths': ['Local analysis'],
            'weaknesses': ['Limited capabilities'],
            'potential_rating': 70.0,
            'nhl_readiness': 'Unknown',
            'scouting_notes': text
        }
    
    def _fallback_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis."""
        return {
            'overall_rating': 65.0,
            'strengths': ['Basic evaluation'],
            'weaknesses': ['No AI available'],
            'potential_rating': 65.0,
            'nhl_readiness': 'Unknown',
            'scouting_notes': 'Ollama unavailable'
        }


def get_ai_service(service_type: str = 'openai') -> AIService:
    """Factory function to get AI service instance.
    
    Args:
        service_type: Type of AI service ('openai', 'anthropic', 'ollama')
        
    Returns:
        AIService instance
    """
    service_type = service_type.lower()
    
    if service_type == 'openai':
        return OpenAIService()
    elif service_type == 'anthropic':
        return AnthropicService()
    elif service_type == 'ollama':
        return OllamaService()
    else:
        logger.warning(f"Unknown service type: {service_type}, defaulting to OpenAI")
        return OpenAIService()
