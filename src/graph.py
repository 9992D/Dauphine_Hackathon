import io
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------------------------------
# 1) Charger la matrice de transition depuis un texte CSV (ou remplacer par read_csv).
# ------------------------------------------------------------------------------------
csv_data = """
,Conversion,No_Conversion,Prog_Contextual,Prog_Retargeting,Start,TV
Conversion,1.0,0.0,0.0,0.0,0.0,0.0
No_Conversion,0.0,1.0,0.0,0.0,0.0,0.0
Prog_Contextual,0.023357405249688736,0.23333577606450456,0.704396681136055,0.03395318003946945,0.0,0.004956957510282234
Prog_Retargeting,0.10451606176537992,0.3510461980926976,0.12139154824310569,0.4019175738981602,0.0,0.021128618000656553
Start,0.5610502126411914,0.0,0.21810676996767447,0.10116699007410963,0.0,0.1196760273170245
TV,0.01006104881314975,0.3132096023251891,0.004093196567938068,0.0379376267475144,0.0,0.6346985255462088
"""
# On lit la matrice sous forme de DataFrame
df = pd.read_csv(io.StringIO(csv_data), index_col=0)

# ------------------------------------------------------------------------------------
# 2) Construire un graphe dirigé à partir de la matrice, avec networkx.
# ------------------------------------------------------------------------------------
G = nx.DiGraph()

# Ajouter chaque état comme nœud
for state in df.index:
    G.add_node(state)

# Ajouter les arêtes avec leur poids (probabilité)
# On ignore les transitions de probabilité nulle pour alléger le graphe
for src in df.index:
    for dst in df.columns:
        prob = df.loc[src, dst]
        if prob > 0:
            G.add_edge(src, dst, weight=prob)

# ------------------------------------------------------------------------------------
# 3) Choisir une mise en page adaptée et dessiner le graphe.
#    On va utiliser la disposition 'shell' ou 'spring' pour une meilleure visualisation.
# ------------------------------------------------------------------------------------
plt.figure(figsize=(10, 7))

# Mise en page du graphe : positions circulaires en couches (shell)
# On peut créer deux couches : états absorbants d'un côté, états intermédiaires de l'autre
absorbants = ["Conversion", "No_Conversion"]
intermediaires = [n for n in G.nodes if n not in absorbants]

pos = {}
# On place les absorbants sur un demi-cercle en haut
angle_step_ab = 180 / (len(absorbants) + 1)
for i, node in enumerate(absorbants, start=1):
    angle = i * angle_step_ab
    x = 1.5 * np.cos(np.deg2rad(angle))
    y = 1.5 * np.sin(np.deg2rad(angle))
    pos[node] = (x, y)

# On place les intermédiaires sur un demi-cercle en bas
angle_step_int = 180 / (len(intermediaires) + 1)
for i, node in enumerate(intermediaires, start=1):
    angle = 180 + i * angle_step_int
    x = 1.5 * np.cos(np.deg2rad(angle))
    y = 1.5 * np.sin(np.deg2rad(angle))
    pos[node] = (x, y)

# Récupérer les poids des arêtes pour ajuster l’épaisseur
weights = [G[u][v]['weight'] for u, v in G.edges()]
# Normaliser les poids pour qu'ils soient visibles (par ex. multiplier par un facteur)
max_weight = max(weights) if weights else 1
edge_widths = [ (weight / max_weight) * 5 for weight in weights ]  # facteur 5 pour visibilité

# Dessiner le graphe avec labels
nx.draw_networkx_nodes(G, pos, node_size=1200, node_color='#ade6ff')
nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

# Dessiner les arêtes avec des flèches et des épaisseurs variables
nx.draw_networkx_edges(
    G, pos,
    arrowstyle='->',
    arrowsize=15,
    width=edge_widths,
    edge_color='#555555',
    connectionstyle='arc3,rad=0.1'  # courbure légère pour lisibilité si double-arêtes
)

# Annoter chaque arête avec sa probabilité (optionnel, peut surcharger le visuel)
edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='#222222', font_size=8)

plt.title("Graphe de Markov (Probabilités de Transition)")
plt.axis('off')
plt.tight_layout()
plt.show()
