# -*- coding: utf-8 -*-
"""
Módulo de análisis cuantitativo determinista.
Calcula KPIs, agregados, tendencias, correlaciones y anomalías.
Genérico para cualquier tipo de dataset.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

from .config import MAX_CATEGORIES_DISPLAY

logger = logging.getLogger(__name__)


class QuantitativeAnalyzer:
    """Realiza análisis cuantitativo automático de datos tabulares."""

    def __init__(self, sheets_data: Dict[str, pd.DataFrame], metadata: Dict[str, Any]):
        self.sheets_data = sheets_data
        self.metadata = metadata

    def analyze(self) -> Dict[str, Any]:
        """Ejecuta análisis completo y retorna resultados."""
        results: Dict[str, Any] = {
            "kpis": {},
            "aggregations": {},
            "trends": {},
            "distributions": {},
            "correlations": {},
            "anomalies": {},
        }

        for sheet_name, df in self.sheets_data.items():
            logger.info("Analyzing sheet: %s", sheet_name)
            results["kpis"][sheet_name] = self._calculate_kpis(df)
            results["aggregations"][sheet_name] = self._calculate_aggregations(df)
            results["distributions"][sheet_name] = self._analyze_distributions(df)
            results["correlations"][sheet_name] = self._calculate_correlations(df)
            results["trends"][sheet_name] = self._detect_trends(df)
            results["anomalies"][sheet_name] = self._detect_anomalies(df)

        results["global_kpis"] = self._calculate_global_kpis()
        return results

    # ─── KPIs ────────────────────────────────────────────────────────────────

    def _calculate_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula KPIs automáticos basados en estructura de datos."""
        kpis: Dict[str, Any] = {
            "total_records": len(df),
            "completeness_rate": round(
                (df.count().sum() / max(1, len(df) * len(df.columns))) * 100, 2
            ),
            "missing_values_total": int(df.isnull().sum().sum()),
        }

        # KPIs numéricos
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            vals = df[col].dropna()
            if len(vals) == 0:
                continue
            kpis[f"{col}_stats"] = {
                "mean": round(float(vals.mean()), 2),
                "median": round(float(vals.median()), 2),
                "std": round(float(vals.std()), 2),
                "min": round(float(vals.min()), 2),
                "max": round(float(vals.max()), 2),
                "sum": round(float(vals.sum()), 2),
            }

        # KPIs categóricos
        categorical_cols = df.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            kpis["categorical_summary"] = {}
            for col in categorical_cols:
                unique_values = df[col].nunique()
                mode_values = df[col].mode()
                kpis["categorical_summary"][col] = {
                    "unique_values": unique_values,
                    "most_common": mode_values.iloc[0] if len(mode_values) > 0 else None,
                    "diversity_score": round(
                        (unique_values / max(1, len(df))) * 100, 2
                    ),
                }

        return kpis

    # ─── Agregaciones ────────────────────────────────────────────────────────

    def _calculate_aggregations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula agregaciones cruzando columnas categóricas × numéricas."""
        aggregations: Dict[str, Any] = {}

        categorical_cols = df.select_dtypes(include=["object"]).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(categorical_cols) == 0 or len(numeric_cols) == 0:
            return aggregations

        for cat_col in categorical_cols:
            if df[cat_col].nunique() > 50:
                continue
            aggregations[cat_col] = {}
            for num_col in numeric_cols:
                grouped = df.groupby(cat_col)[num_col].agg(["mean", "sum", "count"]).round(2)
                aggregations[cat_col][num_col] = grouped.to_dict()

        return aggregations

    # ─── Distribuciones ──────────────────────────────────────────────────────

    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza distribuciones de variables numéricas."""
        distributions: Dict[str, Any] = {}

        for col in df.select_dtypes(include=[np.number]).columns:
            values = df[col].dropna()
            if len(values) == 0:
                continue
            distributions[col] = {
                "quartiles": {
                    "Q1": round(float(values.quantile(0.25)), 2),
                    "Q2": round(float(values.quantile(0.50)), 2),
                    "Q3": round(float(values.quantile(0.75)), 2),
                },
                "skewness": round(float(values.skew()), 2) if len(values) > 2 else None,
                "kurtosis": round(float(values.kurtosis()), 2) if len(values) > 3 else None,
            }

        return distributions

    # ─── Correlaciones ───────────────────────────────────────────────────────

    def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula correlaciones entre variables numéricas."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return {}

        try:
            corr_matrix = df[numeric_cols].corr().round(2)

            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    val = corr_matrix.iloc[i, j]
                    if abs(val) > 0.5 and not pd.isna(val):
                        strong_correlations.append({
                            "var1": corr_matrix.columns[i],
                            "var2": corr_matrix.columns[j],
                            "correlation": float(val),
                        })

            return {
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": strong_correlations,
            }
        except Exception as e:
            logger.warning("Error calculating correlations: %s", e)
            return {}

    # ─── Tendencias ──────────────────────────────────────────────────────────

    def _detect_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta tendencias temporales si hay columnas de fecha."""
        trends: Dict[str, Any] = {}

        datetime_cols = df.select_dtypes(include=["datetime"]).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(datetime_cols) == 0 or len(numeric_cols) == 0:
            return trends

        date_col = datetime_cols[0]
        df_sorted = df.sort_values(date_col)

        for num_col in numeric_cols:
            values = df_sorted[num_col].dropna()
            if len(values) < 3:
                continue
            try:
                x = np.arange(len(values))
                slope = float(np.polyfit(x, values, 1)[0])
                trends[num_col] = {
                    "trend": "increasing" if slope > 0 else "decreasing",
                    "slope": round(slope, 4),
                }
            except Exception:
                pass

        return trends

    # ─── Anomalías ───────────────────────────────────────────────────────────

    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta valores anómalos usando IQR."""
        anomalies: Dict[str, Any] = {}

        for col in df.select_dtypes(include=[np.number]).columns:
            values = df[col].dropna()
            if len(values) < 5:
                continue
            Q1 = float(values.quantile(0.25))
            Q3 = float(values.quantile(0.75))
            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            outliers = values[(values < lower) | (values > upper)]
            if len(outliers) > 0:
                anomalies[col] = {
                    "count": len(outliers),
                    "percentage": round((len(outliers) / len(values)) * 100, 2),
                    "bounds": {"lower": round(lower, 2), "upper": round(upper, 2)},
                }

        return anomalies

    # ─── KPIs globales ───────────────────────────────────────────────────────

    def _calculate_global_kpis(self) -> Dict[str, Any]:
        """Calcula KPIs globales de todo el dataset."""
        total_records = sum(len(df) for df in self.sheets_data.values())
        total_columns = sum(len(df.columns) for df in self.sheets_data.values())
        n_sheets = len(self.sheets_data)

        return {
            "total_sheets": n_sheets,
            "total_records": total_records,
            "total_columns": total_columns,
            "avg_records_per_sheet": round(total_records / max(1, n_sheets), 2),
        }

    # ─── Formateo para reporte ───────────────────────────────────────────────

    def format_for_report(self) -> str:
        """Formatea resultados del análisis para incluir en el reporte.
        Genérico: analiza todas las columnas sin asumir dominio específico."""
        analysis = self.analyze()

        report = "## ANÁLISIS CUANTITATIVO DETERMINISTA\n\n"

        # KPIs globales
        report += "### MÉTRICAS GLOBALES\n"
        for key, value in analysis["global_kpis"].items():
            report += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        report += "\n"

        # Análisis por hoja
        for sheet_name, df in self.sheets_data.items():
            report += f"### ANÁLISIS DE HOJA: '{sheet_name}'\n\n"
            report += f"**Total registros**: {len(df)}\n\n"

            # ── Columnas numéricas: estadísticas descriptivas ──
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                report += "#### ESTADÍSTICAS NUMÉRICAS\n\n"
                report += "| Columna | Media | Mediana | Mín | Máx | Desv. Std |\n"
                report += "|---------|-------|---------|-----|-----|-----------|\n"
                for col in numeric_cols:
                    vals = df[col].dropna()
                    if len(vals) == 0:
                        continue
                    report += (
                        f"| {col} | {vals.mean():.2f} | {vals.median():.2f} "
                        f"| {vals.min():.2f} | {vals.max():.2f} | {vals.std():.2f} |\n"
                    )
                report += "\n"

            # ── Columnas categóricas: distribución de valores ──
            categorical_cols = df.select_dtypes(include=["object"]).columns
            if len(categorical_cols) > 0:
                report += "#### DISTRIBUCIÓN POR COLUMNAS CATEGÓRICAS\n\n"
                for col in categorical_cols:
                    col_data = df[col].dropna()
                    if len(col_data) == 0:
                        continue
                    value_counts = col_data.value_counts()
                    if len(value_counts) > MAX_CATEGORIES_DISPLAY:
                        continue
                    total = len(col_data)
                    report += f"**{col}:**\n"
                    report += "| Valor | Cantidad | Porcentaje |\n"
                    report += "|-------|----------|------------|\n"
                    for val, count in value_counts.items():
                        pct = (count / total) * 100
                        val_str = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
                        report += f"| {val_str} | {count} | {pct:.1f}% |\n"
                    report += "\n"

            # ── Columnas temporales ──
            datetime_cols = df.select_dtypes(include=["datetime"]).columns
            if len(datetime_cols) > 0:
                report += "#### RANGO TEMPORAL\n\n"
                for col in datetime_cols:
                    vals = df[col].dropna()
                    if len(vals) > 0:
                        report += f"- **{col}**: {vals.min().strftime('%d/%m/%Y')} → {vals.max().strftime('%d/%m/%Y')}\n"
                report += "\n"

            # ── Correlaciones fuertes ──
            correlations = analysis["correlations"].get(sheet_name, {})
            strong_corr = correlations.get("strong_correlations", [])
            if strong_corr:
                report += "#### CORRELACIONES SIGNIFICATIVAS (|r| > 0.5)\n\n"
                report += "| Variable 1 | Variable 2 | Correlación |\n"
                report += "|-----------|-----------|-------------|\n"
                for c in strong_corr:
                    report += f"| {c['var1']} | {c['var2']} | {c['correlation']:.2f} |\n"
                report += "\n"

            # ── Anomalías detectadas ──
            anomalies = analysis["anomalies"].get(sheet_name, {})
            if anomalies:
                report += "#### ANOMALÍAS DETECTADAS (IQR)\n\n"
                report += "| Columna | Outliers | % del total | Rango esperado |\n"
                report += "|---------|----------|-------------|----------------|\n"
                for col, info in anomalies.items():
                    report += (
                        f"| {col} | {info['count']} | {info['percentage']:.1f}% "
                        f"| [{info['bounds']['lower']:.2f}, {info['bounds']['upper']:.2f}] |\n"
                    )
                report += "\n"

            # ── Tendencias ──
            trends = analysis["trends"].get(sheet_name, {})
            if trends:
                report += "#### TENDENCIAS TEMPORALES\n\n"
                for col, info in trends.items():
                    direction = "↑ Creciente" if info["trend"] == "increasing" else "↓ Decreciente"
                    report += f"- **{col}**: {direction} (pendiente: {info['slope']})\n"
                report += "\n"

        return report
