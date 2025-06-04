import logging
import pandas as pd
import subprocess
from src import data_loading, preprocessing, transition_counter, markov_model, attribution, visualization
from src.config import MATRICES_DIR, FIGURES_DIR, LOGS_DIR


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOGS_DIR / 'pipeline.log'),
            logging.StreamHandler()
        ]
    )


def run_transition_analysis():
    logging.info("Étape 1 : Prétraitement et construction de la matrice de transition…")
    merged_path = preprocessing.preprocess_data_in_chunks()
    sorted_path = merged_path.parent / 'merged_sorted.csv'

    cmd = ['sort', '-t', ',', '-k1,1', '-k2,2', str(merged_path), '-o', str(sorted_path)]
    subprocess.run(cmd, check=True)

    transition_counts, states_set = transition_counter.compute_transition_counts_from_file(sorted_path)
    trans_matrix = transition_counter.build_transition_matrix(transition_counts, states_set)

    MATRICES_DIR.mkdir(exist_ok=True, parents=True)
    trans_matrix.to_csv(MATRICES_DIR / 'transition_matrix.csv')
    logging.info("Matrice de transition sauvegardée.")
    return trans_matrix


def run_conversion_analysis(trans_matrix):
    logging.info("Étape 2 : Calcul du taux de conversion global…")
    base_rate = markov_model.compute_conversion_rate(trans_matrix)
    logging.info(f"Taux de conversion (Start → Conversion) : {base_rate:.4f}")
    return base_rate


def run_removal_analysis(trans_matrix, base_rate):
    logging.info("Étape 3 : Calcul des effets de suppression par canal…")
    removal_effects = markov_model.compute_all_removal_effects(trans_matrix, base_rate)
    df_ret = data_loading.load_retailer_events()
    total_conversions = df_ret['customer_id'].nunique()

    attribution_df = attribution.compute_channel_attribution(removal_effects, total_conversions)
    attribution_df.to_csv(MATRICES_DIR / 'attribution_by_channel.csv')
    logging.info("Attribution sauvegardée.")
    return attribution_df


def run_visualizations(trans_matrix, attribution_df):
    logging.info("Étape 4 : Visualisations...")
    FIGURES_DIR.mkdir(exist_ok=True, parents=True)
    visualization.plot_transition_matrix(trans_matrix, output='transition_matrix_heatmap.png')
    visualization.plot_channel_attribution(attribution_df, output='attribution_bar_chart.png')
    logging.info("Visualisations générées.")


def main():
    setup_logging()
    logging.info("Début du pipeline Markov multi-fichiers.")

    try:
        trans_matrix = run_transition_analysis()
        base_rate = run_conversion_analysis(trans_matrix)
        attribution_df = run_removal_analysis(trans_matrix, base_rate)
        run_visualizations(trans_matrix, attribution_df)
        logging.info("Pipeline terminé avec succès.")
    except Exception as e:
        logging.error(f"Erreur dans le pipeline : {e}")


if __name__ == '__main__':
    main()
