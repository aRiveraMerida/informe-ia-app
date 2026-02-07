# -*- coding: utf-8 -*-
"""
Gestión centralizada del session state de Streamlit.
"""
import streamlit as st
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# Claves y valores por defecto del session state
_DEFAULTS: Dict[str, Any] = {
    "analysis_complete": False,
    "quantitative_results": None,
    "qualitative_results": None,
    "processed_data": None,
    "cost_summary": None,
    "file_content": None,
    "filename": None,
    "chart_configs": [],       # Lista de configuraciones de gráficos del usuario
    "chart_images": [],        # Lista de bytes PNG generados
    "custom_prompt": None,     # Prompt personalizado (None = usar default)
}


def init_session_state() -> None:
    """Inicializa todas las claves del session state con valores por defecto."""
    for key, default_value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_session_state() -> None:
    """Reinicia todo el session state (para analizar otro archivo)."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def reset_analysis() -> None:
    """Reinicia solo los resultados del análisis, manteniendo el archivo."""
    analysis_keys = [
        "analysis_complete", "quantitative_results", "qualitative_results",
        "processed_data", "cost_summary", "chart_images",
    ]
    for key in analysis_keys:
        st.session_state[key] = _DEFAULTS.get(key)


def store_file(content: bytes, filename: str) -> None:
    """Almacena el archivo subido en session state."""
    st.session_state.file_content = content
    st.session_state.filename = filename


def store_analysis_results(
    processed_data: Dict[str, Any],
    quantitative_results: Dict[str, Any],
    qualitative_results: Dict[str, Any],
    cost_summary: Dict[str, Any],
) -> None:
    """Almacena los resultados completos del análisis."""
    st.session_state.processed_data = processed_data
    st.session_state.quantitative_results = quantitative_results
    st.session_state.qualitative_results = qualitative_results
    st.session_state.cost_summary = cost_summary
    st.session_state.analysis_complete = True


def store_chart_images(images: List[bytes]) -> None:
    """Almacena las imágenes de gráficos generados."""
    st.session_state.chart_images = images


def get(key: str, default: Any = None) -> Any:
    """Obtiene un valor del session state con fallback."""
    return st.session_state.get(key, default)
