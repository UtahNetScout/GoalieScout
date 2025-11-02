"""
Social Media Module - Automated posting to X (Twitter)
"""

import os
from typing import List, Dict
import requests
from datetime import datetime


class XPoster:
    """Post updates to X (formerly Twitter)"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 access_token: str = None, access_token_secret: str = None):
        """
        Initialize X API credentials
        You'll need to apply for X API access at https://developer.twitter.com/
        """
        self.api_key = api_key or os.getenv("X_API_KEY")
        self.api_secret = api_secret or os.getenv("X_API_SECRET")
        self.access_token = access_token or os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("X_ACCESS_TOKEN_SECRET")
        
        # For API v2, you can also use Bearer Token
        self.bearer_token = os.getenv("X_BEARER_TOKEN")
        
    def create_prospect_post(self, goalie: Dict) -> str:
        """Create a post about a goalie prospect"""
        name = goalie.get('name', 'Unknown')
        team = goalie.get('team', 'Unknown')
        league = goalie.get('league', 'Unknown')
        tier = goalie.get('tier', 'Unknown')
        score = goalie.get('ai_score', 0)
        
        # Keep under 280 characters
        post = f"""🏒 Goalie Spotlight: {name}
        
{team} ({league})
Tier: {tier} | AI Score: {score}/100

#{league.replace(' ', '')} #GoalieProspects #HockeyScout"""
        
        return post[:280]  # Ensure it's under the limit
    
    def create_top_prospects_post(self, goalies: List[Dict], top_n: int = 3) -> str:
        """Create a post about top prospects"""
        top_goalies = sorted(goalies, key=lambda x: x.get("ai_score", 0), reverse=True)[:top_n]
        
        post = f"🔥 Top {top_n} Goalie Prospects (AI-Ranked):\n\n"
        
        for idx, goalie in enumerate(top_goalies, 1):
            name = goalie.get('name', 'Unknown')
            score = goalie.get('ai_score', 0)
            post += f"{idx}. {name} ({score}/100)\n"
        
        post += "\n#GoalieScout #HockeyProspects"
        
        return post[:280]
    
    def create_league_update_post(self, league: str, goalie_count: int) -> str:
        """Create a post about league coverage"""
        post = f"""📊 {league} Update

Tracking {goalie_count} goalies in our database. Latest AI scouting reports are now available!

#HockeyScout #{league.replace(' ', '')} #GoalieProspects"""
        
        return post[:280]
    
    def post_tweet(self, text: str, dry_run: bool = True) -> bool:
        """
        Post a tweet to X
        
        Args:
            text: Tweet content
            dry_run: If True, just print without posting (for testing)
        
        Returns:
            True if successful, False otherwise
        """
        if dry_run:
            print(f"\n[DRY RUN] Would post to X:\n{'-'*50}")
            print(text)
            print(f"{'-'*50}\n")
            return True
        
        if not self.bearer_token:
            print("[!] X Bearer Token not configured. Set X_BEARER_TOKEN environment variable.")
            return False
        
        # X API v2 endpoint
        url = "https://api.twitter.com/2/tweets"
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 201:
                print(f"[✓] Posted to X successfully!")
                return True
            else:
                print(f"[!] X API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[!] Error posting to X: {e}")
            return False
    
    def post_daily_update(self, goalies: List[Dict], dry_run: bool = True):
        """Post a daily update with top prospects"""
        post = self.create_top_prospects_post(goalies, top_n=3)
        return self.post_tweet(post, dry_run=dry_run)
    
    def post_prospect_spotlight(self, goalie: Dict, dry_run: bool = True):
        """Post a spotlight on a specific goalie"""
        post = self.create_prospect_post(goalie)
        return self.post_tweet(post, dry_run=dry_run)
    
    def post_weekly_summary(self, goalies: List[Dict], dry_run: bool = True):
        """Post a weekly summary"""
        total_goalies = len(goalies)
        top_prospects = len([g for g in goalies if g.get('tier') == 'Top Prospect'])
        sleepers = len([g for g in goalies if g.get('tier') == 'Sleeper'])
        
        post = f"""📈 Weekly Goalie Scout Summary

Total Tracked: {total_goalies}
Top Prospects: {top_prospects}
Sleepers: {sleepers}

Latest AI analysis updated!

#GoalieScout #HockeyProspects #AI"""
        
        return self.post_tweet(post, dry_run=dry_run)


class AutomatedSocialMedia:
    """Automated social media posting scheduler"""
    
    def __init__(self, x_poster: XPoster = None):
        self.x_poster = x_poster or XPoster()
        self.last_post_file = Path("last_social_post.json")
        
    def should_post_daily_update(self) -> bool:
        """Check if we should post daily update (once per day)"""
        if not self.last_post_file.exists():
            return True
        
        with open(self.last_post_file, 'r') as f:
            data = json.load(f)
        
        last_daily = data.get('last_daily_update')
        if not last_daily:
            return True
        
        last_date = datetime.fromisoformat(last_daily).date()
        today = datetime.now().date()
        
        return today > last_date
    
    def record_post(self, post_type: str):
        """Record that we made a post"""
        data = {}
        if self.last_post_file.exists():
            with open(self.last_post_file, 'r') as f:
                data = json.load(f)
        
        data[f'last_{post_type}'] = datetime.now().isoformat()
        
        with open(self.last_post_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run_automated_posting(self, goalies: List[Dict], dry_run: bool = True):
        """Run automated posting based on schedule"""
        posted_count = 0
        
        # Daily update
        if self.should_post_daily_update():
            if self.x_poster.post_daily_update(goalies, dry_run=dry_run):
                self.record_post('daily_update')
                posted_count += 1
        
        # Weekly summary (check if it's been 7 days)
        # Add similar logic for weekly posts
        
        print(f"[✓] Automated posting complete. {posted_count} posts made.")
        return posted_count


# For backward compatibility
from pathlib import Path
import json
