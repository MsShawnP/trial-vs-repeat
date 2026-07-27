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

### 2026-07-27 — "deploy" collided with an in-flight background task's uncommitted edits

**Attempted:** Deploy on Shawn's request, right after spawning a background task
(type-scale reconciliation) that edits this same working tree in a separate session.

**Why it didn't work:** `git status` showed three files modified (app.py, lailara-frame.css,
style.css) that I hadn't touched — the background task's uncommitted output. Deploying then
would have shipped a half-applied change (Fly builds from the working dir), or raced the
other session's commit.

**What we tried instead:** Paused, inspected the diffs (coherent type-scale work), waited
for the task to finish and commit (`1c79467`), verified clean HEAD + tests, then deployed.

**Status:** Resolved. **Lesson:** when a spawned task edits the current repo, check
`git status` before any commit/deploy — the tree may not be only yours.
**Tags:** deploy, background-task, git-status, race, multi-session

### 2026-07-27 — ui-review-skill can't exclude .venv (recursive globs don't work)

**Attempted:** Exclude the in-tree `.venv` from the ui-review content scan via
`exclude: [".venv/**", "packages/**"]` in review.yaml.

**Why it didn't work:** The tool's glob matcher (src/checks/content.js) expands `*` to
"non-separator chars" with no real `**` support, and its walker doesn't skip dot-dirs — so
recursive excludes silently never match (worse on Windows: backslash paths vs forward-slash
globs). Only basename globs like `*.md` work. Result: ~963 false warnings from `.venv`.

**What we tried instead:** Documented the limitation in review.yaml, relied on the DOM
checks (8/8 pass) as the real signal, and spawned a task to fix the tool (skip dot-dirs).

**Status:** Resolved (workaround) + tool fix flagged. **Tags:** ui-review, glob, venv,
exclude, windows

### 2026-07-27 — Dash dev server doesn't hot-reload Python

**Attempted:** Edit layout.py / a view callback, then reload the browser to see the change.

**Why it didn't work:** `wsgi.py` runs without the reloader, so Python edits (layout,
callbacks) don't take effect on a browser reload — the server keeps serving the old modules.
Early edits looked un-applied. (CSS/assets DO hot-load; only .py needs a restart.)

**What we tried instead:** `preview_stop` + `preview_start` to restart the server after any
Python change, then re-verify.

**Status:** Resolved. **Tags:** dash, dev-server, hot-reload, python, preview

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
