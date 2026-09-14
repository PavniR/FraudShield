"""
FraudShield Machine Learning Service
------------------------------------
Loads trained Random Forest model & scalar, transforms runtime transaction features,
and computes ML fraud probability score.
"""

import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings


class MLFraudDetector:
    _instance = None
    _model = None
    _scaler = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        model_path = getattr(settings, "ML_MODEL_PATH", None)
        scaler_path = getattr(settings, "ML_SCALER_PATH", None)

        if model_path and os.path.exists(model_path):
            try:
                self._model = joblib.load(model_path)
                print(f"[ML FraudDetector] Model loaded successfully from {model_path}")
            except Exception as e:
                print(f"[ML FraudDetector] Error loading model: {e}")

        if scaler_path and os.path.exists(scaler_path):
            try:
                self._scaler = joblib.load(scaler_path)
            except Exception as e:
                print(f"[ML FraudDetector] Error loading scaler: {e}")

    def predict_fraud_probability(self, transaction, account_profile):
        """
        Computes ML fraud probability between 0.0 and 1.0.
        """
        amount = float(transaction.amount)
        avg_amount = float(account_profile.average_transaction_amount)
        amount_ratio = amount / (avg_amount + 1e-5)
        account_age = int(account_profile.account_age_days)
        is_new_device = 1 if transaction.is_new_device else 0
        recent_count = int(transaction.recent_transaction_count)
        hour = transaction.timestamp.hour if hasattr(transaction.timestamp, "hour") else 12
        location_match = 1 if transaction.location.strip().lower() == account_profile.usual_location.strip().lower() else 0

        features_df = pd.DataFrame([{
            "amount": amount,
            "user_avg_amount": avg_amount,
            "amount_ratio": amount_ratio,
            "account_age_days": account_age,
            "is_new_device": is_new_device,
            "recent_transaction_count": recent_count,
            "hour_of_day": hour,
            "location_match": location_match
        }])

        if self._model is not None:
            try:
                prob = self._model.predict_proba(features_df)[0][1]
                return float(prob)
            except Exception as e:
                print(f"[ML FraudDetector] Inference error: {e}")

        # Heuristic fallback if model isn't available
        base_prob = 0.05
        if amount_ratio > 3.0:
            base_prob += 0.45
        if is_new_device:
            base_prob += 0.25
        if location_match == 0:
            base_prob += 0.15
        return min(base_prob, 0.99)
