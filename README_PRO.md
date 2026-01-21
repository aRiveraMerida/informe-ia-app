# 📊 Generador de Informes Ejecutivos con IA - Versión Profesional

Aplicación completa de análisis de datos que combina **análisis cuantitativo determinista** con **análisis estratégico de IA ** para generar informes ejecutivos profesionales en PDF personalizable.

## 🌟 Características Principales

### 1. **Análisis Dual**
- ✅ **Análisis Cuantitativo Determinista**: KPIs automáticos, agregaciones, correlaciones, tendencias, detección de anomalías
- ✅ **Análisis Cualitativo con IA**: interpreta datos, genera insights estratégicos y recomendaciones accionables

### 2. **Procesamiento Inteligente de Datos**
- 📁 Soporte para **múltiples hojas** en Excel (XLSX/XLS)
- 📄 Soporte para CSV
- 🔍 Detección automática de estructura y tipos de datos
- 🧹 Limpieza y normalización automática
- 📊 Inferencia de KPIs específicos por dominio (ventas, satisfacción, conversión)

### 3. **Tracking de Costes en Tiempo Real**
- 💰 Estimación de costes antes de ejecutar
- 📊 Desglose de tokens (entrada/salida)
- 📈 Costes acumulados por sesión
- 💵 Transparencia total en facturación

### 4. **Generación de PDF Profesional**
- 📄 Portada personalizable con **logo de empresa**
- 👣 Pie de página con **logo de cliente**
- 📋 Metadatos del informe (cliente, periodo, fecha)
- 🎨 Formato profesional con tablas, headings y estilos
- 📊 Conversión automática de markdown a PDF

### 5. **Preview Interactivo**
- 👀 Vista previa de datos antes de analizar
- 📊 Métricas instantáneas (filas, columnas, completitud)
- 📑 Navegación por hojas
- ✅ Revisión del análisis antes de descargar

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- API Key de Anthropic ([obtener aquí](https://console.anthropic.com))

### Instalación Local

```bash
# 1. Clonar el repositorio
cd informe-ia-app

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# 3. Activar entorno virtual
# En Mac/Linux:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicación
streamlit run app_pro.py
```

### Configurar API Key

**Opción 1: Variable de entorno (recomendada)**
```bash
export ANTHROPIC_API_KEY='tu-api-key-aqui'
streamlit run app_pro.py
```

**Opción 2: En la interfaz**
Introduce tu API key directamente en el campo de la barra lateral.

## 📖 Uso

### Flujo Completo

1. **Configuración Inicial**
   - Introduce tu API Key de Anthropic
   - Selecciona el modelo (Sonnet 4 recomendado para balance calidad/precio)
   - Configura metadatos: nombre del cliente, periodo, tipo de informe

2. **Carga de Datos**
   - Arrastra tu archivo Excel o CSV
   - Revisa la vista previa automática
   - Verifica métricas básicas (hojas, filas, completitud)

3. **Generación del Informe**
   - Revisa la estimación de coste
   - Haz clic en "🚀 Generar Informe Completo"
   - Monitorea el progreso en tiempo real

4. **Revisión y Descarga**
   - **Tab 1**: Análisis Cuantitativo (KPIs automáticos)
   - **Tab 2**: Análisis Estratégico (insights de Claude)
   - **Tab 3**: Generar y descargar PDF personalizado

5. **Personalización del PDF (Opcional)**
   - Sube logo de tu empresa (aparece en portada)
   - Sube logo del cliente (aparece en pie de página)

### Tipos de Análisis Soportados

#### 1. Satisfacción del Cliente
- NPS (Net Promoter Score)
- CSAT (Customer Satisfaction Score)
- Tasas de contactabilidad
- Propensión a recomendar
- Intención de recompra

#### 2. Ventas y KPIs
- Ingresos totales y promedios
- Performance por categoría/producto
- Análisis de tendencias
- Comparativa vs objetivos
- Top performers

#### 3. Operaciones
- Eficiencia operacional
- Tiempos de proceso
- Cuellos de botella
- Tasas de conversión
- Métricas de calidad

#### 4. Análisis General
- Análisis exploratorio automático
- Detección de patrones
- Correlaciones entre variables
- Distribuciones estadísticas
- Detección de anomalías

## 📁 Estructura del Proyecto

```
informe-ia-app/
├── app_pro.py                 # Aplicación principal Streamlit
├── modules/
│   ├── __init__.py
│   ├── data_processor.py      # Procesamiento y normalización de datos
│   ├── quantitative_analyzer.py # Análisis cuantitativo (sin IA)
│   ├── claude_analyzer.py     # Integración con Claude + tracking costes
│   └── pdf_generator.py       # Generación de PDFs profesionales
├── requirements.txt           # Dependencias Python
├── README_PRO.md             # Esta documentación
└── .streamlit/
    └── config.toml           # Configuración de Streamlit
```

## 🔧 Arquitectura

### Módulos Principales

#### 1. `DataProcessor`
- Lee archivos Excel/CSV con múltiples hojas
- Detecta y limpia estructura de datos
- Infiere tipos de datos automáticamente
- Calcula metadata y estadísticas básicas

#### 2. `QuantitativeAnalyzer`
- **KPIs automáticos**: media, mediana, suma, min, max, desviación estándar
- **Agregaciones**: por categorías y dimensiones
- **Distribuciones**: cuartiles, skewness, kurtosis
- **Correlaciones**: matriz de correlación, correlaciones significativas
- **Tendencias**: detección de tendencias temporales
- **Anomalías**: detección de outliers con IQR
- **KPIs específicos**: satisfacción, ventas, conversión (detectados por nombre de columna)

#### 3. `ClaudeAnalyzer`
- Integración con API de Anthropic
- Prompts estructurados para análisis estratégico
- **Tracking de costes**:
  - Cálculo preciso por tokens
  - Historial de llamadas
  - Resumen de sesión
- Manejo robusto de errores

#### 4. `PDFReportGenerator`
- Portada con logo de empresa
- Pie de página con logo de cliente
- Parsing de markdown a ReportLab
- Tablas, headings, bullets formateados
- Estilos profesionales personalizados

### Flujo de Datos

```
1. Upload XLSX/CSV
   ↓
2. DataProcessor → Normalización + Metadata
   ↓
3. QuantitativeAnalyzer → KPIs automáticos
   ↓
4. ClaudeAnalyzer → Análisis cualitativo (con contexto cuantitativo)
   ↓
5. PDFReportGenerator → PDF final personalizado
```

## 💰 Costes y Pricing

### Modelos Disponibles (Enero 2025)

| Modelo | Input ($/MTok) | Output ($/MTok) | Uso Recomendado |
|--------|---------------|-----------------|-----------------|
| **Sonnet 4** | $3.00 | $15.00 | ⭐ Balance calidad/precio |
| **Opus 4** | $15.00 | $75.00 | Máxima calidad |
| **Haiku 4** | $0.80 | $4.00 | Máxima economía |

### Estimación de Costes por Informe

| Tamaño Archivo | Sonnet 4 | Opus 4 | Haiku 4 |
|---------------|----------|---------|---------|
| ~25 KB | $0.05-0.15 | $0.25-0.75 | $0.02-0.05 |
| ~50 KB | $0.10-0.30 | $0.50-1.50 | $0.03-0.10 |
| ~100 KB | $0.20-0.60 | $1.00-3.00 | $0.05-0.20 |
| ~200 KB | $0.40-1.20 | $2.00-6.00 | $0.10-0.40 |

**Nota**: Los costes varían según la complejidad del análisis y los tokens de salida generados.

## 🔒 Seguridad y Privacidad

- ✅ API Key nunca se almacena en disco
- ✅ Archivos procesados en memoria (no persisten)
- ✅ Conexión encriptada con Anthropic
- ✅ Sin telemetría ni tracking externo
- ✅ Datos eliminados al cerrar sesión

## 🐛 Troubleshooting

### Error: "Invalid API Key"
```bash
# Verifica que tu API key sea correcta
echo $ANTHROPIC_API_KEY

# O introduce directamente en la UI
```

### Error al leer archivo Excel
```python
# Asegúrate de que el archivo tenga:
# - Headers en la primera fila
# - Formato válido (.xlsx, .xls, .csv)
# - No esté corrupto
```

### Error al generar PDF
```bash
# Reinstala ReportLab
pip install --upgrade reportlab pillow
```

### Problema con logos
```python
# Los logos deben ser:
# - Formato: PNG, JPG, JPEG
# - Tamaño razonable (< 5MB)
# - Dimensiones recomendadas: 
#   - Logo empresa: 800x400px
#   - Logo cliente: 400x200px
```

## 📊 Ejemplos de Output

### Análisis Cuantitativo (Automático)
```markdown
## ANÁLISIS CUANTITATIVO DETERMINISTA

### KPIs Globales
- Total Sheets: 2
- Total Records: 1,245
- Total Columns: 15

### Análisis de 'Ventas'
**Registros totales**: 1,245
**Completitud**: 98.5%

#### Métricas de Ventas
- **Ingresos**: Total $1,234,567.89, Promedio $991.45
- **Unidades Vendidas**: Total 12,450, Promedio 10

### Correlaciones Significativas
- Precio vs. Unidades Vendidas: -0.72 (correlación negativa fuerte)
```

### Análisis Estratégico (Claude)
```markdown
## INSIGHTS ESTRATÉGICOS

### 1. Hallazgos Clave
Los datos revelan una **correlación negativa significativa** entre precio 
y volumen de ventas (-0.72), sugiriendo alta elasticidad de precio en el 
mercado actual...

### 2. Análisis Comparativo
**Productos Top 10%**: generan el 65% de los ingresos totales, mientras 
que el 40% inferior contribuye menos del 5%...

### 3. Recomendaciones Prioritarias

**Quick Wins (0-1 mes)**
- Optimizar precio de productos elásticos
- Promocionar top performers
- Eliminar productos de baja rotación

**Tácticas (1-3 meses)**
- Implementar pricing dinámico
- Segmentación de clientes por sensibilidad
...
```

## 🚀 Próximas Mejoras

- [ ] Gráficos interactivos en PDF (matplotlib/plotly)
- [ ] Análisis comparativo histórico
- [ ] Exportación a PowerPoint
- [ ] Plantillas de informe personalizables
- [ ] Análisis multiidioma
- [ ] Dashboard de seguimiento de KPIs
- [ ] Integración con Google Sheets
- [ ] API REST para automatización

## 🤝 Contribuciones

Este proyecto es de uso educativo y comercial. Para contribuir:

1. Fork el repositorio
2. Crea una rama con tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Libre para uso educativo y comercial.

## 📞 Soporte

Para consultas técnicas o reportar issues, contacta al desarrollador.

---


*Transformando datos en decisiones estratégicas*
