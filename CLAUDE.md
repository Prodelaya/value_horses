# ChileSharp - Value Betting Automation System

## Project Overview

Value betting automation system for Chilean horse racing. Exploits information asymmetry between the local parimutuel pool (Teletrak.cl) and Spanish betting houses (Versus.es) by identifying and executing value bets where soft odds exceed fair odds derived from the sharp pool.

- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 ORM
- **Status**: Phase 0 - Validation / Early Development

## Directory Structure

```
horses/
├── config/settings.py        # Thresholds, polling intervals, edge parameters
├── db/models.py              # SQLAlchemy ORM models (races, runners, snapshots)
├── db/migrations/            # Alembic migrations
├── engine/
│   ├── matching.py           # Horse name normalization & mapping
│   ├── pricing.py            # Fair odds & edge calculation
│   └── signals.py            # Value bet signal generation
├── scrapers/
│   ├── teletrak_program.py   # Daily race program (1x/day)
│   ├── teletrak_odds.py      # Pool odds polling (15s interval)
│   └── versus_odds.py        # Fixed odds scraper (20s interval)
├── scripts/
│   ├── run_scrapers_loop.py  # Scraper orchestrator
│   ├── run_engine_loop.py    # Pricing/signals engine
│   └── run_settlement.py     # Daily settlement
├── settlement/
│   ├── results_scraper.py    # Official race results
│   └── settle_paper.py       # Paper trading P&L
└── utils/
    ├── normalization.py      # Horse name normalization
    └── timezone.py           # CLT/UTC/CET conversions
```

## Run Commands

```bash
# Scrape daily program
python -m scripts.run_scrapers_loop teletrak_program

# Run odds scrapers (during active window)
python -m scripts.run_scrapers_loop teletrak_odds
python -m scripts.run_scrapers_loop versus_odds

# Run pricing engine
python -m scripts.run_engine_loop

# Run daily settlement
python -m scripts.run_settlement
```

## Key Configuration (config/settings.py)

- `MIN_EDGE`: 10% (paper), 15% (production)
- `DELTA_SOFT_FAIR`: 10% minimum odds distance
- `WINDOW_START_MINUTES`: 10 (T-10 before race)
- `WINDOW_END_MINUTES`: 1 (T-1 before race)
- Polling: Teletrak 15s, Versus 20s, Engine 15s

## Core Formulas

- Fair probability: `p_fair = pool_amount / total_pool` (normalized without vig)
- Fair odds: `O_fair = 1 / p_fair`
- Edge: `edge = p_fair * O_soft - 1`

## Code Style

- snake_case for files and functions
- Type hints in all function signatures
- Docstrings in Spanish, technical terms in English
- All timestamps stored in UTC
- Decimal precision for odds calculations
- Imports: stdlib → third-party → local

## Tech Stack

- HTTP: requests, httpx
- Parsing: BeautifulSoup4
- Browser: Playwright (JS-heavy pages)
- Scheduling: cron / systemd timers
- Future API: FastAPI
- Containers: Docker, docker-compose
