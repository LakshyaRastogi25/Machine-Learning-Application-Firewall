import numpy as np 
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

print("Generating synthetic fraud dataset ...")
X, y = make_classification(
    n_samples=10000,
    n_features=5,
    n_informative=4,
    n_redundant=1,
    random_state=42,
    weights=[0.90, 0.10]
)

feature_names = [
    "transaction_amount",
    "account_balance",
    "device_trust_score",
    "time_since_last_login",
    "distance_from_home"
]

df_X = pd.DataFrame(X, columns=feature_names)

X_train, X_test, y_train, y_test = train_test_split(df_X, y, test_size=0.2, random_state=42)
print("Training MLP Classifier...")
model = MLPClassifier(
    hidden_layer_sizes=(16,8),
    activation='relu',
    solver='adam',
    max_iter=500,
    random_state=42
)

model.fit(X_train, y_train)
accuracy = model.score(X_test, y_test)
print(f"Model trained successfully. Test Accuracy: {accuracy:.4f}")

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/fraud_model.joblib")
print("Model saved to models/fraud_model.joblib")