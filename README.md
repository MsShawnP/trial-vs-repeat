# Leaky Bucket — Trial vs Repeat Analyzer

Of the people who tried us, how many came back — and is our penetration growth real adoption or just expensive sampling?

**Live:** https://leakybucket.lailarallc.com

## What it does

Leaky Bucket is a CEO/CFO-facing analyzer that separates a brand from a promotion. It measures trial (first-ever buyers) against repeat (who came back within the repeat window) and flags trial-heavy, repeat-light items — the launches that looked great in month one and got discontinued after a "successful" year.

Three views over a seed-locked synthetic household panel:

- **Verdict** — the executive answer: is growth sticking or leaking?
- **Flow** — where buyers go after trial: repeat, lapse, or churn
- **Cohort** — repeat behavior by trial cohort over time

Tool #4 of 5 in the Cinderhaven household-penetration series (Door Math · Spin Rate · Void Finder · Decompose · **Leaky Bucket**). The integrity check on Decompose: #3 says how many buyers, #4 says whether they stuck.

## Why it matters

Household penetration can rise every quarter while a business dies: if new buyers pour in and almost none repeat, growth is a treadmill that collapses the moment acquisition spend stops. Distinguishing adoption from sampling changes real decisions — which launches get renewed trade support, which get discontinued, and whether the growth story presented to retailers and investors survives scrutiny.

## Quick start

Prerequisites: Python 3.11+. No database — the app warms a seed-locked, in-process synthetic panel at startup.

```bash
# 1. Install vendored packages (order matters: store universe before panel)
pip install packages/lailara-palette/
pip install packages/cinderhaven-store-universe/
pip install packages/cinderhaven-household-panel/

# 2. Install the app
pip install .

# 3. Run
python wsgi.py
# → http://localhost:8050
```

Or with Docker:

```bash
docker build -t leaky-bucket .
docker run -p 8050:8050 leaky-bucket
```

Tests: `pip install .[dev] && pytest`. Deploys to Fly.io (`fly.toml`); production serving is Gunicorn (`wsgi:server`).

## Tech stack

- **Python 3.11** — Dash 3.x, Plotly 6.0, dash-ag-grid, pandas/numpy
- **Data** — in-process `cinderhaven-household-panel` package (seed-locked, no DB), vendored under `packages/` alongside `cinderhaven-store-universe` and the `lailara-palette` design tokens
- **Serving** — Gunicorn, Docker, Fly.io

## Project structure

```
app/        Dash app: trial/repeat math (trial_repeat.py), charts, filters,
            views/ (verdict, flow, cohort), executive shell (lailara_frame.py)
assets/     CSS, fonts, clientside JS
packages/   Vendored data + design packages (each with its own tests)
tests/      pytest suite for math, filters, views, layout
wsgi.py     Entry point (dev server + gunicorn target, /health route)
```

## Data note

All figures come from a synthetic, seed-locked Cinderhaven household panel. No real customer data. This is a portfolio demonstration.

## License

MIT

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and analytics consulting for specialty food brands scaling into national retail.
