"""Goalie record deduplication using fuzzy name matching and DOB comparison.

Detects duplicate player records across data sources, merges them into
enriched profiles, tracks data provenance, and resolves field-level
conflicts using a configurable source priority.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Source priority for conflict resolution: higher index = higher authority.
# When two sources disagree on a value, the one with the higher priority wins.
_SOURCE_PRIORITY: List[str] = [
    "EliteProspects",
    "HockeyDB",
    "MoneyPuck",
    "NaturalStatTrick",
    "NHL",
]


def _source_rank(source: str) -> int:
    """Return the authority rank of *source* (higher is more authoritative).

    Args:
        source: Source identifier string.

    Returns:
        Integer rank; sources not in the priority list receive rank 0.
    """
    try:
        return _SOURCE_PRIORITY.index(source) + 1
    except ValueError:
        return 0


def _bigrams(s: str) -> set:
    """Return the set of character bigrams for string *s*.

    Args:
        s: Input string (should already be lowercased).

    Returns:
        Set of two-character substrings.
    """
    return {s[i:i + 2] for i in range(len(s) - 1)}


def _fuzzy_ratio(a: str, b: str) -> float:
    """Compute a simple character-overlap similarity ratio.

    Uses the Levenshtein edit distance via the ``python-Levenshtein``
    package when available, falling back to a basic Jaccard bigram
    overlap otherwise.

    Args:
        a: First string.
        b: Second string.

    Returns:
        Float in [0, 100] representing percentage similarity.
    """
    a = a.lower().strip()
    b = b.lower().strip()
    if a == b:
        return 100.0

    try:
        import Levenshtein  # type: ignore[import]
        return Levenshtein.ratio(a, b) * 100.0
    except ImportError:
        pass

    # Fallback: Jaccard similarity on character bigrams
    ba, bb = _bigrams(a), _bigrams(b)
    if not ba or not bb:
        return 0.0
    union = ba | bb
    return len(ba & bb) / len(union) * 100.0


class GoalieDeduplicator:
    """Detect and merge duplicate goalie records across data sources.

    Uses fuzzy name matching combined with date-of-birth comparison to
    identify duplicates.  Merges records using source-priority-based
    conflict resolution and tracks data provenance.

    Args:
        name_threshold: Minimum fuzzy name similarity (0-100) required
            to consider two records potentially the same player.
        dob_required: If ``True``, DOB must also match when available to
            confirm a duplicate.

    Example::

        deduplicator = GoalieDeduplicator()
        merged = deduplicator.merge_records([ep_record, hockeydb_record])
    """

    def __init__(
        self,
        name_threshold: float = 85.0,
        dob_required: bool = False,
    ) -> None:
        self.name_threshold = name_threshold
        self.dob_required = dob_required

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_duplicates(
        self, records: List[Dict[str, Any]]
    ) -> List[Tuple[int, int, float]]:
        """Identify pairs of records that likely refer to the same player.

        Args:
            records: List of goalie record dictionaries.  Each record
                should have at least a ``name`` field and optionally a
                ``dob`` field.

        Returns:
            List of ``(i, j, score)`` tuples where *i* and *j* are
            indices into *records* and *score* is the similarity value
            (0-100).
        """
        duplicates: List[Tuple[int, int, float]] = []

        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                score = self._similarity(records[i], records[j])
                if score >= self.name_threshold:
                    duplicates.append((i, j, score))
                    logger.debug(
                        "Potential duplicate: '%s' vs '%s' (score=%.1f)",
                        records[i].get("name"),
                        records[j].get("name"),
                        score,
                    )

        return duplicates

    def merge_records(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge a list of records for the same player into one enriched profile.

        Field-level conflicts are resolved by source priority: when two
        sources provide different values for the same field, the value
        from the higher-priority source is used.  All contributing
        sources are listed in the ``data_sources`` field of the result.

        Args:
            records: List of records all referring to the same player,
                potentially from different sources.

        Returns:
            Single merged record dictionary with a ``data_sources`` list
            and ``_provenance`` mapping (field → source).
        """
        if not records:
            return {}
        if len(records) == 1:
            result = records[0].copy()
            result.setdefault("data_sources", [result.get("source", "unknown")])
            return result

        # Sort so highest-priority source comes last (wins in overwrite)
        def priority(r: Dict[str, Any]) -> int:
            return _source_rank(r.get("source", ""))

        sorted_records = sorted(records, key=priority)

        merged: Dict[str, Any] = {}
        provenance: Dict[str, str] = {}

        for record in sorted_records:
            source = record.get("source", "unknown")
            for key, value in record.items():
                if key in ("source", "data_sources", "_provenance"):
                    continue
                if value not in (None, "", [], {}):
                    merged[key] = value
                    provenance[key] = source

        merged["data_sources"] = list({r.get("source", "unknown") for r in records})
        merged["_provenance"] = provenance
        return merged

    def deduplicate_list(
        self, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicates from a list of goalie records.

        Identifies duplicate pairs, groups them into clusters, merges
        each cluster, and returns a deduplicated list.

        Args:
            records: Raw list of goalie records, potentially containing
                duplicates from multiple sources.

        Returns:
            Deduplicated list of merged goalie records.
        """
        if not records:
            return []

        duplicate_pairs = self.find_duplicates(records)
        if not duplicate_pairs:
            return list(records)

        # Build a union-find structure to cluster duplicates
        parent = list(range(len(records)))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x: int, y: int) -> None:
            parent[find(x)] = find(y)

        for i, j, _ in duplicate_pairs:
            union(i, j)

        clusters: Dict[int, List[int]] = {}
        for idx in range(len(records)):
            root = find(idx)
            clusters.setdefault(root, []).append(idx)

        merged_records: List[Dict[str, Any]] = []
        for cluster_indices in clusters.values():
            cluster = [records[i] for i in cluster_indices]
            merged_records.append(self.merge_records(cluster))

        logger.info(
            "Deduplicated %d records into %d unique profiles",
            len(records),
            len(merged_records),
        )
        return merged_records

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _similarity(
        self, record_a: Dict[str, Any], record_b: Dict[str, Any]
    ) -> float:
        """Compute similarity score between two records.

        Args:
            record_a: First record.
            record_b: Second record.

        Returns:
            Similarity score 0-100.  Returns 0 if both DOBs are present
            but do not match (when *dob_required* is ``True``).
        """
        name_a = str(record_a.get("name") or "")
        name_b = str(record_b.get("name") or "")
        name_score = _fuzzy_ratio(name_a, name_b)

        if name_score < self.name_threshold:
            return name_score

        dob_a = record_a.get("dob") or record_a.get("date_of_birth")
        dob_b = record_b.get("dob") or record_b.get("date_of_birth")

        if dob_a and dob_b:
            if str(dob_a).strip() == str(dob_b).strip():
                return min(name_score + 10.0, 100.0)
            elif self.dob_required:
                return 0.0

        return name_score
