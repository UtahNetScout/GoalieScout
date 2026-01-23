"""
Scouting Report Generator
Generates AI-powered scouting reports, scores, tiers, and rankings.
"""
import json
from typing import Dict, Any, List
from src.ai_providers import AIProvider


class ReportGenerator:
    """Generate scouting reports using AI providers."""
    
    def __init__(self, ai_provider: AIProvider):
        """
        Initialize the report generator.
        
        Args:
            ai_provider: AI provider instance for report generation
        """
        self.ai_provider = ai_provider
    
    def generate_player_prompt(self, player_name: str, position: str, 
                               metrics: Dict[str, Any]) -> str:
        """
        Generate a prompt for the AI to analyze a player.
        
        Args:
            player_name: Name of the player
            position: Player's position
            metrics: Dictionary of calculated metrics
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze the following hockey player's movement performance:

Player: {player_name}
Position: {position}

Movement Metrics:
- Total Distance Traveled: {metrics.get('total_distance', 0):.2f} units
- Average Speed: {metrics.get('average_speed', 0):.2f} units/sec
- Maximum Speed: {metrics.get('max_speed', 0):.2f} units/sec
- Direction Changes: {metrics.get('direction_changes', 0)}
- On-Puck Carrying Distance: {metrics.get('on_puck_distance', 0):.2f} units
- Space Creation: {metrics.get('space_creation', 0):.2f} units
- Events: {metrics.get('events_count', 0)}
"""
        
        # Add position-specific metrics
        if position.upper() in ['G', 'GOALIE', 'GOALKEEPER']:
            prompt += f"""
Goalie-Specific Metrics:
- Crease Movement: {metrics.get('crease_movement', 0):.2f}
- Lateral Movement: {metrics.get('lateral_movement', 0):.2f}
"""
        elif position.upper() in ['D', 'DEFENSE', 'DEFENSEMAN']:
            prompt += f"""
Defenseman-Specific Metrics:
- Gap Control: {metrics.get('gap_control', 0):.2f}
"""
        elif position.upper() in ['F', 'FORWARD']:
            prompt += f"""
Forward-Specific Metrics:
- High-Danger Positioning: {metrics.get('high_danger_positioning', 0):.2f}
"""
        
        prompt += """
Provide a brief scouting report (3-5 sentences) focusing on:
1. Movement efficiency and skating ability
2. Positioning and spatial awareness
3. Key strengths and areas for improvement
4. Overall assessment of their movement contribution to team play
"""
        
        return prompt
    
    def generate_player_report(self, player_name: str, position: str, 
                              metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete scouting report for a player.
        
        Args:
            player_name: Name of the player
            position: Player's position
            metrics: Dictionary of calculated metrics
            
        Returns:
            Dictionary containing report, score, tier
        """
        # Generate the scouting notes
        prompt = self.generate_player_prompt(player_name, position, metrics)
        scouting_notes = self.ai_provider.generate_report(prompt)
        
        # Generate a score
        score = self.ai_provider.generate_score(prompt)
        
        # Determine tier based on score
        tier = self._score_to_tier(score)
        
        return {
            'player_name': player_name,
            'position': position,
            'metrics': metrics,
            'scouting_notes': scouting_notes,
            'score': score,
            'tier': tier
        }
    
    @staticmethod
    def _score_to_tier(score: int) -> str:
        """
        Convert a numeric score to a tier rating.
        
        Args:
            score: Score from 0-100
            
        Returns:
            Tier rating (S, A, B, C, D, or F)
        """
        if score >= 90:
            return 'S'  # Elite
        elif score >= 80:
            return 'A'  # Excellent
        elif score >= 70:
            return 'B'  # Good
        elif score >= 60:
            return 'C'  # Average
        elif score >= 50:
            return 'D'  # Below Average
        else:
            return 'F'  # Poor
    
    def rank_players(self, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank players by their scores.
        
        Args:
            reports: List of player reports
            
        Returns:
            Sorted list of player reports with rankings
        """
        # Sort by score descending
        sorted_reports = sorted(reports, key=lambda x: x['score'], reverse=True)
        
        # Add rankings
        for rank, report in enumerate(sorted_reports, 1):
            report['rank'] = rank
        
        return sorted_reports
    
    def generate_summary(self, ranked_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of all player reports.
        
        Args:
            ranked_reports: List of ranked player reports
            
        Returns:
            Summary dictionary
        """
        if not ranked_reports:
            return {
                'total_players': 0,
                'tier_distribution': {},
                'top_3_players': []
            }
        
        # Count tier distribution
        tier_counts = {}
        for report in ranked_reports:
            tier = report['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        # Get top 3 players
        top_3 = [
            {
                'rank': report['rank'],
                'name': report['player_name'],
                'position': report['position'],
                'score': report['score'],
                'tier': report['tier']
            }
            for report in ranked_reports[:3]
        ]
        
        return {
            'total_players': len(ranked_reports),
            'tier_distribution': tier_counts,
            'top_3_players': top_3,
            'average_score': sum(r['score'] for r in ranked_reports) / len(ranked_reports)
        }
    
    def save_reports_json(self, ranked_reports: List[Dict[str, Any]], 
                         summary: Dict[str, Any], output_path: str):
        """
        Save reports to a JSON file.
        
        Args:
            ranked_reports: List of ranked player reports
            summary: Summary statistics
            output_path: Path to save the JSON file
        """
        output_data = {
            'summary': summary,
            'player_reports': ranked_reports
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Reports saved to: {output_path}")
