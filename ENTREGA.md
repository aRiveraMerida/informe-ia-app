# Reporte de Entrega — Herramienta de Análisis de Datos con IA

**Cliente:** Movimer Group
**Fecha de entrega:** Febrero 2026
**Versión:** 1.0

---

## 1. Descripción de la herramienta

Plataforma web de generación automática de informes ejecutivos que combina dos capas de análisis sobre cualquier conjunto de datos tabulares (Excel / CSV):

- **Capa cuantitativa (determinista):** cálculo automático de KPIs, agregaciones, correlaciones, distribuciones estadísticas, detección de tendencias temporales y anomalías. No depende de IA y produce resultados reproducibles.
- **Capa estratégica (IA):** análisis cualitativo mediante Claude de Anthropic que recibe como contexto el análisis cuantitativo previo y genera insights, oportunidades, riesgos y recomendaciones accionables priorizadas.

El resultado se entrega en formato **PDF**, **DOCX** y/o **PPTX** con marca corporativa Movimer y gráficos integrados.

---

## 2. Capacidades

### 2.1 Procesamiento de datos

- Lectura de archivos Excel (XLSX/XLS) con soporte para múltiples hojas.
- Lectura de archivos CSV.
- Detección automática de tipos de datos (numéricos, categóricos, temporales).
- Limpieza y normalización automática de la estructura.
- Vista previa interactiva antes de lanzar el análisis.

### 2.2 Análisis cuantitativo automático

- **KPIs globales:** media, mediana, suma, mínimo, máximo, desviación estándar.
- **Agregaciones por categoría:** métricas agrupadas por columnas categóricas.
- **Distribuciones:** cuartiles, asimetría (skewness), curtosis (kurtosis).
- **Correlaciones:** matriz completa y detección de correlaciones significativas.
- **Tendencias temporales:** si el dataset contiene fechas, se detectan y analizan.
- **Anomalías:** detección de outliers mediante el método IQR.
- **KPIs de dominio:** detección inteligente por nombre de columna (satisfacción, ventas, conversión, NPS, etc.).

### 2.3 Análisis estratégico con IA

- Interpretación de los datos cuantitativos en contexto de negocio.
- Identificación de hallazgos clave y patrones no evidentes.
- Recomendaciones priorizadas: quick wins (0-1 mes), tácticas (1-3 meses) y estratégicas (3-12 meses).
- Identificación de riesgos y oportunidades.
- Prompts editables para personalizar el tipo de análisis.

### 2.4 Validación de calidad de datos

- Score de calidad (0-100) calculado automáticamente al cargar datos.
- Detección de: hojas vacías, columnas con alto % de nulos, filas duplicadas, columnas de varianza cero.
- Indicador visual de estado (Excelente / Bueno / Aceptable / Deficiente / Crítico).

### 2.5 Streaming de respuesta

- La respuesta de Claude se muestra en tiempo real durante el análisis.
- Feedback visual inmediato sin esperar a que termine el procesamiento completo.

### 2.6 Generación de informes

- **PDF:** portada con logo Movimer, secciones estructuradas, gráficos inline, pie de página con logo del cliente.
- **DOCX:** documento Word con la misma estructura para edición posterior.
- **PPTX:** presentación PowerPoint ejecutiva con portada, secciones y gráficos integrados.
- Gráficos generados automáticamente: barras, líneas, circular, dispersión, histograma, mapa de calor.
- Personalización de metadatos: nombre del cliente, periodo analizado, tipo de informe.

### 2.7 Plantillas de prompt especializadas

- Prompts optimizados por tipo de informe: Ventas, Satisfacción, Encuestas, Operaciones, Marketing, RRHH, Financiero.
- El prompt se selecciona automáticamente según el tipo de informe elegido.
- Posibilidad de editar y personalizar el prompt desde la UI.

### 2.5 Transparencia de costes

- Estimación del coste antes de ejecutar el análisis.
- Desglose en tiempo real de tokens de entrada y salida.
- Historial de costes acumulados por sesión.
- Tres modelos disponibles para ajustar coste vs. calidad.

---

## 3. Guía de uso

### 3.1 Acceso

Abrir la aplicación en el navegador. Si se ejecuta en local: `http://localhost:8501`.

### 3.2 Configuración inicial (panel lateral)

1. **API Key:** introducir la clave de Anthropic. Si está preconfigurada como variable de entorno o en Streamlit Secrets, aparecerá como "API Key configurada".
2. **Modelo de IA:** seleccionar el modelo deseado.
   - *Sonnet 4* — recomendado, balance calidad/precio (~$0.10–0.30 por informe).
   - *Opus 4* — máxima calidad, mayor coste.
   - *Haiku 4* — más económico, útil para pruebas o datasets grandes.
3. **Metadatos del informe:** nombre del cliente, fechas del periodo analizado, tipo de informe.
4. **Logos (opcional):** subir logo de empresa (portada) y logo del cliente (pie de página).

### 3.3 Carga de datos

1. Arrastrar o seleccionar el archivo Excel/CSV en la zona de carga.
2. La aplicación mostrará automáticamente:
   - Número de hojas, filas y columnas.
   - Porcentaje de completitud de los datos.
   - Vista previa de cada hoja.

### 3.4 Generación del informe

1. Revisar la estimación de coste mostrada.
2. Pulsar **"Generar Informe Completo"**.
3. La aplicación ejecutará secuencialmente:
   - Análisis cuantitativo determinista.
   - Análisis estratégico con IA.
   - Generación de gráficos.
4. Tiempo estimado: 30–60 segundos según tamaño del dataset.

### 3.5 Revisión y descarga

Los resultados se muestran en pestañas:

- **Análisis Cuantitativo:** KPIs, correlaciones, tendencias calculadas sin IA.
- **Análisis Estratégico:** insights, recomendaciones y hallazgos generados por Claude.
- **Informe PDF/DOCX:** generación y descarga del documento final con gráficos integrados.

### 3.6 Recomendaciones para mejores resultados

- Utilizar cabeceras descriptivas en la primera fila (ej: `Satisfaccion_Cliente`, `Ingreso_Total`).
- Incluir columnas de fecha para habilitar análisis de tendencias.
- Eliminar filas y columnas completamente vacías antes de cargar.
- Nombres de hoja descriptivos en archivos multi-hoja.

---

## 4. Tipos de análisis soportados

| Dominio | Detección automática por columnas |
|---------|----------------------------------|
| Satisfacción del cliente | `satisfaction`, `nps`, `rating`, `score`, `csat` |
| Ventas | `ventas`, `sales`, `revenue`, `ingreso`, `precio` |
| Conversión | `tasa`, `rate`, `conversion`, `%` |
| General | Cualquier dataset tabular con cabeceras |

---

## 5. Arquitectura técnica

```
Archivo Excel/CSV
       │
       ▼
 DataProcessor           →  Normalización, detección de tipos, metadata
       │
       ▼
 QuantitativeAnalyzer    →  KPIs, correlaciones, tendencias, anomalías
       │
       ▼
 ClaudeAnalyzer          →  Análisis estratégico con contexto cuantitativo
       │
       ▼
 ChartGenerator          →  Gráficos matplotlib desde tablas del informe
       │
       ▼
 PDF / DOCX Generator    →  Documento final con marca Movimer
```

### Stack tecnológico

- **Frontend:** Streamlit
- **IA:** Claude (Anthropic) — modelos Sonnet 4, Opus 4, Haiku 4
- **Análisis de datos:** Pandas, NumPy
- **Gráficos:** Matplotlib
- **Generación PDF:** ReportLab
- **Generación DOCX:** python-docx
- **Generación PPTX:** python-pptx
- **Lectura Excel:** openpyxl, xlrd
- **Tests:** pytest

---

## 6. Seguridad y privacidad

- Las claves API se gestionan en memoria y nunca se persisten en disco.
- Los archivos cargados se procesan en memoria sin almacenamiento permanente.
- La comunicación con la API de Anthropic se realiza mediante conexión cifrada (HTTPS).
- No se envía telemetría ni datos a terceros.
- El estado de sesión se limpia al cerrar el navegador.

---

## 7. Costes operativos de referencia

Los costes dependen del modelo seleccionado y del tamaño del dataset:

| Tamaño del archivo | Sonnet 4 | Opus 4 | Haiku 4 |
|-------------------|----------|--------|---------|
| ~25 KB | $0.05 – $0.15 | $0.25 – $0.75 | $0.02 – $0.05 |
| ~50 KB | $0.10 – $0.30 | $0.50 – $1.50 | $0.03 – $0.10 |
| ~100 KB | $0.20 – $0.60 | $1.00 – $3.00 | $0.05 – $0.20 |

El hosting en Streamlit Cloud es gratuito (plan Community).

---

## 8. Entregables incluidos

| Componente | Descripción |
|-----------|-------------|
| `app.py` | Aplicación principal Streamlit |
| `modules/` | Módulos Python (procesamiento, análisis, generación) |
| `prompts/` | Plantillas de prompt especializadas por tipo de informe |
| `tests/` | Tests automatizados con pytest (39 tests) |
| `requirements.txt` | Dependencias del proyecto |
| `start.sh` | Script de inicio rápido (Mac/Linux) |
| `Dockerfile` | Configuración para despliegue Docker |
| `docker-compose.yml` | Orquestación Docker Compose |
| `Procfile` | Configuración para Heroku |
| `.streamlit/config.toml` | Configuración del servidor y tema visual |
| `LogoMovimer.png` | Logo corporativo integrado en los informes |
| `README.md` | Documentación técnica de instalación y despliegue |
| `ENTREGA.md` | Este documento |

---

## 9. Soporte y mantenimiento

### Logs

La aplicación genera logs en consola a nivel `INFO` durante la ejecución, incluyendo:
- Hojas procesadas.
- Llamadas a la API de Claude (modelo, tokens, coste).
- Errores con trazas completas.

### Actualización de modelos

Los modelos de IA y sus precios se configuran en `modules/config.py`. Para actualizar a nuevos modelos de Anthropic, basta con modificar las listas `MODELS` y `MODEL_PRICING`.

### Extensibilidad

La arquitectura modular permite:
- Añadir nuevos tipos de gráficos en `chart_generator.py`.
- Personalizar prompts en `prompt_manager.py`.
- Crear nuevas plantillas de informe modificando los generadores PDF/DOCX.
- Integrar nuevos formatos de exportación.

---

*Herramienta desarrollada para Movimer Group — Transformando datos en decisiones estratégicas.*
