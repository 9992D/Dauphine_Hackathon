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

def main():
    setup_logging()
    logging.info("Début du pipeline d'attribution Markov (mode chunk).")

    # 1) Prétraitement en chunks → merged_data.csv
    logging.info("Étape 1/4 : Prétraitement par chunks...")
    merged_path = preprocessing.preprocess_data_in_chunks()
    logging.info(f"Fichier consolidé non trié créé : {merged_path}")

    # 2) Tri du fichier consolidé par customer_id, timestamp → merged_sorted.csv
    sorted_path = merged_path.parent / 'merged_sorted.csv'
    logging.info("Étape 2/4 : Tri du fichier consolidé (par customer_id, timestamp)…")
    cmd = [
        'sort', '-t', ',', '-k1,1', '-k2,2',
        str(merged_path),
        '-o',
        str(sorted_path)
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur pendant le tri : {e}")
        return
    logging.info(f"Fichier trié enregistré : {sorted_path}")

    # 3) Calcul des comptes de transition en streaming
    logging.info("Étape 3/4 : Calcul des comptes de transition (streaming)…")
    transition_counts, states_set = transition_counter.compute_transition_counts_from_file(sorted_path)
    logging.info(f"États uniques repérés : {len(states_set)}")

    # 4) Construction + sauvegarde de la matrice de transition
    logging.info("Étape 4/4 : Construction de la matrice de transition Markov…")
    trans_matrix = transition_counter.build_transition_matrix(transition_counts, states_set)
    MATRICES_DIR.mkdir(exist_ok=True, parents=True)
    trans_matrix.to_csv(MATRICES_DIR / 'transition_matrix.csv')
    logging.info("Matrice de transition sauvegardée dans results/matrices/transition_matrix.csv")

    # 5) Calcul du taux de conversion global
    logging.info("Calcul du taux de conversion global (à partir de 'Start')…")
    base_conv_rate = markov_model.compute_conversion_rate(trans_matrix)
    logging.info(f"Taux de conversion global estimé : {base_conv_rate:.4f}")

    # 6) Calcul des effets de suppression + attribution
    logging.info("Calcul des effets de suppression par canal…")
    removal_effects = attribution.compute_all_removal_effects(trans_matrix, base_conv_rate)

    # Pour calculer le nombre réel de conversions (distinct customers), on recharge le fichier Retailer
    df_ret = data_loading.load_retailer_events()
    total_conversions = df_ret['customer_id'].nunique()
    attribution_df = attribution.compute_channel_attribution(removal_effects, total_conversions)

    attribution_df.to_csv(MATRICES_DIR / 'attribution_by_channel.csv')
    logging.info("Attribution par canal sauvegardée dans results/matrices/attribution_by_channel.csv")

    # 7) Visualisations
    logging.info("Génération des visualisations…")
    FIGURES_DIR.mkdir(exist_ok=True, parents=True)
    visualization.plot_transition_matrix(trans_matrix, output='transition_matrix_heatmap.png')
    visualization.plot_channel_attribution(attribution_df, output='attribution_bar_chart.png')
    logging.info("Visualisations enregistrées dans results/figures/")

    logging.info("Pipeline terminé avec succès.")

if __name__ == '__main__':
    main()
