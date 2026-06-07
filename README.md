# GoalieScout

GoalieScout is an AI-assisted hockey goalie scouting and analytics platform.
It combines normalized data ingestion, advanced performance metrics, multiple
LLM providers, report generation, and a command-line workflow in one Python
package.

The project is an active alpha and portfolio system. It demonstrates the
architecture and integration patterns for a larger scouting product; it is not
yet a production service.

## What Is Implemented

- Multi-source ingestion clients for NHL data, MoneyPuck, and Natural Stat Trick
- Prospect discovery through hockey data scrapers
- Validation, normalization, and goalie deduplication
- JSON persistence plus a SQLAlchemy SQLite/PostgreSQL-ready backend
- Advanced analytics for GSAx, shot quality, danger-zone save percentage,
  rebound control, rush defense, consistency, movement, and age curves
- A configurable composite GoalieScout score with data-completeness reporting
- OpenAI, Anthropic, and Ollama service adapters
- Markdown and HTML scouting reports, blog content, and social output
- CLI commands for scouting, analytics, synchronization, discovery, and data
  validation
- Unit tests and GitHub Actions continuous integration

## Architecture

```text
External data sources
        |
        v
API clients and scrapers
        |
        v
Normalization -> validation -> deduplication
        |
        v
JSON database or SQLAlchemy database
        |
        +--> advanced analytics
        |
        +--> AI-assisted scouting analysis
        |
        +--> reports, rankings, and CLI output
```

Key packages:

- `goaliescout.scraping`: source clients, scrapers, pipeline, and validation
- `goaliescout.data`: backward-compatible JSON models and persistence
- `goaliescout.database`: SQLAlchemy models, migrations, and repositories
- `goaliescout.analytics`: statistical and composite scoring modules
- `goaliescout.ai`: provider adapters for cloud and local language models
- `goaliescout.content`: report, blog, and social-content generators
- `goaliescout.cli`: end-to-end command-line workflows

See [PIPELINE.md](PIPELINE.md) for the ingestion workflow and
[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for module-level detail.

## Installation

Requires Python 3.10 or newer.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS or Linux
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e .
```

Copy `.env.example` to `.env` and add only the credentials for services you
intend to use. Unit tests do not require live API credentials.

## Quick Start

```bash
goaliescout init
goaliescout list-goalies
goaliescout stats
goaliescout sync --source nhl
goaliescout discover --league ohl --min-games 5
goaliescout validate-data
```

Analytics commands:

```bash
goaliescout advanced-stats PLAYER_ID
goaliescout black-ops-score PLAYER_ID
goaliescout compare PLAYER_ID_1 PLAYER_ID_2
```

AI and content commands:

```bash
goaliescout analyze PLAYER_ID --ai-model openai
goaliescout generate-report PLAYER_ID --format markdown
goaliescout create-blog PLAYER_ID
goaliescout tweet PLAYER_ID
```

Run `goaliescout --help` for the complete command list.

## Testing

```bash
pytest -q
```

The pipeline tests mock remote services. They verify transformation,
validation, persistence, and orchestration behavior without depending on live
third-party endpoints.

## Scoring Methodology

The composite score combines normalized component metrics:

| Component | Weight |
| --- | ---: |
| GSAx per game | 25% |
| High-danger save percentage | 20% |
| Rebound control | 15% |
| Consistency | 15% |
| Movement | 10% |
| Puck handling | 10% |
| Development trajectory | 5% |

Missing components are assigned a neutral value and reported through the
`data_completeness` field. The current weights and normalization ranges are
product hypotheses, not a peer-reviewed player-evaluation standard.

## Current Limitations

- The platform is a CLI and library, not a deployed multi-user web service.
- Several scrapers depend on third-party page structures and require ongoing
  maintenance.
- Remote-source tests use mocked responses; live integration checks are still
  needed.
- The composite score requires broader historical calibration and validation.
- Authentication, authorization, production observability, rate-limit
  management, and deployment infrastructure are not yet implemented.
- AI-generated scouting text must be reviewed by a human before publication or
  decision-making.

## Roadmap

1. Add live-source contract tests and fixture-based integration tests.
2. Consolidate persistence around the SQLAlchemy backend.
3. Add a web API and authenticated product interface.
4. Add job telemetry, retry reporting, and operational dashboards.
5. Calibrate scoring against larger historical datasets and documented
   evaluation criteria.

## Responsible Use

GoalieScout supports analysis and scouting workflows. It does not replace
official statistics, video review, medical evaluation, or professional
judgment.
