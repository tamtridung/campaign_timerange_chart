from __future__ import annotations

import pandas as pd

import campaign_timerange_chart as ctc


def main() -> None:
    df = pd.DataFrame(
        [
            {
                "campaign": "Camp_A",
                "start_date": "2026-01-01",
                "end_date": "2026-01-15",
                "status": "success",
            },
            {
                "campaign": "Camp_B",
                "start_date": "2026-01-05",
                "end_date": "2026-01-22",
                "status": "expired",
            },
            {
                "campaign": "Camp_C",
                "start_date": "2026-01-12",
                "end_date": "2026-01-27",
                "status": "success",
            },
        ]
    )

    ax = ctc.campaign_timerangeplot(
        df,
        campaign_col="campaign",
        start_col="start_date",
        end_col="end_date",
        hue_col="status",
        palette={"success": "#2e8b57", "expired": "#f28e2b"},
        title="Campaign timeline with Vietnam holidays",
    )

    ctc.save_png(ax, "out.png", dpi=200)


if __name__ == "__main__":
    main()
