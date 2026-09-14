"""
FraudShield ML Training Pipeline
--------------------------------
Generates a realistic synthetic financial transaction dataset, performs feature
engineering, trains a Random Forest Classifier to detect fraudulent transactions,
evaluates performance metrics (Precision, Recall, F1, ROC-AUC), and persists the model.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    auc,
)

# Ensure output directories exist
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def generate_synthetic_fraud_dataset(n_samples=10000, random_state=42):
    """
    Generates synthetic financial transaction dataset mimicking real-world
    fraud characteristics (class imbalance ~4.5%).
    """
    np.random.seed(random_state)

    # 1. Legitimate transactions (95.5%)
    n_legit = int(n_samples * 0.955)
    legit_amount = np.random.exponential(scale=2500, size=n_legit) + 100
    legit_user_avg = legit_amount * np.random.uniform(0.7, 1.3, size=n_legit)
    legit_account_age = np.random.randint(30, 1800, size=n_legit)
    legit_new_device = np.random.choice([0, 1], size=n_legit, p=[0.92, 0.08])
    legit_recent_count = np.random.poisson(lam=1.5, size=n_legit)
    legit_p = np.array([0.02,0.01,0.01,0.01,0.01,0.02,0.03,0.05,0.07,0.08,0.08,0.07,0.07,0.07,0.07,0.06,0.06,0.05,0.04,0.04,0.03,0.03,0.02,0.00])
    legit_p = legit_p / legit_p.sum()
    legit_hour = np.random.choice(range(24), size=n_legit, p=legit_p)
    legit_location_match = np.random.choice([1, 0], size=n_legit, p=[0.95, 0.05])
    legit_is_fraud = np.zeros(n_legit, dtype=int)

    # 2. Fraudulent transactions (4.5%)
    n_fraud = n_samples - n_legit
    fraud_amount = np.random.exponential(scale=45000, size=n_fraud) + 5000
    fraud_user_avg = np.random.exponential(scale=2000, size=n_fraud) + 100
    fraud_account_age = np.random.randint(1, 180, size=n_fraud)
    fraud_new_device = np.random.choice([0, 1], size=n_fraud, p=[0.30, 0.70])
    fraud_recent_count = np.random.poisson(lam=6.0, size=n_fraud)
    fraud_p = np.array([0.08,0.10,0.12,0.10,0.08,0.05,0.02,0.01,0.01,0.01,0.02,0.02,0.02,0.03,0.03,0.04,0.04,0.04,0.04,0.03,0.03,0.03,0.03,0.01])
    fraud_p = fraud_p / fraud_p.sum()
    fraud_hour = np.random.choice(range(24), size=n_fraud, p=fraud_p)
    fraud_location_match = np.random.choice([1, 0], size=n_fraud, p=[0.25, 0.75])
    fraud_is_fraud = np.ones(n_fraud, dtype=int)

    # Combine into DataFrames
    df_legit = pd.DataFrame({
        "amount": legit_amount,
        "user_avg_amount": legit_user_avg,
        "account_age_days": legit_account_age,
        "is_new_device": legit_new_device,
        "recent_transaction_count": legit_recent_count,
        "hour_of_day": legit_hour,
        "location_match": legit_location_match,
        "is_fraud": legit_is_fraud
    })

    df_fraud = pd.DataFrame({
        "amount": fraud_amount,
        "user_avg_amount": fraud_user_avg,
        "account_age_days": fraud_account_age,
        "is_new_device": fraud_new_device,
        "recent_transaction_count": fraud_recent_count,
        "hour_of_day": fraud_hour,
        "location_match": fraud_location_match,
        "is_fraud": fraud_is_fraud
    })

    df = pd.concat([df_legit, df_fraud], ignore_index=True).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    
    # Feature Engineering
    df["amount_ratio"] = df["amount"] / (df["user_avg_amount"] + 1e-5)
    
    return df


def train_and_evaluate():
    print("=" * 60)
    print("FraudShield ML Pipeline Training")
    print("=" * 60)

    # 1. Load Data
    df = generate_synthetic_fraud_dataset(n_samples=10000)
    csv_path = os.path.join(DATA_DIR, "financial_transactions.csv")
    df.to_csv(csv_path, index=False)
    print(f"[1] Dataset generated and saved to {csv_path}")
    print(f"    Total samples: {len(df)}")
    print(f"    Class distribution:\n{df['is_fraud'].value_counts(normalize=True)}")

    # 2. Features and Target Selection
    feature_cols = [
        "amount",
        "user_avg_amount",
        "amount_ratio",
        "account_age_days",
        "is_new_device",
        "recent_transaction_count",
        "hour_of_day",
        "location_match"
    ]
    X = df[feature_cols]
    y = df["is_fraud"]

    # 3. Train-Test Split (Stratified to maintain 4.5% fraud ratio in both sets)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 5. Model 1: Logistic Regression Baseline
    print("\n[2] Training Baseline Model (Logistic Regression)...")
    lr = LogisticRegression(class_weight="balanced", random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_preds = lr.predict(X_test_scaled)
    lr_probs = lr.predict_proba(X_test_scaled)[:, 1]
    print("    Baseline ROC-AUC:", roc_auc_score(y_test, lr_probs))

    # 6. Model 2: Random Forest Classifier (Primary Model)
    print("\n[3] Training Primary Model (Random Forest Classifier)...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight="balanced",
        random_state=42
    )
    rf.fit(X_train, y_train)  # Random Forest works directly on raw feature distributions
    rf_preds = rf.predict(X_test)
    rf_probs = rf.predict_proba(X_test)[:, 1]

    # 7. Evaluation
    print("\n" + "=" * 60)
    print("Random Forest Model Evaluation Report")
    print("=" * 60)
    print("Classification Report:\n", classification_report(y_test, rf_preds, target_names=["Legitimate", "Fraud"]))
    
    cm = confusion_matrix(y_test, rf_preds)
    print("Confusion Matrix:\n", cm)
    print(f"  True Negatives (Legit allowed):  {cm[0][0]}")
    print(f"  False Positives (Legit flagged): {cm[0][1]}")
    print(f"  False Negatives (Fraud missed):  {cm[1][0]}")
    print(f"  True Positives (Fraud caught):   {cm[1][1]}")

    roc_auc = roc_auc_score(y_test, rf_probs)
    precision_curve, recall_curve, _ = precision_recall_curve(y_test, rf_probs)
    pr_auc = auc(recall_curve, precision_curve)
    
    print(f"\nROC-AUC Score: {roc_auc:.4f}")
    print(f"PR-AUC Score:  {pr_auc:.4f}")

    # 8. Save Artifacts
    model_path = os.path.join(MODELS_DIR, "fraud_model.joblib")
    scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")

    joblib.dump(rf, model_path)
    joblib.dump(scaler, scaler_path)

    print(f"\n[4] Models saved successfully:")
    print(f"    Model:  {model_path}")
    print(f"    Scaler: {scaler_path}")
    print("=" * 60)


if __name__ == "__main__":
    train_and_evaluate()
