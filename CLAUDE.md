# trial-vs-repeat (Leaky Bucket) — Project Context for Claude

Tier: Heavy

## What this project is

A CEO/CFO-facing analyzer that separates real adoption from expensive
sampling. It shows, per item, how many households tried the brand and
how many came back — turning household-penetration growth into an
honest read: a brand vs. a promotion. This is **tool #4 of 5** in the
Cinderhaven penetration series (Door Math, Spin Rate, Void Finder,
Decompose, Leaky Bucket) and the **final** project. It is the integrity
check on Decompose (#3): #3 says how many buyers, #4 says whether they
stuck. Deployed as a Dash app to `leakybucket.lailarallc.com` (name/
subdomain to confirm with Shawn before deploy).

**Business question this project answers:** Of the people who tried us,
how many came back — and is our penetration growth real adoption or just
expensive sampling?

## Stack and tools

- Primary language: Python 3.11
- Key packages/libraries: Dash 3.x, Plotly 6.0, dash-ag-grid, Gunicorn
- Data: in-process `cinderhaven_household_panel` package — **no Postgres,
  no cinderhaven-db, no DATABASE_URL.** Panel built/cached in memory at
  startup. Health check = liveness only. (Same architecture as Decompose.)
- Entry point: `app.py` (mirror Spin Rate)
- Deploy: Gunicorn + Docker + Fly.io (shared-cpu-1x, iad)

## Project files

- CLAUDE.md (this file) — permanent rules and facts
- DECISIONS.md — durable choices and reasoning
- HANDOFF.md — current session state
- PLAN.md — current work arc (filled by /clarify)
- FAILURES.md — things tried that didn't work

Read PLAN.md and HANDOFF.md at session start. DECISIONS.md and
FAILURES.md as relevant.

## Voice and standards

- Exec-facing (CEO/CFO). Lead with a big headline number in plain
  language a CFO can't misread.
- Economist style for written deliverables: sober, declarative,
  data-forward. Charts readable by a non-data-scientist.
- No marketing voice or consultant filler ("leverage," "synergy,"
  "best-in-class," "unlock," "drive value").
- No hedging that softens a real finding.
- **LABEL every number with its timeframe.** (A prior tool shipped a
  figure mislabeled "annual" that was cumulative-to-date — don't repeat.)
- Keep the synthetic-data disclosure visible. Expect a copy pass from Shawn.

## The one statistical trap — handle explicitly

**Right-censoring.** Recent cohorts haven't had time to repeat yet, so a
naive repeat-rate stat understates recent performance. The cohort triangle
handles this visually; any *summary* repeat number needs a maturity cutoff
(only count cohorts that have had the full repeat window). Make the
**repeat window a parameter** (8/12 weeks, category-dependent) and state
the maturity cutoff in-app. This is the credibility make-or-break — tests
must cover the maturity-cutoff / right-censoring logic and the trial/repeat
math.

## Data rules

- Reuse the shared `cinderhaven_household_panel` package — do not
  duplicate the data or stand up a second copy.
- The panel must already carry (from #3): a **burn-in period** before the
  analysis window (to identify first-ever purchases / trial) and **two
  seeded launch stories** — one high-trial / ~15% repeat (doomed launch),
  one modest-trial / 45%+ repeat (quiet winner). If either is missing,
  that's a panel change under #3, not a #4-local hack.
- Locked/versioned seeds. Anything that would move canonical figures goes
  through the change protocol + canonical-figures impact check + Shawn's
  explicit approval.

## Rules

### Honesty and judgment

- Say "I don't know" or "I can't verify this" instead of guessing.
- Tell Shawn what she needs to hear, not what she wants to hear.
- Flag any rule too vague to verify rather than guessing at compliance.

### Building and proposing

- No speculative abstractions. Build what's needed now.
- When proposing a tool/library/approach, give at least two alternatives
  with tradeoffs. Tie every proposal back to the business question above.
- Reuse Spin Rate's tokens, layout components, and header/footer chrome —
  don't rebuild. Reuse the UCI Report 1 cohort machinery
  (`online-retail-analysis` repo) — don't re-derive it.

### How to work the project

- Work in vertical slices, not horizontal phases. One chart/section
  end-to-end (input → output), reviewed in its own slice.
- When a feature works, suggest a quick test to keep it working.
- Do not start work outside the current PLAN.md arc without flagging it.
- Do not refactor unrelated code or rename things unprompted.

### Git branching and worktrees

- Work on main by default. No worktrees/branches unless Shawn asks.
- Suggest a branch before risky/experimental changes.

### Scope creep detection

- Periodically check current work against PLAN.md; flag drift gently.

## Deployed UI gate — no exemptions

This renders in a browser and deploys to a lailarallc.com subdomain.
Before writing any UI code: read `LAILARA_DESIGN_SYSTEM.md`, apply its
tokens (colors, type scale, spacing), apply the baseline layout contract
(~1200px centered container, brand header/footer, section rhythm), and
check the result at 1440px AND 375px before calling it done. "It's just a
demo" is not an exemption.

### Chart rules (hard-won on Void Finder — put ALL in the shared template, then verify every chart)

- Category-axis labels must not clip (automargin / adequate margins).
- Currency tick formatter shows each tick's true value, evenly spaced,
  NO duplicates (we shipped "$100k, $100k, $200k, $200k").
- Legends at the BOTTOM, never overlapping bars.
- Bold value data labels. Then click every chart and confirm.

### Tabs / tables

- Each tab renders its own distinct content; add a regression test so a
  style change can't silently disconnect the tab-content callback.
- Never truncate the key identifier column; clear headers; scores as % or
  High/Med/Low, not raw decimals; tooltips on computed columns.

### Exec content

- Big plain-language headline number; every metric/filter has a tooltip;
  a short "why this matters" panel; a glossary; synthetic-data disclosure.

## Session start protocol

**Do this BEFORE responding to the first message.** Read CLAUDE.md,
PLAN.md, HANDOFF.md, DECISIONS.md; skim FAILURES.md. Also read carried-in
memory (infra notes, Spin Rate / Void Finder / Decompose HANDOFF +
FAILURES, chart-config + design notes) and report what you're carrying in
before coding. State the starting point so Shawn confirms you're caught up.

## Process — don't skip

Run `/ce:compound` and the multi-agent code review before calling anything
done; drive findings to resolution. Write HANDOFF.md + FAILURES.md and save
a memory. Tests green before done.

## Defaults

- Flag gaps rather than fill with plausible-but-unverified content.
- Short responses unless the task is substantive.
- Ask before promoting a log entry to a DECISIONS.md entry.
- Answer, don't offer to answer.
