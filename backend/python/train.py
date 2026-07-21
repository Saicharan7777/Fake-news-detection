"""
Fake News Detector — Training Script
=====================================
Trains a One-Class novelty-detection model on the FULL Fake.csv dataset.

The model learns the text distribution of fake news articles.
At prediction time:
  - Text that matches fake-news patterns  → "Fake"
  - Text that does NOT match              → "Real"

Algorithm:  TF-IDF  →  SGDOneClassSVM  (linear, sparse-friendly)
Dataset:    dataset/Fake.csv  (23,481 rows — title, text, subject, date)
Output:     backend/python/fake_news_model.pkl
"""

import os
import sys
import re
import pickle
import time

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------
try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas is required.  Install with:  pip install pandas")
    sys.exit(1)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDOneClassSVM
except ImportError:
    print("ERROR: scikit-learn >= 0.24 is required.  Install with:  pip install scikit-learn")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(SCRIPT_DIR, "fake_news_model.pkl")

# Look for Fake.csv — first in ../../dataset/, then in the script dir itself
DATASET_DIR  = os.path.join(SCRIPT_DIR, "..", "..", "dataset")
FAKE_CSV     = os.path.join(DATASET_DIR, "Fake.csv")

if not os.path.exists(FAKE_CSV):
    # Fallback: check if it's right next to this script
    FAKE_CSV = os.path.join(SCRIPT_DIR, "Fake.csv")

if not os.path.exists(FAKE_CSV):
    print(f"ERROR: Fake.csv not found in {DATASET_DIR} or {SCRIPT_DIR}")
    print("Please place the complete Fake.csv dataset file in the dataset/ folder.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Basic text cleaning — lowercase, strip URLs, strip punctuation."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)          # URLs
    text = re.sub(r"[^a-z\s]", " ", text)                  # non-alpha
    text = re.sub(r"\s+", " ", text).strip()                # collapse spaces
    return text


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("=" * 60)
    print("  Fake News Detector — Training Pipeline")
    print("=" * 60)
    start = time.time()

    # ------------------------------------------------------------------
    # 1. Load the FULL Fake.csv
    # ------------------------------------------------------------------
    print(f"\n[1/5] Loading dataset: {FAKE_CSV}")
    df = pd.read_csv(FAKE_CSV)
    print(f"      Loaded {len(df):,} rows  |  Columns: {list(df.columns)}")

    if len(df) < 100:
        print("ERROR: Dataset is too small (<100 rows). Use the complete Fake.csv.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Combine title + text for richer features
    # ------------------------------------------------------------------
    print("\n[2/5] Preprocessing text (combining title + text, cleaning)...")

    if "title" in df.columns and "text" in df.columns:
        df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")
    elif "text" in df.columns:
        df["combined"] = df["text"].fillna("")
    elif "title" in df.columns:
        df["combined"] = df["title"].fillna("")
    else:
        print(f"ERROR: Expected 'text' or 'title' column. Found: {list(df.columns)}")
        sys.exit(1)

    df["combined"] = df["combined"].apply(clean_text)

    # Drop rows where the cleaned text is too short
    before = len(df)
    df = df[df["combined"].str.len() > 20].reset_index(drop=True)
    dropped = before - len(df)
    if dropped > 0:
        print(f"      Dropped {dropped} rows with <20 chars after cleaning.")
    print(f"      Final dataset: {len(df):,} rows")

    # ------------------------------------------------------------------
    # 3. TF-IDF Vectorization
    # ------------------------------------------------------------------
    print("\n[3/5] Fitting TF-IDF vectorizer (max_features=10,000)...")
    tfidf = TfidfVectorizer(
        max_features=10_000,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=3,
        max_df=0.85,
    )
    X = tfidf.fit_transform(df["combined"])
    print(f"      TF-IDF matrix shape: {X.shape}")

    # ------------------------------------------------------------------
    # 4. Train One-Class SVM  (learns the fake-news distribution)
    # ------------------------------------------------------------------
    print("\n[4/5] Training SGDOneClassSVM on fake-news distribution...")
    model = SGDOneClassSVM(
        nu=0.05,             # expected fraction of outliers
        max_iter=1000,
        tol=1e-4,
        random_state=42,
        learning_rate="optimal",
    )
    model.fit(X)

    # Quick sanity check — how many training samples are classified as inliers?
    preds = model.predict(X)
    inlier_pct = (preds == 1).sum() / len(preds) * 100
    print(f"      Training inlier rate: {inlier_pct:.1f}% "
          f"({(preds == 1).sum():,} / {len(preds):,})")

    # ------------------------------------------------------------------
    # 5. Save the model artefacts
    # ------------------------------------------------------------------
    print(f"\n[5/5] Saving model to: {MODEL_PATH}")
    artifacts = {
        "vectorizer": tfidf,
        "model": model,
        "model_type": "oneclass",
        "training_rows": len(df),
        "feature_count": X.shape[1],
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifacts, f)

    elapsed = time.time() - start
    size_kb = os.path.getsize(MODEL_PATH) / 1024
    print(f"\n{'=' * 60}")
    print(f"  Training complete in {elapsed:.1f}s")
    print(f"  Model size: {size_kb:.0f} KB")
    print(f"  Trained on {len(df):,} fake-news articles from Fake.csv")
    print(f"  Saved to: {MODEL_PATH}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
