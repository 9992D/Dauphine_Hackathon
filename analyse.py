import pandas as pd
from collections import defaultdict

df = pd.read_csv("data/processed/merged_sorted.csv")

journeys = defaultdict(list)
for row in df.itertuples():
    journeys[row.customer_id].append(row.state)

with_retargeting = [seq for seq in journeys.values() if "Prog_Retargeting" in seq]
without_retargeting = [seq for seq in journeys.values() if "Prog_Retargeting" not in seq]

def conversion_rate(sequences):
    total = len(sequences)
    converted = sum("Conversion" in seq for seq in sequences)
    return converted / total if total else 0.0

rate_with = conversion_rate(with_retargeting)
rate_without = conversion_rate(without_retargeting)

print(f"Taux de conversion avec Prog_Retargeting : {rate_with:.2%}")
print(f"Taux de conversion sans Prog_Retargeting : {rate_without:.2%}")

def remove_channel(sequences, channel):
    return [[s for s in seq if s != channel] for seq in sequences]

simulated_journeys = remove_channel(with_retargeting, "Prog_Retargeting")
simulated_rate = conversion_rate(simulated_journeys)

print(f"Taux de conversion simulé après suppression de Prog_Retargeting : {simulated_rate:.2%}")
