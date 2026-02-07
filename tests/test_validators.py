# -*- coding: utf-8 -*-
"""Tests para módulo de validación de calidad de datos."""
import pytest
import pandas as pd
import numpy as np

from modules.validators import validate_quality, DataQualityReport


class TestValidateQuality:
    def test_perfect_data(self):
        sheets = {"Sheet1": pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})}
        report = validate_quality(sheets)

        assert isinstance(report, DataQualityReport)
        assert report.score > 80
        assert report.status in ("excelente", "bueno", "aceptable", "deficiente", "crítico")

    def test_data_with_nulls(self):
        sheets = {"Sheet1": pd.DataFrame({
            "a": [1, None, None, None, 5],
            "b": [None, None, None, None, None],
        })}
        report = validate_quality(sheets)

        assert report.score < 100
        assert report.total_issues > 0

    def test_empty_sheet_detected(self):
        sheets = {"Vacía": pd.DataFrame()}
        report = validate_quality(sheets)

        assert report.total_issues > 0

    def test_duplicate_rows(self):
        sheets = {"Sheet1": pd.DataFrame({
            "x": [1, 1, 1, 2, 2],
            "y": ["a", "a", "a", "b", "b"],
        })}
        report = validate_quality(sheets)

        # Duplicates should be flagged
        has_dup_issue = any("duplic" in i.message.lower() for i in report.issues)
        assert has_dup_issue

    def test_score_range(self):
        sheets = {"Sheet1": pd.DataFrame({"val": list(range(100))})}
        report = validate_quality(sheets)

        assert 0 <= report.score <= 100
