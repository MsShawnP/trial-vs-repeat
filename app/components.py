"""Shared UI building blocks for the Leaky Bucket views — headings, stat cards, the
'why this matters' panel, and the exec glossary."""

from dash import html

# The exec-facing glossary. Plain phrasing so a CFO reads it without a stats background.
GLOSSARY = [
    ("Trial",
     "A household's first-ever purchase of the brand (or of a specific item). The "
     "cumulative trial curve is how many households have tried you by a given quarter."),
    ("Repeat rate",
     "Of the households that tried you, the share who bought again within the repeat "
     "window. This is the difference between a brand and a promotion."),
    ("Repeat window",
     "How long a trier has to come back and still count as a repeat. A parameter (8, "
     "12, 26, or 52 weeks) because categories repeat on different clocks — pantry "
     "staples and snack bites cycle quarterly, so the default is 52 weeks."),
    ("Maturity cutoff",
     "Recent triers haven't had a full repeat window yet, so counting them would drag "
     "the repeat rate down for no real reason (right-censoring). Every summary repeat "
     "number counts only triers whose window has fully elapsed. The cutoff date is "
     "stated on the page."),
    ("Cohort retention",
     "Group households by the quarter they first bought, then track what share buy "
     "again each later quarter. Recent cohorts have fewer observable quarters — the "
     "triangle shape is that right-censoring, shown rather than hidden."),
    ("Depth of repeat",
     "Among triers who had a full window, how many came back once (2×), twice or more "
     "(3×+), or never (1× — trial only)."),
    ("Leaky-bucket flow",
     "Each quarter, buyers flow in (new) and out (lapsed). The net line is whether the "
     "bucket is filling or draining — penetration can rise while the bucket leaks."),
    ("Promotion or brand?",
     "A trial-heavy, repeat-light item is a promotion: expensive sampling that "
     "collapses when spend stops. A repeating item is a brand. The verdict flags each "
     "launch item against a repeat-rate threshold."),
]


def view_heading(title: str, blurb: str):
    """A view's serif heading plus a one-line 'why this matters' blurb."""
    return html.Div(
        [
            html.H2(title, className="view-title ll-section-title"),
            html.P(blurb, className="view-blurb"),
        ],
        className="view-heading",
    )


def metric_card(label, value, foot=None, delta=None, delta_class=None, tip=None):
    """A stat card: small label, big value, optional delta line and footnote.

    Primary/secondary hierarchy: value dominates, label and foot are muted. ``tip`` sets
    a hover tooltip on the card (exec rule: every metric has a tooltip).
    """
    children = [
        html.Div(label, className="metric-card-label"),
        html.Div(value, className="metric-card-value ll-benchmark-value"),
    ]
    if delta is not None:
        children.append(html.Div(delta, className=f"metric-card-delta {delta_class or ''}".strip()))
    if foot is not None:
        children.append(html.Div(foot, className="metric-card-foot"))
    return html.Div(children, className="metric-card", title=tip or "")


def metric_cards_grid(cards, caption=None):
    """A responsive grid of stat cards, with an optional caption below."""
    children = [html.Div(cards, className="metric-cards-grid")]
    if caption:
        children.append(html.P(caption, className="metric-cards-caption"))
    return html.Div(children)


def why_this_matters(text: str):
    """A muted, collapsible 'why this matters' panel for exec context."""
    return html.Details(
        [
            html.Summary("Why this matters", className="why-toggle"),
            html.P(text, className="why-body"),
        ],
        className="why-details",
    )


def definitions_panel():
    """A collapsible glossary of the terms used across the tool."""
    items = [
        html.Div(
            [
                html.Dt(term, className="glossary-term"),
                html.Dd(definition, className="glossary-def"),
            ],
            className="glossary-row",
        )
        for term, definition in GLOSSARY
    ]
    return html.Details(
        [
            html.Summary("Glossary", className="why-toggle"),
            html.Dl(items, className="glossary-list"),
        ],
        className="why-details glossary-details",
    )
