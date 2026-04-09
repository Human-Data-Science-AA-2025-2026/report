"""
generate_charts.py
Genera i 5 grafici per il paper "The Invisible Exodus"
Input:  migration_gap.csv  (DESTINATION_STATE, YEAR, ISTAT_DELETED, DEST_REGISTERED)
Output: figures/fig1_trend.pdf ... fig5_boxplot.pdf
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
from pathlib import Path

# Config

Path("figures").mkdir(exist_ok=True)

PALETTE = "#2e4057"  # blu scuro per elementi principali
ACCENT = "#e63946"  # rosso per evidenziare il gap
GREY = "#adb5bd"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
})

df = pd.read_csv("../data/migration_gap.csv")
df.columns = df.columns.str.strip()

df["GAP"] = df["DEST_REGISTERED"] - df["ISTAT_DELETED"]
df["GAP_PCT"] = df["GAP"] / df["DEST_REGISTERED"] * 100

COUNTRY_NAMES = {
    "AT": "Austria",
    "DE": "Germany",
    "DK": "Denmark",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "NO": "Norway",
    "SE": "Sweden",
}

# Nomi leggibili per i paesi
df["COUNTRY"] = df["DESTINATION_STATE"].map(COUNTRY_NAMES).fillna(df["DESTINATION_STATE"])

# Fig 1 Trend
def figure_1():
    annual = df.groupby("YEAR")[["ISTAT_DELETED", "DEST_REGISTERED"]].sum().reset_index()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xticks(np.arange(min(annual["YEAR"]), max(annual["YEAR"]) + 1))
    ax.plot(annual["YEAR"], annual["DEST_REGISTERED"],
            color=PALETTE, lw=2.2, marker="o", ms=10, label="Destination countries (Eurostat)")
    ax.plot(annual["YEAR"], annual["ISTAT_DELETED"],
            color=ACCENT, lw=2.2, marker="s", ms=10, linestyle="--", label="ISTAT / AIRE")
    ax.fill_between(annual["YEAR"], annual["ISTAT_DELETED"], annual["DEST_REGISTERED"],
                    alpha=0.12, color=ACCENT, label="Gap area")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Year")
    ax.set_ylabel("Emigration flows (total)")
    ax.set_title("Figure 1: Aggregate emigration flows: ISTAT vs destination countries", pad=12)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig("figures/fig1_trend.pdf")
    fig.savefig("figures/fig1_trend.png")
    plt.close()
    print("Fig 1 saved")

# Fig 2 - Gap by country
def figure_2():
    by_country = (df.groupby("COUNTRY")
                  .agg(GAP_PCT_MEAN=("GAP_PCT", "mean"),
                       GAP_MEAN=("GAP", "mean"))
                  .reset_index()
                  .sort_values("GAP_PCT_MEAN", ascending=True))

    fig, ax = plt.subplots(figsize=(7, 0.6 * len(by_country) + 1.5))
    bars = ax.barh(by_country["COUNTRY"], by_country["GAP_PCT_MEAN"],
                   color=PALETTE, edgecolor="white", linewidth=0.4)

    for bar, val in zip(bars, by_country["GAP_PCT_MEAN"]):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9.5, color=PALETTE)

    ax.axvline(0, color=GREY, lw=0.8)
    ax.set_xlabel("Average gap (%): (Eurostat − ISTAT) / Eurostat")
    ax.set_title("Figure 2: Mean undercount rate by destination country", pad=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    fig.tight_layout()
    fig.savefig("figures/fig2_gap_by_country.pdf")
    fig.savefig("figures/fig2_gap_by_country.png")
    plt.close()
    print("Fig 2 saved")

# Fig 3 - Heatmap
def figure_3():
    pivot = df.pivot_table(index="COUNTRY", columns="YEAR",
                           values="GAP_PCT", aggfunc="mean")
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(max(8, len(pivot.columns) * 0.8), len(pivot) * 0.65 + 1.5))
    sns.heatmap(pivot, ax=ax,
                cmap="YlOrRd", annot=True, fmt=".0f",
                linewidths=0.4, linecolor="#eeeeee",
                cbar_kws={"label": "Gap (%)", "shrink": 0.7},
                annot_kws={"size": 9})

    ax.set_xlabel("Year")
    ax.set_ylabel("")
    ax.set_title("Figure 3: Undercount rate (%) by country and year", pad=12)
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()
    fig.savefig("figures/fig3_heatmap.pdf")
    fig.savefig("figures/fig3_heatmap.png")
    plt.close()
    print("Fig 3 saved")

# Fig 4 - Tabella riepilogativa
def figure_4():
    stats = (df.groupby("COUNTRY")
             .agg(
        Years=("YEAR", "count"),
        ISTAT_total=("ISTAT_DELETED", "sum"),
        DEST_total=("DEST_REGISTERED", "sum"),
        Gap_mean=("GAP", "mean"),
        Gap_pct_mean=("GAP_PCT", "mean"),
        Gap_pct_std=("GAP_PCT", "std"),
    )
             .reset_index()
             .sort_values("Gap_pct_mean", ascending=False))

    stats_display = stats.copy()
    stats_display["ISTAT_total"] = stats_display["ISTAT_total"].map(lambda x: f"{int(x):,}")
    stats_display["DEST_total"] = stats_display["DEST_total"].map(lambda x: f"{int(x):,}")
    stats_display["Gap_mean"] = stats_display["Gap_mean"].map(lambda x: f"{int(x):,}")
    stats_display["Gap_pct_mean"] = stats_display["Gap_pct_mean"].map(lambda x: f"{x:.1f}%")
    stats_display["Gap_pct_std"] = stats_display["Gap_pct_std"].map(lambda x: f"{x:.1f}%")
    stats_display = stats_display.rename(columns={
        "COUNTRY": "Country",
        "Years": "N years",
        "ISTAT_total": "ISTAT total",
        "DEST_total": "Dest. total",
        "Gap_mean": "Avg gap",
        "Gap_pct_mean": "Gap % (mean)",
        "Gap_pct_std": "Gap % (std)",
    })

    fig, ax = plt.subplots(figsize=(11, 0.45 * len(stats_display) + 1.8))
    ax.axis("off")
    tbl = ax.table(
        cellText=stats_display.values,
        colLabels=stats_display.columns,
        cellLoc="center", loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    tbl.scale(1, 1.55)

    # Header styling
    for j in range(len(stats_display.columns)):
        tbl[0, j].set_facecolor(PALETTE)
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    # Alternating rows
    for i in range(1, len(stats_display) + 1):
        color = "#f0f0f8" if i % 2 == 0 else "white"
        for j in range(len(stats_display.columns)):
            tbl[i, j].set_facecolor(color)

    ax.set_title("Table 1: Summary statistics by destination country",
                 pad=14, fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig("figures/fig4_table.pdf")
    fig.savefig("figures/fig4_table.png")
    plt.close()
    print("Fig 4 saved")

# Fig 5 - Boxplot
def figure_5():
    order = (df.groupby("COUNTRY")["GAP_PCT"]
             .median()
             .sort_values(ascending=False)
             .index.tolist())

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bp = ax.boxplot(
        [df[df["COUNTRY"] == c]["GAP_PCT"].values for c in order],
        tick_labels=order,
        patch_artist=True,
        medianprops=dict(color=ACCENT, linewidth=2),
        boxprops=dict(facecolor="#dce8f5", linewidth=1.2),
        whiskerprops=dict(linewidth=1),
        capprops=dict(linewidth=1),
        flierprops=dict(marker="o", markerfacecolor=GREY, markersize=4, linestyle="none"),
    )

    ax.axhline(0, color=GREY, lw=0.8, linestyle="--")
    ax.set_ylabel("Gap (%): per country-year observation")
    ax.set_xlabel("Country")
    ax.set_title("Figure 5: Distribution of undercount rate per country", pad=12)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig("figures/fig5_boxplot.pdf")
    fig.savefig("figures/fig5_boxplot.png")
    plt.close()
    print("Fig 5 saved")

figure_1()
figure_2()
figure_3()
figure_4()
figure_5()

print("\nDone. Files in ./figures/")
