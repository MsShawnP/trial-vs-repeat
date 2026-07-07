# trial-vs-repeat (Leaky Bucket) — Failure Log

What was attempted that didn't work, why it didn't work, and what was
tried next.

Lower bar than DECISIONS.md — capture failures even when they didn't
produce a durable rule. The whole point: future-you (or future-Claude)
shouldn't re-attempt dead ends because the lesson got lost.

---

## Format

### YYYY-MM-DD — [One-line failure description]

**Attempted:** [What was tried]

**Why it didn't work:** [Concrete reason, not "it broke."]

**What we tried instead:** [The next attempt]

**Status:** Resolved / open / abandoned

**Tags:** [keywords for future text-search]

---

## Entries

[New entries get added here, most recent at the top]

### 2026-07-06 — Preview screenshot tool times out on the Plotly-heavy page

**Attempted:** `mcp__Claude_Preview__preview_screenshot` to capture the running app for
visual verification at 1440px / 375px.

**Why it didn't work:** Timed out after 30s repeatedly (no JS errors; the app rendered
fine). A tool-side quirk with the heavy Plotly SVG page, not an app bug — confirmed the
page rendered via the accessibility snapshot.

**What we tried instead:** `preview_snapshot` (accessibility tree), `preview_eval` (chart
paint checks, overflow/container measurement), and `preview_inspect` — which the tooling
docs recommend over screenshots for verifying styles/colours/layout anyway. Fully verified
both viewports this way.

**Status:** Resolved (workaround). **Tags:** preview, screenshot, plotly, dash, verification

### 2026-07-06 — Stale git index.lock blocked a commit

**Attempted:** `git commit` for the review-resolution changes.

**Why it didn't work:** `fatal: Unable to create .git/index.lock: File exists` — a stale
lock from an interrupted prior git process (no git actually running).

**What we tried instead:** Verified no git process was running, removed `.git/index.lock`,
re-ran the commit successfully.

**Status:** Resolved. **Tags:** git, index.lock, commit, windows

<!-- Carried-in lessons from sibling tools (Void Finder / Spin Rate) live
     in CLAUDE.md's chart/tab/table rules, not here. This log is for
     failures encountered while building Leaky Bucket specifically. -->
