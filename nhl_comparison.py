"""
NHL Goalie Comparison Module
Compares prospects to historical NHL goalies from any era
"""

from typing import Dict, List, Tuple
import re


# Historical NHL Goalies Database (Famous goalies from different eras)
NHL_GOALIES_DATABASE = [
    # Modern Era (2000s-2020s)
    {
        "name": "Carey Price",
        "era": "2000s-2020s",
        "style": "Hybrid/Butterfly",
        "strengths": ["positioning", "calm demeanor", "puck tracking", "rebound control"],
        "height": 191,
        "team_context": "Elite on struggling teams",
        "accolades": "Vezina, Hart, Olympic Gold",
        "playstyle": "Positional perfection, athletic when needed"
    },
    {
        "name": "Henrik Lundqvist",
        "era": "2000s-2020s", 
        "style": "Hybrid/Butterfly",
        "strengths": ["athleticism", "compete level", "glove hand", "big-game performance"],
        "height": 185,
        "team_context": "Franchise cornerstone",
        "accolades": "Vezina, Olympic Gold",
        "playstyle": "Athletic hybrid, spectacular saves"
    },
    {
        "name": "Marc-Andre Fleury",
        "era": "2000s-2020s",
        "style": "Hybrid/Butterfly",
        "strengths": ["athleticism", "flexibility", "competitiveness", "leadership"],
        "height": 188,
        "team_context": "Championship pedigree",
        "accolades": "3x Stanley Cup, Vezina",
        "playstyle": "Athletic and aggressive, team leader"
    },
    {
        "name": "Connor Hellebuyck",
        "era": "2010s-2020s",
        "style": "Butterfly",
        "strengths": ["size", "positioning", "consistency", "workload"],
        "height": 193,
        "team_context": "Workhorse on defensive teams",
        "accolades": "Vezina",
        "playstyle": "Positional giant, handles heavy workload"
    },
    {
        "name": "Andrei Vasilevskiy",
        "era": "2010s-2020s",
        "style": "Butterfly",
        "strengths": ["size", "athleticism", "tracking", "compete"],
        "height": 193,
        "team_context": "Elite team anchor",
        "accolades": "2x Stanley Cup, 2x Vezina",
        "playstyle": "Athletic giant, championship mindset"
    },
    {
        "name": "Igor Shesterkin",
        "era": "2020s",
        "style": "Hybrid",
        "strengths": ["athleticism", "quickness", "tracking", "confidence"],
        "height": 185,
        "team_context": "Modern elite",
        "accolades": "Vezina",
        "playstyle": "Ultra-athletic, modern hybrid"
    },
    
    # 1990s-2000s Era
    {
        "name": "Martin Brodeur",
        "era": "1990s-2010s",
        "style": "Hybrid/Stand-up",
        "strengths": ["puck handling", "positioning", "consistency", "durability"],
        "height": 188,
        "team_context": "All-time wins leader",
        "accolades": "3x Stanley Cup, 4x Vezina",
        "playstyle": "Complete goalie, exceptional puck handler"
    },
    {
        "name": "Dominik Hasek",
        "era": "1990s-2000s",
        "style": "Unorthodox/Butterfly",
        "strengths": ["flexibility", "athleticism", "competitiveness", "unconventional saves"],
        "height": 183,
        "team_context": "Carried mediocre teams",
        "accolades": "2x Stanley Cup, 6x Vezina, 2x Hart",
        "playstyle": "Unorthodox genius, incredibly athletic"
    },
    {
        "name": "Patrick Roy",
        "era": "1980s-2000s",
        "style": "Butterfly",
        "strengths": ["positioning", "butterfly technique", "compete", "clutch"],
        "height": 185,
        "team_context": "Championship legend",
        "accolades": "4x Stanley Cup, 3x Vezina",
        "playstyle": "Butterfly pioneer, intense competitor"
    },
    {
        "name": "Ed Belfour",
        "era": "1990s-2000s",
        "style": "Butterfly",
        "strengths": ["compete level", "positioning", "consistency"],
        "height": 180,
        "team_context": "Elite competitor",
        "accolades": "Stanley Cup, 2x Vezina",
        "playstyle": "Fierce competitor, technically sound"
    },
    
    # 1980s Era
    {
        "name": "Grant Fuhr",
        "era": "1980s-1990s",
        "style": "Stand-up/Hybrid",
        "strengths": ["athleticism", "puck tracking", "competitive", "team player"],
        "height": 180,
        "team_context": "Dynasty goalie",
        "accolades": "5x Stanley Cup, Vezina",
        "playstyle": "Athletic stand-up, championship pedigree"
    },
    {
        "name": "Billy Smith",
        "era": "1970s-1980s",
        "style": "Stand-up",
        "strengths": ["competitiveness", "intimidation", "clutch"],
        "height": 178,
        "team_context": "Dynasty cornerstone",
        "accolades": "4x Stanley Cup, Vezina",
        "playstyle": "Fierce competitor, aggressive"
    },
    
    # 1970s Era
    {
        "name": "Ken Dryden",
        "era": "1970s",
        "style": "Stand-up",
        "strengths": ["size", "positioning", "intelligence", "calm"],
        "height": 193,
        "team_context": "Dynasty goalie",
        "accolades": "6x Stanley Cup, 5x Vezina",
        "playstyle": "Towering presence, intelligent positioning"
    },
    {
        "name": "Bernie Parent",
        "era": "1970s",
        "style": "Stand-up",
        "strengths": ["positioning", "consistency", "compete"],
        "height": 180,
        "team_context": "Championship goalie",
        "accolades": "2x Stanley Cup, 2x Vezina",
        "playstyle": "Positional excellence, championship pedigree"
    },
    
    # 1960s Era
    {
        "name": "Jacques Plante",
        "era": "1950s-1970s",
        "style": "Stand-up",
        "strengths": ["innovation", "positioning", "intelligence"],
        "height": 183,
        "team_context": "Pioneer and winner",
        "accolades": "6x Stanley Cup, 7x Vezina",
        "playstyle": "Innovative, introduced goalie mask"
    },
    {
        "name": "Glenn Hall",
        "era": "1950s-1970s",
        "style": "Butterfly (early)",
        "strengths": ["durability", "butterfly technique", "consistency"],
        "height": 180,
        "team_context": "Ironman goalie",
        "accolades": "Stanley Cup, 3x Vezina",
        "playstyle": "Butterfly pioneer, incredible durability"
    },
    
    # Modern phenoms
    {
        "name": "Ilya Sorokin",
        "era": "2020s",
        "style": "Butterfly",
        "strengths": ["positioning", "consistency", "technique", "calm"],
        "height": 185,
        "team_context": "Modern technical master",
        "accolades": "Vezina finalist",
        "playstyle": "Technically perfect, positionally sound"
    },
    {
        "name": "Juuse Saros",
        "era": "2020s",
        "style": "Butterfly",
        "strengths": ["athleticism", "compete", "quickness"],
        "height": 180,
        "team_context": "Small but elite",
        "accolades": "Vezina finalist",
        "playstyle": "Undersized but supremely athletic"
    }
]


class NHLGoalieComparator:
    """Compare prospects to historical NHL goalies"""
    
    def __init__(self):
        self.nhl_database = NHL_GOALIES_DATABASE
    
    def calculate_similarity_score(self, prospect: Dict, nhl_goalie: Dict) -> float:
        """
        Calculate similarity score between prospect and NHL goalie (0-100)
        """
        score = 0.0
        max_score = 100.0
        
        # Height similarity (20 points max)
        prospect_height = prospect.get("height", 185)
        nhl_height = nhl_goalie["height"]
        height_diff = abs(prospect_height - nhl_height)
        
        if height_diff == 0:
            score += 20
        elif height_diff <= 3:
            score += 15
        elif height_diff <= 6:
            score += 10
        elif height_diff <= 10:
            score += 5
        
        # Tier/quality similarity (30 points max)
        prospect_tier = prospect.get("tier", "Unknown")
        if "Top Prospect" in prospect_tier and "Vezina" in nhl_goalie.get("accolades", ""):
            score += 30
        elif "Sleeper" in prospect_tier:
            score += 20
        elif prospect_tier in ["Watch", "Unknown"]:
            score += 10
        
        # Playing style inference from notes (30 points max)
        prospect_notes = prospect.get("notes", "").lower()
        nhl_style = nhl_goalie.get("playstyle", "").lower()
        
        # Check for style keywords
        style_keywords = ["athletic", "positional", "aggressive", "calm", "technique", "compete"]
        matches = sum(1 for keyword in style_keywords if keyword in prospect_notes and keyword in nhl_style)
        score += min(matches * 6, 30)
        
        # League context (20 points max)
        prospect_league = prospect.get("league", "")
        if any(league in prospect_league for league in ["SHL", "KHL", "Liiga", "DEL"]):
            score += 15  # European leagues like European NHL stars
        elif any(league in prospect_league for league in ["NCAA", "USHL", "CHL", "OHL"]):
            score += 10  # North American development
        
        return min(score, max_score)
    
    def find_best_comparisons(self, prospect: Dict, top_n: int = 3) -> List[Tuple[Dict, float]]:
        """
        Find the top N best NHL goalie comparisons for a prospect
        Returns list of (nhl_goalie, similarity_score) tuples
        """
        comparisons = []
        
        for nhl_goalie in self.nhl_database:
            similarity = self.calculate_similarity_score(prospect, nhl_goalie)
            comparisons.append((nhl_goalie, similarity))
        
        # Sort by similarity score (descending)
        comparisons.sort(key=lambda x: x[1], reverse=True)
        
        return comparisons[:top_n]
    
    def generate_comparison_report(self, prospect: Dict) -> Dict:
        """
        Generate a comprehensive comparison report
        """
        top_comparisons = self.find_best_comparisons(prospect, top_n=3)
        
        if not top_comparisons:
            return {
                "primary_comparison": None,
                "secondary_comparisons": [],
                "summary": "Insufficient data for comparison"
            }
        
        primary = top_comparisons[0]
        secondaries = top_comparisons[1:] if len(top_comparisons) > 1 else []
        
        # Generate summary
        primary_name = primary[0]["name"]
        primary_score = primary[1]
        primary_era = primary[0]["era"]
        primary_style = primary[0]["playstyle"]
        
        summary = f"{prospect.get('name', 'Prospect')} most closely resembles {primary_name} "
        summary += f"({primary_era}) with a {primary_score:.0f}% similarity match. "
        summary += f"Like {primary_name}, shows {primary_style.lower()}. "
        
        if secondaries:
            secondary_names = [comp[0]["name"] for comp in secondaries]
            summary += f"Also comparable to {', '.join(secondary_names)}."
        
        return {
            "primary_comparison": {
                "name": primary[0]["name"],
                "era": primary[0]["era"],
                "style": primary[0]["style"],
                "playstyle": primary[0]["playstyle"],
                "accolades": primary[0]["accolades"],
                "similarity_score": round(primary_score, 1),
                "strengths": primary[0]["strengths"]
            },
            "secondary_comparisons": [
                {
                    "name": comp[0]["name"],
                    "era": comp[0]["era"],
                    "similarity_score": round(comp[1], 1),
                    "playstyle": comp[0]["playstyle"]
                }
                for comp in secondaries
            ],
            "summary": summary
        }
    
    def add_comparison_to_goalie(self, goalie: Dict) -> Dict:
        """
        Add NHL comparison data to a goalie record
        """
        comparison = self.generate_comparison_report(goalie)
        goalie["nhl_comparison"] = comparison
        return goalie


def format_comparison_for_blog(comparison: Dict) -> str:
    """
    Format NHL comparison for blog posts
    """
    if not comparison or not comparison.get("primary_comparison"):
        return ""
    
    primary = comparison["primary_comparison"]
    
    text = f"\n### NHL Comparison\n\n"
    text += f"**Most Similar To:** {primary['name']} ({primary['era']})\n\n"
    text += f"**Similarity Score:** {primary['similarity_score']}/100\n\n"
    text += f"**Playing Style:** {primary['playstyle']}\n\n"
    text += f"**Career Highlights:** {primary['accolades']}\n\n"
    
    if comparison.get("secondary_comparisons"):
        text += f"**Also Comparable To:** "
        names = [f"{comp['name']} ({comp['era']})" for comp in comparison["secondary_comparisons"]]
        text += ", ".join(names) + "\n\n"
    
    text += f"*{comparison['summary']}*\n"
    
    return text
