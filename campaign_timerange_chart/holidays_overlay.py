from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

import holidays
import matplotlib.dates as mdates
from matplotlib.axes import Axes


DateLike = date | datetime


def add_vietnam_holidays(
    ax: Axes,
    *,
    years: Iterable[int],
    start_date: DateLike | None = None,
    end_date: DateLike | None = None,
    linestyle: str = "--",
    color: str = "0.5",
    linewidth: float = 1.0,
    alpha: float = 0.9,
    text: bool = True,
    text_rotation: int = 90,
    text_size: int = 8,
) -> list[date]:
    """Overlay Vietnam public holidays as vertical dashed lines on an axis.

    Returns the list of holiday dates that were plotted.
    """
    years = list(years)
    if not years:
        return []

    if start_date is None or end_date is None:
        x_min, x_max = ax.get_xlim()
        x_start = mdates.num2date(x_min).date()
        x_end = mdates.num2date(x_max).date()
    else:
        x_start = start_date.date() if isinstance(start_date, datetime) else start_date
        x_end = end_date.date() if isinstance(end_date, datetime) else end_date

    if x_end < x_start:
        x_start, x_end = x_end, x_start

    vn_holidays = holidays.Vietnam(years=years)

    plotted_dates: list[date] = []
    y_min, y_max = ax.get_ylim()
    y_span = max(y_max - y_min, 1.0)
    label_y = y_max + y_span * 0.02

    for holiday_date, name in sorted(vn_holidays.items()):
        if holiday_date < x_start or holiday_date > x_end:
            continue

        ax.axvline(
            holiday_date,
            linestyle=linestyle,
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            zorder=1,
        )
        plotted_dates.append(holiday_date)

        if text:
            ax.text(
                holiday_date,
                label_y,
                str(name),
                rotation=text_rotation,
                va="bottom",
                ha="center",
                fontsize=text_size,
                color=color,
                clip_on=False,
            )

    if text and plotted_dates:
        ax.set_ylim(y_min, y_max + y_span * 0.18)

    return plotted_dates
