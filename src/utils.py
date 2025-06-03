import sqlite3
import pandas as pd

DB_PATH = "output/base_retail.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_csv_to_sql(table_name: str, csv_path: str):
    conn = get_connection()
    df = pd.read_csv(csv_path, low_memory=False)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"✅ {table_name} chargé dans SQLite")
    conn.close()


def read_table(table_name: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df