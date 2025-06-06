import pandas as pd
from collections import Counter
import plotly.graph_objects as go

# 1. Charger le fichier trié des parcours
df = pd.read_csv("data/processed/merged_sorted.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(by=["customer_id", "timestamp"])

# 2. Regrouper les états en séquences par client
journeys = df.groupby("customer_id")["state"].apply(list).reset_index(name="journey")

# 3. Identifier la présence de retargeting et la sortie finale
journeys["with_retargeting"] = journeys["journey"].apply(lambda x: "Prog_Retargeting" in x)
journeys["group"] = journeys["with_retargeting"].apply(lambda x: "Avec Retargeting" if x else "Sans Retargeting")
journeys["result"] = journeys["journey"].apply(lambda x: x[-1] if x[-1] in ["Conversion", "No_Conversion"] else "Autre")

# 4. Compter les flux par catégorie
counts = journeys.groupby(["group", "result"]).size().reset_index(name="count")

# 5. Créer le diagramme Sankey
labels = ["Avec Retargeting", "Sans Retargeting", "Conversion", "No_Conversion", "Autre"]
source_map = {"Avec Retargeting": 0, "Sans Retargeting": 1}
target_map = {"Conversion": 2, "No_Conversion": 3, "Autre": 4}

sources = counts["group"].map(source_map)
targets = counts["result"].map(target_map)
values = counts["count"]

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values
    ))])

fig.update_layout(title_text="Flux Retargeting → Conversion / No Conversion", font_size=12)
fig.show()