import matplotlib.pyplot as plt
import seaborn as sns
from src.config import FIGURES_DIR

sns.set(style='whitegrid')


def plot_transition_matrix(matrix_df, output=None):
    """
    Génère une heatmap de la matrice de transition.
    Si 'output' est spécifié, enregistre le fichier dans FIGURES_DIR.
    """
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix_df, annot=True, fmt='.2f', cmap='viridis')
    plt.title('Matrice de transition - Chaîne de Markov')
    plt.tight_layout()
    if output:
        plt.savefig(str(FIGURES_DIR / output))
    plt.close()


def plot_channel_attribution(attribution_df, output=None):
    """
    Trace un diagramme en barres des conversions attribuées par canal.
    """
    plt.figure(figsize=(10, 6))
    df_sorted = attribution_df.sort_values('conversions_attribuees', ascending=False)
    sns.barplot(x='conversions_attribuees', y=df_sorted.index, data=df_sorted)
    plt.xlabel('Conversions attribuées')
    plt.ylabel('Canal')
    plt.title('Attribution des conversions par canal (Markov)')
    plt.tight_layout()
    if output:
        plt.savefig(str(FIGURES_DIR / output))
    plt.close()