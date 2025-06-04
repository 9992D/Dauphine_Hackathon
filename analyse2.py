import pandas as pd
from collections import defaultdict
from src import transition_counter, markov_model, attribution, data_loading, visualization
from src.config import MATRICES_DIR, FIGURES_DIR

df = pd.read_csv("data/processed/merged_sorted.csv") 

journeys = defaultdict(list)
for row in df.itertuples():
    if row.state != "Prog_Retargeting":
        journeys[row.customer_id].append(row.state)

transition_counts = defaultdict(int)
states_set = set(["Start", "Conversion", "No_Conversion"])

for path in journeys.values():
    prev = "Start"
    for state in path:
        transition_counts[(prev, state)] += 1
        states_set.update([prev, state])
        prev = state
    if prev not in ["Conversion", "No_Conversion"]:
        transition_counts[(prev, "No_Conversion")] += 1

trans_matrix = transition_counter.build_transition_matrix(transition_counts, states_set)
trans_matrix.to_csv(MATRICES_DIR / "transition_matrix_no_retargeting.csv")

base_rate = markov_model.compute_conversion_rate(trans_matrix)
print(f"Taux de conversion sans Prog_Retargeting : {base_rate:.4f}")

removal_effects = markov_model.compute_all_removal_effects(trans_matrix, base_rate)
df_ret = data_loading.load_retailer_events()
total_conversions = df_ret['customer_id'].nunique()
attribution_df = attribution.compute_channel_attribution(removal_effects, total_conversions)
attribution_df.to_csv(MATRICES_DIR / "attribution_no_retargeting.csv")

visualization.plot_transition_matrix(trans_matrix, output='transition_matrix_no_retargeting.png')
visualization.plot_channel_attribution(attribution_df, output='attribution_no_retargeting.png')
