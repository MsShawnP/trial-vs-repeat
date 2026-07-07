# Work-page card — Leaky Bucket

*Draft for the lailarallc.com /work page, Door Math / Spin Rate / Void Finder card format. Shawn copy pass + placement pending.*

---

**Leaky Bucket**
*Trial vs repeat analyzer · Cinderhaven series #4 (final)*

Of the households that tried you, how many came back — and is your penetration growth real adoption or just expensive sampling? Leaky Bucket separates a brand from a promotion. Household penetration can rise every quarter while the business quietly dies: if new buyers pour in and almost none repeat, growth is a treadmill that collapses the moment trade spend stops. This is the integrity check on Decompose (#3) — #3 counts the buyers, #4 says whether they stuck.

- **Promotion or brand?** — two launches side by side: one drew a big trial spike and ~14% repeat (a promotion that looked great in month one), the other a modest trial and 51% repeat (the quiet winner). The verdict is computed, not scripted.
- **Cohort retention triangle** — buyers grouped by the quarter they first bought; the missing corner is the honest admission that recent cohorts haven't had time to repeat yet (right-censoring shown, not smoothed).
- **The leaky bucket** — buyers in vs out per quarter, with a net line that shows the bucket filling or draining even as penetration climbs.
- **Maturity cutoff, stated** — every summary repeat number counts only triers whose repeat window has fully elapsed. The window is a parameter (8 / 12 / 26 / 52 weeks).

**Stack:** Python · Dash · Plotly · pandas · Gunicorn/Docker/Fly.io. Data is the same in-process, seed-locked synthetic household panel Decompose built — no database.

**Live:** https://leakybucket.lailarallc.com

---

*Card fields to confirm with Shawn: exact tagline, whether to lead with the "penetration up ≠ growth" hook, thumbnail (suggest the promotion-vs-brand scatter with the two launch items either side of the brand line). Repeat-window default is 52 weeks — see DECISIONS.md for why (the panel repeats on a quarterly cycle).*
