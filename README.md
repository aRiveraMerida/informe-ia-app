# 📊 Generador de Informes Ejecutivos con IA

Aplicación Streamlit que utiliza Claude 4.5 para transformar datos en informes ejecutivos profesionales automáticamente.

## 🚀 Características

- **Análisis automatizado** de archivos Excel y CSV
- **Generación de informes ejecutivos** con estructura profesional
- **Insights estratégicos** y recomendaciones accionables
- **Interfaz intuitiva** diseñada para no-técnicos
- **Procesamiento seguro** sin almacenamiento de datos

## 📋 Requisitos Previos

- Python 3.8 o superior
- API Key de Anthropic ([obtener aquí](https://console.anthropic.com))

## 🛠️ Instalación

### Opción 1: Instalación local

```bash
# 1. Clonar o descargar los archivos
# 2. Crear entorno virtual (recomendado)
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicación
streamlit run app.py
```

### Opción 2: Deploy en Streamlit Cloud

1. Sube los archivos a un repositorio de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. La app se desplegará automáticamente

## 📖 Uso

1. **Configurar API Key**: Introduce tu API key de Anthropic en el panel lateral
2. **Subir datos**: Arrastra tu archivo Excel o CSV
3. **Generar informe**: Haz clic en "Generar Informe Ejecutivo"
4. **Descargar resultado**: Obtén tu informe en formato TXT (próximamente DOCX)

## 📁 Estructura de Archivos

```
.
├── app.py              # Aplicación principal de Streamlit
├── requirements.txt    # Dependencias de Python
└── README.md          # Este archivo
```

## 🔒 Seguridad y Privacidad

- Las API keys se manejan en memoria, nunca se almacenan
- Los archivos se procesan temporalmente y se eliminan después
- No se guardan datos en servidores
- Comunicación encriptada con la API de Anthropic

## 🎯 Tipos de Análisis Soportados

- ✅ Encuestas de satisfacción del cliente
- ✅ Datos de ventas y KPIs comerciales
- ✅ Métricas de rendimiento operacional
- ✅ Análisis competitivo
- ✅ Cualquier dataset tabular con headers

## 🔧 Personalización

### Modificar el prompt de análisis

Edita la variable `prompt` en `app.py` (línea ~200) para ajustar el tipo de análisis:

```python
prompt = """Tu prompt personalizado aquí..."""
```

### Cambiar el modelo de IA

En el sidebar, selecciona entre:
- `claude-sonnet-4-20250514` (recomendado: equilibrio calidad/velocidad)
- `claude-opus-4-20250514` (máxima calidad)
- `claude-haiku-4-20250514` (máxima velocidad)

## 📊 Ejemplo de Salida

El informe generado incluye:

1. **Resumen Ejecutivo** con métricas clave
2. **Análisis de Contactabilidad** (si aplica)
3. **Satisfacción y Recomendación**
4. **Análisis Competitivo**
5. **Intención de Recompra**
6. **Recomendaciones Estratégicas**

## 🐛 Troubleshooting

### Error: "Invalid API Key"
- Verifica que tu API key sea correcta
- Asegúrate de tener créditos disponibles en tu cuenta

### Error al leer archivo
- Verifica que el archivo sea .xlsx, .xls o .csv
- Asegúrate de que el archivo no esté corrupto
- Revisa que tenga headers en la primera fila

### La app no carga
```bash
# Reinstalar dependencias
pip install -r requirements.txt --upgrade

# Limpiar caché de Streamlit
streamlit cache clear
```

## 🚀 Próximas Mejoras

- [ ] Generación de archivos DOCX completos
- [ ] Gráficos y visualizaciones integradas
- [ ] Plantillas personalizables de informes
- [ ] Exportación a PowerPoint
- [ ] Análisis multiidioma
- [ ] Comparación histórica de datasets

## 💡 Casos de Uso

### Marketing y Ventas
- Análisis de campañas
- Satisfacción del cliente (NPS, CSAT)
- Pipeline de ventas

### Operaciones
- KPIs de rendimiento
- Análisis de eficiencia
- Gestión de inventario

### Recursos Humanos
- Encuestas de clima laboral
- Análisis de rotación
- Performance reviews

### Finanzas
- Análisis de gastos
- Proyecciones
- Comparativas presupuestarias

## 📞 Soporte

Para consultas o reportar issues, contacta al desarrollador.

## 📄 Licencia

Este proyecto es de uso libre para propósitos educativos y comerciales.

---

**Desarrollado con ❤️ usando Claude 4.5 de Anthropic**
