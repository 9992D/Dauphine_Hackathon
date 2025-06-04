import pandas as pd
import numpy as np
from src.markov_model import compute_conversion_rate


def compute_removal_effect(transition_matrix, channel):
    """
    Calcule le taux de conversion sans l'état 'channel'.
    Retourne le taux de conversion du modèle modifié.
    """
    if channel not in transition_matrix.index:
        raise KeyError(f"État '{channel}' non trouvé dans la matrice de transition.")

    states = list(transition_matrix.index)
    idx = states.index(channel)

    # Retirer ligne et colonne correspondantes
    new_states = [s for s in states if s != channel]
    new_vals = np.delete(np.delete(transition_matrix.values, idx, axis=0), idx, axis=1)
    P_new = pd.DataFrame(new_vals, index=new_states, columns=new_states)

    # Recalculer taux de conversion avec la nouvelle matrice
    new_rate = compute_conversion_rate(P_new)
    return new_rate


def compute_all_removal_effects(transition_matrix, base_conv_rate):
    """
    Pour chaque canal (état non-absorbant sauf 'Start'), calcule l'effet de suppression.
    Retourne dict {etat: effet} avec effet = base_conv_rate - taux_sans_etat.
    """
    effects = {}
    states = list(transition_matrix.index)
    excluded = {'Conversion', 'No_Conversion', 'Start'}
    for state in states:
        if state in excluded:
            continue
        new_rate = compute_removal_effect(transition_matrix, state)
        effects[state] = base_conv_rate - new_rate
    return effects


def compute_channel_attribution(removal_effects, total_conversions):
    """
    Calcule les conversions attribuées par canal selon les effets de suppression.
    Retourne un DataFrame indexé par canal avec colonnes ['removal_effect', 'proportion', 'conversions_attribuees'].
    """
    df = pd.DataFrame.from_dict(removal_effects, orient='index', columns=['removal_effect'])
    total_effect = df['removal_effect'].sum()
    df['proportion'] = df['removal_effect'] / total_effect
    df['conversions_attribuees'] = df['proportion'] * total_conversions
    return df