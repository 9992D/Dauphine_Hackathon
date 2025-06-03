import pandas as pd
from utils import read_table, get_connection

retail = read_table("retail")
tv = read_table("tv")
prog = read_table("prog")
map_df = read_table("mapping")

for df in [retail, tv, prog]:
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

tv = tv.merge(map_df[["customer_id", "device_id"]], on="device_id", how="left")
prog = prog.merge(map_df[["customer_id", "dsp_id"]], on="dsp_id", how="left")

tv_sorted = tv.sort_values('timestamp_utc')
prog_sorted = prog.sort_values('timestamp_utc')

def assign_last_touch(retail_df, tv_df, prog_df):
    retail_df = retail_df.copy()
    retail_df['last_channel'] = 'none'

    for idx, row in retail_df.iterrows():
        cid = row['customer_id']
        purchase_time = row['timestamp_utc']
        tvs = tv_df[tv_df['customer_id'] == cid]
        progs = prog_df[prog_df['customer_id'] == cid]
        merged = pd.concat([
            tvs.assign(channel='tv'),
            progs.assign(channel='prog')
        ])
        merged = merged[merged['timestamp_utc'] < purchase_time]
        if merged.empty:
            retail_df.at[idx, 'last_channel'] = 'none'
        else:
            last = merged.sort_values('timestamp_utc').iloc[-1]['channel']
            retail_df.at[idx, 'last_channel'] = last

    return retail_df

retail_lt = assign_last_touch(retail, tv_sorted, prog_sorted)
conn = get_connection()
retail_lt[['customer_id', 'timestamp_utc', 'last_channel']].to_sql(
    "retail_attribution", conn, if_exists="replace", index=False
)
conn.close()
print("✅ retail_attribution enregistré dans SQLite")