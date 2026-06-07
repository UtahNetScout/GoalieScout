# GoalieScout Automated Data Pipeline

This document explains how the GoalieScout automated data pipeline works, how to configure it, and how to add new data sources.

---

## Table of Contents

1. [Overview](#overview)
2. [Available Data Sources](#available-data-sources)
3. [Configuration](#configuration)
4. [Running the Pipeline](#running-the-pipeline)
5. [CLI Commands](#cli-commands)
6. [Scheduling](#scheduling)
7. [Adding New Data Sources](#adding-new-data-sources)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The automated data pipeline (Phase 2) transforms GoalieScout from a static scouting database into a continuously updated intelligence platform.  Every night it:

1. Calls the **NHL API** to pull fresh game logs and season stats
2. Downloads **MoneyPuck** advanced analytics CSVs
3. Fetches **Natural Stat Trick** situational splits
4. Validates and normalises every record
5. Deduplicates players across sources
6. Merges enriched records into the database
7. Runs alert checks (breakout games, regression patterns)

---

## Available Data Sources

| Source | Module | What It Provides | Auth Required |
|--------|--------|-----------------|---------------|
| NHL API | `scraping/apis/nhl_api.py` | Goalie rosters, season stats, game logs, bio data | None |
| MoneyPuck | `scraping/apis/moneypuck.py` | GSAx, xGoals, shot quality, rebound data | None |
| Natural Stat Trick | `scraping/apis/natural_stat_trick.py` | 5v5/PP/PK splits, HD/MD/LD save%, GSAA | None |
| EliteProspects | `scraping/scrapers_v2/elite_prospects.py` | Multi-league stats, bio, career history | None (web scraping) |
| HockeyDB | `scraping/scrapers_v2/hockey_db.py` | Career stats, cross-reference | None (web scraping) |

### NHL API (`NHLAPIClient`)

Uses the public NHL stats API.  No API key required.

```python
from goaliescout.scraping.apis.nhl_api import NHLAPIClient

client = NHLAPIClient()
goalies = client.get_all_goalies("20232024")
bio = client.get_goalie_bio(8480045)       # Connor Hellebuyck
game_log = client.get_game_log(8480045, "20232024")
todays_games = client.get_todays_games()
```

### MoneyPuck (`MoneyPuckClient`)

Downloads free CSV data from moneypuck.com.

```python
from goaliescout.scraping.apis.moneypuck import MoneyPuckClient

client = MoneyPuckClient()
df = client.download_season_data("2023")   # 2023-24 season
gsax = client.get_goalie_gsax("Connor Hellebuyck", "2023")
rankings = client.get_all_goalie_rankings("2023")
shot_quality = client.get_shot_quality_data("Juuse Saros", "2023")
```

### Natural Stat Trick (`NaturalStatTrickClient`)

Scrapes situational splits from naturalstattrick.com.

```python
from goaliescout.scraping.apis.natural_stat_trick import NaturalStatTrickClient

client = NaturalStatTrickClient()
df_5v5 = client.get_goalie_splits("20232024", situation="5v5")
danger_df = client.get_danger_zone_stats("20232024")
individual = client.get_individual_goalie("Connor Hellebuyck", "20232024")
```

---

## Configuration

Copy `.env.example` to `.env` and adjust the pipeline section:

```bash
# Pipeline schedule
PIPELINE_NIGHTLY_HOUR=2       # Hour (UTC) for nightly run (default: 2 AM)
PIPELINE_WEEKLY_DAY=sun       # Day of week for weekly full scrape
PIPELINE_WEEKLY_HOUR=6        # Hour for weekly run

# Rate limiting
SCRAPING_DELAY=2.0            # Seconds between requests
SCRAPING_MAX_RETRIES=3        # Retry attempts on failure

# Enable/disable individual sources
ENABLE_NHL_API=true
ENABLE_MONEYPUCK=true
ENABLE_NATURAL_STAT_TRICK=true
ENABLE_ELITE_PROSPECTS=true
ENABLE_HOCKEY_DB=true

# Goalie discovery
DISCOVERY_MIN_GAMES=5
DISCOVERY_LEAGUES=OHL,WHL,QMJHL,NCAA,USHL
```

---

## Running the Pipeline

### Manual run (all sources)

```bash
goaliescout sync
```

### Manual run (single source)

```bash
goaliescout sync --source nhl
goaliescout sync --source moneypuck
goaliescout sync --source nst
```

### Specify a season

```bash
goaliescout sync --season 20232024
```

### Python API

```python
from goaliescout.scraping.pipeline.daily_update import DailyUpdatePipeline

pipeline = DailyUpdatePipeline(db=my_db, season="20232024")
result = pipeline.run()
print(result.to_dict())
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `goaliescout sync` | Run the full daily update pipeline |
| `goaliescout sync --source nhl` | Sync from a specific source only |
| `goaliescout discover --league OHL --min-games 5` | Run goalie discovery |
| `goaliescout pipeline-status` | Show health and last run times |
| `goaliescout validate` | Validate all database records |

---

## Scheduling

The `PipelineScheduler` uses **APScheduler** to run jobs automatically:

```python
from goaliescout.scraping.pipeline.scheduler import PipelineScheduler

scheduler = PipelineScheduler(db=my_db, timezone="UTC")
scheduler.start()

# Runs jobs in the background:
# - 02:00 UTC daily   → daily update
# - Sunday 06:00 UTC  → weekly full re-scrape
# - Sunday 07:00 UTC  → goalie discovery
# - 1st of month 03:00 UTC → integrity check

# ... application runs ...
scheduler.stop()
```

---

## Adding New Data Sources

1. **Create a client class** in `src/goaliescout/scraping/apis/` or `scrapers_v2/`.
2. Extend `GoalieScraper` for web scrapers, or create a standalone class for API clients.
3. Include `retry` logic using `tenacity`.
4. Add a `_fetch_<source>` method in `DailyUpdatePipeline` (`pipeline/daily_update.py`).
5. Wire the new fetch method into `DailyUpdatePipeline.run()` with an env-var toggle.
6. Add an entry to `_SOURCE_PRIORITY` in `validation/deduplication.py`.
7. Add the source toggle to `.env.example`.
8. Write tests in `tests/test_<source>.py`.

**Source priority** determines which source wins when two sources provide conflicting values for the same field.  The current order (lowest to highest priority) is:

```
EliteProspects < HockeyDB < MoneyPuck < NaturalStatTrick < NHL
```

Edit `_SOURCE_PRIORITY` in `deduplication.py` to change this.

---

## Troubleshooting

### "No records fetched; pipeline run produced no data"

- Check that at least one source is enabled (`ENABLE_NHL_API=true`).
- Verify internet connectivity.
- Run `goaliescout pipeline-status` to see last successful run times.

### MoneyPuck download fails

- MoneyPuck CSV URL format may have changed.  Inspect `moneypuck.py` and update `_MP_GOALIE_CSV`.
- The season parameter is a 4-digit year (e.g. `"2023"` for 2023-24).

### Natural Stat Trick returns empty DataFrames

- NST uses HTML tables that may change structure.  Run `NaturalStatTrickClient().get_goalie_splits("20232024")` interactively and inspect the HTML if the parser finds no table.

### Duplicate goalies in database

- Run `goaliescout validate` to identify records.
- Adjust `GoalieDeduplicator(name_threshold=...)` if the fuzzy threshold needs tuning.

### APScheduler not found

- Install it: `pip install apscheduler>=3.10`
- The scheduler degrades gracefully if not installed; you can still run the pipeline manually.
