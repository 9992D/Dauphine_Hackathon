import csv
from collections import defaultdict
from src.config import CSV_RETAILER


def compute_transition_counts_from_file(sorted_csv_path):
    """
    Parcourt le fichier CSV trié (colonnes [customer_id, timestamp, state, channel])
    et calcule les comptes de transitions (src -> dst) en mode streaming.
    Retourne :
      - transition_counts : dict[(src_state, dst_state)] = count
      - states_set : set de tous les états observés (incluant 'Start', 'Conversion', 'No_Conversion')
    """
    transition_counts = defaultdict(int)
    states_set = set(['Start', 'Conversion', 'No_Conversion'])

    prev_customer = None
    prev_state = None

    # Ouvrir le CSV trié
    with open(sorted_csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cust = row['customer_id']
            state = row['state']

            if cust != prev_customer:
                if prev_customer is not None and prev_state and prev_state != 'Start' and prev_state != 'Conversion':
                    transition_counts[(prev_state, 'No_Conversion')] += 1
                prev_customer = cust
                prev_state = 'Start'

            transition_counts[(prev_state, state)] += 1
            states_set.add(prev_state)
            states_set.add(state)

            if state == 'Conversion':
                transition_counts[('Conversion', 'Conversion')] += 1
                prev_state = 'Start'
            else:
                prev_state = state

    if prev_customer is not None and prev_state and prev_state != 'Start' and prev_state != 'Conversion':
        transition_counts[(prev_state, 'No_Conversion')] += 1

    return transition_counts, states_set


def build_transition_matrix(transition_counts, states_set):
    """
    À partir des counts et de l'ensemble des états, construit une matrice de transition pandas DataFrame.
    """
    import pandas as pd
    states = sorted(states_set)
    n = len(states)
    idx_map = {s: i for i, s in enumerate(states)}

    import numpy as np
    counts = np.zeros((n, n), dtype=int)
    for (src, dst), c in transition_counts.items():
        i = idx_map[src]
        j = idx_map[dst]
        counts[i, j] = c

    probs = np.zeros_like(counts, dtype=float)
    for i in range(n):
        total = counts[i].sum()
        if total > 0:
            probs[i] = counts[i] / total
        else:
            probs[i, i] = 1.0

    df_matrix = pd.DataFrame(probs, index=states, columns=states)
    return df_matrix