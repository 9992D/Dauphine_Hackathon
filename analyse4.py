import pandas as pd
import matplotlib.pyplot as plt

# === 1. Charger attribution proprement ===
attribution = pd.read_csv("results/matrices/attribution_by_channel.csv", index_col=False)

if 'channel' not in attribution.columns:
    attribution.rename(columns={attribution.columns[0]: 'channel'}, inplace=True)
attribution['channel'] = attribution['channel'].astype(str).str.strip()
attribution['channel'] = attribution['channel'].replace({
    'Contextual': 'Prog_Contextual',
    'Retargeting': 'Prog_Retargeting'
})

conversions = attribution[['channel', 'conversions_attribuees']].copy()
conversions.columns = ['Channel', 'Conversions']

# === 2. Charger les coûts ===
tv = pd.read_csv("data/TV_PUBLISHER.csv")
prog = pd.read_csv("data/PROGRAMMATIC_PUBLISHER.csv")
tv_cost = tv['cost_milli_cent'].sum() / 100000
prog['channel'] = prog['campaign_name'].str.extract(r'(Contextual|Retargeting)', expand=False)
cost_prog = prog.groupby('channel')['cost_milli_cent'].sum().to_dict()
ctx_cost = cost_prog.get('Contextual', 0) / 100000
ret_cost = cost_prog.get('Retargeting', 0) / 100000

costs = pd.DataFrame({
    'Channel': ['TV', 'Prog_Contextual', 'Prog_Retargeting'],
    'Cost': [tv_cost, ctx_cost, ret_cost]
})

# === 3. Fusion données ===
conversions['Channel'] = conversions['Channel'].astype(str).str.strip()
costs['Channel'] = costs['Channel'].astype(str).str.strip()
df = pd.merge(conversions, costs, on='Channel', how='inner')
df['Revenue'] = df['Conversions'] * 20
df['ROI_$'] = df['Revenue'] - df['Cost']

# === 4. Scénarios
scenarios = {
    "Scenario 1": {"TV": 1.0, "Prog_Contextual": 1.2, "Prog_Retargeting": 0.5},
    "Scenario 2": {"TV": 1.0, "Prog_Contextual": 1.25, "Prog_Retargeting": 0.5},
    "Scenario 3": {"TV": 1.167, "Prog_Contextual": 1.0, "Prog_Retargeting": 0.5},
    "Scenario 4": {"TV": 1.083, "Prog_Contextual": 1.125, "Prog_Retargeting": 0.5},
    "Scenario 5": {"TV": 0.933, "Prog_Contextual": 1.2, "Prog_Retargeting": 0.8},
    "Scenario 6": {"TV": 1.0, "Prog_Contextual": 1.5, "Prog_Retargeting": 0.0},
    "Scenario 7": {"TV": 0.0, "Prog_Contextual": 2.0, "Prog_Retargeting": 0.1}
}

# === 5. Simulation
results = []
for name, mult in scenarios.items():
    total_cost = total_revenue = total_conversions = 0
    for _, row in df.iterrows():
        chan = row["Channel"]
        if chan not in mult:
            continue
        factor = mult[chan]
        new_cost = row["Cost"] * factor
        new_conv = row["Conversions"] * factor
        new_revenue = new_conv * 20
        total_cost += new_cost
        total_conversions += new_conv
        total_revenue += new_revenue
    roi_global = total_revenue - total_cost
    results.append({
        "Scenario": name,
        "ROI Global ($)": round(roi_global, 2)
    })

results_df = pd.DataFrame(results)

# === 6. Graphique
plt.figure(figsize=(10, 6))
bars = plt.bar(results_df["Scenario"], results_df["ROI Global ($)"], color='mediumseagreen')
plt.axhline(y=0, color='gray', linestyle='--')
plt.title("ROI global estimé par scénario de réallocation budgétaire", fontsize=14)
plt.ylabel("ROI ($)")
plt.xticks(rotation=45)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1000000, f"{int(yval):,}", ha='center', fontsize=9)

plt.tight_layout()
plt.savefig("results/figures/roi_scenarios_clean.png")
plt.show()