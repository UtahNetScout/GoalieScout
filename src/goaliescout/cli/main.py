"""Command-line interface for Black Ops Goalie Scouting Platform."""

import click
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..data import GoalieDatabase, GoalieProfile, Demographics, PerformanceMetrics, AIAnalysis
from ..ai import get_ai_service
from ..analytics import GoalieAnalytics, ComparisonEngine
from ..analytics.composite_score import calculate_black_ops_score, classify_tier
from ..analytics.consistency import calculate_consistency
from ..analytics.gsax import aggregate_gsax
from ..analytics.slot_save_pct import aggregate_zone_save_pct
from ..content import ReportGenerator, BlogGenerator, SocialMediaManager
from ..scraping import DataEnricher

# Load environment variables
load_dotenv()

# Initialize console for rich output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='0.1.0')
def main():
    """Black Ops Goalie Scouting Platform - AI-powered goalie scouting and analysis."""
    pass


@main.command()
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
def init(db_path):
    """Initialize the scouting database."""
    try:
        db = GoalieDatabase(db_path)
        console.print(Panel.fit(
            f"[green]✓ Database initialized at {db_path}[/green]",
            title="Success"
        ))
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")


@main.command()
@click.option('--name', prompt='Player name', help='Name of the goalie')
@click.option('--country', prompt='Country', help='Country of origin')
@click.option('--dob', prompt='Date of birth (YYYY-MM-DD)', help='Date of birth')
@click.option('--league', prompt='League', help='Current league')
@click.option('--team', default='', help='Current team')
@click.option('--height', default='', help='Height')
@click.option('--weight', default='', help='Weight')
@click.option('--catches', default='', help='Catches (L/R)')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
def add_goalie(name, country, dob, league, team, height, weight, catches, db_path):
    """Add a new goalie to the database."""
    try:
        db = GoalieDatabase(db_path)
        
        # Create player ID from name
        player_id = name.lower().replace(' ', '_')
        
        # Create demographics
        demographics = Demographics(
            name=name,
            country=country,
            date_of_birth=dob,
            height=height or None,
            weight=weight or None,
            catches=catches or None
        )
        
        # Create profile
        profile = GoalieProfile(
            player_id=player_id,
            demographics=demographics,
            league=league,
            current_team=team or None
        )
        
        # Add to database
        db.add_goalie(profile)
        
        console.print(Panel.fit(
            f"[green]✓ Added goalie: {name}[/green]",
            title="Success"
        ))
        
    except Exception as e:
        console.print(f"[red]Error adding goalie: {e}[/red]")
        logger.error(f"Error adding goalie: {e}", exc_info=True)


@main.command()
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
@click.option('--league', help='Filter by league')
@click.option('--country', help='Filter by country')
def list_goalies(db_path, league, country):
    """List all goalies in the database."""
    try:
        db = GoalieDatabase(db_path)
        
        # Apply filters if provided
        if league or country:
            filters = {}
            if league:
                filters['league'] = league
            if country:
                filters['country'] = country
            goalies = db.search_goalies(**filters)
        else:
            goalies = db.get_all_goalies()
        
        if not goalies:
            console.print("[yellow]No goalies found[/yellow]")
            return
        
        # Create table
        table = Table(title=f"Goalies ({len(goalies)} found)")
        table.add_column("Name", style="cyan")
        table.add_column("Country", style="magenta")
        table.add_column("League", style="green")
        table.add_column("Team", style="yellow")
        
        for goalie in goalies:
            table.add_row(
                goalie.demographics.name,
                goalie.demographics.country,
                goalie.league,
                goalie.current_team or "N/A"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing goalies: {e}[/red]")


@main.command()
@click.argument('player_id')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
@click.option('--ai-model', default='openai', help='AI model to use (openai, anthropic, ollama)')
def analyze(player_id, db_path, ai_model):
    """Analyze a goalie using AI."""
    try:
        db = GoalieDatabase(db_path)
        profile = db.get_goalie(player_id)
        
        if not profile:
            console.print(f"[red]Goalie not found: {player_id}[/red]")
            return
        
        console.print(f"[cyan]Analyzing {profile.demographics.name} using {ai_model}...[/cyan]")
        
        # Get AI service
        ai_service = get_ai_service(ai_model)
        
        # Analyze goalie
        profile_dict = profile.to_dict()
        analysis_result = ai_service.analyze_goalie(profile_dict)
        
        # Create AIAnalysis object
        ai_analysis = AIAnalysis(
            overall_rating=analysis_result.get('overall_rating', 0),
            strengths=analysis_result.get('strengths', []),
            weaknesses=analysis_result.get('weaknesses', []),
            potential_rating=analysis_result.get('potential_rating', 0),
            nhl_readiness=analysis_result.get('nhl_readiness', 'Unknown'),
            scouting_notes=analysis_result.get('scouting_notes', ''),
            model_used=ai_model
        )
        
        # Update profile
        profile.ai_analysis = ai_analysis
        db.add_goalie(profile)
        
        # Display results
        console.print(Panel.fit(
            f"[green]Overall Rating: {ai_analysis.overall_rating}/100[/green]\n"
            f"[blue]Potential: {ai_analysis.potential_rating}/100[/blue]\n"
            f"[yellow]NHL Readiness: {ai_analysis.nhl_readiness}[/yellow]",
            title=f"Analysis: {profile.demographics.name}"
        ))
        
        console.print("\n[bold]Strengths:[/bold]")
        for strength in ai_analysis.strengths:
            console.print(f"  ✓ {strength}")
        
        console.print("\n[bold]Weaknesses:[/bold]")
        for weakness in ai_analysis.weaknesses:
            console.print(f"  ✗ {weakness}")
        
        console.print("\n[bold]Scouting Notes:[/bold]")
        console.print(ai_analysis.scouting_notes)
        
    except Exception as e:
        console.print(f"[red]Error analyzing goalie: {e}[/red]")
        logger.error(f"Error analyzing goalie: {e}", exc_info=True)


@main.command()
@click.argument('player_id')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
@click.option('--ai-model', default='openai', help='AI model to use')
@click.option('--format', type=click.Choice(['markdown', 'html']), default='markdown', help='Report format')
@click.option('--output-dir', default='./reports', help='Output directory')
def generate_report(player_id, db_path, ai_model, format, output_dir):
    """Generate a detailed scouting report."""
    try:
        db = GoalieDatabase(db_path)
        profile = db.get_goalie(player_id)
        
        if not profile:
            console.print(f"[red]Goalie not found: {player_id}[/red]")
            return
        
        console.print(f"[cyan]Generating {format} report for {profile.demographics.name}...[/cyan]")
        
        # Get AI service and generate detailed report
        ai_service = get_ai_service(ai_model)
        profile_dict = profile.to_dict()
        ai_report = ai_service.generate_scouting_report(profile_dict)
        
        # Generate report
        report_gen = ReportGenerator(output_dir)
        
        if format == 'markdown':
            content = report_gen.generate_markdown_report(profile_dict, ai_report)
        else:
            content = report_gen.generate_html_report(profile_dict, ai_report)
        
        # Save report
        filepath = report_gen.save_report(content, profile.demographics.name, format)
        
        console.print(Panel.fit(
            f"[green]✓ Report generated: {filepath}[/green]",
            title="Success"
        ))
        
    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")
        logger.error(f"Error generating report: {e}", exc_info=True)


@main.command()
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
@click.option('--metric', default='save_percentage', help='Metric to rank by')
@click.option('--league', help='Filter by league')
def rank(db_path, metric, league):
    """Rank goalies by performance metrics."""
    try:
        db = GoalieDatabase(db_path)
        
        # Get goalies
        if league:
            goalies = db.search_goalies(league=league)
        else:
            goalies = db.get_all_goalies()
        
        if not goalies:
            console.print("[yellow]No goalies found[/yellow]")
            return
        
        # Rank goalies
        rankings = GoalieAnalytics.rank_goalies(goalies, metric)
        
        # Create table
        table = Table(title=f"Goalie Rankings by {metric}")
        table.add_column("Rank", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("League", style="green")
        table.add_column(metric.replace('_', ' ').title(), style="yellow")
        
        for ranking in rankings[:20]:  # Top 20
            table.add_row(
                str(ranking['rank']),
                ranking['name'],
                ranking['league'],
                f"{ranking.get(metric, 0):.3f}"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error ranking goalies: {e}[/red]")


@main.command()
@click.argument('player_id')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
@click.option('--output-dir', default='./content/blog', help='Output directory')
def create_blog(player_id, db_path, output_dir):
    """Create a blog post spotlight for a goalie."""
    try:
        db = GoalieDatabase(db_path)
        profile = db.get_goalie(player_id)
        
        if not profile:
            console.print(f"[red]Goalie not found: {player_id}[/red]")
            return
        
        console.print(f"[cyan]Creating blog post for {profile.demographics.name}...[/cyan]")
        
        # Generate blog post
        blog_gen = BlogGenerator(output_dir)
        profile_dict = profile.to_dict()
        content = blog_gen.generate_player_spotlight(profile_dict)
        
        # Save blog post
        filepath = blog_gen.save_blog_post(content, profile.demographics.name)
        
        console.print(Panel.fit(
            f"[green]✓ Blog post created: {filepath}[/green]",
            title="Success"
        ))
        
    except Exception as e:
        console.print(f"[red]Error creating blog post: {e}[/red]")


@main.command()
@click.argument('player_id')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
@click.option('--post', is_flag=True, help='Actually post to Twitter (requires API keys)')
def tweet(player_id, db_path, post):
    """Create (and optionally post) a tweet about a goalie."""
    try:
        db = GoalieDatabase(db_path)
        profile = db.get_goalie(player_id)
        
        if not profile:
            console.print(f"[red]Goalie not found: {player_id}[/red]")
            return
        
        # Generate tweet
        social_media = SocialMediaManager()
        profile_dict = profile.to_dict()
        tweet_text = social_media.create_player_tweet(profile_dict)
        
        console.print(Panel.fit(
            tweet_text,
            title="Tweet Preview"
        ))
        
        if post:
            console.print("[cyan]Posting to Twitter...[/cyan]")
            success = social_media.post_to_twitter(tweet_text)
            
            if success:
                console.print("[green]✓ Tweet posted successfully[/green]")
            else:
                console.print("[red]Failed to post tweet. Check API credentials.[/red]")
        else:
            console.print("[yellow]Use --post flag to actually post to Twitter[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error creating tweet: {e}[/red]")


@main.command()
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
def stats(db_path):
    """Display database statistics."""
    try:
        db = GoalieDatabase(db_path)
        db_stats = db.get_stats()
        
        console.print(Panel.fit(
            f"[cyan]Total Goalies: {db_stats['total_goalies']}[/cyan]",
            title="Database Statistics"
        ))
        
        if db_stats['leagues']:
            table = Table(title="Goalies by League")
            table.add_column("League", style="cyan")
            table.add_column("Count", style="green")
            
            for league, count in sorted(db_stats['leagues'].items(), key=lambda x: x[1], reverse=True):
                table.add_row(league, str(count))
            
            console.print(table)
        
        if db_stats['countries']:
            table = Table(title="Goalies by Country")
            table.add_column("Country", style="cyan")
            table.add_column("Count", style="green")
            
            for country, count in sorted(db_stats['countries'].items(), key=lambda x: x[1], reverse=True)[:10]:
                table.add_row(country, str(count))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error getting statistics: {e}[/red]")


@main.command('advanced-stats')
@click.argument('player_id')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
def advanced_stats(player_id, db_path):
    """Show advanced analytics for a goalie (GSAx, HD SV%, consistency, etc.)."""
    try:
        db = GoalieDatabase(db_path)
        profile = db.get_goalie(player_id)

        if not profile:
            console.print(f"[red]Goalie not found: {player_id}[/red]")
            return

        career = GoalieAnalytics.calculate_career_stats(profile)
        metrics = profile.performance_metrics

        # Consistency from season-level SV% data
        sv_pcts = [m.save_percentage for m in metrics if m.save_percentage > 0]
        consistency_result = calculate_consistency(sv_pcts) if sv_pcts else {}

        console.print(Panel.fit(
            f"[cyan]{profile.demographics.name}[/cyan] — Advanced Analytics",
            title="Black Ops Goalie Scout"
        ))

        # Career stats table
        career_table = Table(title="Career Statistics")
        career_table.add_column("Metric", style="cyan")
        career_table.add_column("Value", style="green")
        for key, value in career.items():
            display_key = key.replace("career_", "").replace("_", " ").title()
            if isinstance(value, float):
                career_table.add_row(display_key, f"{value:.3f}")
            else:
                career_table.add_row(display_key, str(value))
        console.print(career_table)

        # Consistency
        if consistency_result:
            console.print(Panel.fit(
                f"[green]Consistency Score: {consistency_result.get('consistency_score', 'N/A')}[/green]\n"
                f"[blue]SV% Std Dev: {consistency_result.get('std_dev', 'N/A')}[/blue]\n"
                f"[yellow]Streak: {consistency_result.get('streak_info', {}).get('type', 'N/A')} "
                f"({consistency_result.get('streak_info', {}).get('length', 0)} games)[/yellow]\n"
                f"[magenta]Sample Confidence: {consistency_result.get('confidence', 'N/A')}[/magenta]",
                title="Consistency Index"
            ))

    except Exception as e:
        console.print(f"[red]Error retrieving advanced stats: {e}[/red]")
        logger.error(f"Error retrieving advanced stats: {e}", exc_info=True)


@main.command('black-ops-score')
@click.argument('player_id')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
def black_ops_score(player_id, db_path):
    """Show the Black Ops composite score with full breakdown for a goalie."""
    try:
        db = GoalieDatabase(db_path)
        profile = db.get_goalie(player_id)

        if not profile:
            console.print(f"[red]Goalie not found: {player_id}[/red]")
            return

        career = GoalieAnalytics.calculate_career_stats(profile)
        metrics = profile.performance_metrics

        sv_pcts = [m.save_percentage for m in metrics if m.save_percentage > 0]
        consistency_result = calculate_consistency(sv_pcts) if sv_pcts else {}

        # Estimate a rough HD SV% from career SV% (no shot-level data yet)
        career_sv = career.get("career_save_percentage", 0.0)
        hd_sv_est = max(0.820, career_sv - 0.040) if career_sv > 0 else None

        result = calculate_black_ops_score(
            hd_sv_pct=hd_sv_est,
            consistency_score=consistency_result.get("consistency_score"),
            games_played=career.get("career_games", 0),
        )

        tier_colour = {
            "Elite": "bright_green",
            "Above Average": "green",
            "Average": "yellow",
            "Below Average": "dark_orange",
            "Needs Improvement": "red",
        }.get(result["tier"], "white")

        console.print(Panel.fit(
            f"[bold white]{profile.demographics.name}[/bold white]\n\n"
            f"[bold {tier_colour}]★ Black Ops Score: {result['black_ops_score']}/100[/bold {tier_colour}]\n"
            f"[{tier_colour}]Tier: {result['tier']} — {result['tier_description']}[/{tier_colour}]\n"
            f"[dim]Confidence Interval: {result['confidence_interval']['lower']} – "
            f"{result['confidence_interval']['upper']}[/dim]\n"
            f"[dim]Data Completeness: {result['data_completeness'] * 100:.0f}%[/dim]",
            title="🏒 Black Ops Score"
        ))

        breakdown_table = Table(title="Component Breakdown")
        breakdown_table.add_column("Component", style="cyan")
        breakdown_table.add_column("Score (0-100)", style="green")
        breakdown_table.add_column("Weight", style="yellow")

        labels = {
            "gsax": "GSAx",
            "hd_sv_pct": "High-Danger SV%",
            "rebound_control": "Rebound Control",
            "consistency": "Consistency Index",
            "movement": "Movement Efficiency",
            "puck_handling": "Puck Handling",
            "development": "Development Trajectory",
        }
        for key, score in result["component_scores"].items():
            weight = result["component_weights"].get(key, 0)
            breakdown_table.add_row(
                labels.get(key, key),
                f"{score:.1f}",
                f"{weight * 100:.0f}%",
            )
        console.print(breakdown_table)

    except Exception as e:
        console.print(f"[red]Error calculating Black Ops Score: {e}[/red]")
        logger.error(f"Error calculating Black Ops Score: {e}", exc_info=True)


@main.command('compare')
@click.argument('player_id_1')
@click.argument('player_id_2')
@click.option('--db-path', default='./data/goalie_database.json', help='Path to database file')
def compare(player_id_1, player_id_2, db_path):
    """Side-by-side advanced comparison of two goalies."""
    try:
        db = GoalieDatabase(db_path)
        profile1 = db.get_goalie(player_id_1)
        profile2 = db.get_goalie(player_id_2)

        if not profile1:
            console.print(f"[red]Goalie not found: {player_id_1}[/red]")
            return
        if not profile2:
            console.print(f"[red]Goalie not found: {player_id_2}[/red]")
            return

        comparison = ComparisonEngine.compare_goalies(profile1, profile2)

        name1 = profile1.demographics.name
        name2 = profile2.demographics.name

        table = Table(title=f"Comparison: {name1} vs {name2}")
        table.add_column("Metric", style="cyan")
        table.add_column(name1, style="green")
        table.add_column(name2, style="yellow")
        table.add_column("Advantage", style="magenta")

        for metric, diff_data in comparison.get("differences", {}).items():
            display = metric.replace("career_", "").replace("_", " ").title()
            val1 = comparison["goalie1"]["stats"].get(metric, 0)
            val2 = comparison["goalie2"]["stats"].get(metric, 0)
            advantage = diff_data.get("advantage", "equal")
            adv_str = name1 if advantage == "goalie1" else (name2 if advantage == "goalie2" else "Equal")

            if isinstance(val1, float):
                table.add_row(display, f"{val1:.3f}", f"{val2:.3f}", adv_str)
            else:
                table.add_row(display, str(val1), str(val2), adv_str)

        console.print(table)

        # Black Ops scores
        def _score(profile):
            career = GoalieAnalytics.calculate_career_stats(profile)
            sv_pcts = [m.save_percentage for m in profile.performance_metrics if m.save_percentage > 0]
            cons = calculate_consistency(sv_pcts) if sv_pcts else {}
            hd_est = max(0.820, career.get("career_save_percentage", 0) - 0.040)
            return calculate_black_ops_score(
                hd_sv_pct=hd_est,
                consistency_score=cons.get("consistency_score"),
                games_played=career.get("career_games", 0),
            )

        bos1 = _score(profile1)
        bos2 = _score(profile2)

        score_table = Table(title="Black Ops Score Comparison")
        score_table.add_column("", style="cyan")
        score_table.add_column(name1, style="green")
        score_table.add_column(name2, style="yellow")

        score_table.add_row(
            "Black Ops Score",
            f"{bos1['black_ops_score']}/100",
            f"{bos2['black_ops_score']}/100",
        )
        score_table.add_row("Tier", bos1["tier"], bos2["tier"])

        console.print(score_table)

    except Exception as e:
        console.print(f"[red]Error comparing goalies: {e}[/red]")
        logger.error(f"Error comparing goalies: {e}", exc_info=True)


if __name__ == '__main__':
    main()
