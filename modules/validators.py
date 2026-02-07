# -*- coding: utf-8 -*-
"""
Validación de calidad de datos pre-análisis.
Genera un reporte de calidad con score y advertencias.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataQualityIssue:
    """Un problema de calidad detectado."""
    severity: str          # "error", "warning", "info"
    category: str          # "nulls", "duplicates", "variance", "types", "structure"
    column: str            # Columna afectada (o "_global")
    message: str
    detail: str = ""


@dataclass
class DataQualityReport:
    """Reporte completo de calidad de un dataset."""
    score: float = 100.0                          # 0-100
    total_issues: int = 0
    issues: List[DataQualityIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if self.score >= 80:
            return "bueno"
        elif self.score >= 50:
            return "aceptable"
        else:
            return "deficiente"

    @property
    def status_emoji(self) -> str:
        if self.score >= 80:
            return "✅"
        elif self.score >= 50:
            return "⚠️"
        else:
            return "❌"

    @property
    def errors(self) -> List[DataQualityIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[DataQualityIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def validate_quality(sheets_data: Dict[str, pd.DataFrame]) -> DataQualityReport:
    """Ejecuta validación completa de calidad sobre un dataset multi-hoja."""
    report = DataQualityReport()
    penalty = 0.0

    total_rows = 0
    total_cols = 0

    for sheet_name, df in sheets_data.items():
        total_rows += len(df)
        total_cols += len(df.columns)

        # --- Estructura ---
        if df.empty:
            report.issues.append(DataQualityIssue(
                severity="error", category="structure", column="_global",
                message=f"Hoja '{sheet_name}' está vacía",
            ))
            penalty += 20
            continue

        if len(df) < 3:
            report.issues.append(DataQualityIssue(
                severity="warning", category="structure", column="_global",
                message=f"Hoja '{sheet_name}' tiene solo {len(df)} filas",
                detail="Pocas filas pueden producir un análisis poco representativo.",
            ))
            penalty += 5

        # --- Valores nulos ---
        null_pct = (df.isnull().sum().sum() / max(1, df.size)) * 100
        if null_pct > 0:
            report.summary[f"{sheet_name}_null_pct"] = round(null_pct, 1)
            if null_pct > 50:
                report.issues.append(DataQualityIssue(
                    severity="error", category="nulls", column="_global",
                    message=f"'{sheet_name}': {null_pct:.1f}% de valores nulos",
                    detail="Más de la mitad de los datos faltan.",
                ))
                penalty += 25
            elif null_pct > 20:
                report.issues.append(DataQualityIssue(
                    severity="warning", category="nulls", column="_global",
                    message=f"'{sheet_name}': {null_pct:.1f}% de valores nulos",
                ))
                penalty += 10
            elif null_pct > 5:
                report.issues.append(DataQualityIssue(
                    severity="info", category="nulls", column="_global",
                    message=f"'{sheet_name}': {null_pct:.1f}% de valores nulos",
                ))
                penalty += 3

        # --- Columnas con alta nulidad ---
        for col in df.columns:
            col_null_pct = (df[col].isnull().sum() / len(df)) * 100
            if col_null_pct > 80:
                report.issues.append(DataQualityIssue(
                    severity="warning", category="nulls", column=col,
                    message=f"Columna '{col}' en '{sheet_name}': {col_null_pct:.0f}% nulos",
                    detail="Considerar eliminar esta columna.",
                ))
                penalty += 3

        # --- Filas duplicadas ---
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            dup_pct = (dup_count / len(df)) * 100
            report.issues.append(DataQualityIssue(
                severity="warning" if dup_pct > 10 else "info",
                category="duplicates", column="_global",
                message=f"'{sheet_name}': {dup_count} filas duplicadas ({dup_pct:.1f}%)",
            ))
            if dup_pct > 10:
                penalty += 5

        # --- Columnas sin varianza ---
        for col in df.columns:
            non_null = df[col].dropna()
            if len(non_null) > 0 and non_null.nunique() == 1:
                report.issues.append(DataQualityIssue(
                    severity="info", category="variance", column=col,
                    message=f"Columna '{col}' en '{sheet_name}' tiene un solo valor único",
                    detail=f"Valor constante: {non_null.iloc[0]}",
                ))
                penalty += 2

        # --- Columnas numéricas sin tipo correcto ---
        for col in df.select_dtypes(include=["object"]).columns:
            sample = df[col].dropna().head(20)
            numeric_count = sum(1 for v in sample if _is_numeric_string(str(v)))
            if len(sample) > 0 and numeric_count / len(sample) > 0.8:
                report.issues.append(DataQualityIssue(
                    severity="info", category="types", column=col,
                    message=f"Columna '{col}' en '{sheet_name}' parece numérica pero es texto",
                    detail="Se intentará conversión automática.",
                ))

    report.score = max(0, round(100 - penalty, 1))
    report.total_issues = len(report.issues)
    report.summary["total_rows"] = total_rows
    report.summary["total_cols"] = total_cols
    report.summary["total_sheets"] = len(sheets_data)

    return report


def _is_numeric_string(value: str) -> bool:
    """Comprueba si un string representa un número."""
    clean = value.replace(",", "").replace(".", "").replace("-", "").replace(" ", "")
    return clean.isdigit()
