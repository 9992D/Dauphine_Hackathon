import numpy as np
import pandas as pd


def compute_transition_matrix(journeys):
    """
    À partir des parcours clients (dict de listes de séquences), calcule la matrice de transition
    pour la chaîne de Markov.
    Retourne un DataFrame pandas où lignes et colonnes sont les états, et cellules les probabilités.
    """
    all_states = set()
    for paths in journeys.values():
        for path in paths:
            all_states.update(path)
    all_states = sorted(all_states)

    index_map = {state: i for i, state in enumerate(all_states)}
    n = len(all_states)
    counts = np.zeros((n, n), dtype=int)

    for paths in journeys.values():
        for path in paths:
            for i in range(len(path) - 1):
                src = index_map[path[i]]
                dst = index_map[path[i + 1]]
                counts[src, dst] += 1

    probs = np.zeros_like(counts, dtype=float)
    for i in range(n):
        s = counts[i].sum()
        if s > 0:
            probs[i] = counts[i] / s
        else:
            probs[i, i] = 1.0 

    df_matrix = pd.DataFrame(probs, index=all_states, columns=all_states)
    return df_matrix


def compute_conversion_rate(transition_matrix):
    """
    Calcule le taux de conversion du modèle Markov (probabilité d'atteindre 'Conversion' depuis 'Start').
    Utilise la décomposition en états absorbants.
    """
    states = list(transition_matrix.index)
    if 'Start' not in states or 'Conversion' not in states or 'No_Conversion' not in states:
        raise ValueError("Les états 'Start', 'Conversion' et 'No_Conversion' doivent être présents.")

    idx_start = states.index('Start')
    absorbing = ['Conversion', 'No_Conversion']
    non_abs = [i for i, s in enumerate(states) if s not in absorbing]
    abs_idx = [i for i, s in enumerate(states) if s in absorbing]

    P = transition_matrix.values
    Q = P[np.ix_(non_abs, non_abs)]
    R = P[np.ix_(non_abs, abs_idx)]

    I = np.eye(Q.shape[0])
    N = np.linalg.inv(I - Q)
    B = N.dot(R)

    conv_abs_index = abs_idx.index(states.index('Conversion'))
    start_nonabs_index = non_abs.index(idx_start)
    conv_prob = B[start_nonabs_index, conv_abs_index]
    return conv_prob