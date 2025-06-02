import pandas as pd
from tqdm import tqdm

# Initialiser tqdm pour Pandas
tqdm.pandas()

print("🔄 Début du traitement...")

# Étapes avec barre de progression manuelle
steps = [
    "Chargement des données",
    "Nettoyage",
    "Fusion des bases",
    "Création des features client",
    "Export de la base client"
]

for i, step in enumerate(tqdm(steps, desc="📊 Pipeline", unit="étape")):
    if step == "Chargement des données":
        path = "data/"
        df_retail = pd.read_csv(path + 'retailer.csv', parse_dates=['timestamp_utc'])
        df_tv = pd.read_csv(path + 'tv_publisher.csv', parse_dates=['timestamp_utc'])
        df_prog = pd.read_csv(path + 'programmatic_publisher.csv', parse_dates=['timestamp_utc'])
        df_mapping = pd.read_csv(path + 'mapping_transac_to_tv.csv')
        df_socio = pd.read_csv(path + 'socio_demo.csv')

    elif step == "Nettoyage":
        df_retail.dropna(subset=['customer_id'], inplace=True)
        df_mapping.drop_duplicates(inplace=True)
        df_tv.drop_duplicates(inplace=True)
        df_prog.drop_duplicates(inplace=True)

    elif step == "Fusion des bases":
        df_merged = df_retail.merge(df_mapping, on='customer_id', how='left')
        df_merged = df_merged.merge(df_tv, on='device_id', how='left', suffixes=('', '_tv'))
        df_merged = df_merged.merge(df_prog, on='dsp_id', how='left', suffixes=('', '_prog'))
        df_merged = df_merged.merge(df_socio, on='customer_id', how='left')

    elif step == "Création des features client":
        freq = df_retail.groupby('customer_id')['timestamp_utc'].nunique().reset_index(name='purchase_days')
        total = df_retail.groupby('customer_id')['sales'].sum().reset_index(name='total_sales')
        top_prod = df_retail.groupby(['customer_id', 'product_name'])['quantity'].sum().reset_index()
        top_prod = top_prod.sort_values(['customer_id', 'quantity'], ascending=[True, False])
        top_prod = top_prod.groupby('customer_id').first().reset_index()[['customer_id', 'product_name']]
        expo_tv = df_merged[df_merged['timestamp_utc_tv'].notna()].groupby('customer_id').size().reset_index(name='tv_exposures')
        expo_prog = df_merged[df_merged['timestamp_utc_prog'].notna()].groupby('customer_id').size().reset_index(name='prog_exposures')

        df_features = freq.merge(total, on='customer_id') \
                          .merge(top_prod, on='customer_id') \
                          .merge(expo_tv, on='customer_id', how='left') \
                          .merge(expo_prog, on='customer_id', how='left') \
                          .merge(df_socio, on='customer_id', how='left') \
                          .fillna(0)

    elif step == "Export de la base client":
        df_features.to_csv("output/base_clients.csv", index=False)

print("✅ Traitement terminé – fichier prêt dans output/base_clients.csv")
