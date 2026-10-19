"""BCG X-style practice assessment. COMPLETE EACH FUNCTION YOURSELF.

Work in order. Read README.md and TASKS.md before starting.
Do not rename functions, parameters, or output columns.
"""

import numpy as np
import pandas as pd


MODEL_NUMERIC = [
    "age", "tenure_days", "support_tickets", "sessions", "active_days",
    "total_minutes", "avg_pages", "inactivity_score",
]
MODEL_CATEGORICAL = ["plan_type", "country"]
MODEL_FEATURES = MODEL_NUMERIC + MODEL_CATEGORICAL


def clean_events(events: pd.DataFrame) -> pd.DataFrame:
    """Stage 1: clean raw events. See TASKS.md."""
    raise NotImplementedError("Stage 1: clean_events")


def build_features(customers: pd.DataFrame, events_clean: pd.DataFrame) -> pd.DataFrame:
    """Stage 2: create customer-level ML features. See TASKS.md."""
    raise NotImplementedError("Stage 2: build_features")


def inactivity_score(features: pd.DataFrame) -> np.ndarray:
    """Stage 3: vectorized NumPy inactivity score. See TASKS.md."""
    raise NotImplementedError("Stage 3: inactivity_score")


def train_model(features: pd.DataFrame):
    """Stage 4A: return (fitted_pipeline, X_test, y_test). See TASKS.md."""
    raise NotImplementedError("Stage 4A: train_model")


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Stage 4B: model metrics. See TASKS.md."""
    raise NotImplementedError("Stage 4B: evaluate_model")


def prioritize_customers(
    model,
    live_features: pd.DataFrame,
    budget: float = 600.0,
    outreach_cost: float = 12.0,
    retention_value: float = 140.0,
    retention_uplift: float = 0.30,
) -> pd.DataFrame:
    """Stage 5: intervention ranking subject to budget. See TASKS.md."""
    raise NotImplementedError("Stage 5: prioritize_customers")
