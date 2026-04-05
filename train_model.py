import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Paths
base_dir = os.path.dirname(os.path.dirname(__file__))
dataset_path = os.path.join(base_dir, 'dataset.csv')

print("Loading dataset...")
df = pd.read_csv(dataset_path)

# 1. CLEAN THE DATA: Remove hidden spaces from column names
df.columns = df.columns.str.strip()

# 2. Drop any empty columns caused by trailing commas in the CSV
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# 3. Separate features (symptoms) and target (prognosis)
X = df.drop('prognosis', axis=1)
y = df['prognosis']

print(f"Training model on {len(X.columns)} symptoms and {len(y.unique())} diseases...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# Save the model and the exact raw symptom names
model_data = {
    'model': rf_model,
    'symptoms': list(X.columns)
}

model_path = os.path.join(base_dir, 'model', 'model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"Success! Model trained and saved at {model_path}")