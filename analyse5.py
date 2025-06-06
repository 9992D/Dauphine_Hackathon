import pandas as pd
from ast import literal_eval
import matplotlib.pyplot as plt

# === 1. Charger le fichier trié
df = pd.read_csv("data/processed/merged_sorted.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(by=["customer_id", "timestamp"])

# === 2. Construire les parcours clients
journeys = df.groupby("customer_id")["state"].apply(list).reset_index(name="journey")

# === 3. Filtrer ceux qui incluent du retargeting
journeys_retarget = journeys[journeys["journey"].apply(lambda x: "Prog_Retargeting" in x)]

# === 4. Compter les parcours les plus fréquents avec retargeting
journey_counts = journeys_retarget["journey"].apply(str).value_counts().head(10).reset_index()
journey_counts.columns = ["journey_sequence", "count"]
journey_counts["journey_sequence"] = journey_counts["journey_sequence"].apply(literal_eval)

# === 5. Créer un graphique horizontal
plt.figure(figsize=(10, 6))
labels = [' → '.join(seq) for seq in journey_counts['journey_sequence']]
counts = journey_counts['count']

bars = plt.barh(range(len(labels)), counts, color='lightcoral')
plt.yticks(range(len(labels)), labels, fontsize=9)
plt.xlabel("Nombre de clients", fontsize=11)
plt.title("Top 10 des parcours contenant du Retargeting", fontsize=13)
plt.gca().invert_yaxis()

# Annoter les barres avec les valeurs
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 1000, bar.get_y() + bar.get_height()/2, f"{counts[i]:,}", va='center', fontsize=9)

plt.tight_layout()
plt.savefig("results/figures/top10_retargeting_journeys.png")
plt.show()