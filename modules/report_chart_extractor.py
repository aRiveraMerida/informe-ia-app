# -*- coding: utf-8 -*-
"""
Extrae secciones y tablas del informe ejecutivo de Claude,
genera gráficos automáticos a partir de las tablas encontradas.
"""
import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .chart_generator import ChartGenerator

logger = logging.getLogger(__name__)


@dataclass
class ReportSection:
    """Sección del informe con su texto y gráficos asociados."""
    heading: str                         # Título de la sección (## ...)
    text: str                            # Contenido markdown de la sección
    chart_images: List[Tuple[str, bytes]] = field(default_factory=list)


# ─── Parsing ─────────────────────────────────────────────────────────────────

def extract_sections(markdown: str) -> List[ReportSection]:
    """Divide el informe markdown en secciones por ## (heading nivel 2).

    El texto antes del primer ## se agrupa como sección con heading vacío.
    """
    sections: List[ReportSection] = []
    # Separar por líneas que empiecen con ##, pero NO ### ni más
    pattern = re.compile(r"^(## .+)$", re.MULTILINE)
    parts = pattern.split(markdown)

    # parts alterna entre texto-antes y heading+texto-después
    i = 0
    while i < len(parts):
        part = parts[i]
        if pattern.match(part.strip()):
            heading = part.strip().lstrip("#").strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append(ReportSection(heading=heading, text=body.strip()))
            i += 2
        else:
            # Texto antes del primer ## (puede incluir # título principal)
            if part.strip():
                sections.append(ReportSection(heading="", text=part.strip()))
            i += 1

    return sections


def extract_tables(text: str) -> List[Tuple[str, List[str], List[List[str]]]]:
    """Extrae tablas markdown de un bloque de texto.

    Returns:
        Lista de (context_hint, headers, rows).
        context_hint: línea anterior a la tabla (a menudo un subtítulo).
    """
    lines = text.split("\n")
    tables: List[Tuple[str, List[str], List[List[str]]]] = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        # Detectar inicio de tabla: línea con | seguida de separador ---
        if (
            "|" in line
            and i + 1 < len(lines)
            and re.search(r"-{2,}", lines[i + 1])
            and "|" in lines[i + 1]
        ):
            # Contexto: línea anterior no vacía
            context = ""
            for back in range(i - 1, max(i - 4, -1), -1):
                candidate = lines[back].strip()
                if candidate and not candidate.startswith("|"):
                    context = candidate.lstrip("#").strip(" *_")
                    break

            headers = _parse_table_row(line)
            i += 2  # Saltar separador

            rows: List[List[str]] = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                row = _parse_table_row(lines[i])
                if row:
                    rows.append(row)
                i += 1

            if headers and rows:
                tables.append((context, headers, rows))
            continue

        i += 1

    return tables


def _parse_table_row(line: str) -> List[str]:
    """Parsea una fila de tabla markdown en celdas limpias."""
    cells = [c.strip() for c in line.split("|")]
    # Eliminar celdas vacías de los bordes
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


# ─── Análisis de tablas y selección de gráfico ───────────────────────────────

def _extract_numeric(value: str) -> Optional[float]:
    """Intenta extraer un número de una celda (maneja %, $, comas, etc.)."""
    clean = value.replace(",", "").replace("$", "").replace("€", "").strip()
    # Extraer primer número con decimales
    m = re.search(r"-?\d+\.?\d*", clean)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None


def _has_percentage_column(headers: List[str], rows: List[List[str]]) -> Optional[int]:
    """Busca una columna que contenga porcentajes. Devuelve índice o None."""
    for col_idx in range(len(headers)):
        pct_count = 0
        for row in rows:
            if col_idx < len(row) and "%" in row[col_idx]:
                pct_count += 1
        if pct_count >= len(rows) * 0.5:
            return col_idx
    return None


def _find_numeric_columns(headers: List[str], rows: List[List[str]]) -> List[int]:
    """Identifica columnas numéricas (>50% de celdas son números)."""
    numeric_cols = []
    for col_idx in range(len(headers)):
        num_count = 0
        for row in rows:
            if col_idx < len(row) and _extract_numeric(row[col_idx]) is not None:
                num_count += 1
        if num_count >= len(rows) * 0.5:
            numeric_cols.append(col_idx)
    return numeric_cols


def determine_chart_type(
    headers: List[str], rows: List[List[str]]
) -> Optional[str]:
    """Decide el tipo de gráfico más apropiado para una tabla.

    Returns:
        'bar', 'bar_h', 'pie', 'grouped_bar' o None si no se debe graficar.
    """
    if len(rows) < 2 or len(headers) < 2:
        return None

    pct_col = _has_percentage_column(headers, rows)
    numeric_cols = _find_numeric_columns(headers, rows)

    # Tabla de KPIs (etiqueta + valor + estado) → barras horizontales siempre
    if len(rows) <= 12 and len(numeric_cols) == 1:
        if pct_col is not None and len(rows) <= 8:
            return "pie"
        return "bar" if len(rows) <= 8 else "bar_h"

    # Tabla con múltiples columnas numéricas → barras agrupadas
    if len(numeric_cols) >= 2:
        return "grouped_bar"

    # Tabla con una columna numérica
    if len(numeric_cols) == 1:
        if pct_col is not None and len(rows) <= 8:
            return "pie"
        return "bar" if len(rows) <= 8 else "bar_h"

    return None


# ─── Generación de gráficos para el informe ──────────────────────────────────

def generate_charts_for_report(
    markdown: str,
    chart_gen: Optional[ChartGenerator] = None,
) -> List[ReportSection]:
    """Pipeline completo: parsea informe → extrae tablas → genera gráficos.

    Args:
        markdown: Texto markdown del informe ejecutivo de Claude.
        chart_gen: Instancia de ChartGenerator (para reusar estilo).
                   Si es None, se crea una sin datos de hojas.

    Returns:
        Lista de ReportSection con gráficos asociados.
    """
    if chart_gen is None:
        chart_gen = ChartGenerator(sheets_data={})

    sections = extract_sections(markdown)
    color_idx = 0

    for section in sections:
        tables = extract_tables(section.text)

        for context, headers, rows in tables:
            chart_type = determine_chart_type(headers, rows)
            if chart_type is None:
                continue

            # Título del gráfico: contexto o heading de la sección
            chart_title = context if context else section.heading
            if not chart_title:
                chart_title = "Datos del informe"

            try:
                png_bytes = chart_gen.generate_from_table(
                    title=chart_title,
                    headers=headers,
                    rows=rows,
                    chart_type=chart_type,
                    color_index=color_idx,
                )
                if png_bytes:
                    section.chart_images.append((chart_title, png_bytes))
                    color_idx += 1
            except Exception as e:
                logger.warning("Error generando gráfico para '%s': %s", chart_title, e)

    return sections
