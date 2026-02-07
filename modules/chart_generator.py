# -*- coding: utf-8 -*-
"""
Generador de gráficos profesionales con matplotlib.
Soporta: barras, barras horizontales, líneas, pie, scatter, histograma, heatmap.
También genera gráficos a partir de tablas markdown extraídas del informe.
"""
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
import re as _re
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from .config import THEME, MAX_CHART_CATEGORIES

logger = logging.getLogger(__name__)

# Paleta corporativa Movimer
_CORP_PALETTE = [
    "#70ae00", "#8cc000", "#aacf65", "#3d6b00",
    "#575757", "#7f7f7f", "#2c2c2c", "#b5b5b5",
    "#4a8c00", "#c8e690",
]


@dataclass
class ChartConfig:
    """Configuración de un gráfico individual."""
    chart_type: str          # bar, bar_h, line, pie, scatter, histogram, heatmap
    title: str
    sheet_name: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    group_by: Optional[str] = None
    color_index: int = 0     # Índice en la paleta de colores


class ChartGenerator:
    """Genera gráficos profesionales como imágenes PNG en memoria."""

    def __init__(self, sheets_data: Dict[str, pd.DataFrame]):
        self.sheets_data = sheets_data
        self._setup_style()

    def _setup_style(self) -> None:
        """Configura el estilo global de matplotlib — look ejecutivo."""
        plt.rcParams.update({
            "figure.facecolor": "#FAFAFA",
            "axes.facecolor": "#FAFAFA",
            "axes.edgecolor": "#D0D0D0",
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.alpha": 0.25,
            "grid.color": "#C0C0C0",
            "grid.linestyle": "--",
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.titlepad": 14,
            "axes.labelsize": 11,
            "axes.labelpad": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "figure.dpi": 150,
        })

    def generate_chart(self, config: ChartConfig) -> Optional[bytes]:
        """Genera un gráfico según la configuración y devuelve bytes PNG."""
        df = self.sheets_data.get(config.sheet_name)
        if df is None or df.empty:
            logger.warning("Hoja '%s' no encontrada o vacía", config.sheet_name)
            return None

        try:
            generators = {
                "bar": self._generate_bar,
                "bar_h": self._generate_bar_h,
                "line": self._generate_line,
                "pie": self._generate_pie,
                "scatter": self._generate_scatter,
                "histogram": self._generate_histogram,
                "heatmap": self._generate_heatmap,
            }
            generator = generators.get(config.chart_type)
            if generator is None:
                logger.warning("Tipo de gráfico no soportado: %s", config.chart_type)
                return None

            fig = generator(df, config)
            if fig is None:
                return None

            return self._fig_to_png(fig)

        except Exception as e:
            logger.error("Error generando gráfico '%s': %s", config.title, e)
            return None

    def generate_all(self, configs: List[ChartConfig]) -> List[Tuple[str, bytes]]:
        """Genera todos los gráficos configurados. Devuelve lista de (título, bytes_png)."""
        results = []
        for config in configs:
            png_bytes = self.generate_chart(config)
            if png_bytes:
                results.append((config.title, png_bytes))
        return results

    # ─── Generadores individuales ────────────────────────────────────────────

    def _generate_bar(self, df: pd.DataFrame, config: ChartConfig) -> Optional[plt.Figure]:
        """Gráfico de barras verticales."""
        if not config.x_column:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = self._get_colors(config.color_index)

        if config.y_column and config.y_column in df.columns:
            # Barras con x categórico e y numérico
            data = df.groupby(config.x_column)[config.y_column].sum().sort_values(ascending=False)
            data = data.head(MAX_CHART_CATEGORIES)
            ax.bar(range(len(data)), data.values, color=colors[:len(data)])
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels([str(x)[:20] for x in data.index], rotation=45, ha="right")
            ax.set_ylabel(config.y_column)
        else:
            # Distribución de columna categórica
            data = df[config.x_column].value_counts().head(MAX_CHART_CATEGORIES)
            ax.bar(range(len(data)), data.values, color=colors[:len(data)])
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels([str(x)[:20] for x in data.index], rotation=45, ha="right")
            ax.set_ylabel("Frecuencia")

        ax.set_title(config.title)
        fig.tight_layout()
        return fig

    def _generate_bar_h(self, df: pd.DataFrame, config: ChartConfig) -> Optional[plt.Figure]:
        """Gráfico de barras horizontales."""
        if not config.x_column:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = self._get_colors(config.color_index)

        if config.y_column and config.y_column in df.columns:
            data = df.groupby(config.x_column)[config.y_column].sum().sort_values(ascending=True)
            data = data.tail(MAX_CHART_CATEGORIES)
        else:
            data = df[config.x_column].value_counts().sort_values(ascending=True).tail(MAX_CHART_CATEGORIES)

        ax.barh(range(len(data)), data.values, color=colors[:len(data)])
        ax.set_yticks(range(len(data)))
        ax.set_yticklabels([str(x)[:30] for x in data.index])
        ax.set_xlabel(config.y_column or "Frecuencia")
        ax.set_title(config.title)
        fig.tight_layout()
        return fig

    def _generate_line(self, df: pd.DataFrame, config: ChartConfig) -> Optional[plt.Figure]:
        """Gráfico de líneas."""
        if not config.x_column or not config.y_column:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        color = THEME.chart_palette[config.color_index % len(THEME.chart_palette)]

        plot_df = df[[config.x_column, config.y_column]].dropna().sort_values(config.x_column)

        ax.plot(plot_df[config.x_column], plot_df[config.y_column],
                color=color, linewidth=2, marker="o", markersize=4)
        ax.set_xlabel(config.x_column)
        ax.set_ylabel(config.y_column)
        ax.set_title(config.title)

        # Rotar etiquetas si son muchas
        if len(plot_df) > 10:
            plt.xticks(rotation=45, ha="right")

        fig.tight_layout()
        return fig

    def _generate_pie(self, df: pd.DataFrame, config: ChartConfig) -> Optional[plt.Figure]:
        """Gráfico circular (pie)."""
        if not config.x_column:
            return None

        fig, ax = plt.subplots(figsize=(8, 8))
        colors = self._get_colors(config.color_index)

        data = df[config.x_column].value_counts().head(MAX_CHART_CATEGORIES)

        # Agrupar categorías pequeñas en "Otros"
        if len(data) > 8:
            top = data.head(7)
            others = data.iloc[7:].sum()
            data = pd.concat([top, pd.Series({"Otros": others})])

        wedges, texts, autotexts = ax.pie(
            data.values,
            labels=[str(x)[:20] for x in data.index],
            autopct="%1.1f%%",
            colors=colors[:len(data)],
            startangle=90,
            pctdistance=0.85,
        )

        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight("bold")

        ax.set_title(config.title)
        fig.tight_layout()
        return fig

    def _generate_scatter(self, df: pd.DataFrame, config: ChartConfig) -> Optional[plt.Figure]:
        """Gráfico de dispersión."""
        if not config.x_column or not config.y_column:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        color = THEME.chart_palette[config.color_index % len(THEME.chart_palette)]

        plot_df = df[[config.x_column, config.y_column]].dropna()

        ax.scatter(plot_df[config.x_column], plot_df[config.y_column],
                   color=color, alpha=0.6, edgecolors="white", linewidth=0.5)
        ax.set_xlabel(config.x_column)
        ax.set_ylabel(config.y_column)
        ax.set_title(config.title)
        fig.tight_layout()
        return fig

    def _generate_histogram(self, df: pd.DataFrame, config: ChartConfig) -> Optional[plt.Figure]:
        """Histograma."""
        col = config.x_column or config.y_column
        if not col:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        color = THEME.chart_palette[config.color_index % len(THEME.chart_palette)]

        values = df[col].dropna()
        if not pd.api.types.is_numeric_dtype(values):
            return None

        ax.hist(values, bins=min(30, len(values.unique())), color=color,
                edgecolor="white", alpha=0.8)
        ax.set_xlabel(col)
        ax.set_ylabel("Frecuencia")
        ax.set_title(config.title)
        fig.tight_layout()
        return fig

    def _generate_heatmap(self, df: pd.DataFrame, config: ChartConfig) -> Optional[plt.Figure]:
        """Mapa de calor de correlaciones."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return None

        # Limitar a 15 columnas para legibilidad
        numeric_cols = numeric_cols[:15]
        corr = df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(max(8, len(numeric_cols)), max(6, len(numeric_cols) * 0.8)))

        im = ax.imshow(corr.values, cmap="RdBu_r", aspect="auto", vmin=-1, vmax=1)
        fig.colorbar(im, ax=ax, shrink=0.8)

        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels([c[:15] for c in numeric_cols], rotation=45, ha="right")
        ax.set_yticklabels([c[:15] for c in numeric_cols])

        # Anotar valores
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                val = corr.values[i, j]
                if not np.isnan(val):
                    text_color = "white" if abs(val) > 0.5 else "black"
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            color=text_color, fontsize=8)

        ax.set_title(config.title)
        fig.tight_layout()
        return fig

    # ─── Generación desde tablas del informe ────────────────────────────────

    def generate_from_table(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        chart_type: str = "bar",
        color_index: int = 0,
    ) -> Optional[bytes]:
        """Genera un gráfico a partir de datos tabulares extraídos del informe.

        Args:
            title: Título del gráfico.
            headers: Cabeceras de la tabla.
            rows: Filas de la tabla (lista de listas de strings).
            chart_type: 'bar', 'bar_h', 'pie', 'grouped_bar'.
            color_index: Índice de inicio en la paleta.

        Returns:
            Bytes PNG o None.
        """
        try:
            labels, numeric_cols = self._parse_table_data(headers, rows)
            if not labels or not numeric_cols:
                return None

            generators = {
                "bar": self._table_bar,
                "bar_h": self._table_bar_h,
                "pie": self._table_pie,
                "grouped_bar": self._table_grouped_bar,
            }
            gen = generators.get(chart_type, self._table_bar)
            fig = gen(title, labels, numeric_cols, color_index)
            if fig is None:
                return None
            return self._fig_to_png(fig)

        except Exception as e:
            logger.error("Error generando gráfico de tabla '%s': %s", title, e)
            return None

    @staticmethod
    def _parse_table_data(
        headers: List[str], rows: List[List[str]]
    ) -> Tuple[List[str], Dict[str, List[float]]]:
        """Convierte datos tabulares a etiquetas + columnas numéricas."""
        if not rows or not headers:
            return [], {}

        # Encontrar columnas numéricas vs etiqueta
        label_col_idx = 0
        numeric_cols: Dict[str, List[float]] = {}

        for col_idx in range(len(headers)):
            num_values = []
            is_numeric = False
            for row in rows:
                if col_idx >= len(row):
                    num_values.append(0.0)
                    continue
                val = row[col_idx]
                # Limpiar y extraer número
                clean = val.replace(",", "").replace("$", "").replace("€", "").replace("%", "").strip()
                m = _re.search(r"-?\d+\.?\d*", clean)
                if m:
                    num_values.append(float(m.group()))
                    is_numeric = True
                else:
                    num_values.append(0.0)

            if is_numeric and sum(1 for v in num_values if v != 0.0) >= len(rows) * 0.4:
                numeric_cols[headers[col_idx]] = num_values

        # Etiquetas: primera columna no numérica
        labels = []
        for col_idx in range(len(headers)):
            if headers[col_idx] not in numeric_cols:
                label_col_idx = col_idx
                labels = [row[col_idx] if col_idx < len(row) else "" for row in rows]
                break

        if not labels:
            labels = [row[0] if row else "" for row in rows]

        # Truncar etiquetas largas
        labels = [l[:30] for l in labels]

        return labels, numeric_cols

    def _table_bar(
        self, title: str, labels: List[str],
        numeric_cols: Dict[str, List[float]], color_index: int,
    ) -> Optional[plt.Figure]:
        """Barras verticales desde datos de tabla."""
        col_name = next(iter(numeric_cols))
        values = numeric_cols[col_name]

        fig, ax = plt.subplots(figsize=(8, 5))
        colors = self._get_corp_colors(len(values), color_index)
        bars = ax.bar(range(len(values)), values, color=colors, width=0.65,
                      edgecolor="white", linewidth=0.5)

        # Etiquetas de valor encima de las barras
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    self._format_value(val), ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color="#333333")

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=9)
        ax.set_ylabel(col_name, fontsize=10)
        ax.set_title(title, fontsize=13, fontweight="bold", color="#3d6b00", pad=12)
        ax.set_axisbelow(True)
        fig.tight_layout()
        return fig

    def _table_bar_h(
        self, title: str, labels: List[str],
        numeric_cols: Dict[str, List[float]], color_index: int,
    ) -> Optional[plt.Figure]:
        """Barras horizontales desde datos de tabla."""
        col_name = next(iter(numeric_cols))
        values = numeric_cols[col_name]

        fig, ax = plt.subplots(figsize=(8, max(4, len(values) * 0.5)))
        colors = self._get_corp_colors(len(values), color_index)
        y_pos = range(len(values))
        bars = ax.barh(y_pos, values, color=colors, height=0.6,
                       edgecolor="white", linewidth=0.5)

        for bar, val in zip(bars, values):
            ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                    f"  {self._format_value(val)}", ha="left", va="center",
                    fontsize=9, fontweight="bold", color="#333333")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel(col_name, fontsize=10)
        ax.set_title(title, fontsize=13, fontweight="bold", color="#3d6b00", pad=12)
        ax.invert_yaxis()
        ax.set_axisbelow(True)
        fig.tight_layout()
        return fig

    def _table_pie(
        self, title: str, labels: List[str],
        numeric_cols: Dict[str, List[float]], color_index: int,
    ) -> Optional[plt.Figure]:
        """Gráfico circular desde datos de tabla."""
        col_name = next(iter(numeric_cols))
        values = numeric_cols[col_name]
        # Filtrar valores <= 0
        filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
        if not filtered:
            return None
        labels_f, values_f = zip(*filtered)

        fig, ax = plt.subplots(figsize=(7, 6))
        colors = self._get_corp_colors(len(values_f), color_index)

        wedges, texts, autotexts = ax.pie(
            values_f,
            labels=None,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            pctdistance=0.8,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        for at in autotexts:
            at.set_fontsize(9)
            at.set_fontweight("bold")
            at.set_color("white")
            at.set_path_effects([pe.withStroke(linewidth=2, foreground="#333")])

        ax.legend(labels_f, loc="center left", bbox_to_anchor=(1, 0.5),
                  fontsize=9, frameon=False)
        ax.set_title(title, fontsize=13, fontweight="bold", color="#3d6b00", pad=12)
        fig.tight_layout()
        return fig

    def _table_grouped_bar(
        self, title: str, labels: List[str],
        numeric_cols: Dict[str, List[float]], color_index: int,
    ) -> Optional[plt.Figure]:
        """Barras agrupadas para tablas con múltiples columnas numéricas."""
        n_groups = len(labels)
        n_bars = len(numeric_cols)
        bar_width = 0.7 / n_bars

        fig, ax = plt.subplots(figsize=(max(8, n_groups * 0.8), 5))

        for i, (col_name, values) in enumerate(numeric_cols.items()):
            x = np.arange(n_groups) + i * bar_width
            color = _CORP_PALETTE[(color_index + i) % len(_CORP_PALETTE)]
            ax.bar(x, values, width=bar_width, label=col_name, color=color,
                   edgecolor="white", linewidth=0.5)

        ax.set_xticks(np.arange(n_groups) + bar_width * (n_bars - 1) / 2)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=9)
        ax.legend(fontsize=9, frameon=False)
        ax.set_title(title, fontsize=13, fontweight="bold", color="#3d6b00", pad=12)
        ax.set_axisbelow(True)
        fig.tight_layout()
        return fig

    # ─── Utilidades

    @staticmethod
    def _format_value(val: float) -> str:
        """Formatea un valor para etiqueta: entero si es redondo, 1 decimal si no."""
        if val == int(val):
            return f"{int(val):,}".replace(",", ".")
        return f"{val:,.1f}".replace(",", ".")

    @staticmethod
    def _get_corp_colors(n: int, start: int = 0) -> List[str]:
        """Devuelve n colores de la paleta corporativa."""
        palette = _CORP_PALETTE
        return [palette[(start + i) % len(palette)] for i in range(n)]

    def _get_colors(self, start_index: int = 0) -> List[str]:
        """Devuelve la paleta de colores rotada desde start_index."""
        palette = THEME.chart_palette
        n = len(palette)
        return [palette[(start_index + i) % n] for i in range(n * 3)]

    def _fig_to_png(self, fig: plt.Figure) -> bytes:
        """Convierte una figura matplotlib a bytes PNG."""
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    @staticmethod
    def suggest_charts(sheets_data: Dict[str, pd.DataFrame]) -> List[ChartConfig]:
        """Sugiere gráficos automáticos basados en la estructura de los datos."""
        suggestions: List[ChartConfig] = []
        color_idx = 0

        for sheet_name, df in sheets_data.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
            datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

            # Sugerir barras para categóricas con pocas categorías
            for col in categorical_cols[:3]:
                if 1 < df[col].nunique() <= MAX_CHART_CATEGORIES:
                    suggestions.append(ChartConfig(
                        chart_type="bar",
                        title=f"Distribución: {col}",
                        sheet_name=sheet_name,
                        x_column=col,
                        color_index=color_idx,
                    ))
                    color_idx += 1

            # Sugerir histograma para numéricas
            for col in numeric_cols[:2]:
                suggestions.append(ChartConfig(
                    chart_type="histogram",
                    title=f"Distribución: {col}",
                    sheet_name=sheet_name,
                    x_column=col,
                    color_index=color_idx,
                ))
                color_idx += 1

            # Sugerir línea temporal si hay fechas
            if datetime_cols and numeric_cols:
                suggestions.append(ChartConfig(
                    chart_type="line",
                    title=f"Evolución: {numeric_cols[0]} en el tiempo",
                    sheet_name=sheet_name,
                    x_column=datetime_cols[0],
                    y_column=numeric_cols[0],
                    color_index=color_idx,
                ))
                color_idx += 1

            # Sugerir heatmap si hay 3+ numéricas
            if len(numeric_cols) >= 3:
                suggestions.append(ChartConfig(
                    chart_type="heatmap",
                    title=f"Correlaciones: {sheet_name}",
                    sheet_name=sheet_name,
                    color_index=color_idx,
                ))
                color_idx += 1

        return suggestions
