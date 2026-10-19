import numpy as np
import pandas as pd
import pytest
from assessment.solution import prioritize_customers, MODEL_FEATURES


class FakeModel:
    def predict_proba(self, X):
        assert list(X.columns) == MODEL_FEATURES
        # To keep IDs away from the model, use the 'age' feature as a fixed signal.
        score = X["age"].map({33: 0.9, 31: .5, 32: .2, 34: .5}).to_numpy()
        assert np.isfinite(score).all()
        return np.column_stack([1-score, score])


def live_fixture():
    return pd.DataFrame({"customer_id": ["c1", "c2", "c3", "c4"], "age": [31, 32, 33, 34], "tenure_days": [20]*4, "support_tickets": [1]*4, "sessions": [1]*4, "active_days": [1]*4, "total_minutes": [10]*4, "avg_pages": [2]*4, "inactivity_score": [.5]*4, "plan_type": ["basic"]*4, "country": ["ES"]*4})


def test_budget_ranking_and_correct_net_value():
    out = prioritize_customers(FakeModel(), live_fixture(), budget=24, outreach_cost=12, retention_value=140, retention_uplift=.3)
    assert list(out.columns) == ["customer_id", "churn_probability", "expected_net_value"]
    assert out.customer_id.tolist() == ["c3", "c1"]
    assert np.isclose(out.expected_net_value.iloc[0], .9*.3*140-12)
    assert np.isclose(out.churn_probability.iloc[1], .5)


def test_exclude_negative_roi_and_no_budget():
    model, live = FakeModel(), live_fixture()
    out = prioritize_customers(model, live, budget=1000, outreach_cost=12, retention_value=140, retention_uplift=.3)
    assert "c2" not in out.customer_id.tolist()  # .2 * .3 * 140 - 12 < 0
    assert prioritize_customers(model, live, budget=0).empty
    with pytest.raises(ValueError):
        prioritize_customers(model, live, outreach_cost=0)


def test_no_mutation():
    live = live_fixture()
    orig = live.copy(deep=True)
    prioritize_customers(FakeModel(), live)
    pd.testing.assert_frame_equal(live, orig)
