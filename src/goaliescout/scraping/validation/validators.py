"""Data validation engine for goalie statistics and biographical data.

Validates stat ranges, biographical data, and flags anomalous records
for manual review.  Returns :class:`ValidationResult` objects that
describe what passed and what failed.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Outcome of a validation check.

    Attributes:
        passed: ``True`` if all checks passed.
        errors: List of error message strings for failed checks.
        warnings: List of warning messages for suspicious-but-valid data.
        field_errors: Mapping of field name to its specific error string.
    """

    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_errors: Dict[str, str] = field(default_factory=dict)

    def fail(self, message: str, field_name: Optional[str] = None) -> None:
        """Record a validation failure.

        Args:
            message: Human-readable error description.
            field_name: Optional name of the field that failed validation.
        """
        self.passed = False
        self.errors.append(message)
        if field_name:
            self.field_errors[field_name] = message

    def warn(self, message: str) -> None:
        """Record a validation warning without marking the result as failed.

        Args:
            message: Human-readable warning description.
        """
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


class GoalieDataValidator:
    """Validates goalie statistical and biographical records.

    Provides methods to check individual stat dictionaries for
    out-of-range values, missing required fields, and suspicious
    anomalies that warrant review.

    Example::

        validator = GoalieDataValidator()
        result = validator.validate_stats({"save_percentage": 0.915, "games_played": 30})
        if not result:
            print(result.errors)
    """

    # Reasonable bounds for goalie statistics
    STAT_BOUNDS: Dict[str, Dict[str, Any]] = {
        "save_percentage": {"min": 0.0, "max": 1.0, "warn_low": 0.850, "warn_high": 0.980},
        "goals_against_average": {"min": 0.0, "max": 20.0, "warn_high": 6.0},
        "games_played": {"min": 1, "max": 100},
        "wins": {"min": 0, "max": 82},
        "losses": {"min": 0, "max": 82},
        "overtime_losses": {"min": 0, "max": 40},
        "shutouts": {"min": 0, "max": 82},
        "shots_against": {"min": 0, "max": 5000},
        "saves": {"min": 0, "max": 5000},
        "goals_against": {"min": 0, "max": 500},
        "minutes_played": {"min": 0.0, "max": 6000.0},
    }

    # Reasonable physical bounds for bio data
    BIO_BOUNDS: Dict[str, Dict[str, Any]] = {
        "height_cm": {"min": 150, "max": 220},
        "weight_kg": {"min": 60, "max": 130},
        "height_inches": {"min": 59, "max": 87},
        "weight_lbs": {"min": 130, "max": 290},
    }

    # Fields that are required in a stats record
    REQUIRED_STAT_FIELDS = {"games_played"}
    REQUIRED_BIO_FIELDS = {"name"}

    def validate_stats(self, stats: Dict[str, Any]) -> ValidationResult:
        """Validate a goalie statistics dictionary.

        Args:
            stats: Dictionary of statistical fields and their values.

        Returns:
            :class:`ValidationResult` describing any failures or warnings.
        """
        result = ValidationResult()

        # Required fields
        for field_name in self.REQUIRED_STAT_FIELDS:
            if field_name not in stats or stats[field_name] is None:
                result.fail(f"Missing required field: {field_name}", field_name)

        # Range checks
        for field_name, bounds in self.STAT_BOUNDS.items():
            if field_name not in stats or stats[field_name] is None:
                continue

            try:
                value = float(stats[field_name])
            except (TypeError, ValueError):
                result.fail(f"Non-numeric value for {field_name}: {stats[field_name]!r}", field_name)
                continue

            if value < bounds["min"]:
                result.fail(
                    f"{field_name} value {value} is below minimum {bounds['min']}",
                    field_name,
                )
            elif value > bounds["max"]:
                result.fail(
                    f"{field_name} value {value} exceeds maximum {bounds['max']}",
                    field_name,
                )
            else:
                if "warn_low" in bounds and value < bounds["warn_low"]:
                    result.warn(f"{field_name} = {value} is unusually low")
                if "warn_high" in bounds and value > bounds["warn_high"]:
                    result.warn(f"{field_name} = {value} is unusually high")

        # Logical consistency checks
        self._check_stat_consistency(stats, result)

        return result

    def _check_stat_consistency(
        self, stats: Dict[str, Any], result: ValidationResult
    ) -> None:
        """Check logical relationships between stat fields.

        Args:
            stats: Statistics dictionary.
            result: :class:`ValidationResult` to append issues to.
        """
        gp = stats.get("games_played")
        wins = stats.get("wins")
        losses = stats.get("losses")
        otl = stats.get("overtime_losses", 0) or 0
        saves = stats.get("saves")
        shots = stats.get("shots_against")
        goals = stats.get("goals_against")

        if gp and wins is not None and losses is not None:
            try:
                total_decisions = int(wins) + int(losses) + int(otl)
                if total_decisions > int(gp):
                    result.fail(
                        f"W+L+OTL ({total_decisions}) exceeds games_played ({gp})"
                    )
            except (TypeError, ValueError):
                pass

        if saves is not None and shots is not None and goals is not None:
            try:
                if int(saves) + int(goals) != int(shots):
                    result.warn(
                        f"saves ({saves}) + goals_against ({goals}) != shots_against ({shots})"
                    )
            except (TypeError, ValueError):
                pass

    def validate_bio(self, bio: Dict[str, Any]) -> ValidationResult:
        """Validate a goalie biographical record.

        Args:
            bio: Dictionary with biographical fields.

        Returns:
            :class:`ValidationResult` describing any failures or warnings.
        """
        result = ValidationResult()

        # Required fields
        for field_name in self.REQUIRED_BIO_FIELDS:
            if not bio.get(field_name):
                result.fail(f"Missing required bio field: {field_name}", field_name)

        # DOB validation
        dob_str = bio.get("dob") or bio.get("date_of_birth")
        if dob_str:
            parsed_dob = self._parse_date(str(dob_str))
            if parsed_dob is None:
                result.fail(f"Invalid date of birth: {dob_str!r}", "dob")
            else:
                today = date.today()
                age = (today - parsed_dob).days / 365.25
                if age < 14 or age > 55:
                    result.warn(f"Unusual age derived from DOB: {age:.1f} years")

        # Physical measurements
        for field_name, bounds in self.BIO_BOUNDS.items():
            if field_name not in bio or bio[field_name] is None:
                continue
            try:
                value = float(bio[field_name])
            except (TypeError, ValueError):
                continue
            if value < bounds["min"] or value > bounds["max"]:
                result.warn(
                    f"{field_name} = {value} is outside expected range "
                    f"[{bounds['min']}, {bounds['max']}]"
                )

        # Catches
        catches = bio.get("catches")
        if catches and str(catches).upper() not in ("L", "R", "LEFT", "RIGHT", ""):
            result.warn(f"Unexpected catches value: {catches!r}")

        return result

    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        """Attempt to parse a date string into a :class:`date`.

        Args:
            date_str: String representation of a date.

        Returns:
            Parsed :class:`date` or ``None`` if parsing fails.
        """
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        return None

    def validate_record(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate a combined record containing both bio and stats fields.

        Args:
            record: Dictionary that may contain any combination of
                biographical and statistical fields.

        Returns:
            Merged :class:`ValidationResult` combining bio and stats
            validation outcomes.
        """
        bio_result = self.validate_bio(record)
        stats_result = self.validate_stats(record)

        combined = ValidationResult()
        combined.passed = bio_result.passed and stats_result.passed
        combined.errors = bio_result.errors + stats_result.errors
        combined.warnings = bio_result.warnings + stats_result.warnings
        combined.field_errors = {**bio_result.field_errors, **stats_result.field_errors}
        return combined
