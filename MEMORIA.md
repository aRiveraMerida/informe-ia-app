# MEMORIA DEL PROYECTO
## Generador de Informes Ejecutivos con IA — Movimer Group

**Versión:** 2.0
**Fecha:** Febrero 2026
**Cliente:** Movimer Group

---

## 1. DESCRIPCIÓN GENERAL

Plataforma web que transforma cualquier conjunto de datos tabulares (Excel / CSV) en informes ejecutivos profesionales mediante un enfoque de doble análisis:

1. **Análisis cuantitativo determinista** — Cálculo automático de KPIs, agregaciones, correlaciones, distribuciones estadísticas, tendencias temporales y detección de anomalías. No depende de IA, produce resultados reproducibles y verificables.

2. **Análisis estratégico con IA** — Interpretación cualitativa mediante Claude (Anthropic) que recibe como contexto el análisis cuantitativo previo y genera insights de negocio, oportunidades, riesgos y recomendaciones accionables.

El resultado se entrega en tres formatos: **PDF** (con marca corporativa), **DOCX** (editable en Word) y **PPTX** (presentación ejecutiva).

---

## 2. CAPACIDADES FUNCIONALES

### 2.1 Procesamiento de datos

- Lectura de archivos **Excel** (XLSX/XLS) con soporte para múltiples hojas.
- Lectura de archivos **CSV**.
- Detección automática de tipos de datos: numéricos, categóricos, temporales.
- Limpieza automática: eliminación de filas/columnas vacías, renombrado de columnas sin nombre.
- Inferencia inteligente de tipos (texto → número, texto → fecha).
- Vista previa interactiva de cada hoja antes de lanzar el análisis.
- Tamaño máximo de archivo: **200 MB**.

### 2.2 Validación de calidad de datos

Al cargar un archivo, el sistema evalúa automáticamente:

- **Score de calidad** (0–100) con indicador visual (Excelente / Bueno / Aceptable / Deficiente / Crítico).
- Detección de hojas vacías o con pocas filas.
- Columnas con porcentaje alto de valores nulos (>50%).
- Filas duplicadas.
- Columnas de varianza cero (un solo valor).
- Columnas categóricas que podrían ser numéricas (posible error de tipo).
- Lista expandible de incidencias con severidad (error / warning / info).

### 2.3 Análisis cuantitativo automático (sin IA)

- **KPIs numéricos:** media, mediana, desviación estándar, mínimo, máximo, suma.
- **KPIs categóricos:** valores únicos, moda, índice de diversidad.
- **Agregaciones cruzadas:** métricas numéricas agrupadas por columnas categóricas.
- **Distribuciones:** cuartiles (Q1, Q2, Q3), asimetría (skewness), curtosis (kurtosis).
- **Correlaciones:** matriz completa + detección de correlaciones significativas (|r| > 0.5).
- **Tendencias temporales:** detección automática de tendencia (creciente/decreciente) con pendiente calculada.
- **Anomalías:** detección de outliers mediante método IQR (rango intercuartílico).

### 2.4 Análisis estratégico con IA (Claude)

- Interpretación de datos cuantitativos en contexto de negocio.
- Identificación de hallazgos clave y patrones no evidentes.
- Recomendaciones priorizadas: quick wins (0–1 mes), tácticas (1–3 meses), estratégicas (3–12 meses).
- Detección de brechas y contradicciones en los datos.
- **Streaming en tiempo real:** la respuesta de Claude se muestra progresivamente mientras se genera, sin esperas.

### 2.5 Plantillas de prompt especializadas

El sistema selecciona automáticamente un prompt optimizado según el tipo de informe:

| Tipo de informe | Enfoque del prompt |
|---|---|
| Análisis General | Genérico para cualquier dataset |
| Ventas y KPIs | Dashboard comercial, análisis ABC, rentabilidad |
| Satisfacción del Cliente | NPS/CSAT, mapa de prioridades, brechas |
| Análisis de Encuestas | Ficha técnica, distribuciones, cruces |
| Operaciones | Eficiencia, cuellos de botella, tiempos |
| Marketing y Campañas | ROI/ROAS, rendimiento por canal/campaña |
| Recursos Humanos | Rotación, clima, composición de plantilla |
| Financiero | Ingresos, gastos, márgenes, liquidez |
| Personalizado | Prompt editable libremente por el usuario |

Los prompts son **editables desde la interfaz** (sección "Prompt Maestro"). Cualquier modificación se aplica solo a la sesión activa.

### 2.6 Generación de informes

**PDF:**
- Portada con logo Movimer, nombre del cliente, periodo y fecha.
- Secciones estructuradas con formato profesional.
- Gráficos integrados inline (generados automáticamente desde las tablas del informe).
- Pie de página con logo del cliente (opcional).
- Marca de agua discreta con fecha de generación.

**DOCX:**
- Misma estructura que el PDF, editable en Microsoft Word.
- Gráficos integrados como imágenes.
- Ideal para que el cliente personalice antes de presentar.

**PPTX:**
- Presentación ejecutiva con diseño Movimer (barras verdes corporativas).
- Portada con título, cliente, periodo y fecha.
- Un slide por sección del informe con texto simplificado.
- Gráficos integrados (máximo 2 por slide).
- Slide de cierre con metadatos de generación.

### 2.7 Gráficos automáticos

Los gráficos se generan automáticamente a partir de las **tablas que aparecen en el informe de IA**, sin intervención del usuario:

- Barras verticales y horizontales.
- Líneas (tendencias).
- Circular (pie).
- Dispersión (scatter).
- Histogramas.
- Mapas de calor (correlaciones).

Paleta corporativa Movimer aplicada automáticamente.

### 2.8 Transparencia de costes

- Estimación del coste **antes** de ejecutar el análisis.
- Desglose en tiempo real: tokens de entrada, tokens de salida, coste en USD.
- Historial acumulado por sesión.
- Elección de modelo para ajustar coste vs. calidad.

---

## 3. MODELOS DE IA DISPONIBLES

| Modelo | Input ($/MTok) | Output ($/MTok) | Uso recomendado |
|---|---|---|---|
| **Sonnet 4** | 3.00 | 15.00 | Uso general — mejor balance calidad/precio |
| **Opus 4** | 15.00 | 75.00 | Informes de alta exigencia, análisis complejos |
| **Haiku 4** | 0.80 | 4.00 | Pruebas, datasets grandes, presupuesto ajustado |

### Costes operativos estimados por informe

| Tamaño del archivo | Sonnet 4 | Opus 4 | Haiku 4 |
|---|---|---|---|
| ~25 KB (datos simples) | $0.05 – $0.15 | $0.25 – $0.75 | $0.02 – $0.05 |
| ~50 KB (datos medios) | $0.10 – $0.30 | $0.50 – $1.50 | $0.03 – $0.10 |
| ~100 KB (datos grandes) | $0.20 – $0.60 | $1.00 – $3.00 | $0.05 – $0.20 |

> **Nota:** El hosting no tiene coste adicional si se usa Streamlit Cloud (plan Community gratuito). Solo se paga el consumo de la API de Anthropic.

---

## 4. GUÍA DE USO

### 4.1 Acceso

Abrir la aplicación en el navegador. URL por defecto en local: `http://localhost:8501`.

### 4.2 Configuración (panel lateral izquierdo)

1. **API Key de Claude:** Introducir la clave de Anthropic. Si está preconfigurada (variable de entorno o Streamlit Secrets), aparecerá automáticamente como "API Key configurada".
2. **Modelo de IA:** Seleccionar según necesidad (ver tabla de costes arriba).
3. **Metadatos del informe:**
   - Nombre del cliente.
   - Fechas de inicio y fin del periodo analizado.
   - Tipo de informe (selección entre los 9 disponibles).
4. **Logos (opcional):** Subir logo de empresa (aparece en la portada) y logo del cliente (aparece en el pie).

### 4.3 Carga de datos

1. Arrastrar o seleccionar el archivo Excel/CSV.
2. El sistema muestra automáticamente:
   - Número de hojas, filas y columnas detectadas.
   - Porcentaje de completitud.
   - Score de calidad (0–100) con lista de incidencias.
   - Vista previa de cada hoja.

### 4.4 Generación del informe

1. (Opcional) Editar el prompt en la sección "Prompt Maestro" si se desea personalizar el análisis.
2. Verificar la estimación de coste.
3. Pulsar **"Generar Informe Completo"**.
4. El sistema ejecuta secuencialmente:
   - Procesamiento y validación de datos.
   - Análisis cuantitativo determinista.
   - Análisis estratégico con Claude (streaming en tiempo real).
   - Generación de gráficos.
5. Tiempo estimado: **30–90 segundos** según tamaño del dataset y modelo seleccionado.

### 4.5 Revisión y descarga

Los resultados se presentan en **5 pestañas**:

1. **Informe Ejecutivo** — Texto completo del análisis con formato Markdown.
2. **Visualizaciones** — Todos los gráficos generados desde las tablas del informe.
3. **Descargar DOCX** — Generar y descargar documento Word.
4. **Descargar PDF** — Generar y descargar PDF con marca Movimer.
5. **Descargar PPTX** — Generar y descargar presentación PowerPoint.

### 4.6 Recomendaciones para mejores resultados

- Usar **cabeceras descriptivas** en la primera fila (ej: `Satisfaccion_Cliente`, `Ingreso_Total`).
- Incluir **columnas de fecha** para habilitar análisis de tendencias.
- Eliminar filas y columnas completamente vacías antes de cargar.
- En archivos multi-hoja, usar **nombres descriptivos** para cada hoja.
- Para informes especializados, seleccionar el **tipo de informe** adecuado (Ventas, RRHH, etc.).
- El modelo **Sonnet 4** es el recomendado para uso general.

---

## 5. ARQUITECTURA TÉCNICA

### 5.1 Estructura del proyecto

```
informe-ia-app/
├── app.py                          # Aplicación principal Streamlit (586 líneas)
├── modules/                        # Módulos Python (14 archivos, ~3.500 líneas)
│   ├── __init__.py                 # Exportación centralizada
│   ├── config.py                   # Configuración: modelos, precios, tema, límites
│   ├── styles.py                   # CSS de la interfaz
│   ├── session_state.py            # Gestión de estado de sesión Streamlit
│   ├── prompt_manager.py           # Gestión de prompts con soporte para plantillas
│   ├── data_processor.py           # Lectura y normalización de Excel/CSV
│   ├── quantitative_analyzer.py    # KPIs, correlaciones, tendencias, anomalías
│   ├── claude_analyzer.py          # Integración Claude API + streaming + costes
│   ├── validators.py               # Validación de calidad de datos
│   ├── chart_generator.py          # Generación de gráficos matplotlib
│   ├── report_chart_extractor.py   # Extracción de tablas del informe → gráficos
│   ├── pdf_generator.py            # Generación de PDF (ReportLab)
│   ├── docx_generator.py           # Generación de DOCX (python-docx)
│   └── pptx_generator.py           # Generación de PPTX (python-pptx)
├── prompts/                        # Plantillas de prompt por tipo de informe (7 archivos)
├── tests/                          # Tests automatizados (39 tests, pytest)
├── .streamlit/config.toml          # Configuración de Streamlit (tema, servidor)
├── requirements.txt                # Dependencias Python
├── Dockerfile                      # Imagen Docker para despliegue
├── docker-compose.yml              # Orquestación Docker
├── Procfile                        # Configuración para Heroku
├── .dockerignore                   # Exclusiones para build Docker
├── start.sh                        # Script de inicio rápido (Mac/Linux)
└── LogoMovimer.png                 # Logo corporativo
```

**Métricas del código:**
- Total de líneas de código: ~5.150
- Módulos Python: 14
- Plantillas de prompt: 7
- Tests automatizados: 39

### 5.2 Flujo de datos

```
 Archivo Excel/CSV
        │
        ▼
 ┌─────────────────┐
 │  DataProcessor   │  → Lectura, limpieza, detección de tipos, metadata
 └────────┬────────┘
          │
          ▼
 ┌─────────────────────┐
 │  validate_quality()  │  → Score de calidad, detección de issues
 └────────┬────────────┘
          │
          ▼
 ┌────────────────────────┐
 │  QuantitativeAnalyzer   │  → KPIs, agregaciones, correlaciones, tendencias, anomalías
 └────────┬───────────────┘
          │
          ▼
 ┌─────────────────┐
 │  ClaudeAnalyzer  │  → Prompt especializado + datos + análisis cuantitativo → Claude
 └────────┬────────┘       (streaming en tiempo real)
          │
          ▼
 ┌──────────────────────────┐
 │  report_chart_extractor   │  → Extrae tablas del informe → genera gráficos matplotlib
 └────────┬─────────────────┘
          │
          ▼
 ┌───────────────────────────────────────┐
 │  PDF / DOCX / PPTX Generator          │  → Documento final con marca Movimer
 └───────────────────────────────────────┘
```

### 5.3 Stack tecnológico

| Componente | Tecnología | Versión mínima |
|---|---|---|
| Frontend / UI | Streamlit | 1.28.0 |
| IA / LLM | Claude (Anthropic) | API 0.39.0 |
| Análisis de datos | Pandas, NumPy | 2.0.0 / 1.24.0 |
| Gráficos | Matplotlib | 3.7.0 |
| PDF | ReportLab | 4.0.0 |
| DOCX | python-docx | 1.1.0 |
| PPTX | python-pptx | 0.6.21 |
| Excel | openpyxl, xlrd | 3.1.0 / 2.0.0 |
| Imágenes | Pillow | 10.0.0 |
| Tests | pytest | — |

### 5.4 Dependencias externas

La única dependencia externa de pago es la **API de Anthropic** (Claude). No hay otras APIs, bases de datos ni servicios de terceros involucrados.

---

## 6. SEGURIDAD Y PRIVACIDAD

- **API Keys:** Se gestionan en memoria y nunca se persisten en disco. Pueden configurarse mediante variables de entorno, Streamlit Secrets o introducción manual en la UI.
- **Datos del usuario:** Los archivos cargados se procesan **íntegramente en memoria** (BytesIO). No se guardan en disco ni se envían a terceros distintos de Anthropic para el análisis.
- **Comunicación API:** Conexión cifrada (HTTPS) con la API de Anthropic.
- **Sin telemetría:** `gatherUsageStats = false` configurado en Streamlit. No se envían datos de uso.
- **Estado de sesión:** Se limpia automáticamente al cerrar el navegador o al pulsar "Analizar Otro Archivo".
- **CORS/XSRF:** Deshabilitados en configuración de Streamlit para compatibilidad con proxies y reverse proxies.

### Datos enviados a Anthropic

Al generar un informe, se envía a la API de Claude:
- El contenido del archivo convertido a texto Markdown (tablas).
- El análisis cuantitativo previo (texto).
- El prompt del informe (texto).

**No se envían:** API keys de otros servicios, datos de sesión del navegador, información del servidor.

---

## 7. MANTENIMIENTO

### 7.1 Actualización de modelos de IA

Cuando Anthropic publique nuevos modelos, actualizar en `modules/config.py`:

```python
MODELS = ["claude-sonnet-4-20250514", ...]  # Añadir nuevo modelo
MODEL_PRICING = { "nuevo-modelo": {"input": X.XX, "output": X.XX}, ... }
```

No requiere cambios en ningún otro archivo.

### 7.2 Añadir un nuevo tipo de informe

1. Crear un archivo de plantilla en `prompts/` (ej: `nuevo_tipo.txt`) con las variables `{client_name}`, `{period}`, `{report_type}`, `{total_records}`, `{data_summary}`, `{quantitative_analysis}`.
2. Añadir la entrada en `modules/prompt_manager.py` → `TEMPLATE_MAP`.
3. Añadir el nombre en `modules/config.py` → `REPORT_TYPES`.

### 7.3 Personalizar marca corporativa

- **Logo:** Reemplazar `LogoMovimer.png` en la raíz del proyecto.
- **Colores:** Modificar `modules/config.py` → clase `ThemeColors` y actualizar `.streamlit/config.toml` → `primaryColor`.
- **CSS:** Modificar `modules/styles.py`.
- **PDF:** Estilos en `modules/pdf_generator.py` (fuentes, márgenes, colores).
- **PPTX:** Colores en `modules/pptx_generator.py` (constantes `_GREEN`, `_GREEN_DARK`, etc.).

### 7.4 Añadir un nuevo tipo de gráfico

1. Implementar el método generador en `modules/chart_generator.py`.
2. Registrarlo en el diccionario `generators` del método `generate_chart()`.
3. Añadir la clave en `modules/config.py` → `CHART_TYPES`.

### 7.5 Añadir un nuevo formato de exportación

1. Crear un nuevo módulo `modules/xxx_generator.py` siguiendo el patrón de `pptx_generator.py`.
2. Exportar la clase en `modules/__init__.py`.
3. Importar en `app.py` y añadir una nueva pestaña en la sección de resultados.

### 7.6 Logs y depuración

La aplicación genera logs en consola a nivel `INFO`:
- Hojas procesadas y sus dimensiones.
- Llamadas a la API de Claude (modelo, tokens, coste).
- Errores con trazas completas (`logger.exception`).

Para activar logs más detallados, cambiar `logging.basicConfig(level=logging.DEBUG)` en `app.py`.

### 7.7 Tests

Ejecutar la suite de tests:

```bash
pip install pytest
python -m pytest tests/ -v
```

39 tests cubren: procesamiento de datos, análisis cuantitativo, validación de calidad, gestión de prompts y generación PPTX.

### 7.8 Actualización de dependencias

```bash
pip install --upgrade -r requirements.txt
```

Verificar compatibilidad ejecutando los tests después de actualizar.

---

## 8. LIMITACIONES CONOCIDAS

- **Tamaño de contexto:** Los modelos Claude tienen un límite de tokens de entrada (~200K). Archivos muy grandes se truncan automáticamente a las primeras 2.000 filas por hoja para el envío a la API (el análisis cuantitativo sí usa todos los datos).
- **Formato de archivo:** Solo se soportan archivos con cabeceras en la primera fila. Archivos con estructuras complejas (celdas combinadas, formatos libres) pueden no procesarse correctamente.
- **Gráficos:** Se generan automáticamente desde las tablas del informe. Si Claude no genera tablas en su respuesta, no habrá gráficos.
- **Idioma:** La interfaz y los prompts están en español. Los informes se generan en español.
- **Concurrencia:** Streamlit ejecuta un proceso por usuario. Para alta concurrencia, usar despliegue con múltiples réplicas (Docker / Kubernetes).

---

## 9. ENTREGABLES

| Componente | Descripción |
|---|---|
| `app.py` | Aplicación principal Streamlit |
| `modules/` | 14 módulos Python (procesamiento, análisis, generación) |
| `prompts/` | 7 plantillas de prompt especializadas |
| `tests/` | 39 tests automatizados (pytest) |
| `requirements.txt` | Dependencias Python |
| `start.sh` | Script de inicio rápido (Mac/Linux) |
| `Dockerfile` | Imagen Docker para despliegue en contenedor |
| `docker-compose.yml` | Orquestación Docker Compose |
| `Procfile` | Configuración para despliegue en Heroku |
| `.streamlit/config.toml` | Tema visual y configuración del servidor |
| `LogoMovimer.png` | Logo corporativo integrado |
| `README.md` | Documentación técnica de instalación |
| `ENTREGA.md` | Reporte de entrega del proyecto |
| `GUIA_DESPLIEGUE.md` | Guía completa de despliegue multiplataforma |
| `MEMORIA.md` | Este documento |

---

## 10. CONTACTO Y SOPORTE

Para incidencias técnicas o consultas sobre el mantenimiento de la herramienta, los puntos de acción recomendados son:

1. Consultar la sección de **Mantenimiento** de este documento.
2. Revisar los **logs de consola** para identificar errores.
3. Ejecutar los **tests** para verificar la integridad del sistema.
4. Consultar la documentación de [Streamlit](https://docs.streamlit.io) y [Anthropic](https://docs.anthropic.com) para cuestiones de plataforma o API.

---

*Herramienta desarrollada para Movimer Group — Transformando datos en decisiones estratégicas.*
