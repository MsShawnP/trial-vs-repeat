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

## Visualization

[Chart conventions inherited from Spin Rate / Void Finder shared template.
Log per-project chart decisions here as they're made.]

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
