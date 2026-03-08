import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import Patch

pd.set_option("display.max_columns", 200)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 2000)

script_dir      = os.path.dirname(os.path.abspath(__file__))
data_dir        = os.path.join(script_dir, "..", "Data_Generated")

ds_filename     = "03_5_decision_score_effectiveness.csv"
ds_path_local   = os.path.join(data_dir, ds_filename)

df_ds           = pd.read_csv(ds_path_local)


# -----------------------------
# 03_5_decision_score_effectiveness
# bar chart: 12-month default rate by score band
# -----------------------------

df_plot = df_ds.loc[:, [
    "score_band",
    "loan_count",
    "defaults_12m_count",
    "default_rate_12m",
    "score_band_rank"
]].copy()

df_plot["loan_count"] = pd.to_numeric(df_plot["loan_count"], errors="coerce")
df_plot["defaults_12m_count"] = pd.to_numeric(df_plot["defaults_12m_count"], errors="coerce")
df_plot["default_rate_12m"] = pd.to_numeric(df_plot["default_rate_12m"], errors="coerce")
df_plot["score_band_rank"] = pd.to_numeric(df_plot["score_band_rank"], errors="coerce")

df_plot = df_plot.sort_values("score_band_rank").reset_index(drop=True)


title_fontsize  = 36
label_fontsize  = 24
tick_fontsize   = 24
pct_fontsize    = 20
inside_fontsize = 18
legend_fontsize = 16

fig, ax = plt.subplots(figsize=(14, 8))

bars = ax.bar(
    df_plot["score_band"],
    df_plot["default_rate_12m"]
)

ax.set_title(
    "CicaPRIME - Decision Score Effectiveness - 2023-2024",
    fontsize=title_fontsize,
    fontweight="bold",
    pad=20
)

ax.set_xlabel("")
ax.set_ylabel("Default Rate (12M)", fontsize=label_fontsize)

ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=1))
ax.tick_params(axis="x", labelsize=tick_fontsize)
ax.tick_params(axis="y", labelsize=tick_fontsize)

ax.set_ylim(0, 0.20)


for idx, bar in enumerate(bars):

    flt_height      = bar.get_height()
    int_loan_count  = int(df_plot.loc[idx, "loan_count"])
    int_defaults    = int(df_plot.loc[idx, "defaults_12m_count"])

    # percentage above bar
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        flt_height + 0.005,
        f"{flt_height:.2%}",
        ha="center",
        va="bottom",
        fontsize=pct_fontsize,
        fontweight="bold"
    )

    # d and n inside bar
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        flt_height * 0.55,
        f"d = {int_defaults:,}\nn = {int_loan_count:,}",
        ha="center",
        va="center",
        fontsize=inside_fontsize,
        color="white",
        fontweight="bold"
    )

ax.grid(axis="y", linestyle="--", alpha=0.4)


legend_patch = Patch(
    facecolor="none",
    edgecolor="none",
    label="d = defaults within 12 months\nn = loan count\n\nDefault Rate = d / n"
)

ax.legend(
    handles=[legend_patch],
    loc="upper right",
    fontsize=legend_fontsize,
    frameon=True
)

plt.tight_layout()
plt.show()