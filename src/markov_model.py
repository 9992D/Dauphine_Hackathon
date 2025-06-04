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

def remove_channel(transition_matrix, channel_to_remove):
    """
    Supprime un canal donné (nœud) de la matrice de transition :
    - Redistribue les transitions de ses prédécesseurs vers ses successeurs proportionnellement.
    - Supprime le canal de la matrice.
    """
    if channel_to_remove not in transition_matrix.columns:
        raise ValueError(f"Canal '{channel_to_remove}' introuvable dans la matrice.")

    df = transition_matrix.copy()
    if channel_to_remove in ['Start', 'Conversion', 'No_Conversion']:
        raise ValueError("On ne peut pas supprimer 'Start', 'Conversion' ou 'No_Conversion'.")

    predecessors = df.index[df[channel_to_remove] > 0]
    successors = df.columns[df.loc[channel_to_remove] > 0]

    for pred in predecessors:
        for succ in successors:
            added_prob = df.loc[pred, channel_to_remove] * df.loc[channel_to_remove, succ]
            df.loc[pred, succ] += added_prob
        df.loc[pred, channel_to_remove] = 0.0

    df.drop(index=channel_to_remove, columns=channel_to_remove, inplace=True)

    for i in df.index:
        row_sum = df.loc[i].sum()
        if row_sum > 0:
            df.loc[i] /= row_sum
        else:
            df.loc[i, i] = 1.0

    return df


def compute_all_removal_effects(transition_matrix, base_conversion_rate):
    """
    Pour chaque canal (état non absorbant), calcule la diminution du taux de conversion
    en cas de suppression de ce canal.
    """
    channels = [state for state in transition_matrix.index
                if state not in ('Start', 'Conversion', 'No_Conversion')]
    impacts = {}
    for channel in channels:
        try:
            reduced_matrix = remove_channel(transition_matrix, channel)
            new_rate = compute_conversion_rate(reduced_matrix)
            impacts[channel] = base_conversion_rate - new_rate
        except Exception as e:
            impacts[channel] = None 

    return impacts
