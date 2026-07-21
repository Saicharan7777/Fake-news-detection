"""
Fake News Detector — Prediction Script
=======================================
Reads news text from stdin, loads the trained model, and outputs a JSON
prediction to stdout.

Expected model format (saved by train.py):
  {
      "vectorizer": TfidfVectorizer,
      "model":      SGDOneClassSVM,
      "model_type": "oneclass",
  }

Output JSON:
  {"prediction": "Fake" | "Real", "confidence": 85.5}
"""

import sys
import os
import pickle
import json
import math
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "fake_news_model.pkl")


def clean_text(text: str) -> str:
    """Must mirror the cleaning in train.py exactly."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    # ------------------------------------------------------------------
    # 1. Check model file
    # ------------------------------------------------------------------
    if not os.path.exists(MODEL_PATH):
        print(json.dumps({"error": "Model file not found. Run train.py first."}))
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Read input text from stdin
    # ------------------------------------------------------------------
    text = sys.stdin.buffer.read().decode("utf-8", errors="ignore").strip()

    if not text:
        print(json.dumps({"error": "No input text provided."}))
        sys.exit(1)

    # ------------------------------------------------------------------
    # 3. Load model artefacts
    # ------------------------------------------------------------------
    try:
        with open(MODEL_PATH, "rb") as f:
            artifacts = pickle.load(f)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load model: {e}"}))
        sys.exit(1)

    # Determine model format (supports both old pipeline and new dict)
    if isinstance(artifacts, dict):
        vectorizer = artifacts["vectorizer"]
        model      = artifacts["model"]
        model_type = artifacts.get("model_type", "oneclass")
    else:
        # Legacy format: artifacts is a sklearn Pipeline
        model      = artifacts
        vectorizer = None
        model_type = "pipeline"

    # ------------------------------------------------------------------
    # 4. Preprocess
    # ------------------------------------------------------------------
    cleaned = clean_text(text)
    if len(cleaned) < 5:
        print(json.dumps({"error": "Input text is too short after cleaning."}))
        sys.exit(1)

    # ------------------------------------------------------------------
    # 5. Predict
    # ------------------------------------------------------------------
    try:
        if model_type == "pipeline":
            # Legacy pipeline: predict returns label directly
            prediction = model.predict([cleaned])[0]
            label = "Real" if prediction == 1 else "Fake"
            decision_score = model.decision_function([cleaned])[0]
        else:
            # One-Class model (dict format)
            X = vectorizer.transform([cleaned])
            prediction = model.predict(X)[0]
            decision_score = model.decision_function(X)[0]
            # One-Class SVM: +1 = inlier (matches fake-news) → Fake
            #                -1 = outlier (doesn't match)      → Real
            label = "Fake" if prediction == 1 else "Real"

        # Convert decision score to a 0–100 confidence percentage.
        # One-Class SVM scores are typically small (|score| < 0.1),
        # so we scale them to produce user-meaningful confidence values.
        raw = abs(float(decision_score))
        if model_type == "oneclass":
            # Scale up the small decision scores for better UX
            scaled = raw * 50.0  # amplify the signal
            confidence = 1.0 / (1.0 + math.exp(-scaled))
        else:
            confidence = 1.0 / (1.0 + math.exp(-raw))
        confidence_pct = round(max(confidence, 0.51) * 100, 2)

        print(json.dumps({
            "prediction": label,
            "confidence": confidence_pct,
        }))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
