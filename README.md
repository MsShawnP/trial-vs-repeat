# Leaky Bucket — Trial vs Repeat Analyzer

Of the people who tried us, how many came back — and is our penetration
growth real adoption or just expensive sampling?

Leaky Bucket is a CEO/CFO-facing analyzer that separates a brand from a
promotion. Household penetration can rise every quarter while a business
dies: if new buyers pour in and almost none repeat, growth is a treadmill
that collapses the moment acquisition spend stops. This tool measures
trial (first-ever buyers) against repeat (who came back within the repeat
window) and flags trial-heavy, repeat-light items — the launches that
looked great in month one and got discontinued after a "successful" year.

Tool #4 of 5 in the Cinderhaven household-penetration series (Door Math ·
Spin Rate · Void Finder · Decompose · **Leaky Bucket**). The integrity
check on Decompose: #3 says how many buyers, #4 says whether they stuck.

**Live:** _not yet deployed_ (intended: https://leakybucket.lailarallc.com)

## Run it

_Stack and run instructions land once the first `/clarify` arc is scoped._
Planned stack: Python 3.11, Dash 3.x, Plotly 6.0, dash-ag-grid; served
with Gunicorn, containerized, deployed to Fly.io. Data is an in-process
`cinderhaven_household_panel` package — no database.

## Stack

- Python 3.11 · Dash 3.x · Plotly 6.0 · dash-ag-grid
- In-process synthetic household panel (seed-locked, no DB)
- Gunicorn + Docker + Fly.io

## Data note

All figures come from a synthetic, seed-locked Cinderhaven household panel.
No real customer data. This is a portfolio demonstration.

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and analytics
consulting for specialty food brands scaling into national retail.
