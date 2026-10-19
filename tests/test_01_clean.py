import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from assessment.solution import clean_events


def sample():
    return pd.DataFrame({
        "event_id": ["e1", "e2", "e3", "e1", "e4", "e5", "e6", "e7", " "],
        "customer_id": ["A", " B ", "C", "A", "C", "D", "", "E", "E"],
        "event_date": ["2026-08-01", "2026-08-02", "bad", "2026-08-04", "2026-08-03", "2026-08-05", "2026-08-06", "2026-08-07", "2026-08-09"],
        "minutes_spent": [4., None, 1, 12., -2, "abc", 3., 0., 4.],
        "pages_viewed": [2, 3, 1, 5, 4, 6, 1, "?", 1],
    })


def test_clean_basic_schema_and_values():
    result = clean_events(sample())
    assert list(result.columns) == ["event_id", "customer_id", "event_date", "minutes_spent", "pages_viewed"]
    assert is_datetime64_any_dtype(result["event_date"])
    assert not result.isna().any().any()
    assert result["event_id"].is_unique
    assert set(result["event_id"]) == {"e1", "e2", "e5"}


def test_duplicates_keep_last_and_trim():
    result = clean_events(sample()).set_index("event_id")
    assert result.loc["e1", "minutes_spent"] == 12
    assert result.loc["e1", "pages_viewed"] == 5
    assert result.loc["e2", "customer_id"] == "B"
    assert result.loc["e5", "minutes_spent"] == 0


def test_input_is_unchanged():
    original = sample()
    before = original.copy(deep=True)
    clean_events(original)
    pd.testing.assert_frame_equal(original, before)


def test_full_history_data(history_events):
    result = clean_events(history_events)
    assert len(result) > 1000
    assert result["minutes_spent"].ge(0).all()
    assert result["pages_viewed"].ge(0).all()
    assert result["event_id"].is_unique
