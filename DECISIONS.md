# trial-vs-repeat (Leaky Bucket) — Decisions Log

Permanent record of choices that should survive session turnover.
If a decision is reversed, strike it through and add the replacement
below — don't delete.

---

## Format

Each entry:
- **Date** — when decided
- **Decision** — one sentence, imperative voice
- **Why** — the reasoning, including what was tried and rejected
- **Scope** — what this applies to (file, chunk, deliverable, or "global")
- **Do not** — explicit anti-instructions, if any

---

## Architecture & Pipeline

### 2026-07-06 — Vendor the shared packages into `packages/` (series pattern)
- **Why:** Fly's Docker build context is this repo only; it can't reach a sibling
  repo path. The established series pattern (Spin Rate, Decompose) vendors shared
  packages into each repo's `packages/` and pip-installs them in the Dockerfile.
  #4 vendors `lailara-palette`, `cinderhaven-store-universe`, and
  `cinderhaven-household-panel` from Decompose. The panel is a seed-locked
  deterministic generator, so the vendored copy produces identical data — no
  divergent dataset, honoring "reuse the shared package, no second copy of the data."
- **Scope:** global (build + deploy)
- **Do not:** edit the vendored panel here. If the canonical panel changes in
  Decompose (#3), re-sync the vendored copy under the canonical change protocol —
  it must not drift. Any change that would move canonical figures needs Shawn's approval.

### 2026-07-06 — Use the in-process `cinderhaven_household_panel` package; no database
- **Why:** Matches the architecture locked for Decompose (#3). Keeps Leaky
  Bucket off the cinderhaven-db fragility surface (cred sync, 503
  health-gate, pg health-check). One source of data, built/cached in memory
  at startup.
- **Scope:** global
- **Do not:** stand up Postgres, add DATABASE_URL, or copy the panel data.
  Health check is liveness only.

### 2026-07-06 — Keep folder name `trial-vs-repeat`; product name is "Leaky Bucket"
- **Why:** Shawn chose to keep the existing folder name. Product/branding
  and intended subdomain remain "Leaky Bucket" / `leakybucket.lailarallc.com`.
- **Scope:** global
- **Do not:** rename the folder or assume the subdomain is final — confirm
  subdomain with Shawn before deploy.

---

## Data & Schema

### 2026-07-06 — Panel must carry burn-in + two seeded launch stories (owned by #3)
- **Why:** #4 needs a burn-in period to identify first-ever purchases
  (trial), and the two contrasting launches (high-trial/~15% repeat doomed
  launch; modest-trial/45%+ repeat quiet winner) are the demo.
- **Scope:** shared panel package
- **Do not:** patch these in as a #4-local hack. If missing, it's a #3
  change under the canonical change protocol + Shawn's approval.

---

## Data & Schema (continued)

### 2026-07-06 — Repeat window default is 52 weeks, not the brainstorm's 8/12
- **Why:** Measured the shared panel's actual repeat timing (probe in HANDOFF.md).
  The panel models launch repeat spread across quarters (~0.5/quarter), so repeat
  within 8/12 weeks is near-zero (leaky 1.6%/3.5%, sticky 4.7%/10.3%) and the
  advertised "~15% doomed vs 45%+ winner" story only emerges at ~52 weeks (leaky
  14.3%, sticky 51.4% — matching #3's canonical 16%/55% "ever repeats"). These
  categories (pantry staples, snack bites) repeat on a quarterly cycle, so a 12-month
  window is the honest read. Window stays a parameter (options 8/12/26/52).
- **Scope:** `app/panel_data.py` DEFAULT_REPEAT_WINDOW_WEEKS, filter bar default.
- **Do not:** change the panel to hit the 8/12-week numbers — the panel is #3-owned
  and seed-locked. If Shawn wants the brief's 8/12 default, it's a one-constant change
  here; the sticky>leaky contrast holds at every window regardless.

## Visualization

[Chart conventions inherited from Spin Rate / Void Finder shared template.
Log per-project chart decisions here as they're made.]

### 2026-07-27 — Cohort triangle retention is quarter-grain, distinct from the headline repeat rate
- **Why:** The Cohort Retention triangle measures "share of the cohort that bought again in
  a later *quarter*" — quarter-grain, no maturity cutoff, and *independent of the
  repeat-window slider*. The headline / verdict / depth measure "repeat within W weeks,
  mature triers only." The two answer different questions and will NOT match (e.g. sticky
  item's 51% headline vs its per-quarter triangle cells). A data/math review flagged that
  nothing on-screen reconciled them, so an in-app italic caption now states the difference.
- **Scope:** `app/views/cohort.py` (triangle), `app/trial_repeat.cohort_retention`.
- **Do not:** "fix" the triangle to respond to the repeat-window slider or to match the
  headline repeat rate — that is not a bug. The divergence is intentional and captioned.

### 2026-07-27 — Follow LAILARA_DESIGN_SYSTEM.md; local deviations fixed, type scale is series-level
- **Why:** A design-system audit (measured live computed styles) confirmed high conformance.
  Fixed three Leaky-Bucket-local deviations: secondary text → London-35 (`#595959`, was
  London-40 `#666`); purpose hero → 28px (DS benchmark-value step); retention heatmap light
  anchor → HK-85 `#b5e4d8` (DS reserves step 95 for surface fills, never data — added an
  `HK_85` token to constants.py since lailara-palette doesn't export it). The remaining
  type-scale drift lives in the shared template + vendored lailara-frame, so it was
  reconciled series-wide (commit `1c79467`, lailara-frame v1.2.0), not patched here alone.
- **Scope:** `assets/style.css`, `app/constants.py`, and (series) `assets/lailara-frame.css`.
- **Do not:** hard-code serif sizes inline (use the `.ll-*` type-scale classes from
  lailara-frame v1.2.0); use step-95 family fills as chart data; reintroduce London-40 for
  text. The canonical DS file is at `reference/lailara-design-system/` (global CLAUDE.md's
  path is stale).

---

## Output Formats

[Decisions about deliverable formats, structure, organization]

---

## Writing & Voice

[Voice/terminology decisions specific to this project — logged as made.]

---

## Reversed / Superseded

When a decision is overturned:
1. Strike through the original entry above (don't delete)
2. Add a new entry below with the replacement decision
3. Note the link in both directions
