from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import uvicorn
import logging
import json
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLAF_Proxy")

app = FastAPI(
    TITLE="MLAF Reverse Proxy",
    description="Asynchronous Inference Proxy for ML Worloads",
    version="2.0.0"
)

TARGET_API_URL = "http://localhost:8001"

class MLFirewall:
    @staticmethod
    def sanitize_input(data_array: np.ndarray) -> np.ndarray:
        """Ensure strict mathematical integrity before model ingestion."""
        if not np.isfinite(data_array).all():
            raise ValueError("Payload contains NaN or Infinity.")
        return np.clip(data_array, a_min=-100.0, a_max=100.0)

    @staticmethod
    def limit_distribution(data_array: np.ndarray) -> np.ndarray:
        """Feature Squeezing: Aggressive integer rounding to snap evasion attacks."""
        return np.round(data_array, decimals=0)

    @staticmethod
    def mask_output(response_data: dict) -> dict:
        """Gradient Starvation: Blur exact probabilities to blind attackers."""
        if "confidence_scores" in response_data:
            scores = response_data["confidence_scores"]
            response_data["confidence_scores"] = {
                "legitimate": round(scores.get("legitimate", 0), 2),
                "fraud": round(scores.get("fraud", 0), 2)
            }
        return response_data

@app.post("/predict")
async def secure_predict_route(request: Request):
    """Explicitly intercept the /predict route for Deep Packet Inspection."""
    body = await request.body()
    try:
        payload = json.loads(body)
        
        # Flatten the incoming JSON into a Scikit-Learn friendly array
        raw_data = np.array([
            payload["transaction_amount"],
            payload["account_balance"],
            payload["device_trust_score"],
            payload["time_since_last_login"],
            payload["distance_from_home"]
        ], dtype=np.float32)

        # Scrub and aggressively squeeze the data
        clean_data = MLFirewall.sanitize_input(raw_data)
        squeezed_data = MLFirewall.limit_distribution(clean_data)

        # Reconstruct the exact JSON payload the Target API expects
        payload["transaction_amount"] = float(squeezed_data[0])
        payload["account_balance"] = float(squeezed_data[1])
        payload["device_trust_score"] = float(squeezed_data[2])
        payload["time_since_last_login"] = float(squeezed_data[3])
        payload["distance_from_home"] = float(squeezed_data[4])

        secured_body = json.dumps(payload).encode("utf-8")
    except Exception as e:
        logger.warning(f"Firewall Blocked Request: {str(e)}")
        raise HTTPException(status_code=403, detail="Malicious ML payload detected.")

    # --- PHASE 2: FORWARD TO VULNERABLE TARGET ---
    headers = dict(request.headers)
    for h in ["host", "content-length"]:
        headers.pop(h, None)

    async with httpx.AsyncClient() as client:
        try:
            target_response = await client.post(
                f"{TARGET_API_URL}/predict",
                content=secured_body,
                headers=headers
            )
            
            # --- PHASE 3: EGRESS ACTIVE DEFENSE ---
            response_data = target_response.json()
            
            # Mask the output to prevent gradient mapping
            masked_data = MLFirewall.mask_output(response_data)
            
            return Response(
                content=json.dumps(masked_data).encode("utf-8"),
                status_code=target_response.status_code,
                media_type="application/json"
            )

        except httpx.RequestError as e:
            logger.error(f"Target API unreachable: {e}")
            raise HTTPException(status_code=502, detail="Target API unreachable.")

if __name__ == "__main__":
    uvicorn.run("mlaf_proxy:app", host="0.0.0.0", port=8000, reload=True)