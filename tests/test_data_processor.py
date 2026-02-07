# -*- coding: utf-8 -*-
"""Tests para DataProcessor."""
import pytest
import pandas as pd
from io import BytesIO

from modules.data_processor import DataProcessor


def _make_csv(content: str) -> bytes:
    return content.encode("utf-8")


def _make_xlsx(sheets: dict) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    buf.seek(0)
    return buf.getvalue()


# ─── CSV ──────────────────────────────────────────────────────────────────────

class TestCSVProcessing:
    def test_simple_csv(self):
        csv = _make_csv("nombre,edad,ciudad\nAlice,30,Madrid\nBob,25,Barcelona\n")
        proc = DataProcessor(csv, "test.csv")
        result = proc.process()

        assert result["success"] is True
        assert "Sheet1" in result["sheets"]
        assert len(result["sheets"]["Sheet1"]) == 2
        assert result["metadata"]["_global"]["total_rows"] == 2

    def test_csv_with_missing_values(self):
        csv = _make_csv("a,b,c\n1,,x\n2,3,\n,,z\n")
        proc = DataProcessor(csv, "missing.csv")
        result = proc.process()

        assert result["success"] is True
        df = result["sheets"]["Sheet1"]
        assert df.isnull().sum().sum() > 0

    def test_csv_numeric_inference(self):
        csv = _make_csv("id,valor\n1,100.5\n2,200.3\n3,300.1\n")
        proc = DataProcessor(csv, "nums.csv")
        result = proc.process()

        assert result["success"] is True
        df = result["sheets"]["Sheet1"]
        assert pd.api.types.is_numeric_dtype(df["valor"])

    def test_empty_csv_still_succeeds(self):
        csv = _make_csv("col1,col2\n")
        proc = DataProcessor(csv, "empty.csv")
        result = proc.process()
        # Even if empty, process should not crash
        assert result["success"] is True


# ─── Excel ────────────────────────────────────────────────────────────────────

class TestExcelProcessing:
    def test_single_sheet(self):
        xlsx = _make_xlsx({"Ventas": pd.DataFrame({"producto": ["A", "B"], "cantidad": [10, 20]})})
        proc = DataProcessor(xlsx, "test.xlsx")
        result = proc.process()

        assert result["success"] is True
        assert "Ventas" in result["sheets"]
        assert result["metadata"]["_global"]["total_sheets"] == 1

    def test_multiple_sheets(self):
        xlsx = _make_xlsx({
            "Hoja1": pd.DataFrame({"x": [1, 2]}),
            "Hoja2": pd.DataFrame({"y": [3, 4, 5]}),
        })
        proc = DataProcessor(xlsx, "multi.xlsx")
        result = proc.process()

        assert result["success"] is True
        assert result["metadata"]["_global"]["total_sheets"] == 2
        assert result["metadata"]["_global"]["total_rows"] == 5


# ─── Metadata ─────────────────────────────────────────────────────────────────

class TestMetadata:
    def test_metadata_columns(self):
        csv = _make_csv("nombre,edad,activo\nAlice,30,si\nBob,25,no\n")
        proc = DataProcessor(csv, "meta.csv")
        result = proc.process()

        meta = result["metadata"]["Sheet1"]
        assert "nombre" in meta["column_names"]
        assert meta["rows"] == 2
        assert meta["columns"] == 3
        assert "completeness_pct" in meta

    def test_global_metadata_keys(self):
        csv = _make_csv("a,b\n1,2\n")
        proc = DataProcessor(csv, "g.csv")
        result = proc.process()

        g = result["metadata"]["_global"]
        assert "filename" in g
        assert "total_sheets" in g
        assert "total_rows" in g
        assert "sheet_names" in g


# ─── Sample data ──────────────────────────────────────────────────────────────

class TestSampleData:
    def test_sample_returns_head(self):
        csv = _make_csv("x\n1\n2\n3\n4\n5\n6\n7\n")
        proc = DataProcessor(csv, "s.csv")
        proc.process()
        samples = proc.get_sample_data(n=3)

        assert len(samples["Sheet1"]) == 3
