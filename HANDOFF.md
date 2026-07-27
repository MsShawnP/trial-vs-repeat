# trial-vs-repeat (Leaky Bucket) — Handoff Log

Session-by-session state. Updated by /log mid-session and /wrap at
session end.

For durable choices, see DECISIONS.md.
For the current work arc, see PLAN.md.
For things that didn't work, see FAILURES.md.

---

## 2026-07-27 — /improve pass: exec 30-second comprehension + independent review

**Started from:** LIVE, stable. Shawn ran `/improve`. Two concerns: (1) can a CEO/CFO
grasp the tool's purpose and read in 30 seconds; (2) is the Claude-authored code actually
good / best-practice.

**Log brought current:** 8 polish commits landed after the 2026-07-06 wrap and were never
logged here — README, MIT license, repo cleanup, ag-grid stripe, retention-scale/border
fixes, .gitattributes (CRLF), genuine 700/600 fonts (bold had been a byte-copy of 400),
a11y `html lang`. Working tree was clean at session start.

**Did (all verified in browser at 1440px + 375px, no console errors):**
- **Purpose block (30s fix):** new hero line as the *first* content on the page, above the
  tabs — "Of the households that tried this brand, how many came back?" + a stakes subline.
  Previously the first things a cold exec read were a date and a synthetic-data disclaimer;
  the actual purpose was buried in the footer + collapsed "Why this matters". `layout.py`
  `_build_page_intro()` + `.page-intro*` CSS (responsive: 30px desktop / 24px mobile).
- **Named the winner:** verdict headline was "One of these launches is a brand. The other
  is a promotion." → now "The Snack Bites launch is a promotion. The Pantry Staples launch
  is a real brand." Added a `line_name` column to `trial_repeat.item_verdict` (human
  product-line name, not the SKU) and rewrote `verdict._headline_children` to name items.
  +1 regression test (`test_headline_names_the_promotion_and_the_brand`).
- **Independent review (2 background agents):**
  - *Security:* **clean** — no secrets, no injection, no XSS, safe prod config. Only two
    LOW container nits (gunicorn runs as root; base image floating tag).
  - *Data/math:* **"Trustworthy for exec-facing numbers"** — maturity-cutoff/right-censoring
    correct, centralized, consistently applied; both `tx.merge(mature…)` joins are
    cardinality-safe (many-to-one); denominators correct. No calc/join/off-by-one errors.
- **Review fixes folded in (copy only, no math):**
  - *Finding 1:* the Cohort Retention triangle uses a different "repeat" definition than the
    headline (quarter-grain, window-independent). Added an italic reconciliation note under
    the triangle so a CFO doesn't think the 51% headline and the triangle should match.
  - *Finding 2:* added a caption on the depth chart clarifying depth = distinct purchase
    occasions (shopping trips), so "2×" isn't misread.

**State:** 48 app tests green (was 47), ruff clean, working tree has the above changes
(uncommitted at time of writing → committed this session). Dev-server verified. NOT yet
redeployed to Fly.

**Deferred (not done — Shawn's call):** security container nits (non-root user, pin base
image by digest); data-review findings 3 (cosmetic: trial_reach shown next to n_mature —
harmless with current data) and 4 (nit: heatmap formats NaN before masking). None block.
**Redeploy** to pick up these UI changes when ready.

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

## 2026-07-06 — Session wrap: Leaky Bucket built, reviewed, LIVE

**Started from:** Empty folder + brainstorm. Scaffold → /clarify → build.

**Did:** Scaffolded the project; /clarify parked it (blocked on #3), then un-parked when
#3 shipped; built Slices 0–4 (foundation, trial/repeat math, charts+3 views, exec shell,
deploy); deployed live to leakybucket.lailarallc.com; ran a 5-agent review and resolved
every finding (+25 tests); wrote work-card + blog drafts.

**State:** LIVE at https://leakybucket.lailarallc.com serving the reviewed build. 47 app +
49 panel = 96 tests green, ruff clean. Private repo, all on main. No code outstanding.
**All five Cinderhaven penetration tools are now live.**

**Next:** Copy pass on docs/launch/ (blog + work-card); `/publish` to flip repo public;
place work-card on lailarallc.com/work; optional `/ce:compound`.

---

## 2026-07-06 — Slice 4b: 5-agent code review, all findings resolved

**Ran the multi-agent review** (correctness, kieran-python, maintainability, testing,
project-standards). Drove every real finding to resolution:

**Real bugs fixed:**
- **Empty-slice false "Promotion" verdict** (correctness): a Product line / Retailer
  filter that excluded a launch item made it read as a decisive "Promotion" with 0
  triers, and the headline said "Neither launch kept its triers." Added a distinct
  **"No data"** verdict state (item_verdict) + handled it in headline, cards, scatter,
  and a data-derived cutoff note.
- **cohort._build_triangle KeyError on empty frame** (testing): `drop_duplicates`
  before the len-guards crashed on an empty cohort slice. Added `_empty_figure` guard.

**Quality/standards fixed:** metric-card tooltips (exec rule); bold flow + trial-curve
value labels; flow y-axis "Households (per quarter)" + explicit non-duplicate dtick;
`#e6e4dd` → `GRIDLINE` token (3 spots); deleted dead code (get_metrics, launch_items,
count_yaxis→nice_dtick, fmt_signed_number, VERDICT_MIXED, REPEAT_COLOR, ALL_QUARTERS);
extracted `_mature_triers` (one maturity definition); derived the verdict cutoff note
from data; typed all filter params `str | None`; stable sort in `_first_purchase`.

**Tests added (+25):** No-data verdict regression, empty-slice safety for every math
fn + every figure builder (incl. the cohort crash), buyer_flow accounting identities +
panel mirror, parse_filter_state + scope_sku, product_line/retailer filter path,
figure builders exercised, exec-content contract (headline/why/glossary/synthetic),
filter tooltips; tightened launch-story assertions (bounded both sides + pinned trier
counts 1234/428). **47 app + 49 panel = 96 green, ruff clean.**

**Verified in browser:** all 5 charts paint, cards carry tooltips, no JS errors.

**Next:** redeploy the fixed code; `/publish` when Shawn's ready; her copy pass on drafts.

---

## 2026-07-06 — Slice 4a: DEPLOYED and LIVE

**Deployed and LIVE at https://leakybucket.lailarallc.com** (HTTPS, Let's Encrypt cert
Issued/verified). Also `trial-vs-repeat.fly.dev` (1 machine, iad, shared-cpu-1x,
1024mb, image 106 MB). `/health` → `200 {"status":"ok"}`; production `_dash-layout`
has all chart targets + synthetic disclosure. Deploy-first was Shawn's call.

**Custom domain via Cloudflare API** (token at `~/.config/lailara/cloudflare-dns-token`,
zone 53d54c95…, see [[cloudflare-dns-token]]). Created two DNS-only CNAMEs:
`leakybucket → 12kxz62.trial-vs-repeat.fly.dev` and
`_acme-challenge.leakybucket → leakybucket.lailarallc.com.12kxz62.flydns.net`. Cert
validated in ~15s.

**Remaining Slice 4:** multi-agent code review (Shawn: review AFTER deploy) + drive
findings to resolution; work-page card + blog draft (docs/launch/); `/publish` when ready.

---

## 2026-07-06 — Slices 2 & 3 built (charts, views, exec shell) — app runs

**Did:**
- **charts.py** — reused Decompose's Economist template; added `pct_yaxis` /
  `count_yaxis` helpers (round, non-duplicate ticks).
- **components.py** — view heading, stat cards (metric-card DOM), why-this-matters,
  and a trial/repeat glossary.
- **filters.py** — Leaky Bucket's filter bar: Scope (whole brand / launch item),
  Repeat window (8/12/26/52w), Product line, Retailer; shared filter-state contract.
- **Three views:** `verdict.py` (default tab — headline + two-launch stat cards +
  trial-reach-vs-repeat scatter with brand line), `cohort.py` (retention triangle
  heatmap + depth-of-repeat bars), `flow.py` (leaky-bucket in/out/net + cumulative
  trial curve).
- **layout.py** — frame, 3 tabs, filter bar, pre-rendered panels, tab-visibility
  callback. Loading overlay watches `#verdict-chart`.
- Vendored self-hosted fonts; dev server `threaded=True`.

**Verified in-browser** (dev server): default tab renders with correct numbers
(leaky CHP-SB-010 → 14.3% Promotion / 24.7% reach; sticky CHP-PS-010 → 51.4% Brand /
8.6% reach at 52w). All 5 charts paint (verdict scatter, cohort heatmap, depth, flow,
trial curve). No JS errors. Deployed-UI gate: 1200px centered container, no horizontal
overflow at 1440px or 375px, filter bar wraps on mobile, charts fit on fresh mobile load.

**Tests:** +3 layout/tab-regression tests → **22 app tests + 49 vendored panel = 71 green.**

**Note:** the preview *screenshot* tool times out on this Plotly-heavy page (tool quirk,
not the app — verified via accessibility snapshot + preview_inspect/eval instead).

**State:** App builds, runs, and renders correctly end to end. Not yet: `/ce:compound`
+ code review, deploy, work card, blog (Slice 4).

**Next:** Slice 4 — review, deploy to leakybucket.lailarallc.com (confirm subdomain),
work-page card, blog draft.

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
