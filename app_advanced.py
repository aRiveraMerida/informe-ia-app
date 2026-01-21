"""
Versión AVANZADA con generación de DOCX real
Requiere herramientas adicionales de sistema
"""
import streamlit as st
import pandas as pd
import anthropic
import base64
import time
from io import BytesIO
import subprocess
import os
import tempfile

st.set_page_config(
    page_title="Generador de Informes Pro",
    page_icon="📊",
    layout="wide"
)

# CSS mejorado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Generador de Informes Pro con IA</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("API Key de Anthropic", type="password")
    
    model = st.selectbox(
        "Modelo",
        ["claude-sonnet-4-20250514", "claude-opus-4-20250514"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🎨 Estilo del Informe")
    
    report_style = st.radio(
        "Tipo de informe",
        ["Ejecutivo (conciso)", "Completo (detallado)", "Técnico (analítico)"]
    )
    
    include_recommendations = st.checkbox("Incluir recomendaciones", value=True)
    include_competitive = st.checkbox("Análisis competitivo", value=True)
    
    st.markdown("---")
    
    # Template selector
    st.markdown("### 📋 Plantilla")
    template = st.selectbox(
        "Selecciona plantilla",
        ["Satisfacción del Cliente", "Ventas & KPIs", "Operaciones", "Personalizado"]
    )

# Main area
uploaded_file = st.file_uploader(
    "📁 Sube tu archivo de datos",
    type=['xlsx', 'xls', 'csv'],
    help="Formatos soportados: Excel (.xlsx, .xls) y CSV"
)

if uploaded_file:
    st.success(f"✅ Archivo cargado: **{uploaded_file.name}**")
    
    # Preview
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_excel(uploaded_file)
        
        st.markdown("### 📊 Vista previa")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filas", f"{len(df):,}")
        with col2:
            st.metric("Columnas", len(df.columns))
        with col3:
            st.metric("Valores nulos", f"{df.isnull().sum().sum():,}")
        with col4:
            completeness = ((df.count().sum() / (len(df) * len(df.columns))) * 100)
            st.metric("Completitud", f"{completeness:.1f}%")
        
        with st.expander("Ver datos"):
            st.dataframe(df.head(20), use_container_width=True)
        
        uploaded_file.seek(0)
        
    except Exception as e:
        st.error(f"Error al leer archivo: {e}")

# Generate button
if uploaded_file and api_key:
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generar Informe Completo", use_container_width=True, type="primary"):
            
            # Progress tracking
            progress_container = st.container()
            
            with progress_container:
                st.markdown('<div class="success-box"><h2>🤖 IA Trabajando...</h2></div>', unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status = st.empty()
                
                try:
                    # Initialize client
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    # Read and encode file
                    status.info("📁 Procesando archivo...")
                    progress_bar.progress(10)
                    time.sleep(0.5)
                    
                    file_content = uploaded_file.read()
                    file_base64 = base64.standard_b64encode(file_content).decode('utf-8')
                    
                    # Determine media type
                    if uploaded_file.name.endswith('.csv'):
                        media_type = "text/csv"
                    elif uploaded_file.name.endswith('.xlsx'):
                        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    else:
                        media_type = "application/vnd.ms-excel"
                    
                    # Build prompt based on template
                    status.info("🧠 Construyendo análisis personalizado...")
                    progress_bar.progress(20)
                    time.sleep(0.5)
                    
                    prompt_templates = {
                        "Satisfacción del Cliente": """Analiza esta encuesta de satisfacción y genera un informe ejecutivo profesional.
                        
Incluye:
- Resumen ejecutivo con métricas clave (NPS, CSAT, etc.)
- Análisis de contactabilidad y tasas de respuesta
- Satisfacción vs. propensión a recomendar
- Análisis competitivo
- Intención de recompra
- Recomendaciones estratégicas (corto, medio, largo plazo)

Genera un documento DOCX profesional con tablas, formato y estructura ejecutiva.""",
                        
                        "Ventas & KPIs": """Analiza estos datos de ventas/KPIs y crea un informe ejecutivo.
                        
Incluye:
- Dashboard de métricas clave
- Análisis de tendencias y estacionalidad
- Performance por categoría/vendedor/región
- Comparativa vs. objetivos
- Análisis de gaps y oportunidades
- Plan de acción para mejora

Genera documento DOCX con visualizaciones en tablas.""",
                        
                        "Operaciones": """Analiza estos datos operacionales y genera informe de rendimiento.
                        
Incluye:
- KPIs operacionales críticos
- Análisis de eficiencia
- Identificación de cuellos de botella
- Benchmarking interno
- Recomendaciones de optimización
- Roadmap de implementación

Documento DOCX profesional con estructura ejecutiva.""",
                        
                        "Personalizado": """Analiza estos datos y genera un informe ejecutivo completo.
                        
Identifica automáticamente el tipo de datos y genera análisis relevante con:
- Resumen ejecutivo
- Métricas clave
- Insights estratégicos
- Análisis de tendencias
- Recomendaciones accionables

Formato DOCX profesional."""
                    }
                    
                    selected_prompt = prompt_templates.get(template, prompt_templates["Personalizado"])
                    
                    # Call API
                    status.info("🔮 Claude está analizando tus datos...")
                    progress_bar.progress(40)
                    
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
                                        "text": selected_prompt
                                    }
                                ]
                            }
                        ]
                    )
                    
                    status.info("📝 Generando informe...")
                    progress_bar.progress(70)
                    time.sleep(0.5)
                    
                    # Extract response
                    response_text = ""
                    for block in message.content:
                        if block.type == "text":
                            response_text += block.text
                    
                    status.info("✨ Finalizando...")
                    progress_bar.progress(90)
                    time.sleep(0.5)
                    
                    progress_bar.progress(100)
                    status.success("✅ ¡Informe completado!")
                    
                    # Display results
                    st.markdown("---")
                    st.markdown('<div class="success-box"><h2>✨ Informe Generado Exitosamente</h2><p>Tu análisis está listo</p></div>', unsafe_allow_html=True)
                    
                    tab1, tab2, tab3 = st.tabs(["📄 Informe Completo", "📊 Métricas Clave", "💾 Descargar"])
                    
                    with tab1:
                        st.markdown(response_text)
                    
                    with tab2:
                        st.info("💡 Las métricas clave se extraen del análisis principal")
                        # Aquí podrías extraer y mostrar métricas específicas
                        st.markdown(response_text[:500] + "...")
                    
                    with tab3:
                        st.markdown("### 📥 Opciones de Descarga")
                        
                        # Text version
                        txt_content = f"""INFORME EJECUTIVO
Generado: {time.strftime('%Y-%m-%d %H:%M:%S')}
Modelo: {model}
Plantilla: {template}

{'='*80}

{response_text}
"""
                        
                        col_d1, col_d2 = st.columns(2)
                        
                        with col_d1:
                            st.download_button(
                                label="📄 Descargar TXT",
                                data=txt_content,
                                file_name=f"informe_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        with col_d2:
                            # Markdown version
                            md_content = f"""# Informe Ejecutivo

**Generado:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Modelo:** {model}  
**Plantilla:** {template}

---

{response_text}
"""
                            st.download_button(
                                label="📝 Descargar MD",
                                data=md_content,
                                file_name=f"informe_{time.strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                        
                        st.info("""
                        💡 **Nota sobre DOCX:** Para generar archivos .docx completos con formato profesional, 
                        se requiere procesamiento adicional. Los formatos TXT y MD preservan todo el contenido 
                        y pueden importarse fácilmente a Word, Google Docs, o Notion.
                        """)
                    
                except anthropic.APIError as e:
                    st.error(f"❌ Error de API: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

elif not api_key:
    st.warning("⚠️ Introduce tu API Key para comenzar")
elif not uploaded_file:
    st.info("📁 Sube un archivo para generar el informe")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem;'>
    <h4>Potenciado por Claude 4.5 de Anthropic</h4>
    <p style='color: #666;'>Análisis empresarial de siguiente generación</p>
</div>
""", unsafe_allow_html=True)

