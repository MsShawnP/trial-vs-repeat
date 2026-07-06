# trial-vs-repeat (Leaky Bucket) — Handoff Log

Session-by-session state. Updated by /log mid-session and /wrap at
session end.

For durable choices, see DECISIONS.md.
For the current work arc, see PLAN.md.
For things that didn't work, see FAILURES.md.

---

## 2026-07-06 — Project initialized

**Started from:** New project setup (`/new-project`). Tool #4 of 5 in the
Cinderhaven penetration series — the final project.

**Did:** Created repo scaffold — CLAUDE.md, PLAN.md, HANDOFF.md,
DECISIONS.md, FAILURES.md, README.md, .gitignore, src/ and tests/ with
their CLAUDE.md conventions. Tier: Heavy. Stack: Python 3.11 / Dash 3.x /
Plotly 6.0. Private GitHub repo. Resolved naming: keeping folder name
`trial-vs-repeat`; product/branding name is "Leaky Bucket" with intended
subdomain `leakybucket.lailarallc.com` (confirm before deploy).

**State:** Foundation in place. PLAN.md is a stub awaiting `/clarify`.

**Next:** Run `/clarify` to scope the first arc. Then `/office-hours`
(Heavy tier) to stress-test the concept before building.

---

## Build brainstorm (seed for /clarify)

**Business question:** "Of the people who tried us, how many came back —
and is our penetration growth real adoption or just expensive sampling?"
Penetration can rise every quarter while the business dies: if new buyers
pour in and almost none repeat, growth is a treadmill that collapses when
acquisition spend stops. Repeat rate is the difference between a brand and
a promotion.

**Architecture (locked):** import the same deterministic, seed-locked
`cinderhaven_household_panel` package #3 built; build/cache in memory at
startup. NO database, no cinderhaven-db, no DATABASE_URL. Health check =
liveness only. Keeps Leaky Bucket off the cinderhaven-db fragility surface.

**Panel dependency (should already be in from #3):** a burn-in period
before the analysis window (to identify first-ever purchases / trial), and
two seeded launch stories — one big-trial / ~15% repeat (doomed launch),
one modest-trial / 45%+ repeat (quiet winner). If missing, that's a #3
change, not a #4 hack.

**Core metrics:** trial rate (cumulative first-ever-buyer curve); repeat
rate (% of triers who buy again within N weeks); repeat purchase
frequency; buyer cohort retention curves (cohorted by first-purchase
period); depth of repeat (1x / 2x / 3x+); bucket flow (new in, lapsed out,
net per period).

**Outputs:** cohort retention heatmap/triangle (reuse UCI Report 1 cohort
machinery from `online-retail-analysis`); trial & repeat curves per item
(launch vs established handled differently); leaky-bucket flow chart
(buyers in vs out per period, net line); "Promotion or brand?" verdict per
item (trial-heavy/repeat-light flagged).

**The statistical trap — right-censoring:** recent cohorts haven't had
time to repeat. Cohort triangle handles it visually; any summary repeat
number needs a maturity cutoff (only fully-matured cohorts). Repeat window
is a parameter (8/12 weeks). State the cutoff in-app. Credibility
make-or-break.

**Cinderhaven angle:** the two contrasting launches side by side — doomed
high-trial/low-repeat next to the quiet modest-trial/high-repeat winner —
is the whole story.

**Stack:** Spin Rate's look, Door Math's data pattern. Dash 3.x / Plotly
6.0 / Python 3.11; dash-ag-grid + clientside JS callbacks; Gunicorn +
Docker + Fly.io (shared-cpu-1x, iad).

**Lessons to apply from day one:** read own memory first (infra, Spin
Rate / Void Finder / Decompose HANDOFF+FAILURES, chart-config + design
notes) and report what's carried in. Charts: no clipping, correct/
non-duplicate currency ticks, bottom legends, bold data labels, verify
each. Tabs: distinct content + regression test on tab-content callback.
Tables: never truncate key ID column, tooltips on computed columns. Design:
apply LAILARA_DESIGN_SYSTEM.md, reuse Spin Rate tokens/chrome. Exec:
headline number, timeframe labels, tooltips, why-this-matters panel,
glossary, synthetic-data disclosure.

**Process:** /ce:compound + multi-agent code review before done; drive
findings to resolution; HANDOFF + FAILURES + memory; tests green
(including maturity-cutoff / right-censoring + trial/repeat math).

**Deliverables:** Leaky Bucket app on Spin Rate stack, in-process panel,
deployed to `leakybucket.lailarallc.com`; Work-page card in Door Math /
Spin Rate / Void Finder format; blog post draft pairing with the Decompose
reveal ("penetration up ≠ growth"). Confirm name/subdomain with Shawn.

**Build-order note:** build only AFTER Decompose's shared panel is built,
seed-locked, tests green (with burn-in + two launch seeds). #4 is then pure
reuse — largely the UCI cohort approach pointed at the existing panel — the
cheapest build in the series and the last one.

---
