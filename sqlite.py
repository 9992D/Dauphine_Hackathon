import pandas as pd
import sqlite3

conn = sqlite3.connect("output/base_retail.db")

tables = {
    "retail": "retailer.csv",
    "tv": "tv_publisher.csv",
    "prog": "programmatic_publisher.csv",
    "mapping": "mapping_transac_tv.csv",
    "socio": "socio_demo.csv"
}

for name, file in tables.items():
    df = pd.read_csv(f"data/{file}", low_memory=False)
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"✅ Table {name} enregistrée")
