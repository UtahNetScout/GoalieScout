"""Pipeline task scheduler using APScheduler.

Configures and manages scheduled runs of the daily update pipeline,
weekly full re-scrapes, goalie discovery, and monthly integrity checks.
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PipelineScheduler:
    """Schedule automated pipeline runs using APScheduler.

    Sets up cron-style jobs for:
    - Nightly daily update at 2:00 AM (configurable)
    - Weekly full EliteProspects re-scrape on Sundays at 6:00 AM
    - Weekly goalie discovery on Sundays at 7:00 AM
    - Monthly database integrity check on the 1st at 3:00 AM

    APScheduler is an optional dependency; if it is not installed, the
    scheduler degrades gracefully and logs a warning.

    Args:
        db: Database object to pass to pipeline instances.
        timezone: Timezone string for the scheduler (default ``"UTC"``).

    Example::

        scheduler = PipelineScheduler(db=my_db)
        scheduler.start()
        # ... application runs ...
        scheduler.stop()
    """

    def __init__(self, db: Any = None, timezone: str = "UTC") -> None:
        self.db = db
        self.timezone = timezone
        self._scheduler: Optional[Any] = None
        self._running = False

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def _nightly_hour(self) -> int:
        """Read nightly run hour from environment or use default.

        Returns:
            Hour (0-23) for the nightly pipeline.
        """
        try:
            return int(os.getenv("PIPELINE_NIGHTLY_HOUR", "2"))
        except ValueError:
            return 2

    def _weekly_day(self) -> str:
        """Read weekly run day from environment or use default.

        Returns:
            Day abbreviation string such as ``"sun"``.
        """
        return os.getenv("PIPELINE_WEEKLY_DAY", "sun").lower()

    def _weekly_hour(self) -> int:
        """Read weekly run hour from environment or use default.

        Returns:
            Hour (0-23) for the weekly pipeline.
        """
        try:
            return int(os.getenv("PIPELINE_WEEKLY_HOUR", "6"))
        except ValueError:
            return 6

    # ------------------------------------------------------------------
    # Job callbacks
    # ------------------------------------------------------------------

    def _run_daily_update(self) -> None:
        """Callback that runs the daily update pipeline."""
        from .daily_update import DailyUpdatePipeline
        logger.info("Scheduler: starting nightly daily update")
        pipeline = DailyUpdatePipeline(db=self.db)
        result = pipeline.run()
        logger.info(
            "Scheduler: nightly update finished success=%s saved=%d errors=%d",
            result.success,
            result.records_saved,
            len(result.errors),
        )

    def _run_discovery(self) -> None:
        """Callback that runs the weekly goalie discovery."""
        from .discovery import GoalieDiscovery
        from ..apis.nhl_api import NHLAPIClient

        logger.info("Scheduler: starting weekly discovery")
        discovery = GoalieDiscovery(db=self.db)
        # Use the previous complete season's EP slug
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        year = now.year if now.month >= 10 else now.year - 1
        season = f"{year}-{year + 1}"
        new_goalies = discovery.run(season)
        logger.info("Scheduler: discovery finished new_goalies=%d", len(new_goalies))

    def _run_integrity_check(self) -> None:
        """Callback that runs the monthly database integrity check."""
        logger.info("Scheduler: starting monthly integrity check")
        from .health_check import PipelineHealthCheck
        health = PipelineHealthCheck()
        summary = health.get_status_summary()
        logger.info("Scheduler: integrity check complete — %s", summary)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Configure and start the APScheduler background scheduler.

        Raises a warning and returns gracefully if APScheduler is not
        installed.
        """
        try:
            from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore[import]
            from apscheduler.triggers.cron import CronTrigger  # type: ignore[import]
        except ImportError:
            logger.warning(
                "APScheduler is not installed; pipeline scheduling is disabled. "
                "Install it with: pip install apscheduler>=3.10"
            )
            return

        self._scheduler = BackgroundScheduler(timezone=self.timezone)

        nightly_hour = self._nightly_hour()
        weekly_day = self._weekly_day()
        weekly_hour = self._weekly_hour()

        # Nightly daily update
        self._scheduler.add_job(
            self._run_daily_update,
            CronTrigger(hour=nightly_hour, minute=0),
            id="daily_update",
            name="Nightly goalie data update",
            replace_existing=True,
        )
        logger.info("Scheduled: nightly update at %02d:00 UTC", nightly_hour)

        # Weekly EliteProspects re-scrape (re-uses discovery + full scrape)
        self._scheduler.add_job(
            self._run_daily_update,
            CronTrigger(day_of_week=weekly_day, hour=weekly_hour, minute=0),
            id="weekly_full_scrape",
            name="Weekly full data re-scrape",
            replace_existing=True,
        )
        logger.info(
            "Scheduled: weekly re-scrape on %s at %02d:00 UTC",
            weekly_day,
            weekly_hour,
        )

        # Weekly goalie discovery (one hour after re-scrape)
        discovery_hour = (weekly_hour + 1) % 24
        self._scheduler.add_job(
            self._run_discovery,
            CronTrigger(day_of_week=weekly_day, hour=discovery_hour, minute=0),
            id="weekly_discovery",
            name="Weekly goalie discovery",
            replace_existing=True,
        )
        logger.info(
            "Scheduled: weekly discovery on %s at %02d:00 UTC",
            weekly_day,
            discovery_hour,
        )

        # Monthly integrity check on 1st of month at 3:00 AM
        self._scheduler.add_job(
            self._run_integrity_check,
            CronTrigger(day=1, hour=3, minute=0),
            id="monthly_integrity",
            name="Monthly database integrity check",
            replace_existing=True,
        )
        logger.info("Scheduled: monthly integrity check on 1st at 03:00 UTC")

        self._scheduler.start()
        self._running = True
        logger.info("PipelineScheduler started")

    def stop(self) -> None:
        """Stop the background scheduler if it is running."""
        if self._scheduler is not None and self._running:
            self._scheduler.shutdown(wait=False)
            self._running = False
            logger.info("PipelineScheduler stopped")

    @property
    def is_running(self) -> bool:
        """``True`` if the scheduler is currently active."""
        return self._running
