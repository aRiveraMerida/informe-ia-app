# -*- coding: utf-8 -*-
"""
Configuración centralizada de la aplicación.
"""
from dataclasses import dataclass, field
from typing import Dict, List


# ─── Modelos de IA ───────────────────────────────────────────────────────────

MODELS: List[str] = [
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    "claude-haiku-4-20250514",
]

MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "claude-haiku-4-20250514": {"input": 0.80, "output": 4.00},
}

MODEL_LABELS: Dict[str, str] = {
    "claude-sonnet-4-20250514": "Sonnet 4 – Mejor balance calidad/precio",
    "claude-opus-4-20250514": "Opus 4 – Máxima calidad",
    "claude-haiku-4-20250514": "Haiku 4 – Más económico",
}


# ─── Tipos de informe ────────────────────────────────────────────────────────

REPORT_TYPES: List[str] = [
    "Análisis General",
    "Análisis de Encuestas",
    "Satisfacción del Cliente",
    "Ventas y KPIs",
    "Operaciones",
    "Marketing y Campañas",
    "Recursos Humanos",
    "Financiero",
    "Personalizado",
]


# ─── Tipos de gráfico ────────────────────────────────────────────────────────

CHART_TYPES: Dict[str, str] = {
    "bar": "Barras",
    "bar_h": "Barras Horizontales",
    "line": "Líneas",
    "pie": "Circular (Pie)",
    "scatter": "Dispersión (Scatter)",
    "histogram": "Histograma",
    "heatmap": "Mapa de Calor (Correlaciones)",
}

# Tipos de gráfico recomendados según tipo de columna
CHART_RECOMMENDATIONS = {
    "categorical": ["bar", "bar_h", "pie"],
    "numeric": ["histogram", "line", "scatter"],
    "temporal": ["line", "bar"],
    "correlation": ["heatmap", "scatter"],
}


# ─── Tema de colores ─────────────────────────────────────────────────────────

@dataclass
class ThemeColors:
    primary: str = "#70ae00"
    secondary: str = "#8cc000"
    accent: str = "#70ae00"
    accent_light: str = "#aacf65"
    success: str = "#70ae00"
    warning: str = "#FFC107"
    error: str = "#DC3545"
    text_dark: str = "#000000"
    text_muted: str = "#575757"
    bg_light: str = "#f6f6f6"
    white: str = "#FFFFFF"

    # Paleta para gráficos (10 colores) — Movimer
    chart_palette: List[str] = field(default_factory=lambda: [
        "#70ae00", "#8cc000", "#aacf65", "#3d6b00",
        "#575757", "#7f7f7f", "#b5b5b5", "#2c2c2c",
        "#4a8c00", "#c8e690",
    ])


THEME = ThemeColors()


# ─── Límites ─────────────────────────────────────────────────────────────────

MAX_UPLOAD_SIZE_MB = 200
MAX_ROWS_MARKDOWN = 2000
MAX_CATEGORIES_DISPLAY = 30
MAX_CHART_CATEGORIES = 20
DEFAULT_MAX_TOKENS = 16000
DEFAULT_SAMPLE_ROWS = 5
