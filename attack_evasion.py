import numpy as np
import joblib
import requests
from art.estimators.classification import SklearnClassifier
from art.attacks.evasion import HopSkipJump
API_URL = "http://localhost:8000/predict"
MODEL_PATH = "models/fraud_model.joblib"

model = joblib.load(MODEL_PATH)
classifier = SklearnClassifier(model=model)

original_transaction = np.array([[1.5, 0.5, -1.2, 0.1, 2.5]], dtype=np.float32)

print("--- 1. Executing Original Transaction ---")
print(f"Original Features: {original_transaction[0]}")
res_orig = requests.post(API_URL, json={
    "transaction_amount": 1.5, "account_balance": 0.5,
    "device_trust_score": -1.2, "time_since_last_login": 0.1,
    "distance_from_home": 2.5
})
print(f"API Response: {res_orig.json()}\n")

print("--- 2. Generating FGSM Adversarial Payload ---")
attack = HopSkipJump(
    classifier=classifier, 
    targeted=False, 
    max_iter=50, 
    max_eval=1000, 
    init_eval=10
)
adversarial_transaction = attack.generate(x=original_transaction)
adv_features = adversarial_transaction[0]

print(f"Perturbed Features: {adv_features}")
print("Notice how the numbers barely changed!\n")

print("--- 3. Attacking the live API ---")
res_adv = requests.post(API_URL, json={
    "transaction_amount": float(adv_features[0]),
    "account_balance": float(adv_features[1]),
    "device_trust_score": float(adv_features[2]),
    "time_since_last_login": float(adv_features[3]),
    "distance_from_home": float(adv_features[4])
})

response_data = res_adv.json()
print(f"Adversarial API Response: {response_data}")
if not response_data["fraud_detected"]:
    print("\n[+] Exploit Successful: Fraud filter bypassed.")
else:
    print("\n[-] Exploit Failed: Model resisted.")