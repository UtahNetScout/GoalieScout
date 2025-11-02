"""
Enhanced Data Collection Module
Collects additional stats, videos, social profiles, and draft eligibility
"""

import re
import requests
from typing import Dict, List, Optional
from datetime import datetime


class EnhancedDataCollector:
    """Collect enhanced data for goalie prospects"""
    
    def __init__(self):
        self.youtube_api_key = None  # Set via environment if available
        
    def collect_stats(self, goalie: Dict) -> Dict:
        """
        Collect goalie statistics (placeholder - would integrate with real stats APIs)
        In production, integrate with EliteProspects, HockeyDB, or league APIs
        """
        # Placeholder stats - in production, scrape from actual sources
        stats = {
            "games_played": 0,
            "save_percentage": 0.0,
            "goals_against_average": 0.0,
            "shutouts": 0,
            "wins": 0,
            "losses": 0,
            "season": "2024-25"
        }
        
        # TODO: Implement actual stats scraping based on league
        # Example sources:
        # - EliteProspects API
        # - NHL API for NCAA/junior stats
        # - League-specific websites
        
        return stats
    
    def find_youtube_highlights(self, goalie_name: str, team: str = "") -> List[str]:
        """
        Search YouTube for goalie highlight videos
        Returns list of YouTube video URLs
        """
        video_links = []
        
        try:
            # Construct search query
            query = f"{goalie_name} goalie highlights"
            if team:
                query += f" {team}"
            
            # In production, use YouTube Data API v3
            # For now, construct search URLs
            search_query = query.replace(" ", "+")
            search_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            # Placeholder - would use YouTube API to get actual video IDs
            video_links.append(search_url)
            
            # TODO: Implement YouTube API integration
            # from googleapiclient.discovery import build
            # youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            # search_response = youtube.search().list(q=query, part='id,snippet', maxResults=5).execute()
            
        except Exception as e:
            print(f"[!] Error finding YouTube highlights: {e}")
        
        return video_links
    
    def find_social_profiles(self, goalie_name: str) -> Dict[str, str]:
        """
        Find social media profiles (placeholder)
        In production, would use social media APIs or search
        """
        profiles = {
            "twitter": "",
            "instagram": "",
            "elite_prospects": ""
        }
        
        # Clean name for URL construction
        clean_name = goalie_name.lower().replace(" ", "-")
        
        # Construct likely profile URLs (would verify in production)
        profiles["elite_prospects"] = f"https://www.eliteprospects.com/search/player?name={goalie_name.replace(' ', '+')}"
        
        # TODO: Implement social media search/scraping
        # - Twitter API search
        # - Instagram graph API
        # - Elite Prospects scraping
        
        return profiles
    
    def calculate_draft_eligibility(self, dob: str) -> Dict:
        """
        Calculate NHL draft eligibility based on date of birth
        """
        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            current_year = datetime.now().year
            birth_year = birth_date.year
            
            # NHL draft eligibility: Must turn 18 by September 15 of draft year
            # First eligible draft is the year they turn 18
            draft_year = birth_year + 18
            
            # Check if already drafted or upcoming
            if current_year < draft_year:
                status = "Future Eligible"
                years_until = draft_year - current_year
                note = f"Eligible in {draft_year} ({years_until} year{'s' if years_until > 1 else ''} from now)"
            elif current_year == draft_year:
                status = "Draft Eligible"
                note = f"Eligible for {draft_year} NHL Draft"
            elif current_year == draft_year + 1:
                status = "Recently Eligible"
                note = f"Was eligible in {draft_year}, re-entry possible"
            else:
                status = "Past Eligible"
                years_since = current_year - draft_year
                note = f"Eligible since {draft_year} ({years_since} year{'s' if years_since > 1 else ''} ago)"
            
            return {
                "draft_year": draft_year,
                "status": status,
                "note": note,
                "age": current_year - birth_year
            }
            
        except Exception as e:
            return {
                "draft_year": None,
                "status": "Unknown",
                "note": f"Could not calculate: {e}",
                "age": None
            }
    
    def enhance_goalie_data(self, goalie: Dict) -> Dict:
        """
        Add all enhanced data to a goalie record
        """
        # Add statistics
        goalie["stats"] = self.collect_stats(goalie)
        
        # Find YouTube highlights
        highlights = self.find_youtube_highlights(
            goalie.get("name", ""),
            goalie.get("team", "")
        )
        if highlights:
            goalie["video_links"] = highlights
        
        # Find social profiles
        goalie["social_profiles"] = self.find_social_profiles(goalie.get("name", ""))
        
        # Calculate draft eligibility
        if goalie.get("dob"):
            goalie["draft_info"] = self.calculate_draft_eligibility(goalie["dob"])
        
        return goalie


class TrendAnalyzer:
    """Analyze goalie performance trends over time"""
    
    def __init__(self):
        self.historical_data = {}
    
    def analyze_trend(self, goalie: Dict, historical_scores: List[int]) -> Dict:
        """
        Analyze if goalie is improving, declining, or stable
        """
        if len(historical_scores) < 2:
            return {
                "trend": "Insufficient Data",
                "direction": "unknown",
                "change": 0
            }
        
        # Calculate trend
        recent_avg = sum(historical_scores[-3:]) / min(3, len(historical_scores[-3:]))
        older_avg = sum(historical_scores[:3]) / min(3, len(historical_scores[:3]))
        
        change = recent_avg - older_avg
        
        if change > 5:
            trend = "Improving"
            direction = "up"
        elif change < -5:
            trend = "Declining"
            direction = "down"
        else:
            trend = "Stable"
            direction = "stable"
        
        return {
            "trend": trend,
            "direction": direction,
            "change": round(change, 1),
            "recent_average": round(recent_avg, 1),
            "historical_average": round(older_avg, 1)
        }


class TeamFitAnalyzer:
    """Analyze how well a goalie fits different team systems"""
    
    def analyze_team_fit(self, goalie: Dict, team_style: str = "balanced") -> Dict:
        """
        Analyze goalie fit for different team playing styles
        
        Team styles: offensive (high-scoring), defensive (low-scoring), balanced
        """
        fit_score = 75  # Base score
        
        # Adjust based on goalie tier
        tier = goalie.get("tier", "Unknown")
        if tier == "Top Prospect":
            fit_score += 10
        elif tier == "Sleeper":
            fit_score += 5
        elif tier == "Red Flag":
            fit_score -= 15
        
        # In production, would analyze actual playing style
        # based on stats like save%, rebound control, puck handling, etc.
        
        recommendations = []
        if fit_score >= 85:
            recommendations.append("Excellent fit - Ready for immediate impact")
        elif fit_score >= 75:
            recommendations.append("Good fit - Should adapt well")
        elif fit_score >= 65:
            recommendations.append("Moderate fit - May need adjustment period")
        else:
            recommendations.append("Questionable fit - Significant development needed")
        
        return {
            "team_style": team_style,
            "fit_score": fit_score,
            "recommendations": recommendations
        }


class InjuryRiskPredictor:
    """Predict injury risk based on goalie profile"""
    
    def predict_injury_risk(self, goalie: Dict) -> Dict:
        """
        Assess injury risk based on age, size, playing style
        Note: This is a simplified model - real prediction would use ML
        """
        risk_score = 0
        risk_factors = []
        
        # Age factor
        age = goalie.get("draft_info", {}).get("age", 20)
        if age < 18:
            risk_score += 5
            risk_factors.append("Young age - still developing physically")
        elif age > 24:
            risk_score += 10
            risk_factors.append("Older prospect - more wear")
        
        # Size factor (converted from cm to inches for analysis)
        height_cm = goalie.get("height", 185)
        if height_cm < 180:  # Under 5'11"
            risk_score += 5
            risk_factors.append("Smaller frame - more contact risk")
        elif height_cm > 195:  # Over 6'5"
            risk_score += 5
            risk_factors.append("Large frame - joint stress risk")
        
        # Determine risk level
        if risk_score < 10:
            risk_level = "Low"
        elif risk_score < 20:
            risk_level = "Moderate"
        else:
            risk_level = "Elevated"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendation": "Monitor workload and recovery" if risk_score >= 15 else "Standard monitoring sufficient"
        }
