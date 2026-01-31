#!/usr/bin/env python3
"""
Example usage of the Black Ops Goalie Scouting Platform.

This script demonstrates the key features of the platform:
1. Adding a goalie to the database
2. Analyzing with AI
3. Generating reports
4. Creating blog posts
5. Ranking goalies
"""

from goaliescout.data import (
    GoalieDatabase, 
    GoalieProfile, 
    Demographics, 
    PerformanceMetrics,
    AIAnalysis
)
from goaliescout.ai import get_ai_service
from goaliescout.analytics import GoalieAnalytics
from goaliescout.content import ReportGenerator, BlogGenerator

def main():
    print("=" * 60)
    print("Black Ops Goalie Scouting Platform - Example Usage")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    db = GoalieDatabase('./data/goalie_database.json')
    
    # Create a sample goalie profile
    print("\n2. Creating goalie profile...")
    demographics = Demographics(
        name="Alex Johnson",
        country="Canada",
        date_of_birth="2004-02-10",
        height="6'1\"",
        weight="190 lbs",
        catches="L"
    )
    
    profile = GoalieProfile(
        player_id="alex_johnson",
        demographics=demographics,
        league="OHL",
        current_team="London Knights"
    )
    
    # Add performance metrics
    metrics = PerformanceMetrics(
        games_played=35,
        wins=26,
        losses=7,
        overtime_losses=2,
        save_percentage=0.921,
        goals_against_average=2.28,
        shutouts=6,
        goals_against=80,
        saves=935,
        shots_against=1015,
        minutes_played=2100.0,
        season="2023-24"
    )
    profile.performance_metrics.append(metrics)
    
    # Add to database
    db.add_goalie(profile)
    print(f"   ✓ Added: {profile.demographics.name}")
    
    # Calculate career statistics
    print("\n3. Calculating career statistics...")
    career_stats = GoalieAnalytics.calculate_career_stats(profile)
    print(f"   Games Played: {career_stats['career_games']}")
    print(f"   Save %: {career_stats['career_save_percentage']:.3f}")
    print(f"   GAA: {career_stats['career_gaa']:.2f}")
    print(f"   Shutouts: {career_stats['career_shutouts']}")
    
    # Simulate AI analysis (without actual API call)
    print("\n4. Adding AI analysis...")
    ai_analysis = AIAnalysis(
        overall_rating=84.0,
        strengths=[
            "Excellent positioning and angle play",
            "Quick reflexes on rebounds",
            "Strong mental composure in pressure situations"
        ],
        weaknesses=[
            "Puck handling could be more confident",
            "Occasionally overcommits on breakaways",
            "Rebound control needs refinement"
        ],
        potential_rating=90.0,
        nhl_readiness="Developing - 2-3 years",
        scouting_notes="Johnson shows exceptional fundamentals for his age. "
                      "His positioning is NHL-caliber, and he rarely gets caught "
                      "out of position. With continued development in puck handling "
                      "and rebound control, has high NHL potential.",
        model_used="manual"
    )
    profile.ai_analysis = ai_analysis
    db.add_goalie(profile)
    print(f"   ✓ Overall Rating: {ai_analysis.overall_rating}/100")
    print(f"   ✓ Potential: {ai_analysis.potential_rating}/100")
    
    # Generate reports
    print("\n5. Generating scouting report...")
    report_gen = ReportGenerator('./reports')
    
    # Generate markdown report
    markdown_report = report_gen.generate_markdown_report(
        profile.to_dict(),
        "Detailed AI-generated scouting analysis would appear here."
    )
    report_path = report_gen.save_report(
        markdown_report,
        profile.demographics.name,
        "markdown"
    )
    print(f"   ✓ Markdown report: {report_path}")
    
    # Generate HTML report
    html_report = report_gen.generate_html_report(
        profile.to_dict(),
        "Detailed AI-generated scouting analysis would appear here."
    )
    html_path = report_gen.save_report(
        html_report,
        profile.demographics.name,
        "html"
    )
    print(f"   ✓ HTML report: {html_path}")
    
    # Generate blog post
    print("\n6. Creating blog post...")
    blog_gen = BlogGenerator('./content/blog')
    blog_content = blog_gen.generate_player_spotlight(profile.to_dict())
    blog_path = blog_gen.save_blog_post(blog_content, profile.demographics.name)
    print(f"   ✓ Blog post: {blog_path}")
    
    # List all goalies and rank them
    print("\n7. Ranking goalies...")
    all_goalies = db.get_all_goalies()
    rankings = GoalieAnalytics.rank_goalies(all_goalies, 'save_percentage')
    
    print(f"\n   Top Goalies by Save Percentage:")
    for i, ranking in enumerate(rankings[:5], 1):
        print(f"   {i}. {ranking['name']} - {ranking['save_percentage']:.3f}")
    
    # Display database statistics
    print("\n8. Database statistics...")
    stats = db.get_stats()
    print(f"   Total Goalies: {stats['total_goalies']}")
    print(f"   Leagues: {', '.join(stats['leagues'].keys())}")
    print(f"   Countries: {', '.join(stats['countries'].keys())}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set up API keys in .env file for AI analysis")
    print("2. Use CLI commands: goaliescout --help")
    print("3. Check generated reports in ./reports/")
    print("4. Check blog posts in ./content/blog/")
    print("\n")

if __name__ == '__main__':
    main()
