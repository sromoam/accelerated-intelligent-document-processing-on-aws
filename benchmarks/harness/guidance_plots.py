"""Draw the dot-and-whisker plots for the "Benchmarks by Problem Set" pages.

render_guidance.py calls draw_plot() for each ablation that has measured cells. One
SVG shows one metric: a panel per dataset, a row per value, a dot at the mean of the
runs and a line spanning two standard errors either side. The SVG is static (no
script), follows the light or dark color scheme, and carries a <title> and <desc>
for screen readers; the results table under it holds every number.
"""

from __future__ import annotations

import math
from html import escape

WIDTH = 720
LABEL_W = 260
PLOT_X0 = LABEL_W + 20
PLOT_X1 = WIDTH - 28
ROW_H = 26
ROW_H_WRAPPED = 38
PANEL_TITLE_H = 30
AXIS_H = 26
PANEL_GAP = 18
TOP = 8
CHAR_W = 6.7  # average advance of 12px system-ui, used to wrap value labels
MAX_CHARS = int(LABEL_W / CHAR_W)

STYLE = """
  .viz { --series: #2a78d6; --ring: #ffffff; --ink: #0b0b0b; --ink-2: #52514e;
         --muted: #898781; --grid: #e1e0d9; --axis: #c3c2b7; }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz, svg.viz:root { --series: #3987e5;
      --ring: #17181c; --ink: #f0efec; --ink-2: #c3c2b7; --muted: #898781;
      --grid: #2c2c2a; --axis: #383835; }
  }
  :root[data-theme="dark"] .viz { --series: #3987e5; --ring: #17181c; --ink: #f0efec;
    --ink-2: #c3c2b7; --muted: #898781; --grid: #2c2c2a; --axis: #383835; }
  .viz { max-width: 100%; height: auto; }
  text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  .panel { font-size: 13px; font-weight: 600; fill: var(--ink); }
  .label { font-size: 12px; fill: var(--ink-2); }
  .tick { font-size: 11px; fill: var(--muted); font-variant-numeric: tabular-nums; }
  .none { font-size: 12px; fill: var(--muted); }
  .grid { stroke: var(--grid); stroke-width: 1; }
  .axis { stroke: var(--axis); stroke-width: 1; }
  .whisker { stroke: var(--series); stroke-width: 2; stroke-linecap: round; }
  .dot { fill: var(--series); stroke: var(--ring); stroke-width: 2; }
"""


def nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    """Return round tick values covering [lo, hi]."""
    if hi <= lo:
        hi = lo + (abs(lo) or 1.0)
    raw = (hi - lo) / count
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    start = math.floor(lo / step) * step
    ticks = []
    t = start
    while t <= hi + step * 1e-9:
        ticks.append(round(t, 10))
        t += step
    if ticks[-1] < hi:
        ticks.append(round(ticks[-1] + step, 10))
    return ticks


def fmt(v: float) -> str:
    """Format a tick or mean the way the tables do."""
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    if abs(v) >= 10:
        return f"{v:.0f}"
    return f"{v:.2f}".rstrip("0").rstrip(".") if v != 0 else "0"


def wrap(text: str) -> list[str]:
    """Wrap a value label onto at most two lines, ellipsizing the second."""
    if len(text) <= MAX_CHARS:
        return [text]
    words, first = text.split(), ""
    while words and len(first) + len(words[0]) + (1 if first else 0) <= MAX_CHARS:
        first = f"{first} {words.pop(0)}".strip()
    rest = " ".join(words)
    if len(rest) > MAX_CHARS:
        rest = rest[: MAX_CHARS - 1].rstrip() + "…"
    return [first, rest] if first else [text[: MAX_CHARS - 1] + "…"]


def draw_plot(
    metric_name: str,
    panels: list[tuple[str, list[tuple[str, dict[str, float] | None]]]],
    runs: int,
) -> str:
    """Return an SVG document.

    panels: [(dataset name, [(value label, {"mean": m, "se": s} or None), ...]), ...]
    """
    points = [p for _, rows in panels for _, p in rows if p]
    lo = min(p["mean"] - 2 * p.get("se", 0) for p in points)
    hi = max(p["mean"] + 2 * p.get("se", 0) for p in points)
    pad = (hi - lo) * 0.08 or abs(hi) * 0.05 or 1.0
    ticks = nice_ticks(lo - pad, hi + pad)
    d0, d1 = ticks[0], ticks[-1]

    step = ticks[1] - ticks[0] if len(ticks) > 1 else 1.0
    decimals = max(0, -math.floor(math.log10(step) + 1e-9))

    def tick_text(t: float) -> str:
        return f"{t:,.{decimals}f}"

    def x(v: float) -> float:
        return PLOT_X0 + (v - d0) / (d1 - d0) * (PLOT_X1 - PLOT_X0)

    body: list[str] = []
    y = TOP
    for ds_name, rows in panels:
        body.append(f'<text class="panel" x="0" y="{y + 18}">{escape(ds_name)}</text>')
        y += PANEL_TITLE_H
        top = y
        heights = [ROW_H_WRAPPED if len(wrap(v)) > 1 else ROW_H for v, _ in rows]
        bottom = top + sum(heights)
        for t in ticks:
            body.append(
                f'<line class="grid" x1="{x(t):.1f}" x2="{x(t):.1f}" '
                f'y1="{top}" y2="{bottom}"/>'
            )
        for (value, p), h in zip(rows, heights):
            cy = y + h / 2
            lines = wrap(value)
            first_y = cy + 4 - (len(lines) - 1) * 7
            tspans = "".join(
                f'<tspan x="0" y="{first_y + i * 14:.1f}">{escape(line)}</tspan>'
                for i, line in enumerate(lines)
            )
            body.append(f'<text class="label">{tspans}</text>')
            if p is None:
                body.append(
                    f'<text class="none" x="{PLOT_X0}" y="{cy + 4:.1f}">'
                    "Not measured</text>"
                )
            else:
                m, s = p["mean"], p.get("se", 0)
                body.append(
                    f"<g><title>{escape(value)}: {fmt(m)} ± {fmt(2 * s)}</title>"
                    f'<line class="whisker" x1="{x(m - 2 * s):.1f}" '
                    f'x2="{x(m + 2 * s):.1f}" y1="{cy:.1f}" y2="{cy:.1f}"/>'
                    f'<circle class="dot" cx="{x(m):.1f}" cy="{cy:.1f}" r="5"/></g>'
                )
            y += h
        body.append(
            f'<line class="axis" x1="{PLOT_X0}" x2="{PLOT_X1}" '
            f'y1="{bottom}" y2="{bottom}"/>'
        )
        for t in ticks:
            body.append(
                f'<text class="tick" x="{x(t):.1f}" y="{bottom + 16}" '
                f'text-anchor="middle">{tick_text(t)}</text>'
            )
        y = bottom + AXIS_H + PANEL_GAP
    height = y - PANEL_GAP

    desc = "; ".join(
        f"{ds}: "
        + ", ".join(f"{v} {fmt(p['mean'])}" if p else f"{v} not measured" for v, p in r)
        for ds, r in panels
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="viz" width="{WIDTH}" '
        f'height="{height}" viewBox="0 0 {WIDTH} {height}" role="img">'
        f"<title>{escape(metric_name)}, mean of {runs} runs with two standard "
        f"errors either side</title><desc>{escape(desc)}</desc>"
        f"<style>{STYLE}</style>" + "".join(body) + "</svg>\n"
    )
