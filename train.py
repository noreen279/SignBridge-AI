"""Train a classifier on ml/data.csv and save ml/model.joblib.

Usage: python ml/train.py
The backend automatically uses model.joblib when it exists (otherwise rule-based).
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

here = Path(__file__).parent
df = pd.read_csv(here / "data.csv", header=None)
X, y = df.iloc[:, 1:].values, df.iloc[:, 0].astype(str).values
print(f"{len(df)} samples, classes: {sorted(set(y))}")

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
model = RandomForestClassifier(n_estimators=300, random_state=42).fit(X_tr, y_tr)
print(classification_report(y_te, model.predict(X_te)))

joblib.dump(model, here / "model.joblib")
print("Saved", here / "model.joblib")
