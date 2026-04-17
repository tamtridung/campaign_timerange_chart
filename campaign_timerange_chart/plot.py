from __future__ import annotations

from typing import Any, Iterable, Mapping

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator

from .holidays_overlay import DateLike, add_vietnam_holidays


def _build_color_map(
    series: pd.Series,
    palette: dict[Any, str] | None,
) -> dict[Any, str]:
    unique_vals = list(pd.unique(series))
    cmap: dict[Any, str] = {}

    if palette:
        cmap.update(palette)

    color_cycle = plt.rcParams.get("axes.prop_cycle")
    fallback_colors = (
        color_cycle.by_key().get("color", ["C0", "C1", "C2", "C3", "C4"]) if color_cycle else ["C0", "C1", "C2", "C3", "C4"]
    )

    idx = 0
    for value in unique_vals:
        if value not in cmap:
            cmap[value] = fallback_colors[idx % len(fallback_colors)]
            idx += 1

    return cmap


def campaign_timerangeplot(
    data: pd.DataFrame,
    *,
    campaign_col: str = "campaign",
    start_col: str = "start_date",
    end_col: str = "end_date",
    hue_col: str = "status",
    palette: dict[Any, str] | None = None,
    ax: Axes | None = None,
    show_holidays: bool = True,
    holiday_years: list[int] | None = None,
    custom_holidays: Mapping[DateLike, str] | Iterable[tuple[DateLike, str]] | None = None,
    holiday_text: bool = True,
    x_tick_daily: bool = False,
    date_format: str = "%Y-%m-%d",
    linewidth: float = 8.0,
    row_height: float = 0.8,
    legend: bool = True,
    title: str | None = None,
) -> Axes:
    """Draw campaign time ranges as horizontal line segments.

    Parameters are intentionally seaborn-like: pass a DataFrame and column names.
    """
    required_cols = {campaign_col, start_col, end_col}
    missing_cols = required_cols.difference(data.columns)
    if missing_cols:
        missing = ", ".join(sorted(missing_cols))
        raise ValueError(f"Missing required columns: {missing}")

    plot_df = data.copy()
    plot_df[start_col] = pd.to_datetime(plot_df[start_col])
    plot_df[end_col] = pd.to_datetime(plot_df[end_col])

    invalid_range_mask = plot_df[end_col] < plot_df[start_col]
    if invalid_range_mask.any():
        bad_row = plot_df.loc[invalid_range_mask].iloc[0].to_dict()
        raise ValueError(
            "Found a campaign where end date is earlier than start date: "
            f"{bad_row}"
        )

    campaign_order = list(pd.unique(plot_df[campaign_col]))
    y_map = {name: idx for idx, name in enumerate(campaign_order)}
    plot_df["_y"] = plot_df[campaign_col].map(y_map)

    if hue_col in plot_df.columns:
        color_map = _build_color_map(plot_df[hue_col], palette)
        plot_df["_color"] = plot_df[hue_col].map(color_map)
    else:
        default_color = (palette or {}).get("default", "C0")
        plot_df["_color"] = default_color
        color_map = {"default": default_color}

    if ax is None:
        fig_height = max(3.0, 1.6 + len(campaign_order) * row_height)
        _, ax = plt.subplots(figsize=(15, fig_height))

    for _, row in plot_df.iterrows():
        ax.hlines(
            y=row["_y"],
            xmin=row[start_col],
            xmax=row[end_col],
            colors=row["_color"],
            linewidth=linewidth,
            alpha=0.95,
            zorder=3,
        )

    min_start = plot_df[start_col].min()
    max_end = plot_df[end_col].max()

    ax.set_yticks(list(range(len(campaign_order))))
    ax.set_yticklabels(campaign_order)
    ax.set_ylim(-0.8, len(campaign_order) - 0.2)

    ax.set_xlim(min_start - pd.Timedelta(days=0.5), max_end + pd.Timedelta(days=0.5))
    ax.grid(axis="x", linestyle=":", linewidth=0.8, alpha=0.6)
    ax.tick_params(axis="x", rotation=70)

    ax.set_xlabel("Date")
    ax.set_ylabel("Campaign")
    if title:
        ax.set_title(title)

    plotted_holiday_dates: list[pd.Timestamp] = []
    if show_holidays:
        if holiday_years is None:
            holiday_years = list(range(min_start.year, max_end.year + 1))
        plotted_holiday_dates = [
            pd.Timestamp(d) for d in add_vietnam_holidays(
            ax,
            years=holiday_years,
            start_date=min_start,
            end_date=max_end,
            custom_holidays=custom_holidays,
            text=holiday_text,
            )
        ]

    if x_tick_daily:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    else:
        key_dates: set[pd.Timestamp] = {
            *plot_df[start_col].dt.normalize().tolist(),
            *plot_df[end_col].dt.normalize().tolist(),
            *(d.normalize() for d in plotted_holiday_dates),
        }
        sorted_key_dates = sorted(key_dates)
        if sorted_key_dates:
            ax.xaxis.set_major_locator(FixedLocator(mdates.date2num(sorted_key_dates)))

    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))

    if legend and hue_col in plot_df.columns:
        legend_handles = []
        for label, color in color_map.items():
            legend_handles.append(Line2D([0], [0], color=color, lw=linewidth / 1.5, label=str(label)))
        ax.legend(handles=legend_handles, title=hue_col, loc="upper left", bbox_to_anchor=(1.01, 1.0))

    ax.figure.tight_layout()
    return ax


def save_png(ax: Axes, path: str, *, dpi: int = 300) -> None:
    """Save an axis figure to PNG."""
    ax.figure.savefig(path, dpi=dpi, bbox_inches="tight")
