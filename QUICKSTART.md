# 🚀 Guía de Inicio Rápido

## Instalación en 5 Minutos

### 1. Pre-requisitos
- Python 3.8+ instalado
- API Key de Anthropic ([obtener aquí](https://console.anthropic.com))

### 2. Instalación Automática (Mac/Linux)

```bash
# Navega al directorio
cd informe-ia-app

# Ejecuta el script de inicio
./start.sh
```

El script automáticamente:
- ✅ Crea entorno virtual
- ✅ Instala dependencias
- ✅ Configura API key (opcional)
- ✅ Inicia la aplicación

### 3. Instalación Manual (Todas las plataformas)

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key (opcional)
export ANTHROPIC_API_KEY='tu-api-key'

# 5. Iniciar aplicación
streamlit run app_pro.py
```

## Primer Uso

### Paso 1: Configurar API Key
En la barra lateral, introduce tu API key de Anthropic:
- **Opción A**: Variable de entorno `ANTHROPIC_API_KEY`
- **Opción B**: Campo de texto en la UI (tipo password)

### Paso 2: Configurar Metadatos
Configura los siguientes campos en la barra lateral:
- **Nombre del Cliente**: Ej. "Acme Corp"
- **Periodo**: Ej. "Q4 2024"
- **Tipo de Informe**: Selecciona el más apropiado

### Paso 3: Subir Datos
- Arrastra tu archivo Excel (.xlsx) o CSV
- Verifica la vista previa automática
- Revisa métricas: hojas, filas, columnas, completitud

### Paso 4: Generar Informe
1. Revisa la **estimación de coste** (típicamente $0.10-0.30 con Sonnet 4)
2. Haz clic en **"🚀 Generar Informe Completo"**
3. Espera ~30-60 segundos para análisis completo

### Paso 5: Revisar y Descargar
1. **Tab 1**: Análisis Cuantitativo automático
2. **Tab 2**: Análisis Estratégico con insights de Claude
3. **Tab 3**: Generar y descargar PDF profesional

## Ejemplos de Archivos Soportados

### ✅ Estructura Recomendada

```
┌─────────────┬──────────┬─────────┬───────────┐
│ Producto    │ Ventas   │ Precio  │ Categoría │
├─────────────┼──────────┼─────────┼───────────┤
│ Laptop Pro  │ 125      │ 1299.99 │ Hardware  │
│ Mouse RGB   │ 450      │ 49.99   │ Accesorios│
│ Teclado Mec │ 280      │ 129.99  │ Accesorios│
└─────────────┴──────────┴─────────┴───────────┘
```

**Características:**
- ✅ Primera fila = encabezados
- ✅ Columnas con nombres descriptivos
- ✅ Datos numéricos para métricas
- ✅ Categorías para segmentación
- ✅ Sin filas/columnas completamente vacías

### ❌ Evitar

```
┌─────────────┬──────────┬─────────┐
│             │          │         │  ← Fila vacía
├─────────────┼──────────┼─────────┤
│ Ventas 2024 │          │         │  ← Título sin datos
├─────────────┼──────────┼─────────┤
│ Unnamed     │ Unnamed  │ Unnamed │  ← Sin nombres
└─────────────┴──────────┴─────────┘
```

## Costes Típicos

| Tamaño Archivo | Sonnet 4 | Tiempo |
|---------------|----------|--------|
| 25 KB (pequeño) | ~$0.05-0.15 | ~20-30s |
| 50 KB (mediano) | ~$0.10-0.30 | ~30-45s |
| 100 KB (grande) | ~$0.20-0.60 | ~45-60s |

**Recomendación**: Usa Sonnet 4 para balance óptimo calidad/precio.

## Tips para Mejores Resultados

### 1. Nombra bien tus columnas
✅ **Bueno**: `Satisfacción_Cliente`, `Ingreso_Total`, `Tasa_Conversión`
❌ **Malo**: `Col1`, `Unnamed`, `xyz`

### 2. Incluye contexto
- Si hay fechas, usa columnas de tipo fecha
- Agrupa datos relacionados en la misma hoja
- Usa nombres de hoja descriptivos

### 3. Limpia tus datos
- Elimina filas/columnas completamente vacías
- Asegúrate de tener headers en la primera fila
- Verifica tipos de datos (números como números, no texto)

### 4. Personaliza el PDF
- Sube logos PNG/JPG de alta calidad
- Dimensiones recomendadas:
  - Logo empresa: 800x400px
  - Logo cliente: 400x200px

## Troubleshooting Rápido

### "Invalid API Key"
```bash
# Verifica tu API key
echo $ANTHROPIC_API_KEY

# O introdúcela en la UI
```

### "Error al leer archivo"
- Verifica formato: .xlsx, .xls o .csv
- Asegura headers en primera fila
- Revisa que no esté corrupto

### "Error al generar PDF"
```bash
# Reinstala ReportLab
pip install --upgrade reportlab pillow
```

### Aplicación muy lenta
- Reduce tamaño del archivo si es >200KB
- Usa Haiku 4 para análisis más rápidos
- Cierra otras aplicaciones pesadas

## Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl/Cmd + R` | Recargar app |
| `Ctrl/Cmd + W` | Cerrar pestaña |
| `Esc` | Cerrar modals |

## Próximos Pasos

1. **Lee el README completo**: `README_PRO.md` para documentación detallada
2. **Experimenta con tus datos**: La mejor forma de aprender
3. **Prueba diferentes modelos**: Compara Sonnet vs Opus vs Haiku
4. **Personaliza PDFs**: Agrega tus logos corporativos

## Soporte

¿Problemas o preguntas?
- 📖 Consulta `README_PRO.md` para documentación completa

---

**¡Listo para generar tu primer informe ejecutivo con IA!** 🚀
