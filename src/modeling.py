import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from utils import read_table, get_connection

customer_df = read_table("customer_features")
retail = read_table("retail")

cutoff_date = pd.to_datetime('2025-01-01')
future_revenue = (
    retail[retail['timestamp_utc'] > cutoff_date]
    .groupby('customer_id')['sales'].sum()
    .reset_index().rename(columns={'sales': 'ltv_6m'})
)

df_model = customer_df.merge(future_revenue, on='customer_id', how='left')
df_model['ltv_6m'].fillna(0, inplace=True)

features = [
    'recency', 'frequency', 'monetary', 'tv_ads_seen', 'tv_cost',
    'prog_ads_seen', 'prog_cost', 'age', 'income'
]
X = df_model[features]
y = df_model['ltv_6m']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f"RMSE : {rmse:.2f}")

importances = rf.feature_importances_
feat_imp = pd.Series(importances, index=features).sort_values(ascending=False)
print("Importances des features :")
print(feat_imp)

import pickle
with open('output/rf_model.pkl', 'wb') as f:
    pickle.dump(rf, f)
print("✅ Modèle sauvegardé dans output/rf_model.pkl")