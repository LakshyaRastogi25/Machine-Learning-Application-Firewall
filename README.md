# Machine-Learning-Application-Firewall
---
# 🛡️ MLAF: Machine Learning Application Firewall

**An inline, active-defense proxy neutralizing adversarial ML payloads before they reach production inference APIs.**

## Executive Summary

Modern AI pipelines and ML models are highly susceptible to decision-based black-box attacks. Attackers utilize techniques like HopSkipJump to subtly perturb input data, bypassing fraud detection, safety filters, and LLM guardrails.

This project is a foundational Machine Learning Application Firewall (MLAF) designed to sit in the critical path of an application. It intercepts traffic, neutralizes adversarial perturbations, and provides Security Operations Centers (SOC) with actionable telemetry to remediate vulnerabilities without adding crippling latency to the pipeline.

## 💼 Business Impact & Risk Mitigation

AI security cannot just drop requests; it must inform business operations. This firewall is engineered to protect the bottom line by focusing on:

* **Preventing Evasion & Fraud:** Stops perturbed payloads from bypassing financial or safety classification models.
* **Preserving Intellectual Property:** Blinds attackers from mapping proprietary model decision boundaries via gradient starvation.
* **Actionable SOC Telemetry:** Instead of generic "blocked" errors, the proxy generates structured telemetry identifying the specific evasion technique and providing immediate remediation protocols (e.g., dynamic threshold adjustments or adversarial retraining).

## 🏗️ Architecture & Defense Mechanisms

The MLAF operates as an asynchronous FastAPI reverse proxy, ensuring the vulnerable target model remains entirely isolated from the public internet.

**Active Defense Phases:**

1. **Input Sanitization:** Enforces strict mathematical integrity, dropping mathematically impossible payloads (NaN/Infinity) and dynamically clipping outliers to prevent scalar exhaustion attacks.
2. **Feature Squeezing:** Aggressively limits data distribution. By modifying the input space, it snaps the subtle gradients that optimization-based evasion attacks rely on.
3. **Gradient Starvation (Output Masking):** Masks the exact confidence scores returned to the client. This prevents attackers from calculating the exact distance to the model's decision boundary.

## ⚔️ The Offensive Perspective (Proof of Concept)

This defense was built with an offensive security mindset. The repository includes a live exploit script (`attack_evasion.py`) utilizing the Adversarial Robustness Toolbox (ART).

**To demonstrate the vulnerability and the fix:**

1. **Deploy the Environment:** ```bash
docker-compose up --build
```

```


2. **Run the Exploit:** The script first sends a legitimate payload, then generates a HopSkipJump adversarial payload.
3. **The Result:** Watch the vulnerable target accept the malicious payload, and then watch the MLAF successfully intercept, squeeze, and drop the exact same attack, logging the remediation steps.

---
