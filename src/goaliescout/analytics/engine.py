"""Analytics tools for goalie performance analysis."""

from typing import List, Dict, Any, Optional
import statistics
import logging

from ..data.models import GoalieProfile, PerformanceMetrics

logger = logging.getLogger(__name__)


class GoalieAnalytics:
    """Analytics suite for goalie performance evaluation."""
    
    @staticmethod
    def calculate_career_stats(profile: GoalieProfile) -> Dict[str, float]:
        """Calculate career statistics.
        
        Args:
            profile: GoalieProfile object
            
        Returns:
            Dictionary of career statistics
        """
        metrics = profile.performance_metrics
        
        if not metrics:
            return {
                'career_games': 0,
                'career_wins': 0,
                'career_save_percentage': 0.0,
                'career_gaa': 0.0,
                'career_shutouts': 0
            }
        
        total_games = sum(m.games_played for m in metrics)
        total_wins = sum(m.wins for m in metrics)
        total_shutouts = sum(m.shutouts for m in metrics)
        
        # Weighted average for save percentage
        total_shots = sum(m.shots_against for m in metrics)
        total_saves = sum(m.saves for m in metrics)
        avg_sv_pct = (total_saves / total_shots) if total_shots > 0 else 0.0
        
        # Weighted average for GAA
        total_minutes = sum(m.minutes_played for m in metrics)
        total_goals = sum(m.goals_against for m in metrics)
        avg_gaa = (total_goals * 60 / total_minutes) if total_minutes > 0 else 0.0
        
        return {
            'career_games': total_games,
            'career_wins': total_wins,
            'career_save_percentage': avg_sv_pct,
            'career_gaa': avg_gaa,
            'career_shutouts': total_shutouts
        }
    
    @staticmethod
    def compare_to_league_average(profile: GoalieProfile, league_avg: Dict[str, float]) -> Dict[str, float]:
        """Compare goalie stats to league averages.
        
        Args:
            profile: GoalieProfile object
            league_avg: Dictionary of league average statistics
            
        Returns:
            Dictionary of comparison results
        """
        career_stats = GoalieAnalytics.calculate_career_stats(profile)
        
        comparison = {}
        for key, value in career_stats.items():
            if key in league_avg:
                comparison[f"{key}_vs_avg"] = value - league_avg[key]
                comparison[f"{key}_pct_vs_avg"] = ((value / league_avg[key]) - 1) * 100 if league_avg[key] > 0 else 0
        
        return comparison
    
    @staticmethod
    def rank_goalies(goalies: List[GoalieProfile], metric: str = 'save_percentage') -> List[Dict[str, Any]]:
        """Rank goalies by a specific metric.
        
        Args:
            goalies: List of GoalieProfile objects
            metric: Metric to rank by
            
        Returns:
            Sorted list with rankings
        """
        rankings = []
        
        for goalie in goalies:
            career_stats = GoalieAnalytics.calculate_career_stats(goalie)
            
            rankings.append({
                'player_id': goalie.player_id,
                'name': goalie.demographics.name,
                'league': goalie.league,
                metric: career_stats.get(f'career_{metric}', 0),
                'career_stats': career_stats
            })
        
        # Sort by metric (descending for most metrics)
        reverse = metric != 'gaa'  # GAA is better when lower
        rankings.sort(key=lambda x: x.get(metric, 0), reverse=reverse)
        
        # Add rank
        for i, ranking in enumerate(rankings, 1):
            ranking['rank'] = i
        
        return rankings
    
    @staticmethod
    def calculate_trend(metrics: List[PerformanceMetrics], stat: str) -> Dict[str, Any]:
        """Calculate trend for a specific statistic.
        
        Args:
            metrics: List of PerformanceMetrics
            stat: Statistic name
            
        Returns:
            Trend analysis
        """
        if not metrics:
            return {'trend': 'unknown', 'values': []}
        
        values = [getattr(m, stat, 0) for m in sorted(metrics, key=lambda x: x.season or '')]
        
        if len(values) < 2:
            return {'trend': 'insufficient_data', 'values': values}
        
        # Simple trend calculation
        first_half_avg = statistics.mean(values[:len(values)//2])
        second_half_avg = statistics.mean(values[len(values)//2:])
        
        if second_half_avg > first_half_avg * 1.05:
            trend = 'improving'
        elif second_half_avg < first_half_avg * 0.95:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'values': values,
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg,
            'change_pct': ((second_half_avg / first_half_avg) - 1) * 100 if first_half_avg > 0 else 0
        }
    
    @staticmethod
    def injury_risk_assessment(profile: GoalieProfile) -> Dict[str, Any]:
        """Assess injury risk based on history.
        
        Args:
            profile: GoalieProfile object
            
        Returns:
            Injury risk assessment
        """
        injuries = profile.injury_history
        
        if not injuries:
            return {
                'risk_level': 'low',
                'total_injuries': 0,
                'recent_injuries': 0,
                'severity_score': 0
            }
        
        total_injuries = len(injuries)
        
        # Count recent injuries (placeholder logic)
        recent_injuries = sum(1 for inj in injuries if inj.status in ['Active', 'Ongoing'])
        
        # Calculate severity score
        severity_map = {'Minor': 1, 'Moderate': 2, 'Severe': 3}
        severity_score = sum(severity_map.get(inj.severity, 1) for inj in injuries)
        
        # Determine risk level
        if recent_injuries > 0 or severity_score > 5:
            risk_level = 'high'
        elif total_injuries > 3 or severity_score > 3:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'total_injuries': total_injuries,
            'recent_injuries': recent_injuries,
            'severity_score': severity_score
        }
    
    @staticmethod
    def nhl_readiness_score(profile: GoalieProfile) -> Dict[str, Any]:
        """Calculate NHL readiness score.
        
        Args:
            profile: GoalieProfile object
            
        Returns:
            NHL readiness assessment
        """
        career_stats = GoalieAnalytics.calculate_career_stats(profile)
        
        # Scoring factors (placeholder logic)
        score = 0
        factors = []
        
        # Save percentage
        if career_stats['career_save_percentage'] > 0.920:
            score += 30
            factors.append('Excellent save percentage')
        elif career_stats['career_save_percentage'] > 0.900:
            score += 20
            factors.append('Good save percentage')
        elif career_stats['career_save_percentage'] > 0.880:
            score += 10
            factors.append('Average save percentage')
        
        # Games played
        if career_stats['career_games'] > 100:
            score += 25
            factors.append('Extensive experience')
        elif career_stats['career_games'] > 50:
            score += 15
            factors.append('Good experience')
        elif career_stats['career_games'] > 25:
            score += 5
            factors.append('Moderate experience')
        
        # Win percentage
        win_pct = career_stats['career_wins'] / career_stats['career_games'] if career_stats['career_games'] > 0 else 0
        if win_pct > 0.6:
            score += 20
            factors.append('Strong win record')
        elif win_pct > 0.5:
            score += 10
            factors.append('Decent win record')
        
        # Injury risk
        injury_risk = GoalieAnalytics.injury_risk_assessment(profile)
        if injury_risk['risk_level'] == 'low':
            score += 15
            factors.append('Low injury risk')
        elif injury_risk['risk_level'] == 'moderate':
            score += 5
            factors.append('Moderate injury risk')
        
        # AI analysis
        if profile.ai_analysis:
            if profile.ai_analysis.nhl_readiness in ['Ready', 'NHL Caliber']:
                score += 10
                factors.append('AI assessment positive')
        
        # Determine readiness level
        if score >= 80:
            readiness = 'NHL Ready'
        elif score >= 60:
            readiness = 'Close to NHL Ready'
        elif score >= 40:
            readiness = 'Developing'
        else:
            readiness = 'Needs Development'
        
        return {
            'readiness_score': score,
            'readiness_level': readiness,
            'contributing_factors': factors
        }


class ComparisonEngine:
    """Engine for comparing goalies."""
    
    @staticmethod
    def compare_goalies(goalie1: GoalieProfile, goalie2: GoalieProfile) -> Dict[str, Any]:
        """Compare two goalies side-by-side.
        
        Args:
            goalie1: First goalie profile
            goalie2: Second goalie profile
            
        Returns:
            Comparison results
        """
        stats1 = GoalieAnalytics.calculate_career_stats(goalie1)
        stats2 = GoalieAnalytics.calculate_career_stats(goalie2)
        
        comparison = {
            'goalie1': {
                'name': goalie1.demographics.name,
                'stats': stats1
            },
            'goalie2': {
                'name': goalie2.demographics.name,
                'stats': stats2
            },
            'differences': {}
        }
        
        for key in stats1:
            diff = stats1[key] - stats2[key]
            comparison['differences'][key] = {
                'value': diff,
                'advantage': 'goalie1' if diff > 0 else 'goalie2' if diff < 0 else 'equal'
            }
        
        return comparison
    
    @staticmethod
    def find_similar_nhl_goalies(profile: GoalieProfile, nhl_goalies: List[GoalieProfile], top_n: int = 5) -> List[Dict[str, Any]]:
        """Find NHL goalies with similar playing style/stats.
        
        Args:
            profile: Goalie profile to compare
            nhl_goalies: List of NHL goalie profiles
            top_n: Number of similar goalies to return
            
        Returns:
            List of similar goalies with similarity scores
        """
        target_stats = GoalieAnalytics.calculate_career_stats(profile)
        
        similarities = []
        
        for nhl_goalie in nhl_goalies:
            nhl_stats = GoalieAnalytics.calculate_career_stats(nhl_goalie)
            
            # Calculate similarity score (simple euclidean distance)
            sv_pct_diff = abs(target_stats['career_save_percentage'] - nhl_stats['career_save_percentage'])
            gaa_diff = abs(target_stats['career_gaa'] - nhl_stats['career_gaa'])
            
            # Normalize and combine
            similarity_score = 100 - (sv_pct_diff * 1000 + gaa_diff * 10)
            similarity_score = max(0, min(100, similarity_score))
            
            similarities.append({
                'nhl_goalie': nhl_goalie.demographics.name,
                'similarity_score': similarity_score,
                'comparison': {
                    'save_percentage_diff': sv_pct_diff,
                    'gaa_diff': gaa_diff
                }
            })
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:top_n]
