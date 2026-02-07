# -*- coding: utf-8 -*-
"""
Gestión de prompts editables con variables de plantilla.
Soporte para plantillas especializadas por tipo de informe.
"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ─── Directorio de plantillas ─────────────────────────────────────────────────

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Mapeo: tipo de informe → archivo de plantilla
TEMPLATE_MAP: Dict[str, str] = {
    "Ventas y KPIs": "ventas_kpis.txt",
    "Satisfacción del Cliente": "satisfaccion_cliente.txt",
    "Análisis de Encuestas": "encuestas.txt",
    "Operaciones": "operaciones.txt",
    "Marketing y Campañas": "marketing.txt",
    "Recursos Humanos": "recursos_humanos.txt",
    "Financiero": "financiero.txt",
}

# ─── Prompt por defecto (genérico para cualquier dataset) ────────────────────

DEFAULT_PROMPT = """Eres un consultor senior de datos especializado en generar INFORMES EJECUTIVOS profesionales para cualquier industria o dominio.

# CONTEXTO DEL ANÁLISIS
- **Cliente:** {client_name}
- **Periodo:** {period}
- **Tipo de informe:** {report_type}
- **Total registros analizados:** {total_records}

---

# DATOS COMPLETOS DEL ARCHIVO (ANALIZA TODOS)

{data_summary}

---

# ANÁLISIS CUANTITATIVO PREVIO (YA CALCULADO)

{quantitative_analysis}

---

# TU TAREA: GENERAR INFORME EJECUTIVO PROFESIONAL

Analiza los datos proporcionados y genera un informe ejecutivo en formato Markdown.
**IMPORTANTE:** Todos los números, porcentajes y datos DEBEN provenir de los datos proporcionados. NO inventes datos.

Adapta la estructura del informe al tipo de datos detectado. Usa la siguiente estructura como guía:

---

# INFORME EJECUTIVO
## {report_type}

**Cliente:** {client_name}
**Periodo:** {period}
**Registros analizados:** {total_records}
**Fecha del informe:** [fecha actual]

---

## 1. RESUMEN EJECUTIVO

[Párrafo de 3-5 líneas resumiendo los hallazgos principales con datos concretos extraídos del dataset]

### Indicadores Clave de Rendimiento

| KPI | Valor | Estado |
|-----|-------|--------|
| [KPI relevante 1] | XX% (N de M) | [Bueno/Regular/Crítico] |
| [KPI relevante 2] | XX% (N de M) | [Bueno/Regular/Crítico] |
| [KPI relevante 3] | XX | [Bueno/Regular/Crítico] |

*(Selecciona los KPIs más relevantes según el tipo de datos)*

---

## 2. ANÁLISIS DETALLADO POR DIMENSIÓN

Para cada dimensión principal de los datos, genera una sección con:
- Tablas con cantidades absolutas Y porcentajes
- Hallazgos e insights específicos
- Patrones detectados

*(Adapta las secciones al contenido real de los datos: si son ventas, analiza por producto/región/vendedor; si son encuestas, por preguntas/respuestas; si son operaciones, por procesos/métricas; etc.)*

---

## 3. ANÁLISIS DE TENDENCIAS Y PATRONES

[Si hay datos temporales, analiza evolución. Si no, analiza distribuciones y concentraciones]

---

## 4. ANÁLISIS COMPARATIVO Y SEGMENTACIÓN

[Cruza variables para encontrar insights: ej. satisfacción por segmento, ventas por canal, rendimiento por equipo]

---

## 5. BRECHAS Y ANOMALÍAS DETECTADAS

[Identifica contradicciones, outliers o patrones inesperados en los datos]

**Brecha detectada:** [descripción]
- Dato 1: [valor]
- Dato 2: [valor contradictorio]
- **Impacto potencial:** [análisis]
- **Hipótesis:** [explicación posible]

---

## 6. CONCLUSIONES Y RECOMENDACIONES

### Fortalezas identificadas
1. [Fortaleza] - Dato: [número concreto]
2. [Fortaleza] - Dato: [número concreto]

### Áreas críticas de mejora
1. **[Problema]:** [descripción] - Impacto: [estimación]
2. **[Problema]:** [descripción] - Impacto: [estimación]

### Plan de acción recomendado

**Inmediato (0-30 días):**
- [Acción específica con objetivo medible]

**Corto plazo (1-3 meses):**
- [Iniciativa táctica]

**Medio plazo (3-6 meses):**
- [Transformación estratégica]

---

## REGLAS QUE DEBES SEGUIR:

1. **USA SOLO DATOS REALES** - Cada número debe venir de los datos proporcionados
2. **CALCULA PORCENTAJES** - Siempre muestra cantidad absoluta Y porcentaje
3. **SÉ ESPECÍFICO** - Usa nombres reales de columnas, categorías y valores del dataset
4. **IDENTIFICA PATRONES** - Busca tendencias, concentraciones y distribuciones
5. **DETECTA BRECHAS** - Si hay contradicciones, analiza por qué
6. **RECOMENDACIONES ACCIONABLES** - No generes recomendaciones genéricas; deben basarse en los datos
7. **ADAPTA LA ESTRUCTURA** - Si los datos no encajan en alguna sección, omítela o adáptala

**GENERA EL INFORME AHORA.**"""


# ─── Variables disponibles ───────────────────────────────────────────────────

TEMPLATE_VARIABLES = {
    "client_name": "Nombre del cliente",
    "period": "Periodo analizado",
    "report_type": "Tipo de informe seleccionado",
    "total_records": "Número total de registros",
    "data_summary": "Datos del archivo convertidos a texto (se inserta automáticamente)",
    "quantitative_analysis": "Análisis cuantitativo calculado (se inserta automáticamente)",
}


def render_prompt(
    template: str,
    client_name: str,
    period: str,
    report_type: str,
    total_records: int,
    data_summary: str,
    quantitative_analysis: str,
) -> str:
    """Renderiza el prompt sustituyendo las variables de plantilla."""
    return template.format(
        client_name=client_name,
        period=period,
        report_type=report_type,
        total_records=total_records,
        data_summary=data_summary,
        quantitative_analysis=quantitative_analysis,
    )


def load_template(report_type: str) -> str:
    """Carga la plantilla especializada para el tipo de informe.
    Si no existe, devuelve DEFAULT_PROMPT."""
    filename = TEMPLATE_MAP.get(report_type)
    if filename:
        filepath = _PROMPTS_DIR / filename
        if filepath.exists():
            try:
                return filepath.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning("Error leyendo plantilla '%s': %s", filepath, e)
    return DEFAULT_PROMPT


def get_available_templates() -> Dict[str, str]:
    """Devuelve dict con las plantillas disponibles {tipo: ruta}."""
    available = {}
    for report_type, filename in TEMPLATE_MAP.items():
        filepath = _PROMPTS_DIR / filename
        if filepath.exists():
            available[report_type] = str(filepath)
    return available


def get_prompt(custom_prompt: Optional[str] = None, report_type: Optional[str] = None) -> str:
    """Devuelve el prompt personalizado, la plantilla del tipo de informe, o el default."""
    if custom_prompt and custom_prompt.strip():
        return custom_prompt.strip()
    if report_type and report_type not in ("Análisis General", "Personalizado"):
        return load_template(report_type)
    return DEFAULT_PROMPT


def get_variables_help() -> str:
    """Devuelve texto de ayuda sobre las variables disponibles."""
    lines = ["**Variables disponibles en el prompt:**"]
    for var, desc in TEMPLATE_VARIABLES.items():
        lines.append(f"- `{{{var}}}` → {desc}")
    return "\n".join(lines)
