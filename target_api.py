from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import uvicorn

app = FastAPI(title="Vulnerable Fraud Detection API", version="1.0.0")
try:
    model = joblib.load("models/fraud_model.joblib")
except FileNotFoundError:
    raise RuntimeError("Model file not found. Run train_model.py first")

class TransactionFeatures(BaseModel):
    transaction_amount: float
    account_balance: float
    device_trust_score: float
    time_since_last_login: float
    distance_from_home: float

@app.post("/predict")
async def predict_fraud(features: TransactionFeatures):
    try:
        input_data = np.array([[
            features.transaction_amount,
            features.account_balance,
            features.device_trust_score,
            features.time_since_last_login,
            features.distance_from_home
        ]])

        prediction = model.predict(input_data)[0]
        probalities = model.predict_proba(input_data)[0]

        return {
            "fraud_detected": bool(prediction),
            "confidence_scores": {
                "legitimate": float(probalities[0]),
                "fraud": float(probalities[1])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)