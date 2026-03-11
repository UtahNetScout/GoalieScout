"""Data normalization utilities for goalie records.

Normalises player names, league names, stat field names, and unit
conversions so that data from disparate sources can be merged into a
single unified schema.
"""

import logging
import re
import unicodedata
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# League name normalisation map
# Maps common variations to standard codes.
# ---------------------------------------------------------------------------
_LEAGUE_MAP: Dict[str, str] = {
    # CHL
    "ontario hockey league": "OHL",
    "ontario hl": "OHL",
    "western hockey league": "WHL",
    "western hl": "WHL",
    "quebec major junior hockey league": "QMJHL",
    "ligue de hockey junior majeur du québec": "QMJHL",
    "lhmjq": "QMJHL",
    # North America
    "national hockey league": "NHL",
    "american hockey league": "AHL",
    "united states hockey league": "USHL",
    "echl": "ECHL",
    "ncaa": "NCAA",
    "college hockey": "NCAA",
    # Europe
    "kontinental hockey league": "KHL",
    "kontinental hl": "KHL",
    "swedish hockey league": "SHL",
    "swedish hl": "SHL",
    "finnish liiga": "Liiga",
    "sm-liiga": "Liiga",
    "liiga": "Liiga",
    "national league": "NL",
    "national league a": "NL",
    "czech extraliga": "Czech",
    "tipsport extraliga": "Czech",
    "ahl": "AHL",
    "nhl": "NHL",
    "ohl": "OHL",
    "whl": "WHL",
    "shl": "SHL",
    "khl": "KHL",
    "ushl": "USHL",
    "high school": "HS",
}

# ---------------------------------------------------------------------------
# Field name normalisation map
# Maps source-specific column names to the unified schema field names.
# ---------------------------------------------------------------------------
_FIELD_MAP: Dict[str, str] = {
    # Stats
    "gp": "games_played",
    "games": "games_played",
    "w": "wins",
    "l": "losses",
    "otl": "overtime_losses",
    "ot": "overtime_losses",
    "t": "ties",
    "so": "shutouts",
    "sv%": "save_percentage",
    "svpct": "save_percentage",
    "savepctg": "save_percentage",
    "save_pct": "save_percentage",
    "gaa": "goals_against_average",
    "goalsagainstaverage": "goals_against_average",
    "ga": "goals_against",
    "goalsagainst": "goals_against",
    "sa": "shots_against",
    "shotsagainst": "shots_against",
    "sv": "saves",
    "min": "minutes_played",
    "toi": "minutes_played",
    # Bio
    "first_name": "first_name",
    "last_name": "last_name",
    "fullname": "name",
    "playerfullname": "name",
    "skaterFullName": "name",
    "birthdate": "dob",
    "date_of_birth": "dob",
    "birthcountry": "nationality",
    "nation": "nationality",
    "country": "nationality",
    "heightininches": "height_inches",
    "heightincm": "height_cm",
    "weightinpounds": "weight_lbs",
    "weightinkg": "weight_kg",
    "catches": "catches",
    "shoots": "catches",
}


class DataNormalizer:
    """Normalise player names, league names, stat field names, and units.

    Example::

        normalizer = DataNormalizer()
        name = normalizer.normalize_name("Juuse Saros")
        league = normalizer.normalize_league("Ontario Hockey League")
        stats = normalizer.normalize_stat_fields({"GP": 30, "SV%": 0.915})
    """

    def normalize_name(self, name: str) -> str:
        """Normalize a player name by removing accents and standardizing whitespace.

        Args:
            name: Raw player name string.

        Returns:
            Normalized name with ASCII characters and consistent spacing.
        """
        if not name:
            return ""
        # Decompose unicode characters and strip combining marks
        nfd = unicodedata.normalize("NFD", name)
        ascii_name = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
        # Collapse whitespace
        return re.sub(r"\s+", " ", ascii_name).strip()

    def normalize_league(self, league: str) -> str:
        """Map a league name string to a standard league code.

        Args:
            league: Raw league name or code string.

        Returns:
            Standard league code (e.g. ``"OHL"``, ``"NHL"``).  Returns
            the input uppercased if no mapping is found.
        """
        if not league:
            return ""
        lookup = league.strip().lower()
        mapped = _LEAGUE_MAP.get(lookup)
        if mapped:
            return mapped
        # Try partial matches for longer strings
        for key, code in _LEAGUE_MAP.items():
            if key in lookup or lookup in key:
                return code
        return league.strip().upper()

    def normalize_stat_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Rename record keys to the unified schema field names.

        Args:
            record: Dictionary of stats with potentially inconsistent
                field names from various sources.

        Returns:
            New dictionary with normalized key names.  Unknown keys are
            preserved unchanged.
        """
        normalized: Dict[str, Any] = {}
        for raw_key, value in record.items():
            clean_key = raw_key.strip().replace(" ", "_").replace("%", "pct")
            mapped = _FIELD_MAP.get(clean_key) or _FIELD_MAP.get(clean_key.lower())
            normalized[mapped or clean_key] = value
        return normalized

    def convert_height(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> Optional[float]:
        """Convert height between centimetres and inches.

        Args:
            value: Numeric height value.
            from_unit: Source unit — ``"cm"`` or ``"inches"``.
            to_unit: Target unit — ``"cm"`` or ``"inches"``.

        Returns:
            Converted value rounded to one decimal, or ``None`` if
            unit strings are unrecognised.
        """
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        if from_unit == to_unit:
            return round(float(value), 1)
        if from_unit == "cm" and to_unit in ("in", "inches"):
            return round(value / 2.54, 1)
        if from_unit in ("in", "inches") and to_unit == "cm":
            return round(value * 2.54, 1)
        logger.warning("Unknown height unit conversion: %s -> %s", from_unit, to_unit)
        return None

    def convert_weight(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> Optional[float]:
        """Convert weight between kilograms and pounds.

        Args:
            value: Numeric weight value.
            from_unit: Source unit — ``"kg"`` or ``"lbs"``.
            to_unit: Target unit — ``"kg"`` or ``"lbs"``.

        Returns:
            Converted value rounded to one decimal, or ``None`` if
            unit strings are unrecognised.
        """
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        if from_unit == to_unit:
            return round(float(value), 1)
        if from_unit == "kg" and to_unit == "lbs":
            return round(value * 2.20462, 1)
        if from_unit == "lbs" and to_unit == "kg":
            return round(value / 2.20462, 1)
        logger.warning("Unknown weight unit conversion: %s -> %s", from_unit, to_unit)
        return None

    def normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all normalization steps to a goalie record.

        Normalizes field names, player name, and league name in a single
        pass.

        Args:
            record: Raw goalie record from any data source.

        Returns:
            Fully normalized record ready for validation and database
            insertion.
        """
        normalized = self.normalize_stat_fields(record)

        if "name" in normalized:
            normalized["name"] = self.normalize_name(str(normalized["name"]))

        if "league" in normalized:
            normalized["league"] = self.normalize_league(str(normalized["league"]))

        return normalized
