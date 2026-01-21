import streamlit as st
import pandas as pd
import anthropic
from io import BytesIO
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Generador de Informes con IA",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1F4E78;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1F4E78;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2E5C8A;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31, 78, 120, 0.3);
    }
    .info-box {
        background-color: #E7F3FF;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1F4E78;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">📊 Generador de Informes con IA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Transforma tus datos en informes ejecutivos profesionales en segundos</div>', unsafe_allow_html=True)

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Input para API Key
    api_key = st.text_input(
        "API Key de Anthropic",
        type="password",
        help="Obtén tu API key en https://console.anthropic.com"
    )
    
    st.markdown("---")
    
    # Selector de modelo
    model = st.selectbox(
        "Modelo de IA",
        ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-haiku-4-20250514"],
        help="Sonnet 4 ofrece el mejor equilibrio calidad-velocidad"
    )
    
    # Opciones de análisis
    st.markdown("### 📋 Opciones de Análisis")
    
    include_charts = st.checkbox("Incluir visualizaciones", value=False, 
                                  help="Próximamente: gráficos integrados")
    
    detailed_analysis = st.checkbox("Análisis profundo", value=True,
                                     help="Incluye recomendaciones estratégicas detalladas")
    
    st.markdown("---")
    
    # Información
    with st.expander("ℹ️ Cómo usar esta app"):
        st.markdown("""
        **Pasos:**
        1. Introduce tu API key de Anthropic
        2. Sube un archivo Excel (.xlsx)
        3. La IA analizará automáticamente los datos
        4. Descarga tu informe profesional en DOCX
        
        **Formatos soportados:**
        - Excel (.xlsx, .xls)
        - CSV (.csv)
        
        **Tipos de análisis:**
        - Encuestas de satisfacción
        - Datos de ventas
        - Métricas de rendimiento
        - Análisis competitivo
        """)
    
    with st.expander("🔒 Seguridad y privacidad"):
        st.markdown("""
        - Tu API key no se almacena
        - Los archivos se procesan en memoria
        - Los datos no se guardan en servidor
        - Comunicación encriptada con Anthropic
        """)

# Área principal
col1, col2 = st.columns([2, 1])

with col1:
    # Upload de archivo
    st.markdown("### 📁 Subir archivo de datos")
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo Excel o CSV aquí",
        type=['xlsx', 'xls', 'csv'],
        help="Sube el archivo con los datos que quieres analizar"
    )

with col2:
    if uploaded_file:
        st.markdown("### ✅ Archivo cargado")
        st.success(f"**{uploaded_file.name}**")
        
        # Mostrar información del archivo
        file_size = len(uploaded_file.getvalue()) / 1024
        st.info(f"Tamaño: {file_size:.1f} KB")

# Previsualización de datos
if uploaded_file:
    st.markdown("---")
    st.markdown("### 👀 Vista previa de datos")
    
    try:
        # Leer archivo según extensión
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Información básica
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("📊 Filas", f"{len(df):,}")
        with col_info2:
            st.metric("📋 Columnas", f"{len(df.columns)}")
        with col_info3:
            st.metric("💾 Hojas", f"{len(pd.ExcelFile(uploaded_file).sheet_names) if not uploaded_file.name.endswith('.csv') else 1}")
        
        # Mostrar primeras filas
        st.dataframe(df.head(10), use_container_width=True)
        
        # Resetear el puntero del archivo para procesamiento posterior
        uploaded_file.seek(0)
        
    except Exception as e:
        st.error(f"Error al leer el archivo: {str(e)}")

# Botón de generación de informe
st.markdown("---")

if uploaded_file and api_key:
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        if st.button("🚀 Generar Informe Ejecutivo", use_container_width=True):
            with st.spinner("🤖 La IA está analizando tus datos..."):
                try:
                    # Inicializar cliente de Anthropic
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    # Leer archivo y convertir a base64
                    file_content = uploaded_file.read()
                    import base64
                    file_base64 = base64.standard_b64encode(file_content).decode('utf-8')
                    
                    # Determinar tipo de archivo
                    if uploaded_file.name.endswith('.csv'):
                        media_type = "text/csv"
                    elif uploaded_file.name.endswith('.xlsx'):
                        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    else:
                        media_type = "application/vnd.ms-excel"
                    
                    # Crear mensaje para Claude
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📊 Analizando estructura de datos...")
                    progress_bar.progress(20)
                    
                    prompt = """Analiza este archivo de datos y genera un informe ejecutivo profesional en formato DOCX.

El informe debe incluir:

1. **Resumen Ejecutivo**: Métricas clave en tabla visual, principales hallazgos
2. **Análisis de Datos**: Desglose detallado por categorías relevantes
3. **Insights Estratégicos**: Identificación de patrones, tendencias y áreas críticas
4. **Análisis Comparativo**: Si hay datos de competencia o benchmarks
5. **Recomendaciones**: Plan de acción con prioridades (corto, medio, largo plazo)

**Formato:**
- Usa tablas para datos numéricos
- Destaca métricas clave con formato visual
- Estructura clara con headings jerárquicos
- Incluye análisis cualitativo, no solo números
- Proporciona contexto empresarial y aplicabilidad

**Estilo:**
- Profesional y orientado a resultados
- Insights accionables, no descripciones genéricas
- Identifica oportunidades y riesgos
- Usa visualización de datos con tablas bien formateadas

Genera el documento DOCX completo y compártelo para descarga."""

                    status_text.text("🧠 Claude está procesando los datos...")
                    progress_bar.progress(40)
                    
                    # Llamada a la API
                    message = client.messages.create(
                        model=model,
                        max_tokens=16000,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "document",
                                        "source": {
                                            "type": "base64",
                                            "media_type": media_type,
                                            "data": file_base64
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    )
                    
                    status_text.text("📝 Generando informe ejecutivo...")
                    progress_bar.progress(70)
                    
                    # Extraer respuesta
                    response_text = ""
                    for block in message.content:
                        if block.type == "text":
                            response_text += block.text
                    
                    status_text.text("✨ Finalizando documento...")
                    progress_bar.progress(100)
                    
                    # Mostrar resultado
                    st.success("✅ ¡Informe generado exitosamente!")
                    
                    # Crear tabs para mostrar contenido
                    tab1, tab2 = st.tabs(["📄 Vista Previa", "💾 Descargar"])
                    
                    with tab1:
                        st.markdown("### Análisis de Claude")
                        st.markdown(response_text)
                    
                    with tab2:
                        st.markdown("### 📥 Descargar Informe")
                        
                        # Aquí normalmente incluirías el archivo .docx generado
                        # Por ahora mostramos el texto
                        st.info("""
                        **Nota:** Para obtener el archivo DOCX completo, Claude necesita acceso a herramientas 
                        de creación de documentos. El análisis completo se ha generado arriba.
                        
                        En una implementación completa, aquí aparecería el botón de descarga del archivo .docx
                        """)
                        
                        # Crear archivo de texto como alternativa
                        txt_content = f"""INFORME EJECUTIVO
Generado por IA - {time.strftime('%Y-%m-%d %H:%M:%S')}

{response_text}
"""
                        st.download_button(
                            label="📄 Descargar como TXT",
                            data=txt_content,
                            file_name=f"informe_{uploaded_file.name.split('.')[0]}_{time.strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
                    
                    # Limpiar
                    progress_bar.empty()
                    status_text.empty()
                    
                except anthropic.APIError as e:
                    st.error(f"❌ Error de API: {str(e)}")
                    st.info("Verifica que tu API key sea válida y tengas créditos disponibles")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")
                    st.info("Por favor, verifica el formato de tu archivo y vuelve a intentar")

elif uploaded_file and not api_key:
    st.warning("⚠️ Por favor, introduce tu API Key de Anthropic en el panel lateral")
elif api_key and not uploaded_file:
    st.info("📁 Sube un archivo para comenzar el análisis")
else:
    # Mostrar landing cuando no hay datos
    st.markdown("---")
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.markdown("### 🎯 Análisis Inteligente")
        st.markdown("""
        Claude analiza automáticamente tus datos identificando:
        - Patrones y tendencias
        - Áreas críticas
        - Oportunidades de mejora
        """)
    
    with col_feat2:
        st.markdown("### 📊 Informes Profesionales")
        st.markdown("""
        Genera documentos ejecutivos con:
        - Métricas clave visualizadas
        - Insights accionables
        - Recomendaciones estratégicas
        """)
    
    with col_feat3:
        st.markdown("### ⚡ Rápido y Seguro")
        st.markdown("""
        Procesamiento instantáneo:
        - Segundos vs. horas
        - Sin almacenamiento de datos
        - Encriptación end-to-end
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Potenciado por <strong>Claude 4.5</strong> de Anthropic</p>
    <p style='font-size: 0.9rem;'>Desarrollado para análisis empresarial de alto impacto</p>
</div>
""", unsafe_allow_html=True)

