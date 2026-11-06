import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plot_results import svg_chart


def test_svg_contains_measured_values_and_accessible_title():
    x = pd.DataFrame({"model": ["LR", "RF"], "f1": [.7, .85]})
    output = svg_chart(x, "f1", "F1 score")
    assert "F1 score" in output
    assert "70.00%" in output
    assert "85.00%" in output
    assert "<svg " in output


def test_svg_escapes_model_names():
    x = pd.DataFrame({"model": ["<unknown & sample>"], "recall": [.5]})
    chart = svg_chart(x, "recall", "Attack recall")
    assert "&lt;unknown &amp; sample&gt;" in chart


def test_svg_rejects_invalid_percentages():
    x = pd.DataFrame({"model": ["bad"], "f1": [1.5]})
    with pytest.raises(ValueError):
        svg_chart(x, "f1", "F1")
