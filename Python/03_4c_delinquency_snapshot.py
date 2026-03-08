import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

pd.set_option("display.max_columns", 200)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 2000)

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "..", "Data_Generated")

ds_filename = "03_4c6_bucketed_delinquency_snapshot_table.csv"
ds_path_local = os.path.join(data_dir, ds_filename)

df_ds = pd.read_csv(ds_path_local)

# -----------------------------
# 03_4c6_bucketed_delinquency_snapshot_table
# 5 separate bar charts in ONE PNG
# fixed Y-axis for every subplot: 0% to 100%
# -----------------------------

df_ds["vintage_month"] = pd.to_datetime(df_ds["vintage_month"])
df_ds["mob12_dpd_bucket"] = df_ds["mob12_dpd_bucket"].astype("string")

lst_bucket_order_bottom_to_top = [
    "00_current",
    "01_1_29",
    "02_30_59",
    "03_60_89",
    "04_90_plus"
]

df_counts = (
    df_ds
    .groupby(["vintage_month", "mob12_dpd_bucket"], dropna=False)["loan_id"]
    .count()
    .reset_index(name="n_loans")
)

df_totals = (
    df_ds
    .groupby(["vintage_month"], dropna=False)["loan_id"]
    .count()
    .reset_index(name="n_total")
)

df_counts = df_counts.merge(df_totals, on="vintage_month", how="left")
df_counts["pct"] = np.where(
    df_counts["n_total"] > 0,
    df_counts["n_loans"] / df_counts["n_total"],
    0.0
)

df_vintages = pd.DataFrame({
    "vintage_month": sorted(df_ds["vintage_month"].dropna().unique())
})

df_buckets = pd.DataFrame({
    "mob12_dpd_bucket": lst_bucket_order_bottom_to_top
})

df_grid = (
    df_vintages.assign(_k=1)
    .merge(df_buckets.assign(_k=1), on="_k")
    .drop(columns="_k")
)

df_plot = (
    df_grid
    .merge(df_counts, on=["vintage_month", "mob12_dpd_bucket"], how="left")
    .fillna({"n_loans": 0, "n_total": 0, "pct": 0.0})
    .sort_values(["mob12_dpd_bucket", "vintage_month"])
)

dict_bucket_color = {
    "00_current": "#1f77b4",
    "01_1_29": "#ff7f0e",
    "02_30_59": "#2ca02c",
    "03_60_89": "#d62728",
    "04_90_plus": "#9467bd",
}

fig, axes = plt.subplots(
    nrows=5,
    ncols=1,
    figsize=(16, 14),
    sharex=True,
    sharey=True
)

lst_bucket_order_top_to_bottom = list(reversed(lst_bucket_order_bottom_to_top))

srs_labels = df_vintages["vintage_month"].dt.strftime("%Y-%m")
arr_x = np.arange(len(srs_labels))

for ax, str_bucket in zip(axes, lst_bucket_order_top_to_bottom):
    df_b = (
        df_plot[df_plot["mob12_dpd_bucket"] == str_bucket]
        .sort_values("vintage_month")
    )

    srs_pct = df_b["pct"].astype(float)
    srs_cnt = df_b["n_loans"].astype(int)

    ax.bar(arr_x, srs_pct, color=dict_bucket_color[str_bucket])

    ax.set_ylabel("Share")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.grid(axis="y", linestyle=":", linewidth=0.6)

    # force same scale on every subplot
    ax.set_ylim(0, 1)
    ax.set_yticks([0.00, 0.25, 0.50, 0.75, 1.00])

    ax.text(
        0.5,
        0.93,
        str_bucket,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=12,
        fontweight="bold"
    )

    for i, (cnt, pct) in enumerate(zip(srs_cnt.to_numpy(), srs_pct.to_numpy())):
        y_text = min(pct + 0.01, 0.98)
        ax.text(
            i,
            y_text,
            f"{cnt}\n{pct:.0%}",
            ha="center",
            va="bottom",
            fontsize=8
        )

axes[-1].set_xticks(arr_x)
axes[-1].set_xticklabels(list(srs_labels), rotation=45, ha="right")
axes[-1].set_xlabel("Vintage month")

fig.suptitle("Cica PRIME Delinquency Buckets for 2023-2024 Vintage", fontsize=16, y=0.995)

plt.tight_layout(rect=[0, 0, 1, 0.97])

out_filename = "03_4c6_bucketed_delinquency_5_bar_charts_mob12.png"
out_path = os.path.join(script_dir, out_filename)

plt.savefig(out_path, dpi=200, bbox_inches="tight")
plt.show()

print(out_path)