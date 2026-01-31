"""Utility functions for the scouting platform."""

import re
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def sanitize_player_name(name: str) -> str:
    """Sanitize player name for use as ID or filename.
    
    Args:
        name: Player name
        
    Returns:
        Sanitized name
    """
    # Convert to lowercase
    sanitized = name.lower()
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove special characters
    sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)
    
    return sanitized


def validate_save_percentage(sv_pct: float) -> bool:
    """Validate save percentage is in valid range.
    
    Args:
        sv_pct: Save percentage (0-1 scale)
        
    Returns:
        True if valid
    """
    return 0.0 <= sv_pct <= 1.0


def validate_gaa(gaa: float) -> bool:
    """Validate goals against average is reasonable.
    
    Args:
        gaa: Goals against average
        
    Returns:
        True if valid
    """
    return 0.0 <= gaa <= 10.0


def calculate_age(date_of_birth: str) -> int:
    """Calculate age from date of birth.
    
    Args:
        date_of_birth: Date of birth in YYYY-MM-DD format
        
    Returns:
        Age in years
    """
    from datetime import datetime
    
    try:
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except Exception as e:
        logger.error(f"Error calculating age: {e}")
        return 0


def format_height(height_cm: float) -> str:
    """Format height in feet and inches.
    
    Args:
        height_cm: Height in centimeters
        
    Returns:
        Formatted height string (e.g., "6'2")
    """
    total_inches = height_cm / 2.54
    feet = int(total_inches // 12)
    inches = int(total_inches % 12)
    return f"{feet}'{inches}\""


def format_weight(weight_kg: float) -> str:
    """Format weight in pounds.
    
    Args:
        weight_kg: Weight in kilograms
        
    Returns:
        Formatted weight string (e.g., "185 lbs")
    """
    weight_lbs = int(weight_kg * 2.20462)
    return f"{weight_lbs} lbs"


def validate_profile_data(profile_data: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate goalie profile data.
    
    Args:
        profile_data: Profile dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if 'player_id' not in profile_data:
        errors.append("Missing player_id")
    
    if 'demographics' not in profile_data:
        errors.append("Missing demographics")
    else:
        demographics = profile_data['demographics']
        if 'name' not in demographics:
            errors.append("Missing name in demographics")
        if 'country' not in demographics:
            errors.append("Missing country in demographics")
    
    # Validate performance metrics
    metrics = profile_data.get('performance_metrics', [])
    for i, metric in enumerate(metrics):
        sv_pct = metric.get('save_percentage', 0)
        if not validate_save_percentage(sv_pct):
            errors.append(f"Invalid save percentage in metric {i}: {sv_pct}")
        
        gaa = metric.get('goals_against_average', 0)
        if not validate_gaa(gaa):
            errors.append(f"Invalid GAA in metric {i}: {gaa}")
    
    return len(errors) == 0, errors
