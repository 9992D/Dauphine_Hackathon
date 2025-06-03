import pandas as pd
from utils import read_table, get_connection

retail = read_table("retail")
tv = read_table("tv")
prog = read_table("prog")
map_df = read_table("mapping")
socio = read_table("socio")

for df in [retail, tv, prog]:
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

retail = retail.merge(socio, on="customer_id", how="left")
tv = tv.merge(map_df[["customer_id", "device_id"]], on="device_id", how="left")
prog = prog.merge(map_df[["customer_id", "dsp_id"]], on="dsp_id", how="left")

retail_agg = (
    retail.groupby("customer_id").agg(
        total_sales=("sales", "sum"),
        total_quantity=("quantity", "sum"),
        first_purchase=("timestamp_utc", "min"),
        last_purchase=("timestamp_utc", "max"),
        frequency=("timestamp_utc", "count")
    ).reset_index()
)

today = retail["timestamp_utc"].max() + pd.Timedelta(days=1)
retail_agg["recency"] = (today - retail_agg["last_purchase"]).dt.days

rfm = retail_agg[["customer_id", "recency", "frequency", "total_sales"]].rename(
    columns={"total_sales": "monetary"}
)

tv_exposure = (
    tv.groupby("customer_id").agg(
        tv_ads_seen=("timestamp_utc", "count"),
        tv_cost=("cost_milli_cent", "sum")
    ).reset_index()
)
prog_exposure = (
    prog.groupby("customer_id").agg(
        prog_ads_seen=("timestamp_utc", "count"),
        prog_cost=("cost_milli_cent", "sum")
    ).reset_index()
)

customer_df = (
    rfm
    .merge(tv_exposure, on="customer_id", how="left")
    .merge(prog_exposure, on="customer_id", how="left")
    .merge(socio, on="customer_id", how="left")
)

customer_df.fillna({
    "tv_ads_seen": 0, "tv_cost": 0,
    "prog_ads_seen": 0, "prog_cost": 0
}, inplace=True)

conn = get_connection()
customer_df.to_sql("customer_features", conn, if_exists="replace", index=False)
conn.close()
print("✅ customer_features enregistré dans SQLite")