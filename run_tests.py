#!/usr/bin/env python3
"""
Automated tests for the Black Ops Goalie Scouting Platform.

Run this script to verify all core functionality is working.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from goaliescout.data import (
            GoalieDatabase, GoalieProfile, Demographics, 
            PerformanceMetrics, AIAnalysis
        )
        from goaliescout.ai import get_ai_service
        from goaliescout.analytics import GoalieAnalytics, ComparisonEngine
        from goaliescout.content import ReportGenerator, BlogGenerator, SocialMediaManager
        from goaliescout.scraping import GoalieScraper, DataEnricher
        from goaliescout.cli import main
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_database():
    """Test database operations."""
    print("\nTesting database operations...")
    try:
        from goaliescout.data import GoalieDatabase, GoalieProfile, Demographics
        
        # Create test database
        db = GoalieDatabase('./data/test_database.json')
        
        # Create test profile
        demographics = Demographics(
            name="Test Player",
            country="Canada",
            date_of_birth="2000-01-01"
        )
        profile = GoalieProfile(
            player_id="test_player",
            demographics=demographics,
            league="NHL"
        )
        
        # Test add
        db.add_goalie(profile)
        
        # Test get
        retrieved = db.get_goalie("test_player")
        assert retrieved is not None
        assert retrieved.demographics.name == "Test Player"
        
        # Test search
        results = db.search_goalies(country="Canada")
        assert len(results) > 0
        
        # Test stats
        stats = db.get_stats()
        assert stats['total_goalies'] > 0
        
        # Cleanup
        db.delete_goalie("test_player")
        
        print("  ✓ Database operations successful")
        return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analytics():
    """Test analytics functions."""
    print("\nTesting analytics...")
    try:
        from goaliescout.data import GoalieProfile, Demographics, PerformanceMetrics
        from goaliescout.analytics import GoalieAnalytics
        
        # Create test profile with metrics
        demographics = Demographics(
            name="Analytics Test",
            country="USA",
            date_of_birth="2001-01-01"
        )
        profile = GoalieProfile(
            player_id="analytics_test",
            demographics=demographics,
            league="NCAA"
        )
        
        metrics = PerformanceMetrics(
            games_played=20,
            wins=15,
            losses=5,
            save_percentage=0.915,
            goals_against_average=2.5,
            shots_against=500,
            saves=458,
            goals_against=42
        )
        profile.performance_metrics.append(metrics)
        
        # Test career stats
        career_stats = GoalieAnalytics.calculate_career_stats(profile)
        assert career_stats['career_games'] == 20
        assert career_stats['career_save_percentage'] > 0
        
        # Test ranking
        rankings = GoalieAnalytics.rank_goalies([profile], 'save_percentage')
        assert len(rankings) == 1
        assert rankings[0]['rank'] == 1
        
        # Test injury risk
        injury_risk = GoalieAnalytics.injury_risk_assessment(profile)
        assert 'risk_level' in injury_risk
        
        print("  ✓ Analytics successful")
        return True
    except Exception as e:
        print(f"  ✗ Analytics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_services():
    """Test AI service initialization."""
    print("\nTesting AI services...")
    try:
        from goaliescout.ai import get_ai_service
        
        # Test service creation (without API keys)
        openai_service = get_ai_service('openai')
        anthropic_service = get_ai_service('anthropic')
        ollama_service = get_ai_service('ollama')
        
        assert openai_service is not None
        assert anthropic_service is not None
        assert ollama_service is not None
        
        print("  ✓ AI services initialized")
        return True
    except Exception as e:
        print(f"  ✗ AI service test failed: {e}")
        return False

def test_content_generation():
    """Test content generation."""
    print("\nTesting content generation...")
    try:
        from goaliescout.data import GoalieProfile, Demographics
        from goaliescout.content import ReportGenerator, BlogGenerator, SocialMediaManager
        
        # Create test profile
        demographics = Demographics(
            name="Content Test",
            country="USA",
            date_of_birth="2002-01-01"
        )
        profile = GoalieProfile(
            player_id="content_test",
            demographics=demographics,
            league="OHL"
        )
        
        profile_dict = profile.to_dict()
        
        # Test report generation
        report_gen = ReportGenerator('./reports')
        markdown = report_gen.generate_markdown_report(profile_dict, "Test report")
        assert len(markdown) > 0
        assert "Content Test" in markdown
        
        html = report_gen.generate_html_report(profile_dict, "Test report")
        assert len(html) > 0
        assert "Content Test" in html
        
        # Test blog generation
        blog_gen = BlogGenerator('./content/blog')
        blog = blog_gen.generate_player_spotlight(profile_dict)
        assert len(blog) > 0
        assert "Content Test" in blog
        
        # Test social media
        social = SocialMediaManager()
        tweet = social.create_player_tweet(profile_dict)
        assert len(tweet) > 0
        assert len(tweet) <= 280  # Twitter limit
        
        print("  ✓ Content generation successful")
        return True
    except Exception as e:
        print(f"  ✗ Content generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_models():
    """Test data model creation and serialization."""
    print("\nTesting data models...")
    try:
        from goaliescout.data import (
            Demographics, PerformanceMetrics, InjuryRecord,
            NHLComparison, AIAnalysis, GoalieProfile
        )
        
        # Create all model types
        demographics = Demographics(
            name="Model Test",
            country="Canada",
            date_of_birth="2003-01-01"
        )
        
        metrics = PerformanceMetrics(
            games_played=10,
            save_percentage=0.900
        )
        
        injury = InjuryRecord(
            date="2023-01-01",
            injury_type="Test",
            severity="Minor"
        )
        
        comparison = NHLComparison(
            comparable_player="Test NHL Goalie",
            similarity_score=75.0,
            comparison_notes="Test notes"
        )
        
        ai_analysis = AIAnalysis(
            overall_rating=80.0,
            strengths=["Test strength"],
            weaknesses=["Test weakness"]
        )
        
        # Create profile with all components
        profile = GoalieProfile(
            player_id="model_test",
            demographics=demographics,
            league="Test League",
            ai_analysis=ai_analysis
        )
        profile.performance_metrics.append(metrics)
        profile.injury_history.append(injury)
        profile.nhl_comparisons.append(comparison)
        
        # Test serialization
        profile_dict = profile.to_dict()
        assert profile_dict['player_id'] == "model_test"
        
        # Test deserialization
        restored_profile = GoalieProfile.from_dict(profile_dict)
        assert restored_profile.player_id == "model_test"
        assert restored_profile.demographics.name == "Model Test"
        
        print("  ✓ Data models successful")
        return True
    except Exception as e:
        print(f"  ✗ Data model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Black Ops Goalie Scouting Platform - Test Suite")
    print("=" * 60)
    
    results = {
        'Imports': test_imports(),
        'Data Models': test_data_models(),
        'Database': test_database(),
        'Analytics': test_analytics(),
        'AI Services': test_ai_services(),
        'Content Generation': test_content_generation()
    }
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
