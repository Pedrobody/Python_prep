import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from assessment.solution import clean_events, build_features, inactivity_score, train_model, evaluate_model, MODEL_FEATURES


def training_data(history_customers, history_events):
    f = build_features(history_customers, clean_events(history_events))
    f["inactivity_score"] = inactivity_score(f)
    return f


def test_pipeline_and_split(history_customers, history_events):
    f = training_data(history_customers, history_events)
    model, X_test, y_test = train_model(f)
    assert isinstance(model, Pipeline)
    assert any(isinstance(step, ColumnTransformer) for _, step in model.steps)
    assert list(X_test.columns) == MODEL_FEATURES
    assert set(y_test.unique()).issubset({0, 1})
    assert abs(len(X_test) - round(len(f)*.2)) <= 1
    assert np.isfinite(model.predict_proba(X_test)).all()


def test_learned_model_has_signal(history_customers, history_events):
    f = training_data(history_customers, history_events)
    model, X_test, y_test = train_model(f)
    metric = evaluate_model(model, X_test, y_test)
    assert set(metric) == {"roc_auc", "precision", "recall", "f1"}
    assert all(isinstance(x, (float, np.floating)) and 0 <= x <= 1 for x in metric.values())
    assert metric["roc_auc"] > .62  # sanity check, not an official passing threshold


def test_unseen_category_and_missing_values(history_customers, history_events):
    f = training_data(history_customers, history_events)
    model, X_test, y_test = train_model(f)
    test = X_test.iloc[:4].copy()
    test.loc[test.index[0], "country"] = "NEW_COUNTRY"
    test.loc[test.index[1], "age"] = np.nan
    p = model.predict_proba(test)
    assert p.shape == (4, 2)
    assert np.isfinite(p).all()
