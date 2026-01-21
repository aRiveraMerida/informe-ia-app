"""
Generador de Informes Ejecutivos con IA - Versión Profesional
Análisis cuantitativo + cualitativo (Claude) + PDF personalizable
"""
import streamlit as st
import os
import time
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos propios
from modules import (
    DataProcessor,
    QuantitativeAnalyzer,
    ClaudeAnalyzer,
    PDFReportGenerator,
    DOCXReportGenerator
)

# Configuración de página
st.set_page_config(
    page_title="Generador de Informes Pro - IA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .cost-box {
        background: #FFF3CD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FFC107;
        margin: 1rem 0;
    }
    .success-box {
        background: #D4EDDA;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28A745;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'quantitative_results' not in st.session_state:
    st.session_state.quantitative_results = None
if 'qualitative_results' not in st.session_state:
    st.session_state.qualitative_results = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'cost_summary' not in st.session_state:
    st.session_state.cost_summary = None
if 'file_content' not in st.session_state:
    st.session_state.file_content = None
if 'filename' not in st.session_state:
    st.session_state.filename = None

# Header
st.markdown('<div class="main-header">Generador de Informes Ejecutivos con IA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Análisis cuantitativo + estratégico con IA + PDF personalizable</div>', unsafe_allow_html=True)

# Sidebar - Configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # API Key - Soporta: secrets de Streamlit Cloud, variable de entorno, o input manual
    st.markdown("### API Key de Claude")
    
    # Intentar obtener de Streamlit secrets primero (para Streamlit Cloud)
    default_api_key = ""
    try:
        default_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except:
        pass
    
    # Si no hay en secrets, intentar variable de entorno
    if not default_api_key:
        default_api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    api_key_input = st.text_input(
        "API Key",
        type="password",
        value=default_api_key,
        help="Tu API key de Anthropic. En Streamlit Cloud, configurala en Settings > Secrets",
        key="api_key_input"
    )
    
    api_key = api_key_input if api_key_input else default_api_key
    
    if api_key:
        st.success("API Key configurada")
    else:
        st.warning("API Key requerida")
        st.caption("Configurala en Settings > Secrets en Streamlit Cloud")
    
    st.markdown("---")
    
    # Modelo
    st.markdown("### 🤖 Modelo de IA")
    model = st.selectbox(
        "Modelo",
        [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-haiku-4-20250514"
        ],
        index=0,
        help="Sonnet 4: mejor balance calidad/precio. Opus 4: máxima calidad. Haiku 4: más económico"
    )
    
    # Mostrar pricing
    pricing_info = {
        "claude-sonnet-4-20250514": "$3 / $15 por MTok",
        "claude-opus-4-20250514": "$15 / $75 por MTok",
        "claude-haiku-4-20250514": "$0.80 / $4 por MTok"
    }
    st.caption(f"Precio: {pricing_info[model]} (in/out)")
    
    st.markdown("---")
    
    # Metadatos del informe
    st.markdown("### Metadatos del Informe")
    
    client_name = st.text_input(
        "Nombre del Cliente",
        value="Cliente Ejemplo S.A.",
        help="Aparecerá en la portada del PDF"
    )
    
    st.markdown("**Periodo Analizado**")
    col_fecha1, col_fecha2 = st.columns(2)
    with col_fecha1:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=datetime.now().date() - timedelta(days=30),
            format="DD/MM/YYYY",
            help="Fecha de inicio del periodo"
        )
    with col_fecha2:
        fecha_fin = st.date_input(
            "Fecha fin",
            value=datetime.now().date(),
            format="DD/MM/YYYY",
            help="Fecha de fin del periodo"
        )
    
    # Formatear periodo como string
    period = f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
    st.caption(f"Periodo: {period}")
    
    report_type = st.selectbox(
        "Tipo de Informe",
        [
            "Análisis General",
            "Análisis de encuestas",
            "Satisfacción del Cliente",
            "Ventas y KPIs",
            "Operaciones",
            "otros"
        ]
    )
    
    st.markdown("---")
    
    # Opciones de logos
    st.markdown("### 🎨 Personalización PDF")
    
    use_logos = st.checkbox("Incluir logos", value=False)
    
    company_logo = None
    client_logo = None
    
    if use_logos:
        st.caption("**Logo Empresa (portada)**")
        company_logo_file = st.file_uploader(
            "Logo empresa",
            type=['png', 'jpg', 'jpeg'],
            key='company_logo',
            label_visibility='collapsed'
        )
        
        st.caption("**Logo Cliente (pie de página)**")
        client_logo_file = st.file_uploader(
            "Logo cliente",
            type=['png', 'jpg', 'jpeg'],
            key='client_logo',
            label_visibility='collapsed'
        )
        
        # Guardar temporalmente si se suben
        if company_logo_file:
            company_logo = f"/tmp/company_logo_{int(time.time())}.png"
            with open(company_logo, 'wb') as f:
                f.write(company_logo_file.read())
        
        if client_logo_file:
            client_logo = f"/tmp/client_logo_{int(time.time())}.png"
            with open(client_logo, 'wb') as f:
                f.write(client_logo_file.read())
    
    st.markdown("---")
    
    # Info
    with st.expander("Cómo funciona"):
        st.markdown("""
        **Flujo de análisis:**
        
        1. **Carga de datos**: Sube Excel/CSV
        2. **Análisis cuantitativo**: Análisis determinista sin IA
        3. **Análisis cualitativo**: IA interpreta y recomienda
        4. **Preview**: Revisa el informe
        5. **PDF**: Descarga con personalización
        
        **Tipos de análisis soportados:**
        - Análisis general
        - Análisis de encuestas
        - Satisfacción del cliente
        - Ventas y KPIs
        - Operaciones
        - Cualquier dataset tabular
        
        """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📁 Subir Archivo de Datos")
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo Excel o CSV",
        type=['xlsx', 'xls', 'csv'],
        help="Soporta archivos con múltiples hojas"
    )

with col2:
    if uploaded_file:
        st.markdown("### ✅ Archivo Cargado")
        file_size_kb = len(uploaded_file.getvalue()) / 1024
        
        st.info(f"""
        **{uploaded_file.name}**
        
        Tamaño: {file_size_kb:.1f} KB
        """)
        
        # Guardar en session state
        if st.session_state.file_content is None:
            st.session_state.file_content = uploaded_file.getvalue()
            st.session_state.filename = uploaded_file.name

# Vista previa de datos
if uploaded_file and not st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown("### 👀 Vista Previa de Datos")
    
    try:
        # Procesar datos
        processor = DataProcessor(st.session_state.file_content, st.session_state.filename)
        result = processor.process()
        
        if result['success']:
            metadata = result['metadata']
            
            # Métricas básicas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Hojas", metadata['_global']['total_sheets'])
            with col2:
                st.metric("📝 Filas totales", f"{metadata['_global']['total_rows']:,}")
            with col3:
                st.metric("📋 Columnas totales", metadata['_global']['total_columns'])
            with col4:
                completeness = sum(
                    meta['completeness_pct'] for sheet, meta in metadata.items() if sheet != '_global'
                ) / max(1, len([k for k in metadata.keys() if k != '_global']))
                st.metric("✨ Completitud", f"{completeness:.1f}%")
            
            # Mostrar muestra de cada hoja
            samples = processor.get_sample_data(n=5)
            
            for sheet_name, df_sample in samples.items():
                with st.expander(f"📄 Hoja: {sheet_name} ({len(result['sheets'][sheet_name])} filas)"):
                    st.dataframe(df_sample, width='stretch')
        else:
            st.error(f"❌ Error al procesar archivo: {result.get('error', 'Error desconocido')}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Botón de generación
if uploaded_file and api_key and not st.session_state.analysis_complete:
    st.markdown("---")
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        # Estimar coste
        if api_key:
            try:
                analyzer = ClaudeAnalyzer(api_key)
                estimated_cost = analyzer.estimate_cost_before_call(
                    len(st.session_state.file_content),
                    model
                )
                st.caption(f"💵 Coste estimado: ${estimated_cost:.4f} USD")
            except:
                pass
        
        if st.button("🚀 Generar Informe Completo", width='stretch', type="primary"):
            
            progress_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 1. Procesar datos
                    status_text.info("📁 Procesando archivo y detectando estructura...")
                    progress_bar.progress(10)
                    time.sleep(0.3)
                    
                    processor = DataProcessor(st.session_state.file_content, st.session_state.filename)
                    processed_data = processor.process()
                    
                    if not processed_data['success']:
                        st.error(f"Error al procesar datos: {processed_data.get('error')}")
                        st.stop()
                    
                    st.session_state.processed_data = processed_data
                    
                    # 2. Análisis cuantitativo
                    status_text.info("📊 Ejecutando análisis cuantitativo determinista...")
                    progress_bar.progress(25)
                    time.sleep(0.3)
                    
                    quant_analyzer = QuantitativeAnalyzer(
                        processed_data['sheets'],
                        processed_data['metadata']
                    )
                    quant_results = quant_analyzer.analyze()
                    quant_report = quant_analyzer.format_for_report()
                    
                    st.session_state.quantitative_results = {
                        'results': quant_results,
                        'report': quant_report
                    }
                    
                    progress_bar.progress(40)
                    
                    # 3. Análisis cualitativo con Claude
                    status_text.info("🧠 Claude está analizando los datos y generando insights estratégicos...")
                    progress_bar.progress(50)
                    
                    claude = ClaudeAnalyzer(api_key)
                    
                    report_metadata = {
                        'client_name': client_name,
                        'period': period,
                        'report_type': report_type,
                        'total_sheets': processed_data['metadata']['_global']['total_sheets'],
                        'total_records': processed_data['metadata']['_global']['total_rows']
                    }
                    
                    claude_result = claude.analyze_data(
                        file_content=st.session_state.file_content,
                        filename=st.session_state.filename,
                        quantitative_analysis=quant_report,
                        report_metadata=report_metadata,
                        model=model,
                        max_tokens=16000
                    )
                    
                    if not claude_result['success']:
                        st.error(f"❌ Error de Claude: {claude_result.get('error')}")
                        st.stop()
                    
                    st.session_state.qualitative_results = claude_result
                    st.session_state.cost_summary = claude.get_cost_summary()
                    
                    progress_bar.progress(90)
                    status_text.success("✅ Análisis completado exitosamente!")
                    
                    time.sleep(0.5)
                    progress_bar.progress(100)
                    time.sleep(0.3)
                    
                    # Marcar como completo
                    st.session_state.analysis_complete = True
                    
                    # Limpiar
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Rerun para mostrar resultados
                    st.rerun()
                
                except Exception as e:
                    status_text.error(f"❌ Error inesperado: {str(e)}")
                    logger.exception("Error durante el análisis")
                    st.stop()

# Mostrar resultados si el análisis está completo
if st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown('<div class="success-box"><h2>✨ Análisis Completado</h2></div>', unsafe_allow_html=True)
    
    # Mostrar costes
    if st.session_state.cost_summary:
        cost_summary = st.session_state.cost_summary
        
        col_cost1, col_cost2, col_cost3, col_cost4 = st.columns(4)
        
        with col_cost1:
            st.metric(
                "💰 Coste Total",
                f"${cost_summary['total_cost_usd']:.4f}"
            )
        with col_cost2:
            st.metric(
                "📥 Tokens Entrada",
                f"{cost_summary['total_input_tokens']:,}"
            )
        with col_cost3:
            st.metric(
                "📤 Tokens Salida",
                f"{cost_summary['total_output_tokens']:,}"
            )
        with col_cost4:
            st.metric(
                "🤖 Modelo",
                model.split('-')[1].title()
            )
    
    st.markdown("---")
    
    # Tabs para preview y descarga
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Análisis Cuantitativo", "🧠 Informe Ejecutivo", "📄 Descargar DOCX", "💾 Descargar PDF"])
    
    with tab1:
        st.markdown("### Análisis Cuantitativo (Determinista)")
        if st.session_state.quantitative_results:
            st.markdown(st.session_state.quantitative_results['report'])
    
    with tab2:
        st.markdown("### Informe Ejecutivo Completo (Generado por Claude)")
        if st.session_state.qualitative_results:
            st.markdown(st.session_state.qualitative_results['analysis'])
    
    with tab3:
        st.markdown("### 📄 Descargar como DOCX (Editable)")
        
        st.info("📝 **Recomendado**: Descarga en formato Word para revisar y editar el informe antes de compartirlo con tu cliente.")
        
        if st.button("📃 Generar DOCX Editable", key="btn_docx"):
            with st.spinner("Generando documento Word..."):
                try:
                    # Generar DOCX
                    docx_gen = DOCXReportGenerator(
                        client_name=client_name,
                        period=period,
                        report_title="Informe Ejecutivo"
                    )
                    
                    docx_bytes = docx_gen.generate(
                        analysis_text=st.session_state.qualitative_results['analysis'],
                        metadata={
                            'total_records': st.session_state.processed_data['metadata']['_global']['total_rows'],
                            **st.session_state.cost_summary
                        }
                    )
                    
                    st.success("✅ Documento Word generado exitosamente")
                    
                    # Botón de descarga
                    st.download_button(
                        label="📥 Descargar DOCX",
                        data=docx_bytes,
                        file_name=f"informe_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_docx"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error al generar DOCX: {str(e)}")
                    logger.exception("Error generando DOCX")
    
    with tab4:
        st.markdown("### 💾 Descargar como PDF")
        
        st.info("El PDF incluirá: portada personalizada, análisis cuantitativo, análisis estratégico y metadatos de generación.")
        
        if st.button("🎨 Generar PDF Profesional", key="btn_pdf"):
            with st.spinner("Generando PDF..."):
                try:
                    # Generar PDF
                    pdf_gen = PDFReportGenerator(
                        client_name=client_name,
                        period=period,
                        report_title="Informe Ejecutivo de Análisis de Datos",
                        company_logo_path=company_logo,
                        client_logo_path=client_logo
                    )
                    
                    pdf_bytes = pdf_gen.generate(
                        quantitative_analysis=st.session_state.quantitative_results['report'],
                        qualitative_analysis=st.session_state.qualitative_results['analysis'],
                        metadata=st.session_state.processed_data['metadata']['_global'],
                        cost_info=st.session_state.cost_summary
                    )
                    
                    st.success("✅ PDF generado exitosamente")
                    
                    # Botón de descarga
                    st.download_button(
                        label="📥 Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"informe_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        key="download_pdf"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error al generar PDF: {str(e)}")
                    logger.exception("Error generando PDF")
    
    # Botón para reiniciar
    st.markdown("---")
    if st.button("🔄 Analizar Otro Archivo"):
        # Limpiar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <p style='color: #666;'>
        <small>Análisis cuantitativo determinista + Análisis estratégico con IA</small>
    </p>
</div>
""", unsafe_allow_html=True)
