import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("results/matrices/transition_matrix.csv", index_col=0)

G = nx.DiGraph()
threshold = 0.01

for src in df.index:
    for dst in df.columns:
        weight = df.loc[src, dst]
        if weight > threshold:
            G.add_edge(src, dst, weight=weight)

pos = {
    "Start": (-2, 0),
    "Prog_Contextual": (0, 2),
    "Prog_Retargeting": (0, 0),
    "TV": (0, -2),
    "Conversion": (2, 1),
    "No_Conversion": (2, -1),
}

node_colors = {
    "Start": "#AED6F1",
    "Prog_Contextual": "#F9E79F",
    "Prog_Retargeting": "#F9E79F",
    "TV": "#F9E79F",
    "Conversion": "#82E0AA",
    "No_Conversion": "#F5B7B1"
}

edges_to_conversion = []
edges_others = []
edge_widths_conversion = []
edge_widths_others = []

for u, v, data in G.edges(data=True):
    if v == "Conversion":
        edges_to_conversion.append((u, v))
        edge_widths_conversion.append(5 * data['weight'])
    else:
        edges_others.append((u, v))
        edge_widths_others.append(5 * data['weight'])

plt.figure(figsize=(10, 7))
nx.draw_networkx_nodes(G, pos, node_color=[node_colors[n] for n in G.nodes()], node_size=2000)
nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

nx.draw_networkx_edges(G, pos, edgelist=edges_to_conversion,
                       width=edge_widths_conversion,
                       edge_color='green', arrowstyle='->', arrowsize=20)

nx.draw_networkx_edges(G, pos, edgelist=edges_others,
                       width=edge_widths_others,
                       edge_color='black', arrowstyle='->', arrowsize=20)

edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in G.edges()}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

plt.title("Mise en évidence des stratégies menant à Conversion", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.show()
