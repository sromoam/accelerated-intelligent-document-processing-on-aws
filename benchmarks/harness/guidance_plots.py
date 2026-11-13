"""Draw the plots for the "Benchmarks by Problem Set" pages.

render_guidance.py calls one of two functions for each ablation that has measured cells:

- draw_scatter() when the ablation reports cost or tokens: accuracy against cost per
  1,000 documents (or tokens per page), a panel per dataset and a point per value, with
  a soft band behind each dot spanning two standard errors either side. Up and to the
  left is better. When x is cost and y is an accuracy, thin lines run from the cheapest
  value to each more accurate one, labelled with the marginal cost of error.
- draw_plot() otherwise: one metric, a panel per dataset, a row per value, a dot at the
  mean and a band spanning two standard errors either side.

Each panel carries a subtitle naming the model in force at every step, so a chart on
its own says which models produced it, and a chart that shows cost carries the price
list it was computed from.

Each SVG is static (no script), follows the light or dark color scheme, and carries a
<title> and <desc> for screen readers; the results table under it holds every number.
"""

from __future__ import annotations

import math
from html import escape

#: Metrics where 1 - y is a share of errors, so the marginal cost of error applies.
ERROR_RATE_METRICS = frozenset(
    {
        "weighted_accuracy",
        "all_fields_right",
        "page_accuracy",
        "section_accuracy",
        "completeness",
        "cell_accuracy",
    }
)

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
SUB_CHAR_W = 5.5  # measured advance of 11px system-ui, to wrap the models line
SUB_LINE_H = 13
PRICES_H = 16
#: Half the width of the band behind a dot, in pixels.
BAND = 5

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
  .sub { font-size: 11px; fill: var(--muted); }
  .label { font-size: 12px; fill: var(--ink-2); }
  .tick { font-size: 11px; fill: var(--muted); font-variant-numeric: tabular-nums; }
  .none { font-size: 12px; fill: var(--muted); }
  .grid { stroke: var(--grid); stroke-width: 1; }
  .axis { stroke: var(--axis); stroke-width: 1; }
  .band { fill: var(--series); opacity: 0.12; }
  .dot { fill: var(--series); stroke: var(--ring); stroke-width: 2; }
  .axislabel { font-size: 11px; fill: var(--ink-2); }
  .note { font-size: 11px; fill: var(--muted); font-style: italic; }
  .prices { font-size: 10px; fill: var(--muted); }
  .num { font-size: 11px; font-weight: 700; fill: var(--ink); }
  .halo { paint-order: stroke; stroke: var(--ring); stroke-width: 3px;
          stroke-linejoin: round; }
  .mcoe { stroke: var(--muted); stroke-width: 1; fill: none; }
  .mcoe.noise { stroke-dasharray: 4 3; }
  .mcoelabel { font-size: 11px; fill: var(--ink-2); }
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


def money(v: float) -> str:
    """US dollars: $X.XX under $10, $X.X under $100, else $X,XXX."""
    a = abs(v)
    text = f"{a:.2f}" if a < 10 else f"{a:.1f}" if a < 100 else f"{a:,.0f}"
    return ("-" if v < 0 else "") + "$" + text


def marginal_cost_of_error(
    points: list[tuple[str, dict[str, float], dict[str, float]]],
) -> tuple[str, dict[str, float | None]]:
    """Return the cheapest value and the marginal cost of error of each other value.

    points: [(value, cost per 1,000 documents, accuracy), ...], each {"mean", "se"}.
    The reference is the cheapest value (ties: the less accurate one). For each value
    more accurate than it, the result is the extra cost per document divided by the
    drop in error rate, in US dollars, or None when the gain is within two standard
    errors of the difference. Values no more accurate than the reference are left out.
    """
    ref, rx, ry = min(points, key=lambda p: (p[1]["mean"], p[2]["mean"]))
    out: dict[str, float | None] = {}
    for value, x, y in points:
        gain = y["mean"] - ry["mean"]
        if value == ref or gain <= 0:
            continue
        noise = 2 * math.hypot(ry.get("se", 0), y.get("se", 0))
        out[value] = (x["mean"] - rx["mean"]) / 1000 / gain if gain > noise else None
    return ref, out


def mcoe_text(cost: float | None) -> str:
    return "no measurable gain" if cost is None else f"{money(cost)} per error"


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


def wrap_subtitle(text: str, width: float = WIDTH) -> list[str]:
    """Wrap the models line, breaking between steps first so nothing is clipped."""
    if not text:
        return []
    limit = max(20, int(width / SUB_CHAR_W) - 2)  # room for a trailing " ·"
    lines: list[str] = []
    current = ""
    for part in text.split(" · "):
        joined = f"{current} · {part}" if current else part
        if current and len(joined) > limit:
            lines.append(current)
            current = part
        else:
            current = joined
    if current:
        lines.append(current)
    out: list[str] = []
    for n, line in enumerate(lines):
        pieces: list[str] = []
        while len(line) > limit:  # one step longer than the width still has to break
            cut = line.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            pieces.append(line[:cut])
            line = line[cut:].lstrip()
        pieces.append(line)
        if n < len(lines) - 1:  # the separator stays at the end of the line it broke
            pieces[-1] += " ·"
        out += pieces
    return out


def subtitle_svg(lines: list[str], baseline: float) -> tuple[str, float]:
    """Render the models line under a panel title; return the SVG and its height."""
    if not lines:
        return "", 0.0
    spans = "".join(
        f'<tspan x="0" y="{baseline + 14 + i * SUB_LINE_H:.1f}">{escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return f'<text class="sub">{spans}</text>', SUB_LINE_H * len(lines)


def prices_svg(prices: str, y: float) -> str:
    return (
        f'<text class="prices" x="0" y="{y:.1f}">{escape(prices)}</text>'
        if prices
        else ""
    )


def draw_plot(
    metric_name: str,
    panels: list[tuple[str, str, list[tuple[str, dict[str, float] | None]]]],
    runs: int,
    *,
    prices: str = "",
) -> str:
    """Return an SVG document.

    panels: [(dataset name, models line, [(value label, {"mean", "se"} or None), ...])]
    prices: a price-list note for a chart that shows cost, or "" for one that does not.
    """
    points = [p for _, _, rows in panels for _, p in rows if p]
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
    for ds_name, models, rows in panels:
        body.append(f'<text class="panel" x="0" y="{y + 18}">{escape(ds_name)}</text>')
        sub, sub_h = subtitle_svg(wrap_subtitle(models), y + 18)
        body.append(sub)
        y += PANEL_TITLE_H + sub_h
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
                    f'<rect class="band" x="{x(m - 2 * s):.1f}" '
                    f'y="{cy - BAND:.1f}" width="{x(m + 2 * s) - x(m - 2 * s):.1f}" '
                    f'height="{2 * BAND}" rx="{BAND}"/>'
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
    height = y - PANEL_GAP + (PRICES_H if prices else 0)
    body.append(prices_svg(prices, height - 5))

    desc = "; ".join(
        f"{ds}: "
        + ", ".join(
            f"{v} {fmt(p['mean'])}" if p else f"{v} not measured" for v, p in rows
        )
        for ds, _, rows in panels
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
SC_PLOT_H = 190
SC_BOTTOM = 44
#: Above this many points, only the default and the frontier are labelled.
MAX_LABELLED = 4
#: Width of the "Better: up and to the left" note, which labels must keep off.
NOTE_W = 150


def _span(
    values: list[float],
    *,
    min_span: float = 0.0,
    pad: float = 0.12,
    count: int = 4,
    allow_negative: bool = True,
) -> list[float]:
    """Return round ticks covering the values, padded, with a minimum span.

    The axis is sized to the values themselves, not to zero: on a cost axis two
    values $11 apart would otherwise sit on top of each other in the middle of the
    range. `min_span`, a fraction of the largest value, stops the opposite problem,
    where two close values spread across the whole axis and a small difference reads
    as the whole story. `allow_negative` is False for a cost or a count.
    """
    lo, hi = min(values), max(values)
    if min_span and hi - lo < min_span * abs(hi):
        grow = (min_span * abs(hi) - (hi - lo)) / 2
        lo, hi = lo - grow, hi + grow
    margin = (hi - lo) * pad or abs(hi) * 0.05 or 1.0
    lo, hi = lo - margin, hi + margin
    if not allow_negative:
        lo = max(0.0, lo)
    return nice_ticks(lo, hi, count)


def _compact(v: float, axis_max: float) -> str:
    """One style per axis: compact (5K, 10K) when the axis reaches 10,000."""
    if axis_max >= 10_000:
        return f"{v / 1000:,.{0 if v % 1000 == 0 else 1}f}K" if v else "0"
    return f"{v:,.0f}"


def _money_ticks(ticks: list[float]) -> list[str]:
    """Whole dollars, or cents when a tick falls between them."""
    whole = all(abs(t - round(t)) < 1e-9 for t in ticks)
    return [f"${t:,.0f}" if whole else f"${t:,.2f}" for t in ticks]


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


Rect = tuple[float, float, float, float]


def _rect(lx: float, ly: float, w: float, anchor: str) -> Rect:
    """The box a one-line label at (lx, ly) with this anchor covers."""
    left = lx if anchor == "start" else lx - w if anchor == "end" else lx - w / 2
    return (left, ly - 11, left + w, ly + 3)


def _clear(r: Rect, bounds: Rect, blocked: list[Rect]) -> bool:
    x0, y0, x1, y1 = bounds
    if r[0] < x0 or r[2] > x1 or r[1] < y0 or r[3] > y1:
        return False
    return not any(
        r[0] < o[2] and o[0] < r[2] and r[1] < o[3] and o[1] < r[3] for o in blocked
    )


def _place_on_lines(
    lines: list[tuple[str, float, float, float, float]],
    bounds: Rect,
    blocked: list[Rect],
) -> list[tuple[str, float, float]]:
    """Place a label on each line, near its middle, clear of everything in blocked.

    Labels sit on the line (their halo hides it) and move along it, then just above
    or below it, until clear. A label with no clear spot is left out of the result,
    and the caller lists it in the chart's key instead.
    """
    taken = list(blocked)
    out = []
    for text, ax, ay, bx, by in lines:
        w = len(text) * CHAR_W * 0.92
        for t in (0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74, 0.18, 0.82):
            mx, my = ax + t * (bx - ax), ay + t * (by - ay)
            spot = next(
                (
                    (mx, my + dy)
                    for dy in (4, -7, 15)
                    if _clear(_rect(mx, my + dy, w, "middle"), bounds, taken)
                ),
                None,
            )
            if spot:
                taken.append(_rect(spot[0], spot[1], w, "middle"))
                out.append((text, spot[0], spot[1]))
                break
    return out


def _place_labels(
    points: list[tuple[str, float, float]],
    bounds: Rect,
    obstacles: list[Rect],
) -> list[tuple[str, float, float, str, tuple[float, float] | None]]:
    """Place one label per point without overlaps.

    Tries right, left, above and below each point; takes the first spot clear of the
    other labels, the dots and the plot edges. If none is clear, the label goes below
    the lowest clear spot on the right with a leader line back to its point.
    Returns (text, x, y, anchor, leader start or None).
    """
    taken: list[Rect] = []
    out = []
    rect = _rect

    def clear(r: Rect) -> bool:
        return _clear(r, bounds, taken + obstacles)

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
    panels: list[tuple[str, str, list[tuple[str, dict[str, float], dict[str, float]]]]],
    runs: int,
    *,
    x_money: bool = False,
    mcoe: bool = False,
    prices: str = "",
) -> str:
    """Return an SVG document plotting y (accuracy) against x (cost or tokens).

    panels: [(dataset name, models line, [(value, x {"mean", "se"}, y {...}), ...])]
    x_money: x is cost per 1,000 documents in US dollars (otherwise tokens per page).
    mcoe: draw marginal-cost-of-error lines from each panel's cheapest value.
    prices: a price-list note for a chart that shows cost, or "" for one that does not.
    """

    def x_text(v: float) -> str:
        return money(v) if x_money else _compact(v, 10_000)

    def x_exact(v: float) -> str:
        return money(v) if x_money else fmt(v)

    body: list[str] = []
    desc_parts: list[str] = []
    top = TOP
    for ds_name, models, points in panels:
        # Each dataset gets its own ranges: results on different datasets are not
        # compared with each other, and a shared range squeezes the small ones.
        xt = _span(
            [p[1]["mean"] for p in points],
            min_span=0.20,
            pad=0.15,
            count=5,
            allow_negative=False,
        )
        x_ticks = _money_ticks(xt) if x_money else [_compact(t, xt[-1]) for t in xt]
        ys = [p[2]["mean"] + s * 2 * p[2].get("se", 0) for p in points for s in (-1, 1)]
        yt = _span(ys)
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
        sub, sub_h = subtitle_svg(wrap_subtitle(models), top + 18)
        body.append(sub)
        y0 = top + PANEL_TITLE_H + sub_h
        y1 = y0 + SC_PLOT_H

        def px(v: float, xt: list[float] = xt) -> float:
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
        for t, text in zip(xt, x_ticks):
            body.append(
                f'<text class="tick" x="{px(t):.1f}" y="{y1 + 16}" '
                f'text-anchor="middle">{text}</text>'
            )
        body.append(
            f'<line class="axis" x1="{SC_LEFT}" x2="{SC_RIGHT}" y1="{y1}" y2="{y1}"/>'
            f'<line class="axis" x1="{SC_LEFT}" x2="{SC_LEFT}" y1="{y0}" y2="{y1}"/>'
            f'<text class="axislabel" x="{(SC_LEFT + SC_RIGHT) / 2:.1f}" '
            f'y="{y1 + 34}" text-anchor="middle">{escape(x_name)}</text>'
            f'<text class="axislabel" transform="translate(12 {(y0 + y1) / 2:.1f}) '
            f'rotate(-90)" text-anchor="middle">{escape(y_name)}</text>'
        )
        # Drawn after the lines and dots, so its halo keeps them off the words.
        note = (
            f'<text class="note halo" x="{SC_LEFT + 8}" y="{y0 + 14}">'
            "Better: up and to the left</text>"
        )

        def label(value: str, x: dict[str, float], y: dict[str, float]) -> str:
            y_text = f"{y['mean']:.{max(2, y_dec)}f}"
            return f"{value}: {y_text}, {x_text(x['mean'])}"

        centre = {v: (px(x["mean"]), py(y["mean"])) for v, x, y in points}

        # The bands go down first, so the dots and the cost-of-error lines sit on top.
        # "Better: up and to the left" is already drawn, so nothing may land on it.
        obstacles = [(SC_LEFT + 6, y0 + 2, SC_LEFT + 6 + NOTE_W, y0 + 18)]
        for value, _, y in points:
            cx, cy = centre[value]
            dy = 2 * y.get("se", 0)
            band_top, band_bottom = py(y["mean"] + dy), py(y["mean"] - dy)
            obstacles.append((cx - 7, cy - 7, cx + 7, cy + 7))
            obstacles.append((cx - BAND, band_top, cx + BAND, band_bottom))
            if band_bottom > band_top:
                body.append(
                    f'<rect class="band" x="{cx - BAND:.1f}" y="{band_top:.1f}" '
                    f'width="{2 * BAND}" height="{band_bottom - band_top:.1f}" '
                    f'rx="{BAND}"/>'
                )

        # Marginal cost of error: a thin line from the cheapest value to each value
        # that scores higher, under the dots. Solid when the gain is measurable.
        lines: list[tuple[str, float, float, float, float]] = []
        ref, gains = marginal_cost_of_error(points) if mcoe else ("", {})
        for value, cost in gains.items():
            (ax, ay), (bx, by) = centre[ref], centre[value]
            text = mcoe_text(cost)
            lines.append((text, ax, ay, bx, by))
            body.append(
                f"<g><title>{escape(value)} against {escape(ref)}: {text}</title>"
                f'<line class="mcoe{"" if cost is not None else " noise"}" '
                f'x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}"/></g>'
            )
        if gains:
            desc_parts.append(
                f"{ds_name}, marginal cost of error against {ref}: "
                + ", ".join(f"{v} {mcoe_text(c)}" for v, c in gains.items())
            )

        # Few points: label each one next to its dot. Otherwise only the default and
        # the frontier. If a label cannot sit cleanly beside its dot, number every
        # dot instead and list the names and values in a key under the chart.
        labelled = (
            {v for v, _, _ in points}
            if len(points) <= MAX_LABELLED
            else _frontier(points) | {v for v, _, _ in points if "(default)" in v}
        )
        screen = []
        for value, x, y in points:
            cx, cy = centre[value]
            dy = 2 * y.get("se", 0)
            if value in labelled:
                screen.append((label(value, x, y), cx, cy))
            body.append(
                f"<g><title>{escape(value)}: {escape(y_name)} {fmt(y['mean'])} ± "
                f"{fmt(dy)}, {escape(x_name)} {x_exact(x['mean'])}</title>"
                f'<circle class="dot" cx="{cx:.1f}" cy="{cy:.1f}" r="5"/></g>'
            )
        body.append(note)
        # Point labels and dot numbers also keep off the cost-of-error lines.
        on_line = [
            (ax + t * (bx - ax) - 1, ay + t * (by - ay) - 1)
            for _, ax, ay, bx, by in lines
            for n in [max(2, int(math.hypot(bx - ax, by - ay) / 6))]
            for t in (i / n for i in range(1, n))
        ]
        line_boxes = [(lx, ly, lx + 2, ly + 2) for lx, ly in on_line]
        bounds = (SC_LEFT + 2, y0 + 20, SC_RIGHT, y1 - 2)
        placed = _place_labels(screen, bounds, obstacles + line_boxes)
        blocked = obstacles + [
            _rect(lx, ly, len(text) * CHAR_W, anchor)
            for text, lx, ly, anchor, _ in placed
        ]
        on_lines = _place_on_lines(lines, bounds, blocked)
        key_h = 0
        if any(leader for *_, leader in placed) or len(on_lines) < len(lines):
            # Number the dots and list each value, with its marginal cost of error,
            # in a key under the chart.
            numbers = _place_labels(
                [(str(i), cx, cy) for i, (cx, cy) in enumerate(centre.values(), 1)],
                (SC_LEFT + 2, y0, SC_RIGHT, y1 - 2),
                obstacles + line_boxes,
            )
            for text, lx, ly, anchor, leader in numbers:
                if leader:
                    body.append(
                        f'<line class="axis" x1="{leader[0]:.1f}" y1="{leader[1]:.1f}" '
                        f'x2="{lx:.1f}" y2="{ly - 4:.1f}"/>'
                    )
                body.append(
                    f'<text class="num halo" x="{lx:.1f}" y="{ly:.1f}" '
                    f'text-anchor="{anchor}">{text}</text>'
                )
            for i, (value, x, y) in enumerate(points, 1):
                entry = label(value, x, y)
                if value in gains:
                    entry += f"; {mcoe_text(gains[value])}"
                body.append(
                    f'<text class="label" x="{SC_LEFT}" y="{y1 + 58 + (i - 1) * 16}">'
                    f'<tspan class="num">{i}</tspan>  {escape(entry)}</text>'
                )
            key_h = 12 + 16 * len(points)
        else:
            for text, lx, ly, anchor, _ in placed:
                body.append(
                    f'<text class="label halo" x="{lx:.1f}" y="{ly:.1f}" '
                    f'text-anchor="{anchor}">{escape(text)}</text>'
                )
            for text, lx, ly in on_lines:
                body.append(
                    f'<text class="mcoelabel halo" x="{lx:.1f}" y="{ly:.1f}" '
                    f'text-anchor="middle">{escape(text)}</text>'
                )
        top = y1 + SC_BOTTOM + key_h + PANEL_GAP
    height = top - PANEL_GAP + (PRICES_H if prices else 0)
    body.append(prices_svg(prices, height - 5))

    desc = "; ".join(
        [
            f"{ds}: "
            + ", ".join(
                f"{v} {fmt(y['mean'])} at {x_exact(x['mean'])}" for v, x, y in rows
            )
            for ds, _, rows in panels
        ]
        + desc_parts
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="viz" width="{WIDTH}" '
        f'height="{height}" viewBox="0 0 {WIDTH} {height}" role="img">'
        f"<title>{escape(y_name)} against {escape(x_name)}, mean of {runs} runs "
        f"with two standard errors either side</title><desc>{escape(desc)}</desc>"
        f"<style>{STYLE}</style>" + "".join(body) + "</svg>\n"
    )
