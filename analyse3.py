import pandas as pd
import matplotlib.pyplot as plt

attribution_df = pd.read_csv("results/matrices/attribution_by_channel.csv", index_col=0)
attribution_df.reset_index(inplace=True)
attribution_df.rename(columns={"index": "channel"}, inplace=True)
attribution_df["channel"] = attribution_df["channel"].str.strip()

tv_df = pd.read_csv("data/tv_publisher.csv")
tv_df["cost_usd"] = tv_df["cost_milli_cent"] / 100000
tv_cost = tv_df["cost_usd"].sum()

prog_df = pd.read_csv("data/programmatic_publisher.csv")
prog_df["cost_usd"] = prog_df["cost_milli_cent"] / 100000

contextual_cost = prog_df[prog_df["campaign_name"].str.contains("context", case=False, na=False)]["cost_usd"].sum()
retargeting_cost = prog_df[prog_df["campaign_name"].str.contains("retarget", case=False, na=False)]["cost_usd"].sum()

costs_df = pd.DataFrame({
    "channel": ["TV", "Prog_Contextual", "Prog_Retargeting"],
    "cost_usd": [tv_cost, contextual_cost, retargeting_cost]
})

merged_df = attribution_df.merge(costs_df, on="channel", how="left")

merged_df["cost_per_conversion"] = merged_df["cost_usd"] / merged_df["conversions_attribuees"].abs()
revenue_per_conversion = 20  # Prix moyen 55$, cout de revient 20$, frais Amazon 15$ donc revenu estimé de 20$ par conversion
merged_df["roi"] = ((merged_df["conversions_attribuees"] * revenue_per_conversion) - merged_df["cost_usd"]) / merged_df["cost_usd"]

merged_df.to_csv("results/matrices/roi_by_channel.csv", index=False)

plt.figure(figsize=(10, 6))
bars = plt.bar(merged_df["channel"], merged_df["roi"], color=["green" if r > 0 else "red" for r in merged_df["roi"]])
plt.title("ROI par canal marketing (en $)")
plt.ylabel("ROI (Return on Investment)")
plt.axhline(0, color='black', linestyle='--', linewidth=1)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2,
             yval + 0.02 if yval > 0 else yval - 0.05,
             f"{yval:.2f}",
             ha='center', va='bottom' if yval > 0 else 'top', fontsize=10)

plt.tight_layout()
plt.savefig("results/figures/roi_by_channel.png", dpi=300)
plt.show()
