# Campaign Time-Range Chart

A small plotting module to visualize campaign durations on a date axis, with Vietnam holidays overlaid as dashed vertical lines and labels.

## Features

- X-axis: dates (daily ticks)
- Y-axis: campaign names
- Horizontal segment per campaign from start date to end date
- Color mapping by category (for example status)
- Vietnam holidays overlay using `holidays` package
- Compact x-ticks mode (only campaign start/end dates and holiday dates)
- Custom holidays overlay support
- Works with matplotlib subplots by passing `ax`
- Export chart as PNG

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import pandas as pd
import matplotlib.pyplot as plt
import campaign_timerange_chart as ctc

# Sample data
df = pd.DataFrame([
    {"campaign": "Camp_A", "start_date": "2026-01-01", "end_date": "2026-01-15", "status": "success"},
    {"campaign": "Camp_B", "start_date": "2026-01-05", "end_date": "2026-01-22", "status": "expired"},
])

ax = ctc.campaign_timerangeplot(
    df,
    campaign_col="campaign",
    start_col="start_date",
    end_col="end_date",
    hue_col="status",
    palette={"success": "green", "expired": "orange"},
    show_holidays=True,
    custom_holidays={
        pd.Timestamp("2026-01-10"): "Flash Sale",
        pd.Timestamp("2026-01-20"): "Brand Day",
    },
    x_tick_daily=False,
)

ctc.save_png(ax, "timeline.png", dpi=300)
```

## Subplot Integration

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

ctc.campaign_timerangeplot(df_a, ax=axes[0], title="Region A")
ctc.campaign_timerangeplot(df_b, ax=axes[1], title="Region B")

fig.tight_layout()
fig.savefig("multi_panel.png", dpi=300)
```

## Example Script

Run:

```bash
python examples/basic.py
```

This writes `out.png` in the project root.
