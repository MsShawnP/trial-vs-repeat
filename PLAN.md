# trial-vs-repeat (Leaky Bucket) — Current Work Plan

The current arc of work. Updated when the arc changes, not every
session. For session-by-session state, see HANDOFF.md.

---

## ✅ SHIPPED — Leaky Bucket is LIVE (2026-07-06)

The build arc below is **complete**. Leaky Bucket is deployed, reviewed, and
live at **https://leakybucket.lailarallc.com** (Fly, HTTPS). 47 app + 49 panel
tests green, ruff clean, 5-agent review resolved. **All five Cinderhaven
penetration tools are now live** — the series is done.

**Only non-code follow-ups remain (Shawn's):** copy pass on `docs/launch/`
(blog + work-card); `/publish` to flip the repo public; place the work-card on
lailarallc.com/work; optional `/ce:compound`. No open engineering work.

See "Arc history" below for the completed build arc.

---

## Goal (this session)

Produce a scoped, parked build plan for Leaky Bucket — and build nothing
until #3 locks the shared panel.

**Status:** ✅ Done. Scaffold complete, arc planned below, blocker recorded.

## Goal (the parked build arc)

Ship the Leaky Bucket app — a CEO/CFO analyzer that separates real
adoption from expensive sampling — on the Spin Rate stack, reading the
locked in-process panel, deployed to `leakybucket.lailarallc.com` (confirm
subdomain first).

## Why this arc, why now

It's the final tool in the 5-part penetration series and the integrity
check on Decompose: #3 says how many buyers, #4 says whether they stuck.
Parked now because the foundation (the shared panel) isn't locked — see
blocker above.

## Business question this arc answers

Of the people who tried us, how many came back — and is our penetration
growth real adoption or just expensive sampling?

## Tasks (parked build arc — do not start until un-park trigger is met)

Work in vertical slices — one output end-to-end before the next.
Visualizations get reviewed in their own slice, not deferred to polish.

**Slice 0 — prep / reuse setup**
- [ ] Read carried-in memory + report what's carried in: infra notes,
      Spin Rate / Void Finder / Decompose HANDOFF + FAILURES, chart-config
      + design notes.
- [ ] Confirm the locked panel exposes what #4 needs (burn-in, both launch
      seeds, deterministic figures); document the panel interface #4 relies on.
- [ ] Vendor/reuse Spin Rate's shared chart template, design tokens, and
      header/footer chrome. Apply LAILARA_DESIGN_SYSTEM.md. Don't rebuild.
- [ ] Pull in the UCI Report 1 cohort machinery (`online-retail-analysis`);
      don't re-derive it.

**Slice 1 — metric core (tested)**
- [ ] Trial rate (cumulative first-ever-buyer curve).
- [ ] Repeat rate (% of triers who buy again within window N).
- [ ] Maturity-cutoff / right-censoring logic: repeat window a parameter
      (8/12 wks); summary numbers count only fully-matured cohorts; cutoff
      stated in-app. **Tests required** — this is the credibility make-or-break.
- [ ] Repeat purchase frequency; depth of repeat (1x / 2x / 3x+).
- [ ] Bucket flow: new in / lapsed out / net per period.

**Slice 2 — the four outputs (each reviewed as its own slice)**
- [ ] Cohort retention heatmap/triangle (handles right-censoring visually).
- [ ] Trial & repeat curves per item (launch vs established handled differently).
- [ ] Leaky-bucket flow chart (buyers in vs out per period, net line).
- [ ] "Promotion or brand?" verdict per item (trial-heavy/repeat-light flagged).
- [ ] Cinderhaven demo: the two contrasting launches side by side.

**Slice 3 — exec shell + chrome**
- [ ] Headline number in plain CFO-proof language; every number labeled
      with its timeframe; tooltips on every metric + filter; "why this
      matters" panel; glossary; synthetic-data disclosure.
- [ ] Tabs render distinct content + regression test on the tab-content callback.
- [ ] Tables: never truncate key ID column; scores as %/High-Med-Low;
      tooltips on computed columns.
- [ ] Verify every chart: no label clipping (automargin); correct,
      non-duplicate, evenly-spaced currency ticks; bottom legends; bold
      data labels. Check at 1440px AND 375px.

**Slice 4 — ship**
- [ ] Gunicorn + Docker + Fly.io (shared-cpu-1x, iad). Health check =
      liveness only. Confirm name/subdomain with Shawn before deploy.
- [ ] `/ce:compound` + multi-agent code review; drive findings to resolution.
- [ ] Work-page card (Door Math / Spin Rate / Void Finder format).
- [ ] Blog post draft pairing with the Decompose reveal ("penetration up ≠ growth").
- [ ] HANDOFF + FAILURES + memory updated; tests green.

## Out of scope for this arc

- Anything requiring a database — architecture is in-process panel, no DB.
- Panel changes (burn-in, seeded launches) — those belong to #3 Decompose.
- Building against the current unlocked panel (rework risk — ruled out).

## Definition of done

**This session:** ✅ scaffold created, parked arc written, #3 dependency
recorded, no code touched.

**The build arc:** app deployed to its subdomain; the two-launch demo
reads clearly; maturity-cutoff logic tested and stated in-app; every chart
verified; Work card + blog draft done; review findings resolved; tests green.

---

## Arc history

When an arc completes, archive its goal, completion date, and outcome
here. Then start a new arc above.

### 2026-07-06 — Build & ship Leaky Bucket (trial vs repeat analyzer)
- Outcome: Built the full app on the Decompose template (in-process shared panel,
  no DB) — trial/repeat math with maturity cutoff, cohort triangle, leaky-bucket
  flow, promotion-or-brand verdict. Deployed live to leakybucket.lailarallc.com.
  5-agent code review resolved (2 real bugs: empty-slice false "Promotion",
  cohort empty-frame crash). 96 tests green, ruff clean. Final tool in the
  5-part penetration series — all five now live.
- Tag: v0.1-foundation (scaffold). Consider a v1.0 ship tag.
- Remaining (non-code, Shawn): copy pass on docs/launch/, /publish, work-card placement.

---

## Improvement history

Track when this project was reviewed and improved via /improve.

<!-- Entries are added by /improve — don't delete this section -->

### 2026-07-27 — Improvement pass
- **Trigger:** user-initiated (`/improve`). Concerns: (1) 30-second exec comprehension for
  a CEO/CFO; (2) confidence the Claude-authored code is good / best-practice.
- **What was reviewed:** all of `app/` (read every module), the live page top-to-bottom as
  a cold exec, tests + ruff, and two independent background reviews (security; data/math
  correctness).
- **What was fixed:** added a purpose hero line as the first content on the page (30s fix);
  named the promotion/brand in the verdict headline in product terms, not SKU (+`line_name`
  column, +1 regression test); added a caption reconciling the cohort triangle's
  quarter-grain retention with the windowed headline repeat rate (review finding 1); added a
  depth-chart "shopping trips" caption (finding 2). 48 tests green, ruff clean, verified at
  1440px + 375px.
- **Verdict on the code:** independent review confirmed it — security clean; math
  "trustworthy for exec-facing numbers" (maturity-cutoff logic correct/centralized, merges
  cardinality-safe, denominators right). No calculation bugs.
- **Deferred:** security container hardening (non-root user, pin base image by digest);
  data-review findings 3 & 4 (cosmetic / NaN-format nit — harmless with current data);
  redeploy to Fly to ship these UI changes.
- **Next review:** 2026-10-27 (stable/shipped cadence — 90 days — unless it changes sooner).
