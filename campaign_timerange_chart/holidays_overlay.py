from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Mapping

import holidays
import matplotlib.dates as mdates
from matplotlib.axes import Axes


DateLike = date | datetime


def _as_date(value: DateLike) -> date:
    return value.date() if isinstance(value, datetime) else value


def _collect_custom_holidays(
    custom_holidays: Mapping[DateLike, str] | Iterable[tuple[DateLike, str]] | None,
) -> dict[date, str]:
    if not custom_holidays:
        return {}

    items = custom_holidays.items() if isinstance(custom_holidays, Mapping) else custom_holidays
    parsed: dict[date, str] = {}
    for holiday_date, label in items:
        normalized_date = _as_date(holiday_date)
        parsed[normalized_date] = str(label)
    return parsed


def _estimate_label_span_days(label: str, total_days: int) -> float:
    # Approximate horizontal space occupied by a label in date units.
    base = max(1.0, len(label) * max(total_days / 140.0, 0.18))
    return min(base, max(2.0, total_days * 0.35))


def add_vietnam_holidays(
    ax: Axes,
    *,
    years: Iterable[int],
    start_date: DateLike | None = None,
    end_date: DateLike | None = None,
    custom_holidays: Mapping[DateLike, str] | Iterable[tuple[DateLike, str]] | None = None,
    linestyle: str = "--",
    color: str = "0.5",
    linewidth: float = 1.0,
    alpha: float = 0.9,
    text: bool = True,
    text_rotation: int = 0,
    text_size: int = 8,
) -> list[date]:
    """Overlay Vietnam and custom holidays as vertical dashed lines on an axis.

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
        x_start = _as_date(start_date)
        x_end = _as_date(end_date)

    if x_end < x_start:
        x_start, x_end = x_end, x_start

    vn_holidays = holidays.Vietnam(years=years)
    all_holidays: dict[date, str] = {
        holiday_date: str(name) for holiday_date, name in vn_holidays.items()
    }
    all_holidays.update(_collect_custom_holidays(custom_holidays))

    plotted_dates: list[date] = []
    y_min, y_max = ax.get_ylim()
    y_span = max(y_max - y_min, 1.0)
    label_base_y = y_max + y_span * 0.02
    label_step = y_span * 0.1
    total_days = max((x_end - x_start).days + 1, 1)
    level_last_end: list[float] = []
    max_level_used = 0

    for holiday_date, name in sorted(all_holidays.items()):
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
            holiday_num = mdates.date2num(holiday_date)
            label_span_days = _estimate_label_span_days(str(name), total_days)

            assigned_level = 0
            for level, last_end in enumerate(level_last_end):
                if holiday_num >= last_end:
                    assigned_level = level
                    break
            else:
                assigned_level = len(level_last_end)
                level_last_end.append(float("-inf"))

            level_last_end[assigned_level] = holiday_num + label_span_days
            max_level_used = max(max_level_used, assigned_level)

            ax.text(
                holiday_date,
                label_base_y + assigned_level * label_step,
                str(name),
                rotation=text_rotation,
                va="bottom",
                ha="left",
                fontsize=text_size,
                color=color,
                clip_on=False,
            )

    if text and plotted_dates:
        ax.set_ylim(y_min, y_max + y_span * (0.18 + max_level_used * 0.09))

    return plotted_dates
