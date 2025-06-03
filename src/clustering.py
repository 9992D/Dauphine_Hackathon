import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from utils import read_table, get_connection

customer_df = read_table("customer_features")

rfm_features = customer_df[["recency", "frequency", "monetary"]]
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_features)

kmeans = KMeans(n_clusters=4, random_state=42)
customer_df["cluster_rfm"] = kmeans.fit_predict(rfm_scaled)

conn = get_connection()
customer_df.to_sql("customer_segments", conn, if_exists="replace", index=False)
conn.close()
print("✅ customer_segments enregistré avec cluster_rfm")

cluster_profile = (
    customer_df.groupby("cluster_rfm").agg(
        recency_mean=("recency", "mean"),
        frequency_mean=("frequency", "mean"),
        monetary_mean=("monetary", "mean"),
        size=("customer_id", "count")
    ).reset_index()
)
cluster_profile.to_csv("output/cluster_profile.csv", index=False)
print("✅ cluster_profile.csv généré")