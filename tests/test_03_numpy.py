import numpy as np
import pandas as pd
import pytest
from assessment.solution import inactivity_score


def test_score_and_type():
    f = pd.DataFrame({"sessions": [0, 1, 9], "active_days": [0, 15, 30], "support_tickets": [0, 5, 10]})
    out = inactivity_score(f)
    assert isinstance(out, np.ndarray) and out.shape == (3,) and out.dtype.kind == "f"
    np.testing.assert_allclose(out, [0.90, 0.40, 0.16], rtol=0, atol=1e-10)


def test_values_preserve_order():
    f = pd.DataFrame({"sessions": [1, 0], "active_days": [7, 0], "support_tickets": [0, 0]}, index=[99, 10])
    out = inactivity_score(f)
    assert out[0] < out[1]
    assert ((out >= 0) & (out <= 1)).all()


def test_negative_input_raises():
    f = pd.DataFrame({"sessions": [-1], "active_days": [0], "support_tickets": [0]})
    with pytest.raises(ValueError):
        inactivity_score(f)
