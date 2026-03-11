"""Daily update pipeline for automated goalie data synchronization.

Orchestrates the nightly process of pulling fresh goalie data from all
configured sources, validating and normalizing it, merging it into the
database, and triggering alert checks.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..apis.nhl_api import NHLAPIClient
from ..apis.moneypuck import MoneyPuckClient
from ..apis.natural_stat_trick import NaturalStatTrickClient
from ..validation.validators import GoalieDataValidator
from ..validation.normalization import DataNormalizer
from ..validation.deduplication import GoalieDeduplicator

logger = logging.getLogger(__name__)


class PipelineRunResult:
    """Captures the outcome of a pipeline run.

    Attributes:
        started_at: Timestamp when the pipeline started.
        finished_at: Timestamp when the pipeline finished (or ``None``
            if it hasn't finished yet).
        sources_attempted: Names of data sources the pipeline tried.
        records_fetched: Count of raw records fetched per source.
        records_saved: Number of records committed to the database.
        errors: List of error messages encountered during the run.
        success: ``True`` if the run completed without fatal errors.
    """

    def __init__(self) -> None:
        self.started_at: datetime = datetime.now(timezone.utc)
        self.finished_at: Optional[datetime] = None
        self.sources_attempted: List[str] = []
        self.records_fetched: Dict[str, int] = {}
        self.records_saved: int = 0
        self.errors: List[str] = []
        self.success: bool = False

    def finish(self, success: bool = True) -> None:
        """Mark the pipeline run as complete.

        Args:
            success: Whether the run succeeded overall.
        """
        self.finished_at = datetime.now(timezone.utc)
        self.success = success

    @property
    def duration_seconds(self) -> Optional[float]:
        """Elapsed time in seconds, or ``None`` if still running."""
        if self.finished_at is None:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the run result to a plain dictionary."""
        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "sources_attempted": self.sources_attempted,
            "records_fetched": self.records_fetched,
            "records_saved": self.records_saved,
            "errors": self.errors,
            "success": self.success,
        }


class DailyUpdatePipeline:
    """Nightly pipeline that keeps the goalie database current.

    Pulls data from all enabled sources, validates and normalizes
    records, deduplicates, updates the database, and logs a run
    summary.

    Args:
        db: Optional database object.  If ``None``, the pipeline runs
            in dry-run mode (validates and logs but does not persist).
        season: Eight-character NHL season string (e.g. ``"20232024"``).
            Defaults to the current season heuristic.

    Example::

        pipeline = DailyUpdatePipeline(season="20232024")
        result = pipeline.run()
        print(result.to_dict())
    """

    def __init__(
        self,
        db: Any = None,
        season: Optional[str] = None,
    ) -> None:
        self.db = db
        self.season = season or self._current_season()
        self.validator = GoalieDataValidator()
        self.normalizer = DataNormalizer()
        self.deduplicator = GoalieDeduplicator()

        # Clients (only initialised when that source is enabled)
        self._nhl: Optional[NHLAPIClient] = None
        self._moneypuck: Optional[MoneyPuckClient] = None
        self._nst: Optional[NaturalStatTrickClient] = None

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _current_season() -> str:
        """Return the best-guess current NHL season string.

        Returns:
            Eight-character season string such as ``"20232024"``.
        """
        now = datetime.now(timezone.utc)
        year = now.year
        # NHL season starts in October; before October we're still in
        # the prior season for stats purposes.
        if now.month < 10:
            return f"{year - 1}{year}"
        return f"{year}{year + 1}"

    def _enabled(self, env_var: str) -> bool:
        """Check whether a data source is enabled via environment variable.

        Args:
            env_var: Environment variable name to check.

        Returns:
            ``True`` unless the variable is explicitly set to ``"false"``.
        """
        return os.getenv(env_var, "true").lower() not in ("false", "0", "no")

    # ------------------------------------------------------------------
    # Source-specific fetch steps
    # ------------------------------------------------------------------

    def _fetch_nhl(self, run: PipelineRunResult) -> List[Dict[str, Any]]:
        """Fetch active goalie data from the NHL API.

        Args:
            run: Active run result object for logging.

        Returns:
            List of normalized goalie records.
        """
        run.sources_attempted.append("NHL")
        try:
            if self._nhl is None:
                self._nhl = NHLAPIClient()
            raw = self._nhl.get_all_goalies(self.season)
            run.records_fetched["NHL"] = len(raw)
            normalized = [self.normalizer.normalize_record({**r, "source": "NHL"}) for r in raw]
            logger.info("NHL: fetched %d goalie records", len(normalized))
            return normalized
        except Exception as exc:
            msg = f"NHL fetch failed: {exc}"
            run.errors.append(msg)
            logger.exception(msg)
            return []

    def _fetch_moneypuck(self, run: PipelineRunResult) -> List[Dict[str, Any]]:
        """Fetch advanced stats from MoneyPuck.

        Args:
            run: Active run result object for logging.

        Returns:
            List of normalized goalie records.
        """
        run.sources_attempted.append("MoneyPuck")
        # MoneyPuck season is four-digit year (start year of season)
        mp_season = self.season[:4]
        try:
            if self._moneypuck is None:
                self._moneypuck = MoneyPuckClient()
            df = self._moneypuck.download_season_data(mp_season)
            if "situation" in df.columns:
                df = df[df["situation"] == "all"]
            records = df.to_dict(orient="records")
            run.records_fetched["MoneyPuck"] = len(records)
            normalized = [
                self.normalizer.normalize_record({**r, "source": "MoneyPuck"})
                for r in records
            ]
            logger.info("MoneyPuck: fetched %d records", len(normalized))
            return normalized
        except Exception as exc:
            msg = f"MoneyPuck fetch failed: {exc}"
            run.errors.append(msg)
            logger.exception(msg)
            return []

    def _fetch_nst(self, run: PipelineRunResult) -> List[Dict[str, Any]]:
        """Fetch advanced splits from Natural Stat Trick.

        Args:
            run: Active run result object for logging.

        Returns:
            List of normalized goalie records.
        """
        run.sources_attempted.append("NaturalStatTrick")
        try:
            if self._nst is None:
                self._nst = NaturalStatTrickClient()
            df = self._nst.get_goalie_splits(self.season, "5v5")
            if df.empty:
                run.records_fetched["NaturalStatTrick"] = 0
                return []
            records = df.to_dict(orient="records")
            run.records_fetched["NaturalStatTrick"] = len(records)
            normalized = [
                self.normalizer.normalize_record({**r, "source": "NaturalStatTrick"})
                for r in records
            ]
            logger.info("NaturalStatTrick: fetched %d records", len(normalized))
            return normalized
        except Exception as exc:
            msg = f"NaturalStatTrick fetch failed: {exc}"
            run.errors.append(msg)
            logger.exception(msg)
            return []

    # ------------------------------------------------------------------
    # Core pipeline logic
    # ------------------------------------------------------------------

    def _validate_records(
        self, records: List[Dict[str, Any]], run: PipelineRunResult
    ) -> List[Dict[str, Any]]:
        """Validate a list of records, dropping those with fatal errors.

        Args:
            records: List of normalized records.
            run: Active run result for logging warnings/errors.

        Returns:
            Subset of *records* that passed validation.
        """
        valid: List[Dict[str, Any]] = []
        for record in records:
            result = self.validator.validate_record(record)
            if result.passed:
                valid.append(record)
            else:
                source = record.get("source", "unknown")
                name = record.get("name", "unknown")
                logger.warning(
                    "Validation failed for %s (%s): %s",
                    name,
                    source,
                    "; ".join(result.errors),
                )
        return valid

    def _save_to_db(
        self, records: List[Dict[str, Any]], run: PipelineRunResult
    ) -> int:
        """Persist validated records to the database if one is attached.

        Args:
            records: Deduplicated, validated records to save.
            run: Active run result for logging.

        Returns:
            Number of records saved.
        """
        if self.db is None:
            logger.info("No database attached; skipping persistence (dry-run)")
            return 0

        saved = 0
        for record in records:
            try:
                player_id = (
                    str(record.get("name", "unknown"))
                    .lower()
                    .replace(" ", "_")
                )
                self.db.upsert_goalie_record(player_id, record)
                saved += 1
            except Exception as exc:
                name = record.get("name", "unknown")
                msg = f"DB save failed for {name}: {exc}"
                run.errors.append(msg)
                logger.error(msg)

        return saved

    def run(self, sources: Optional[List[str]] = None) -> PipelineRunResult:
        """Execute the daily update pipeline.

        Args:
            sources: Optional list of source names to restrict the run to
                (e.g. ``["nhl"]``).  When ``None``, all enabled sources
                are queried.

        Returns:
            :class:`PipelineRunResult` describing what happened.
        """
        run = PipelineRunResult()
        logger.info("Starting daily update pipeline for season %s", self.season)

        all_records: List[Dict[str, Any]] = []

        # --- Fetch ---
        if sources is None or "nhl" in [s.lower() for s in sources]:
            if self._enabled("ENABLE_NHL_API"):
                all_records.extend(self._fetch_nhl(run))

        if sources is None or "moneypuck" in [s.lower() for s in sources]:
            if self._enabled("ENABLE_MONEYPUCK"):
                all_records.extend(self._fetch_moneypuck(run))

        if sources is None or "nst" in [s.lower() for s in sources]:
            if self._enabled("ENABLE_NATURAL_STAT_TRICK"):
                all_records.extend(self._fetch_nst(run))

        if not all_records:
            logger.warning("No records fetched; pipeline run produced no data")
            run.finish(success=len(run.errors) == 0)
            return run

        # --- Validate ---
        valid_records = self._validate_records(all_records, run)
        logger.info(
            "Validation: %d/%d records passed", len(valid_records), len(all_records)
        )

        # --- Deduplicate ---
        unique_records = self.deduplicator.deduplicate_list(valid_records)
        logger.info(
            "Deduplication: %d records -> %d unique profiles",
            len(valid_records),
            len(unique_records),
        )

        # --- Persist ---
        run.records_saved = self._save_to_db(unique_records, run)

        run.finish(success=len(run.errors) == 0)
        logger.info(
            "Pipeline complete: saved=%d errors=%d duration=%.1fs",
            run.records_saved,
            len(run.errors),
            run.duration_seconds or 0,
        )
        return run
