/**
 * clientside.js — Client-side helpers for Leaky Bucket.
 * Fixes Plotly legend text clipping caused by web-font loading.
 */

/**
 * Fix Plotly legend text clipping caused by the Source Sans 3 web-font
 * loading race. `font-display: swap` (lailara-frame.css) paints legend
 * text with a fallback font immediately, then swaps to Source Sans 3
 * once it downloads. Plotly measures legend entry widths ONCE, at
 * layout time, using whichever font is active at that instant -- if the
 * chart draws before the swap completes, entries are positioned using
 * the (narrower) fallback font's metrics, and the wider Source Sans 3
 * glyphs that paint in afterward overflow past the boundary Plotly
 * already committed to. Plotly never re-measures on its own, and no
 * amount of container CSS can reach inside its <svg> coordinate layout.
 *
 * Fix: once the browser confirms the font has actually finished
 * loading, force every currently-drawn plot to resize/relayout so
 * Plotly re-measures legend text with the correct, final metrics. If
 * the chart hasn't drawn yet at that point, it draws AFTER the font is
 * ready and never hits the race in the first place -- this only needs
 * to run once.
 */
(function () {
    function resizePlotlyCharts() {
        document.querySelectorAll(".js-plotly-plot").forEach(function (gd) {
            if (window.Plotly && gd._fullLayout) {
                window.Plotly.Plots.resize(gd);
            }
        });
    }

    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(resizePlotlyCharts);
    }
})();
