import numpy as np
from fastapi import FastAPI, Request, HTTPException
from  fastapi.responses import JSONResponse
import httpx
import logging

app = FastAPI(title="ML Application Firewall (MLAF)")
TARGET_URL = "http://localhost:8001/predict"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLAF")

class MLFirewall:
    @staticmethod
    def sanitize_input(features: list) -> np.ndarray:
        """Phase 4.1: Input Sanitizer"""
        try:
            data = np.array(features, dtype=np.float32)
        except ValueError:
            raise ValueError("Payload contains non-numeric data.")
        if not np.isfinite(data).all():
            raise ValueError("Payload contains NaN or Infinity.")
        
        data = np.clip(data, a_min=-10.0, a_max=10.0)
        return data
    @staticmethod
    def limit_distribution(data: np.ndarray) -> np.ndarray:
        """Phase 4.2: Distribution Limiter (Feature Squeezing)"""
        return np.round(data, decimals=2)
    @staticmethod
    def mask_output(response_data: dict) -> dict:
        """Phase 4.3: Output Score Masker (Gradient Starvation)"""

        if "confidence" in response_data:
            raw_score = response_data["confidence"]
            response_data["confidence"] = round(raw_score, 2)
        return response_data
    @app.post("/proxy/predict")
    async def inference_proxy(request: Request):
        try:
            body = await request.json()
            raw_features = body.get("features")

            if not raw_features:
                raise HTTPException(status_code=400, detail="Missing 'features' in payload")
            try:
                clean_data = MLFirewall.sanitize_input(raw_features)
                squeezed_data = MLFirewall.limit_distribution(clean_data)
            except ValueError as e:
                logger.warning(f"Firewall Blocked Request: {str(e)}")
                raise HTTPException(status_code=403, detail="Malicious payload detected.")
            safe_payload = {"features": squeezed_data.tolist()}

            async with httpx.AsyncClient() as client:
                target_response = await client.post(TARGET_URL, json=safe_payload)
                target_response.raise_for_status()
                inference_result = target_response.json()

            secured_response = MLFirewall.mask_output(inference_result)
            return JSONResponse(content=secured_response, status_code=200)
        except httpx.HTTPError as e:
            logger.error(f"Upstream target error: {str(e)}")
            raise HTTPException(status_code=502, detail="Error communicating with ML Target")
        except Exception as e:
            logger.error(f"Proxy error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Proxy error.")