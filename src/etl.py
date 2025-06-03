from utils import load_csv_to_sql
import os

os.makedirs("output", exist_ok=True)

table_files = {
    "retail": "data/retailer.csv",
    "tv": "data/tv_publisher.csv",
    "prog": "data/programmatic_publisher.csv",
    "mapping": "data/mapping_transac_tv.csv",
    "socio": "data/socio_demo.csv"
}

for table, path in table_files.items():
    load_csv_to_sql(table, path)