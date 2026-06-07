"""Pipeline health monitoring and status reporting.

Tracks last successful run times, data freshness, error rates per
source, and provides a CLI-friendly status summary.
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_STATE_FILE_DEFAULT = "./data/.pipeline_state.json"
_STALE_HOURS = 48


class PipelineHealthCheck:
    """Monitor pipeline health and data freshness.

    Reads and writes a lightweight JSON state file that records the last
    successful run time for each pipeline task and any recent errors.
    Provides a ``get_status_summary`` method for CLI display.

    Args:
        state_file: Path to the JSON state file.  Defaults to
            ``./data/.pipeline_state.json``.

    Example::

        health = PipelineHealthCheck()
        health.record_run("daily_update", success=True)
        print(health.get_status_summary())
    """

    def __init__(self, state_file: Optional[str] = None) -> None:
        self.state_file = Path(
            state_file or os.getenv("PIPELINE_STATE_FILE", _STATE_FILE_DEFAULT)
        )
        self._state: Dict[str, Any] = self._load_state()

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------

    def _load_state(self) -> Dict[str, Any]:
        """Load state from the JSON file, returning empty state on error.

        Returns:
            Loaded state dictionary.
        """
        if not self.state_file.exists():
            return {"runs": {}, "errors": {}}
        try:
            with self.state_file.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as exc:
            logger.warning("Could not read pipeline state file: %s", exc)
            return {"runs": {}, "errors": {}}

    def _save_state(self) -> None:
        """Persist current state to the JSON file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with self.state_file.open("w", encoding="utf-8") as fh:
                json.dump(self._state, fh, indent=2, default=str)
        except Exception as exc:
            logger.warning("Could not save pipeline state file: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_run(
        self,
        task_name: str,
        success: bool,
        records_saved: int = 0,
        errors: Optional[List[str]] = None,
    ) -> None:
        """Record the outcome of a pipeline task run.

        Args:
            task_name: Identifier for the pipeline task
                (e.g. ``"daily_update"``).
            success: Whether the run completed successfully.
            records_saved: Number of records persisted in this run.
            errors: Optional list of error messages from the run.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        run_entry: Dict[str, Any] = {
            "last_run": now_str,
            "last_success": now_str if success else None,
            "records_saved": records_saved,
        }

        # Preserve previous last_success if this run failed
        existing = self._state["runs"].get(task_name, {})
        if not success and existing.get("last_success"):
            run_entry["last_success"] = existing["last_success"]

        self._state["runs"][task_name] = run_entry

        if errors:
            self._state["errors"].setdefault(task_name, [])
            # Keep only the last 20 errors per task
            self._state["errors"][task_name] = (
                self._state["errors"][task_name] + errors
            )[-20:]

        self._save_state()
        logger.debug("Recorded run for task '%s': success=%s", task_name, success)

    def is_stale(self, task_name: str, max_hours: int = _STALE_HOURS) -> bool:
        """Check whether a task's last successful run is older than *max_hours*.

        Args:
            task_name: Pipeline task identifier.
            max_hours: Maximum acceptable age in hours (default 48).

        Returns:
            ``True`` if no successful run is recorded or the last
            success was more than *max_hours* ago.
        """
        run_info = self._state["runs"].get(task_name, {})
        last_success = run_info.get("last_success")
        if not last_success:
            return True
        try:
            last_dt = datetime.fromisoformat(last_success)
            return (datetime.now(timezone.utc) - last_dt) > timedelta(hours=max_hours)
        except ValueError:
            return True

    def get_status_summary(self) -> str:
        """Return a human-readable status summary of all tracked tasks.

        Returns:
            Multi-line string suitable for CLI display.
        """
        lines: List[str] = ["Pipeline Health Status", "=" * 40]
        runs = self._state.get("runs", {})

        if not runs:
            lines.append("No pipeline runs recorded yet.")
        else:
            for task, info in sorted(runs.items()):
                last_run = info.get("last_run", "never")
                last_success = info.get("last_success", "never")
                records = info.get("records_saved", 0)
                stale = self.is_stale(task)
                stale_flag = " ⚠ STALE" if stale else ""
                lines.append(
                    f"{task}: last_run={last_run}  last_success={last_success}"
                    f"  records_saved={records}{stale_flag}"
                )

        errors = self._state.get("errors", {})
        if errors:
            lines.append("")
            lines.append("Recent Errors")
            lines.append("-" * 20)
            for task, task_errors in errors.items():
                if task_errors:
                    lines.append(f"{task}:")
                    for err in task_errors[-3:]:
                        lines.append(f"  - {err}")

        return "\n".join(lines)

    def get_status_dict(self) -> Dict[str, Any]:
        """Return the health status as a serializable dictionary.

        Returns:
            Dictionary with ``runs``, ``errors``, and ``stale_tasks``
            keys.
        """
        stale_tasks = [
            task
            for task in self._state.get("runs", {})
            if self.is_stale(task)
        ]
        return {
            "runs": self._state.get("runs", {}),
            "errors": self._state.get("errors", {}),
            "stale_tasks": stale_tasks,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
