"""Draw the plots for the "Benchmarks by Problem Set" pages.

render_guidance.py calls one of two functions for each ablation that has measured cells:

- draw_scatter() when the ablation reports tokens: accuracy against tokens per page, a
  panel per dataset and a point per value, with lines spanning two standard errors
  either side on both axes. Up and to the left is better.
- draw_plot() otherwise: one metric, a panel per dataset, a row per value, a dot at the
  mean and a line spanning two standard errors either side.

Each SVG is static (no script), follows the light or dark color scheme, and carries a
<title> and <desc> for screen readers; the results table under it holds every number.
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
  .xwhisker { stroke: var(--series); stroke-width: 1.5; stroke-linecap: round;
              opacity: 0.55; }
  .axislabel { font-size: 11px; fill: var(--ink-2); }
  .note { font-size: 11px; fill: var(--muted); font-style: italic; }
  .num { font-size: 11px; font-weight: 700; fill: var(--ink); }
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
                body.append(
                    f'<text class="label" x="{x(m + 2 * s) + 8:.1f}" y="{cy + 4:.1f}">'
                    f"{fmt(m)}</text>"
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


SC_LEFT = 64
SC_RIGHT = WIDTH - 24
SC_PLOT_H = 230
SC_BOTTOM = 44
#: Above this many points, only the default and the frontier are labelled.
MAX_LABELLED = 4


def _span(values: list[float], start_at_zero: bool) -> list[float]:
    lo, hi = min(values), max(values)
    pad = (hi - lo) * 0.12 or abs(hi) * 0.05 or 1.0
    return nice_ticks(0.0 if start_at_zero else lo - pad, hi + pad, 4)


def _compact(v: float, axis_max: float) -> str:
    """One style per axis: compact (5K, 10K) when the axis reaches 10,000."""
    if axis_max >= 10_000:
        return f"{v / 1000:,.{0 if v % 1000 == 0 else 1}f}K" if v else "0"
    return f"{v:,.0f}"


def _frontier(points: list[tuple[str, dict[str, float], dict[str, float]]]) -> set[str]:
    """Values no other value beats on both axes (fewer tokens and higher accuracy)."""
    keep = set()
    for v, x, y in points:
        if not any(
            ox["mean"] <= x["mean"]
            and oy["mean"] >= y["mean"]
            and (ox["mean"] < x["mean"] or oy["mean"] > y["mean"])
            for ov, ox, oy in points
            if ov != v
        ):
            keep.add(v)
    return keep


def _place_labels(
    points: list[tuple[str, float, float]],
    bounds: tuple[float, float, float, float],
    obstacles: list[tuple[float, float, float, float]],
) -> list[tuple[str, float, float, str, tuple[float, float] | None]]:
    """Place one label per point without overlaps.

    Tries right, left, above and below each point; takes the first spot clear of the
    other labels, the dots and the plot edges. If none is clear, the label goes below
    the lowest clear spot on the right with a leader line back to its point.
    Returns (text, x, y, anchor, leader start or None).
    """
    x0, y0, x1, y1 = bounds
    dots = obstacles
    taken: list[tuple[float, float, float, float]] = []
    out = []

    def rect(lx: float, ly: float, w: float, anchor: str) -> tuple[float, ...]:
        left = lx if anchor == "start" else lx - w if anchor == "end" else lx - w / 2
        return (left, ly - 11, left + w, ly + 3)

    def clear(r: tuple[float, ...]) -> bool:
        if r[0] < x0 or r[2] > x1 or r[1] < y0 or r[3] > y1:
            return False
        return not any(
            r[0] < o[2] and o[0] < r[2] and r[1] < o[3] and o[1] < r[3]
            for o in taken + dots
        )

    for text, cx, cy in sorted(points, key=lambda p: (p[2], p[1])):
        w = len(text) * CHAR_W
        spots = [
            (cx + 10, cy + 4, "start"),
            (cx - 10, cy + 4, "end"),
            (cx, cy - 12, "middle"),
            (cx, cy + 20, "middle"),
            (cx + 8, cy - 10, "start"),
            (cx + 8, cy + 18, "start"),
            (cx - 8, cy - 10, "end"),
            (cx - 8, cy + 18, "end"),
        ]
        for lx, ly, anchor in spots:
            r = rect(lx, ly, w, anchor)
            if clear(r):
                taken.append(r)
                out.append((text, lx, ly, anchor, None))
                break
        else:
            # Search outward, above and below, on both sides; draw a leader line.
            for k in range(1, 16):
                hit = None
                for dy in (-14 * k - 4, 14 * k + 4):
                    for dx, anchor in ((18, "start"), (-18, "end")):
                        lx, ly = cx + dx, cy + dy
                        r = rect(lx, ly, w, anchor)
                        if clear(r):
                            hit = (lx, ly, anchor, r)
                            break
                    if hit:
                        break
                if hit:
                    lx, ly, anchor, r = hit
                    taken.append(r)
                    out.append((text, lx, ly, anchor, (cx, cy)))
                    break
            else:
                out.append((text, cx + 10, cy + 4, "start", (cx, cy)))
    return out


def draw_scatter(
    x_name: str,
    y_name: str,
    panels: list[tuple[str, list[tuple[str, dict[str, float], dict[str, float]]]]],
    runs: int,
) -> str:
    """Return an SVG document plotting y (accuracy) against x (tokens per page).

    panels: [(dataset name, [(value label, x {"mean", "se"}, y {"mean", "se"}), ...])]
    """
    xs = [
        p[1]["mean"] + s * 2 * p[1].get("se", 0)
        for _, r in panels
        for p in r
        for s in (-1, 1)
    ]
    xt = _span(xs, start_at_zero=True)

    body: list[str] = []
    top = TOP
    for ds_name, points in panels:
        # Each dataset gets its own vertical range: scores on different datasets are
        # not compared with each other, and a shared range squeezes the high ones.
        ys = [p[2]["mean"] + s * 2 * p[2].get("se", 0) for p in points for s in (-1, 1)]
        yt = _span(ys, start_at_zero=False)
        # A score that cannot pass 1.0 gets an axis that stops at 1.0.
        if max(p[2]["mean"] for p in points) <= 1.0:
            yt = [t for t in yt if t <= 1.0 + 1e-9]
            if yt[-1] < 1.0 and max(ys) > yt[-1]:
                yt.append(1.0)
        y_step = yt[1] - yt[0] if len(yt) > 1 else 1.0
        y_dec = max(0, -math.floor(math.log10(y_step) + 1e-9))

        body.append(
            f'<text class="panel" x="0" y="{top + 18}">{escape(ds_name)}</text>'
        )
        y0, y1 = top + PANEL_TITLE_H, top + PANEL_TITLE_H + SC_PLOT_H

        def px(v: float) -> float:
            return SC_LEFT + (v - xt[0]) / (xt[-1] - xt[0]) * (SC_RIGHT - SC_LEFT)

        def py(v: float, y0: float = y0, y1: float = y1, yt: list[float] = yt) -> float:
            return y1 - (v - yt[0]) / (yt[-1] - yt[0]) * (y1 - y0)

        for t in yt:
            body.append(
                f'<line class="grid" x1="{SC_LEFT}" x2="{SC_RIGHT}" '
                f'y1="{py(t):.1f}" y2="{py(t):.1f}"/>'
                f'<text class="tick" x="{SC_LEFT - 8}" y="{py(t) + 4:.1f}" '
                f'text-anchor="end">{t:.{y_dec}f}</text>'
            )
        for t in xt:
            body.append(
                f'<text class="tick" x="{px(t):.1f}" y="{y1 + 16}" '
                f'text-anchor="middle">{_compact(t, xt[-1])}</text>'
            )
        body.append(
            f'<line class="axis" x1="{SC_LEFT}" x2="{SC_RIGHT}" y1="{y1}" y2="{y1}"/>'
            f'<line class="axis" x1="{SC_LEFT}" x2="{SC_LEFT}" y1="{y0}" y2="{y1}"/>'
            f'<text class="axislabel" x="{(SC_LEFT + SC_RIGHT) / 2:.1f}" '
            f'y="{y1 + 34}" text-anchor="middle">{escape(x_name)}</text>'
            f'<text class="axislabel" transform="translate(12 {(y0 + y1) / 2:.1f}) '
            f'rotate(-90)" text-anchor="middle">{escape(y_name)}</text>'
            f'<text class="note" x="{SC_LEFT + 8}" y="{y0 + 14}">'
            "Better: up and to the left</text>"
        )

        def label(value: str, x: dict[str, float], y: dict[str, float]) -> str:
            y_text = f"{y['mean']:.{max(2, y_dec)}f}"
            return f"{value}: {y_text}, {_compact(x['mean'], 10_000)}"

        # Few points: label each one next to its dot. Otherwise only the default and
        # the frontier. If a label cannot sit cleanly beside its dot, number every
        # dot instead and list the names and values in a key under the chart.
        labelled = (
            {v for v, _, _ in points}
            if len(points) <= MAX_LABELLED
            else _frontier(points) | {v for v, _, _ in points if "(default)" in v}
        )
        screen, obstacles, centres = [], [], []
        for value, x, y in points:
            cx, cy = px(x["mean"]), py(y["mean"])
            dx, dy = 2 * x.get("se", 0), 2 * y.get("se", 0)
            centres.append((cx, cy))
            obstacles.append((cx - 7, cy - 7, cx + 7, cy + 7))
            obstacles.append((px(x["mean"] - dx), cy - 1, px(x["mean"] + dx), cy + 1))
            obstacles.append((cx - 1, py(y["mean"] + dy), cx + 1, py(y["mean"] - dy)))
            if value in labelled:
                screen.append((label(value, x, y), cx, cy))
            body.append(
                f"<g><title>{escape(value)}: {escape(y_name)} {fmt(y['mean'])} ± "
                f"{fmt(dy)}, {escape(x_name)} {fmt(x['mean'])} ± {fmt(dx)}</title>"
                f'<line class="xwhisker" x1="{px(x["mean"] - dx):.1f}" '
                f'x2="{px(x["mean"] + dx):.1f}" y1="{cy:.1f}" y2="{cy:.1f}"/>'
                f'<line class="xwhisker" x1="{cx:.1f}" x2="{cx:.1f}" '
                f'y1="{py(y["mean"] - dy):.1f}" y2="{py(y["mean"] + dy):.1f}"/>'
                f'<circle class="dot" cx="{cx:.1f}" cy="{cy:.1f}" r="5"/></g>'
            )
        placed = _place_labels(
            screen, (SC_LEFT + 2, y0 + 20, SC_RIGHT, y1 - 2), obstacles
        )
        key_h = 0
        if any(leader for *_, leader in placed):
            for i, ((value, x, y), (cx, cy)) in enumerate(zip(points, centres), 1):
                body.append(
                    f'<text class="num" x="{cx + 7:.1f}" y="{cy - 7:.1f}">{i}</text>'
                )
                body.append(
                    f'<text class="label" x="{SC_LEFT}" y="{y1 + 58 + (i - 1) * 16}">'
                    f'<tspan class="num">{i}</tspan>  {escape(label(value, x, y))}</text>'
                )
            key_h = 12 + 16 * len(points)
        else:
            for text, lx, ly, anchor, _ in placed:
                body.append(
                    f'<text class="label" x="{lx:.1f}" y="{ly:.1f}" '
                    f'text-anchor="{anchor}">{escape(text)}</text>'
                )
        top = y1 + SC_BOTTOM + key_h + PANEL_GAP
    height = top - PANEL_GAP

    desc = "; ".join(
        f"{ds}: "
        + ", ".join(f"{v} {fmt(y['mean'])} at {fmt(x['mean'])}" for v, x, y in r)
        for ds, r in panels
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="viz" width="{WIDTH}" '
        f'height="{height}" viewBox="0 0 {WIDTH} {height}" role="img">'
        f"<title>{escape(y_name)} against {escape(x_name)}, mean of {runs} runs "
        f"with two standard errors either side</title><desc>{escape(desc)}</desc>"
        f"<style>{STYLE}</style>" + "".join(body) + "</svg>\n"
    )
