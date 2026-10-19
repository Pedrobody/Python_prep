import pandas as pd
import numpy as np
from assessment.solution import clean_events, build_features


def fixture_small():
    c = pd.DataFrame({"customer_id": ["A", "B", "C"], "age": [24, 51, 34], "tenure_days": [120, 200, 12], "support_tickets": [0, 1, 4], "plan_type": ["basic", "pro", "plus"], "country": ["ES", "FR", "DE"], "churned": [0, 1, 0]})
    e = pd.DataFrame({"event_id": ["1", "2", "3", "4"], "customer_id": ["A", "A", "B", "Z"], "event_date": pd.to_datetime(["2026-08-01", "2026-08-01", "2026-08-02", "2026-08-03"]), "minutes_spent": [4, 6, 10, 999], "pages_viewed": [2, 6, 5, 8]})
    return c, e


def test_aggregation_and_left_join():
    c, e = fixture_small()
    out = build_features(c, e).set_index("customer_id")
    assert len(out) == 3
    assert out.loc["A", "sessions"] == 2
    assert out.loc["A", "active_days"] == 1
    assert out.loc["A", "total_minutes"] == 10
    assert np.isclose(out.loc["A", "avg_pages"], 4)
    assert out.loc["B", "active_days"] == 1
    assert (out.loc["C", ["sessions", "active_days", "total_minutes", "avg_pages"]] == 0).all()


def test_columns_and_target_retained():
    c, e = fixture_small()
    out = build_features(c, e)
    assert set(out.columns) == set(c.columns) | {"sessions", "active_days", "total_minutes", "avg_pages"}
    assert out.loc[out.customer_id.eq("B"), "churned"].iloc[0] == 1


def test_not_mutating_inputs():
    c, e = fixture_small()
    c0, e0 = c.copy(deep=True), e.copy(deep=True)
    build_features(c, e)
    pd.testing.assert_frame_equal(c, c0)
    pd.testing.assert_frame_equal(e, e0)


def test_real_history_data(history_customers, history_events):
    e = clean_events(history_events)
    f = build_features(history_customers, e)
    assert len(f) == len(history_customers)
    assert f.customer_id.is_unique
    assert f[["sessions", "active_days", "total_minutes", "avg_pages"]].notna().all().all()
    assert f.sessions.ge(0).all()
