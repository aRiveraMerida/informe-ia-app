# 📊 Proyecto: Generador de Informes Ejecutivos con IA

## 🎯 Resumen Ejecutivo

Se ha construido una **aplicación completa de análisis de datos** que combina análisis cuantitativo determinista con análisis estratégico de IA para generar informes ejecutivos profesionales en PDF personalizable.

## ✅ Objetivos Cumplidos

### 1. Análisis Dual ✅
- ✅ **Análisis cuantitativo determinista**: KPIs, agregaciones, correlaciones, tendencias y anomalías calculados sin IA
- ✅ **Análisis cualitativo con Claude**: Interpretación estratégica, insights y recomendaciones accionables
- ✅ El análisis cuantitativo se pasa como contexto a Claude para enriquecer el análisis cualitativo

### 2. Procesamiento de Datos ✅
- ✅ Soporte para múltiples hojas Excel (XLSX/XLS)
- ✅ Soporte para CSV
- ✅ Detección automática de estructura y tipos de datos
- ✅ Limpieza y normalización automática
- ✅ Inferencia de KPIs por dominio (ventas, satisfacción, conversión)

### 3. Tracking de Costes ✅
- ✅ Estimación de costes pre-ejecución
- ✅ Tracking en tiempo real de tokens (entrada/salida)
- ✅ Cálculo preciso de costes según modelo
- ✅ Historial de costes por sesión
- ✅ Transparencia total mostrada en UI

### 4. Generación de PDF ✅
- ✅ Portada personalizable con logo de empresa
- ✅ Pie de página con logo de cliente
- ✅ Metadatos del informe (cliente, periodo, fecha)
- ✅ Formato profesional con tablas, headings y estilos
- ✅ Conversión automática markdown → PDF
- ✅ Secciones estructuradas: portada, metadata, análisis cuantitativo, análisis estratégico, info de generación

### 5. Interfaz de Usuario ✅
- ✅ Configuración de API Key (UI + env var)
- ✅ Selección de modelo Claude (Sonnet/Opus/Haiku)
- ✅ Metadatos personalizables (cliente, periodo, tipo)
- ✅ Upload de logos (empresa y cliente)
- ✅ Vista previa de datos interactiva
- ✅ Preview del análisis en tabs
- ✅ Botón de descarga de PDF
- ✅ Monitoreo de costes en tiempo real

### 6. Flujo Completo ✅
```
1. Usuario sube XLSX/CSV
   ↓
2. DataProcessor: normalización + metadata
   ↓
3. QuantitativeAnalyzer: KPIs automáticos
   ↓
4. ClaudeAnalyzer: análisis cualitativo (con contexto cuantitativo)
   ↓
5. Preview en UI (tabs separados)
   ↓
6. PDFReportGenerator: PDF final con logos y personalización
```

## 📁 Estructura del Proyecto

```
informe-ia-app/
├── app_pro.py                      # ⭐ Aplicación principal (USAR ESTA)
├── app.py                          # Versión básica (legacy)
├── app_advanced.py                 # Versión avanzada (legacy)
│
├── modules/                        # Módulos Python
│   ├── __init__.py                 # Exports del paquete
│   ├── data_processor.py           # Procesamiento de datos XLSX/CSV
│   ├── quantitative_analyzer.py    # Análisis cuantitativo (sin IA)
│   ├── claude_analyzer.py          # Integración Claude + costes
│   └── pdf_generator.py            # Generación de PDFs profesionales
│
├── requirements.txt                # Dependencias Python
├── start.sh                        # Script de inicio rápido (Mac/Linux)
│
├── README_PRO.md                   # 📖 Documentación completa
├── QUICKSTART.md                   # 🚀 Guía de inicio rápido
├── DEPLOYMENT.md                   # ☁️ Guía de deployment
├── PROJECT_SUMMARY.md              # 📊 Este archivo
│
└── .streamlit/
    └── config.toml                 # Configuración de Streamlit
```

## 🚀 Cómo Usar

### Inicio Rápido (1 comando)

```bash
./start.sh
```

### Manual

```bash
# 1. Instalar
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar API key (opcional)
export ANTHROPIC_API_KEY='tu-api-key'

# 3. Ejecutar
streamlit run app_pro.py
```

## 🔧 Arquitectura Técnica

### Módulos Principales

#### 1. `DataProcessor`
**Responsabilidad**: Lectura y normalización de datos

**Funcionalidades**:
- Lee Excel (múltiples hojas) y CSV
- Detecta y limpia estructura
- Infiere tipos de datos automáticamente
- Genera metadata detallada

**Métodos clave**:
- `process()`: Procesa archivo completo
- `get_summary_statistics()`: Estadísticas resumidas
- `get_sample_data()`: Muestra de datos

#### 2. `QuantitativeAnalyzer`
**Responsabilidad**: Análisis cuantitativo sin IA

**Funcionalidades**:
- KPIs automáticos: media, mediana, suma, std, min, max
- Agregaciones por categorías
- Distribuciones: cuartiles, skewness, kurtosis
- Correlaciones: matriz + correlaciones significativas
- Tendencias temporales (si hay fechas)
- Detección de anomalías (IQR)
- KPIs específicos por dominio

**Métodos clave**:
- `analyze()`: Ejecuta análisis completo
- `format_for_report()`: Formatea para reporte

#### 3. `ClaudeAnalyzer`
**Responsabilidad**: Análisis cualitativo con IA + tracking de costes

**Funcionalidades**:
- Integración con API de Anthropic
- Prompts estructurados para análisis estratégico
- Tracking preciso de costes por tokens
- Historial de llamadas
- Estimación pre-ejecución

**Métodos clave**:
- `analyze_data()`: Análisis completo con Claude
- `get_cost_summary()`: Resumen de costes
- `estimate_cost_before_call()`: Estimación previa

**Prompt Engineering**:
El prompt está diseñado para:
- Recibir contexto cuantitativo completo
- Generar insights estratégicos (no repetir números)
- Priorizar recomendaciones (quick wins, tácticas, estratégicas)
- Identificar riesgos y oportunidades

#### 4. `PDFReportGenerator`
**Responsabilidad**: Generación de PDFs profesionales

**Funcionalidades**:
- Portada con logo de empresa
- Pie de página con logo de cliente
- Parsing de markdown a ReportLab
- Tablas, headings, bullets formateados
- Estilos profesionales personalizados

**Métodos clave**:
- `generate()`: Genera PDF completo
- `_parse_markdown_to_flowables()`: Convierte markdown

## 💰 Costes

### Modelos Disponibles

| Modelo | Input ($/MTok) | Output ($/MTok) | Caso de Uso |
|--------|---------------|-----------------|-------------|
| **Sonnet 4** | $3.00 | $15.00 | ⭐ Balance calidad/precio |
| **Opus 4** | $15.00 | $75.00 | Máxima calidad |
| **Haiku 4** | $0.80 | $4.00 | Máxima economía |

### Costes Típicos por Informe

- **Archivo pequeño (25KB)**: $0.05-0.15 (Sonnet)
- **Archivo mediano (50KB)**: $0.10-0.30 (Sonnet)
- **Archivo grande (100KB)**: $0.20-0.60 (Sonnet)

## 🎨 Características Destacadas

### 1. Análisis Inteligente por Dominio
El sistema detecta automáticamente el tipo de datos por nombres de columna:

- **Satisfacción**: detecta columnas con "satisfaction", "nps", "rating", "score"
- **Ventas**: detecta "ventas", "sales", "revenue", "ingreso", "precio"
- **Conversión**: detecta "tasa", "rate", "conversion", "%"

### 2. Preview Interactivo
Antes de generar el informe, el usuario puede:
- Ver muestra de cada hoja
- Revisar métricas básicas
- Verificar estructura de datos
- Estimar costes

### 3. Tracking de Costes Transparente
- Estimación pre-ejecución
- Desglose por tokens (entrada/salida)
- Historial de llamadas en sesión
- Métricas en tiempo real

### 4. Personalización Completa
- Logo de empresa en portada
- Logo de cliente en pie de página
- Nombre de cliente, periodo y metadatos
- Tipo de informe (influye en el prompt)

## 🔒 Seguridad

- ✅ API Key nunca persiste en disco
- ✅ Archivos procesados en memoria
- ✅ Conexión encriptada con Anthropic
- ✅ Sin telemetría externa
- ✅ Session state limpiado al cerrar

## 📊 Tipos de Análisis Soportados

### 1. Satisfacción del Cliente
- NPS, CSAT
- Tasas de contactabilidad
- Propensión a recomendar
- Intención de recompra

### 2. Ventas y KPIs
- Ingresos totales y promedios
- Performance por categoría
- Análisis de tendencias
- Comparativa vs objetivos

### 3. Operaciones
- Eficiencia operacional
- Cuellos de botella
- Métricas de calidad

### 4. General
- Análisis exploratorio
- Detección de patrones
- Correlaciones
- Anomalías

## 🚀 Próximas Mejoras Sugeridas

- [ ] Gráficos interactivos en PDF (matplotlib/plotly)
- [ ] Análisis comparativo histórico (múltiples periodos)
- [ ] Exportación a PowerPoint
- [ ] Plantillas de informe personalizables
- [ ] Análisis multiidioma
- [ ] Dashboard de seguimiento de KPIs
- [ ] Integración con Google Sheets
- [ ] API REST para automatización
- [ ] Cache de análisis para reducir costes
- [ ] Modo batch para múltiples archivos

## 📝 Documentación

- **README_PRO.md**: Documentación completa y técnica
- **QUICKSTART.md**: Guía de inicio en 5 minutos
- **DEPLOYMENT.md**: Guía de deployment a producción
- **PROJECT_SUMMARY.md**: Este archivo (resumen ejecutivo)

## ✨ Logros Clave

1. **Arquitectura modular**: Fácil de extender y mantener
2. **Análisis dual**: Cuantitativo (determinista) + Cualitativo (IA)
3. **Tracking de costes**: Transparencia total
4. **PDFs profesionales**: Con personalización completa
5. **UX optimizada**: Preview, estimaciones, feedback en tiempo real
6. **Documentación completa**: README, Quickstart, Deployment

## 🎓 Aprendizajes

### Prompt Engineering
- Contexto cuantitativo mejora significativamente calidad del análisis
- Prompts estructurados con secciones claras generan mejores resultados
- Instrucciones de "NO repetir números" son cruciales

### Arquitectura
- Separación clara entre análisis determinista e IA reduce costes
- Session state de Streamlit permite flujos complejos
- Módulos independientes facilitan testing y extensión

### UX
- Preview antes de analizar reduce costes en datos incorrectos
- Estimaciones de coste incrementan confianza del usuario
- Tracking en tiempo real mejora percepción de transparencia

## 📞 Soporte y Mantenimiento

**Estructura de archivos**:
- Código modularizado en `modules/`
- Aplicación principal: `app_pro.py`
- Tests: (por implementar en `tests/`)

**Logging**:
- Configurado en nivel INFO
- Logs en consola durante ejecución

**Gestión de errores**:
- Try-catch en todos los módulos
- Mensajes de error claros en UI
- Fallbacks para casos edge

---

## 🎉 Estado del Proyecto

✅ **COMPLETO Y FUNCIONAL**

Todos los objetivos especificados han sido implementados:
- ✅ Análisis cuantitativo determinista
- ✅ Análisis cualitativo con Claude
- ✅ Tracking de costes en tiempo real
- ✅ Generación de PDF personalizable
- ✅ Preview del informe
- ✅ Soporte para múltiples hojas XLSX
- ✅ Configuración de API Key (UI + env var)
- ✅ Documentación completa

**Listo para usar en producción** 🚀

---

**Desarrollado con ❤️ usando Claude de Anthropic**

*Transformando datos en decisiones estratégicas*
