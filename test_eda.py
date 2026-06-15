"""
Unit tests for Sales EDA Toolkit
Run with: pytest tests/ -v
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from eda import data_quality_report, generate_sample_data, revenue_stats


@pytest.fixture
def sample_df():
    return generate_sample_data(n=200, seed=0)


def test_generate_sample_data_shape(sample_df):
    assert sample_df.shape[0] == 200
    assert "revenue" in sample_df.columns
    assert "date" in sample_df.columns


def test_generate_sample_data_revenue_positive(sample_df):
    assert (sample_df["revenue"] >= 0).all()


def test_data_quality_report_returns_dataframe(sample_df):
    report = data_quality_report(sample_df)
    assert isinstance(report, pd.DataFrame)
    assert "nulls" in report.columns
    assert "null_%" in report.columns


def test_revenue_stats_keys(sample_df):
    stats = revenue_stats(sample_df, revenue_col="revenue")
    for key in ["total", "mean", "median", "std", "min", "max", "q25", "q75"]:
        assert key in stats


def test_revenue_stats_total_correct(sample_df):
    stats = revenue_stats(sample_df, revenue_col="revenue")
    expected = sample_df["revenue"].sum()
    assert np.isclose(stats["total"], expected)


def test_revenue_stats_missing_column(sample_df):
    with pytest.raises(KeyError):
        revenue_stats(sample_df, revenue_col="nonexistent_column")


def test_sample_data_has_nulls(sample_df):
    # The generator injects nulls into discount_pct and customer_satisfaction
    total_nulls = sample_df.isnull().sum().sum()
    assert total_nulls > 0


def test_date_column_is_datetime(sample_df):
    assert pd.api.types.is_datetime64_any_dtype(sample_df["date"])
