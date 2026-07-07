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

## 2026-07-06 — Un-parked: #3 Decompose shipped

**Started from:** Post-/clarify parked state (blocked on #3).

**Did:** Confirmed #3 Decompose is fully shipped (built, code-review passed
2026-07-06, custom domain set up). Verified the shared
`cinderhaven_household_panel` now carries everything #4 needs: burn-in (4q
2023 + 8q analysis 2024-25), both launch seeds computed via `LAUNCH_ITEMS`
(`CHP-SB-010` leaky / `CHP-PS-010` sticky, gated by `test_seeded_stories.py`),
deterministic seed-lock. Un-parked PLAN.md, updated memory.

**State:** #4 un-blocked and ready to build at Slice 0. No app code written yet.

**Next:** Decide whether to start the build (Slice 0: install/verify panel,
read carried-in memory, vendor Spin Rate chrome, pull UCI cohort machinery)
or run `/office-hours` first to stress-test the concept.

---

## 2026-07-06 — Slices 0 & 1 built (foundation + metric core)

**Did:**
- **Slice 0 (foundation):** vendored the three shared packages (lailara-palette,
  cinderhaven-store-universe, cinderhaven-household-panel) from Decompose into
  `packages/`; created app factory + branded loading overlay, constants (palette
  tokens + trial/repeat vocabulary), `panel_data.py` data seam (warm cache, no DB),
  Dockerfile/fly.toml/wsgi mirroring Decompose. Smoke-tested: panel warms (5000 hh,
  4 burn-in + 8 analysis q, 53.8k tx), both stories reproduce.
- **Slice 1 (metric core):** `app/trial_repeat.py` — first-ever-purchase trial curve,
  repeat rate within N weeks WITH maturity cutoff (right-censoring), cohort retention
  triangle, depth of repeat, per-item promotion/brand verdict. Wired through
  `panel_data`. 19 new tests + 49 vendored-panel tests = **68 green**.

**Repeat-window probe (grounds the 52w default decision):** measured repeat vs window
on the two launch items —
| window | leaky | sticky |
|--------|-------|--------|
| 8w  | 1.6%  | 4.7%  |
| 12w | 3.5%  | 10.3% |
| 26w | 9.4%  | 35.3% |
| 52w | 14.3% | 51.4% |
| ever| 16.2% | 55.1% |
The brief's 8/12w default would show near-zero repeat; the "15%/45%" story needs ~52w.
Defaulted to 52w, window still a parameter. See DECISIONS.md. **Flag for Shawn:** if
she wants the brief's 8/12 default, it's a one-constant change.

**State:** app boots as far as imports (layout.py not built yet — that's Slice 3).
Tests green. Not deployed.

**Next:** Slice 2 — charts.py + the four views (cohort triangle, trial/repeat curves,
leaky-bucket flow, promotion-or-brand verdict + two-launch side-by-side).

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
