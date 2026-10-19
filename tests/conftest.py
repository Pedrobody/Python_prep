from pathlib import Path
import pandas as pd
import pytest

DATA = Path(__file__).resolve().parents[1] / "data"

@pytest.fixture
def history_customers():
    return pd.read_csv(DATA / "customers_history.csv")

@pytest.fixture
def history_events():
    return pd.read_csv(DATA / "events_history.csv")

@pytest.fixture
def live_customers():
    return pd.read_csv(DATA / "customers_live.csv")

@pytest.fixture
def live_events():
    return pd.read_csv(DATA / "events_live.csv")
