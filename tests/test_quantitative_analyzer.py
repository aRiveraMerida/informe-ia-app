# -*- coding: utf-8 -*-
"""Tests para QuantitativeAnalyzer."""
import pytest
import pandas as pd
import numpy as np

from modules.quantitative_analyzer import QuantitativeAnalyzer


def _make_sheets_and_meta(sheets: dict):
    """Helper: crea sheets_data y metadata como los genera DataProcessor."""
    metadata = {}
    for name, df in sheets.items():
        metadata[name] = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "column_types": {col: str(df[col].dtype) for col in df.columns},
            "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": list(df.select_dtypes(include=["object"]).columns),
            "datetime_columns": list(df.select_dtypes(include=["datetime"]).columns),
            "missing_values": df.isnull().sum().to_dict(),
            "completeness_pct": round(
                (df.count().sum() / max(1, len(df) * len(df.columns))) * 100, 2
            ),
        }
    total_rows = sum(m["rows"] for m in metadata.values())
    total_cols = sum(m["columns"] for m in metadata.values())
    metadata["_global"] = {
        "filename": "test.csv",
        "total_sheets": len(sheets),
        "total_rows": total_rows,
        "total_columns": total_cols,
        "sheet_names": list(sheets.keys()),
    }
    return sheets, metadata


class TestKPIs:
    def test_basic_kpis(self):
        df = pd.DataFrame({"valor": [10, 20, 30], "nombre": ["a", "b", "c"]})
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        results = analyzer.analyze()

        kpis = results["kpis"]["Sheet1"]
        assert kpis["total_records"] == 3
        assert kpis["completeness_rate"] == 100.0
        assert "valor_stats" in kpis
        assert kpis["valor_stats"]["mean"] == 20.0
        assert kpis["valor_stats"]["sum"] == 60.0

    def test_categorical_kpis(self):
        df = pd.DataFrame({"tipo": ["A", "A", "B", "C"]})
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        results = analyzer.analyze()

        kpis = results["kpis"]["Sheet1"]
        assert "categorical_summary" in kpis
        assert kpis["categorical_summary"]["tipo"]["unique_values"] == 3
        assert kpis["categorical_summary"]["tipo"]["most_common"] == "A"


class TestAggregations:
    def test_cross_aggregation(self):
        df = pd.DataFrame({
            "region": ["Norte", "Norte", "Sur", "Sur"],
            "ventas": [100, 200, 150, 250],
        })
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        results = analyzer.analyze()

        agg = results["aggregations"]["Sheet1"]
        assert "region" in agg
        assert "ventas" in agg["region"]

    def test_no_aggregation_without_categorical(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        results = analyzer.analyze()

        assert results["aggregations"]["Sheet1"] == {}


class TestCorrelations:
    def test_strong_correlation_detected(self):
        np.random.seed(42)
        x = np.arange(50, dtype=float)
        df = pd.DataFrame({"x": x, "y": x * 2 + 1, "noise": np.random.randn(50)})
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        results = analyzer.analyze()

        corr = results["correlations"]["Sheet1"]
        assert len(corr["strong_correlations"]) > 0
        # x and y should be strongly correlated
        pairs = [(c["var1"], c["var2"]) for c in corr["strong_correlations"]]
        assert ("x", "y") in pairs or ("y", "x") in pairs

    def test_no_correlation_with_single_numeric(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        results = analyzer.analyze()

        assert results["correlations"]["Sheet1"] == {}


class TestDistributions:
    def test_quartiles_present(self):
        df = pd.DataFrame({"score": list(range(100))})
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        results = analyzer.analyze()

        dist = results["distributions"]["Sheet1"]
        assert "score" in dist
        assert "Q1" in dist["score"]["quartiles"]
        assert "skewness" in dist["score"]


class TestFormatReport:
    def test_format_returns_string(self):
        df = pd.DataFrame({"val": [1, 2, 3], "cat": ["a", "b", "c"]})
        sheets, meta = _make_sheets_and_meta({"Sheet1": df})
        analyzer = QuantitativeAnalyzer(sheets, meta)
        analyzer.analyze()
        report = analyzer.format_for_report()

        assert isinstance(report, str)
        assert len(report) > 0
