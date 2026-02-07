"""
Generador de Informes Ejecutivos con IA — Versión Profesional
Análisis cuantitativo + cualitativo (Claude) + Gráficos + PDF/DOCX
"""
import streamlit as st
import os
import time
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from modules import (
    DataProcessor,
    QuantitativeAnalyzer,
    ClaudeAnalyzer,
    PDFReportGenerator,
    DOCXReportGenerator,
    PPTXReportGenerator,
    ChartGenerator,
    validate_quality,
    prompt_manager,
    config,
    styles,
    session_state,
)
from modules.report_chart_extractor import generate_charts_for_report

# ─── Configuración de página ─────────────────────────────────────────────────

st.set_page_config(
    page_title="Movimer — Informes con IA",
    page_icon="LogoMovimer.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(styles.APP_CSS, unsafe_allow_html=True)
session_state.init_session_state()

# ─── Header ──────────────────────────────────────────────────────────────────

import base64, pathlib
_logo_path = pathlib.Path(__file__).parent / "LogoMovimer.png"
if _logo_path.exists():
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    st.markdown(
        f'<div class="logo-container"><img src="data:image/png;base64,{_logo_b64}" alt="Movimer"></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="main-header">Generador de Informes Ejecutivos con IA</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Analisis cuantitativo + estrategico con IA / Graficos / PDF / DOCX / PPTX</div>',
    unsafe_allow_html=True,
)

# ─── Sidebar — Configuración ─────────────────────────────────────────────────

with st.sidebar:
    st.header("Configuracion")

    # API Key
    st.markdown("### API Key de Claude")
    default_api_key = ""
    try:
        default_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass
    if not default_api_key:
        default_api_key = os.getenv("ANTHROPIC_API_KEY", "")

    api_key_input = st.text_input(
        "API Key",
        type="password",
        value=default_api_key,
        help="Tu API key de Anthropic",
        key="api_key_input",
    )
    api_key = api_key_input or default_api_key

    if api_key:
        st.success("API Key configurada")
    else:
        st.warning("API Key requerida")

    st.markdown("---")

    # Modelo
    st.markdown("### Modelo de IA")
    model = st.selectbox("Modelo", config.MODELS, index=0)
    pricing = config.MODEL_PRICING[model]
    st.caption(f"Precio: ${pricing['input']} / ${pricing['output']} por MTok (in/out)")

    st.markdown("---")

    # Metadatos del informe
    st.markdown("### Metadatos del Informe")
    client_name = st.text_input("Nombre del Cliente", value="Cliente Ejemplo S.A.")

    st.markdown("**Periodo Analizado**")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=datetime.now().date() - timedelta(days=30),
            format="DD/MM/YYYY",
        )
    with col_f2:
        fecha_fin = st.date_input(
            "Fecha fin", value=datetime.now().date(), format="DD/MM/YYYY"
        )
    period = f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
    st.caption(f"Periodo: {period}")

    report_type = st.selectbox("Tipo de Informe", config.REPORT_TYPES)

    st.markdown("---")

    # Logos
    st.markdown("### Personalizacion PDF")
    use_logos = st.checkbox("Incluir logos", value=False)
    company_logo = None
    client_logo = None

    if use_logos:
        company_logo_file = st.file_uploader(
            "Logo empresa (portada)",
            type=["png", "jpg", "jpeg"],
            key="company_logo",
        )
        client_logo_file = st.file_uploader(
            "Logo cliente (pie)", type=["png", "jpg", "jpeg"], key="client_logo"
        )
        if company_logo_file:
            company_logo = f"/tmp/company_logo_{int(time.time())}.png"
            with open(company_logo, "wb") as f:
                f.write(company_logo_file.read())
        if client_logo_file:
            client_logo = f"/tmp/client_logo_{int(time.time())}.png"
            with open(client_logo, "wb") as f:
                f.write(client_logo_file.read())

    st.markdown("---")

    with st.expander("Como funciona"):
        st.markdown("""
        1. **Carga** tu archivo Excel/CSV (cualquier dataset)
        2. **Genera** análisis cuantitativo + ejecutivo con IA
        3. Los gráficos se generan **automáticamente** desde las tablas del informe
        4. **Descarga** PDF o DOCX con gráficos integrados
        """)

# ─── Área principal — Subida de archivo ──────────────────────────────────────

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Subir Archivo de Datos")
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo Excel o CSV",
        type=["xlsx", "xls", "csv"],
        help="Soporta cualquier dataset tabular, múltiples hojas",
    )

with col2:
    if uploaded_file:
        st.markdown("### Archivo Cargado")
        file_size_kb = len(uploaded_file.getvalue()) / 1024
        st.info(f"**{uploaded_file.name}**\n\nTamaño: {file_size_kb:.1f} KB")

        if st.session_state.file_content is None:
            session_state.store_file(uploaded_file.getvalue(), uploaded_file.name)

# ─── Funciones con caché ─────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _process_file(file_content: bytes, filename: str):
    """Procesa el archivo una sola vez y cachea el resultado."""
    processor = DataProcessor(file_content, filename)
    return processor.process(), processor.get_sample_data(n=5)

# ─── Vista previa de datos ───────────────────────────────────────────────────

if uploaded_file and not st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown("### Vista Previa de Datos")

    try:
        result, samples = _process_file(st.session_state.file_content, st.session_state.filename)

        if result["success"]:
            metadata = result["metadata"]

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("Hojas", metadata["_global"]["total_sheets"])
            with col_m2:
                st.metric("Filas totales", f"{metadata['_global']['total_rows']:,}")
            with col_m3:
                st.metric("Columnas totales", metadata["_global"]["total_columns"])
            with col_m4:
                completeness = sum(
                    meta["completeness_pct"]
                    for sheet, meta in metadata.items()
                    if sheet != "_global"
                ) / max(1, len([k for k in metadata.keys() if k != "_global"]))
                st.metric("Completitud", f"{completeness:.1f}%")

            for sheet_name, df_sample in samples.items():
                with st.expander(
                    f"Hoja: {sheet_name} ({len(result['sheets'][sheet_name])} filas)"
                ):
                    st.dataframe(df_sample, width='stretch')

            # Validación de calidad de datos
            quality = validate_quality(result["sheets"])
            st.markdown("### Calidad de Datos")
            qcol1, qcol2, qcol3 = st.columns(3)
            with qcol1:
                st.metric("Score", f"{quality.score}/100 {quality.status_emoji}")
            with qcol2:
                st.metric("Estado", quality.status.capitalize())
            with qcol3:
                st.metric("Incidencias", quality.total_issues)

            if quality.issues:
                with st.expander(f"Ver {quality.total_issues} incidencias detectadas"):
                    for issue in quality.issues:
                        icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "")
                        st.markdown(f"{icon} **{issue.message}**")
                        if issue.detail:
                            st.caption(issue.detail)
        else:
            st.error(f"Error: {result.get('error', 'Error desconocido')}")

    except Exception as e:
        st.error(f"Error: {e}")

# ─── Editor de prompt maestro ────────────────────────────────────────────────────

if uploaded_file and not st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown("### Prompt Maestro")

    with st.expander("Editar prompt (avanzado)", expanded=False):
        st.markdown(
            '<div class="prompt-info">Edita el prompt que se envía a Claude. '
            "Si lo borras completamente, se restaurará el prompt por defecto.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(prompt_manager.get_variables_help())

        current_prompt = (
            st.session_state.custom_prompt
            or prompt_manager.get_prompt(report_type=report_type)
        )
        edited_prompt = st.text_area(
            "Prompt",
            value=current_prompt,
            height=400,
            key="prompt_editor",
            label_visibility="collapsed",
        )

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("Guardar prompt personalizado"):
                st.session_state.custom_prompt = edited_prompt
                st.success("Prompt guardado")
        with col_p2:
            if st.button("Restaurar prompt por defecto"):
                st.session_state.custom_prompt = None
                st.success("Prompt restaurado al valor por defecto")
                st.rerun()

# ─── Botón de generación ─────────────────────────────────────────────────────

if uploaded_file and api_key and not st.session_state.analysis_complete:
    st.markdown("---")

    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        # Estimación de coste
        try:
            analyzer_est = ClaudeAnalyzer(api_key)
            estimated_cost = analyzer_est.estimate_cost_before_call(
                len(st.session_state.file_content), model
            )
            st.caption(f"Coste estimado: ${estimated_cost:.4f} USD")
        except Exception:
            pass

        if st.button("Generar Informe Completo", use_container_width=True, type="primary"):
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # 1. Procesar datos
                    status_text.info("Procesando archivo...")
                    progress_bar.progress(10)

                    processor = DataProcessor(
                        st.session_state.file_content, st.session_state.filename
                    )
                    processed_data = processor.process()

                    if not processed_data["success"]:
                        st.error(f"Error: {processed_data.get('error')}")
                        st.stop()

                    # 2. Analisis cuantitativo
                    status_text.info("Analisis cuantitativo...")
                    progress_bar.progress(20)

                    quant_analyzer = QuantitativeAnalyzer(
                        processed_data["sheets"], processed_data["metadata"]
                    )
                    quant_results = quant_analyzer.analyze()
                    quant_report = quant_analyzer.format_for_report()

                    # 3. Analisis con Claude (streaming)
                    status_text.info(
                        "Claude esta analizando los datos..."
                    )
                    progress_bar.progress(40)

                    claude = ClaudeAnalyzer(api_key)
                    report_metadata = {
                        "client_name": client_name,
                        "period": period,
                        "report_type": report_type,
                        "total_sheets": processed_data["metadata"]["_global"][
                            "total_sheets"
                        ],
                        "total_records": processed_data["metadata"]["_global"][
                            "total_rows"
                        ],
                    }

                    # Streaming: mostrar respuesta en tiempo real
                    stream_container = st.empty()
                    streamed_text = []

                    def _on_stream_chunk(chunk: str):
                        streamed_text.append(chunk)
                        stream_container.markdown("".join(streamed_text) + " ◌")

                    claude_result = claude.analyze_data(
                        file_content=st.session_state.file_content,
                        filename=st.session_state.filename,
                        quantitative_analysis=quant_report,
                        report_metadata=report_metadata,
                        model=model,
                        max_tokens=config.DEFAULT_MAX_TOKENS,
                        custom_prompt=st.session_state.custom_prompt,
                        stream_callback=_on_stream_chunk,
                    )

                    stream_container.empty()

                    if not claude_result["success"]:
                        st.error(f"Error: {claude_result.get('error')}")
                        st.stop()

                    # 4. Generar graficos desde las tablas del informe
                    status_text.info("Generando visualizaciones del informe...")
                    progress_bar.progress(80)

                    chart_gen = ChartGenerator(processed_data["sheets"])
                    report_sections = generate_charts_for_report(
                        markdown=claude_result["analysis"],
                        chart_gen=chart_gen,
                    )

                    # Recopilar todas las imágenes de gráficos
                    all_chart_images = []
                    for sec in report_sections:
                        all_chart_images.extend(sec.chart_images)

                    progress_bar.progress(90)
                    status_text.success("Analisis completado")

                    # Guardar resultados
                    session_state.store_analysis_results(
                        processed_data=processed_data,
                        quantitative_results={"results": quant_results, "report": quant_report},
                        qualitative_results=claude_result,
                        cost_summary=claude.get_cost_summary(),
                    )
                    session_state.store_chart_images(all_chart_images)
                    st.session_state.report_sections = report_sections

                    progress_bar.progress(100)
                    time.sleep(0.3)
                    progress_bar.empty()
                    status_text.empty()
                    st.rerun()

                except Exception as e:
                    status_text.error(f"Error inesperado: {e}")
                    logger.exception("Error durante el análisis")
                    st.stop()

# ─── Resultados ──────────────────────────────────────────────────────────────

if st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown(
        '<div class="success-box"><h2>Analisis Completado</h2></div>',
        unsafe_allow_html=True,
    )

    # Métricas de coste
    if st.session_state.cost_summary:
        cs = st.session_state.cost_summary
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Coste Total", f"${cs['total_cost_usd']:.4f}")
        with c2:
            st.metric("Tokens Entrada", f"{cs['total_input_tokens']:,}")
        with c3:
            st.metric("Tokens Salida", f"{cs['total_output_tokens']:,}")
        with c4:
            st.metric("Modelo", model.split("-")[1].title())

    st.markdown("---")

    # Tabs de resultados
    tabs = st.tabs(
        [
            "Informe Ejecutivo",
            "Visualizaciones",
            "Descargar DOCX",
            "Descargar PDF",
            "Descargar PPTX",
        ]
    )

    with tabs[0]:
        st.markdown("### Informe Ejecutivo")
        if st.session_state.qualitative_results:
            st.markdown(st.session_state.qualitative_results["analysis"])

    with tabs[1]:
        st.markdown("### Visualizaciones (generadas del informe)")
        chart_imgs = st.session_state.get("chart_images", [])
        if chart_imgs:
            for title, png_bytes in chart_imgs:
                st.markdown(f"**{title}**")
                st.image(png_bytes, width='stretch')
                st.markdown("---")
        else:
            st.info("El informe no contenia tablas con datos graficables.")

    with tabs[2]:
        st.markdown("### Descargar como DOCX")
        st.info("Informe unificado con graficos integrados. Editable en Word.")

        if st.button("Generar DOCX", key="btn_docx"):
            with st.spinner("Generando DOCX..."):
                try:
                    docx_gen = DOCXReportGenerator(
                        client_name=client_name,
                        period=period,
                        report_title="Informe Ejecutivo",
                    )
                    docx_bytes = docx_gen.generate(
                        analysis_text=st.session_state.qualitative_results["analysis"],
                        metadata={
                            "total_records": st.session_state.processed_data[
                                "metadata"
                            ]["_global"]["total_rows"],
                            **st.session_state.cost_summary,
                        },
                        quantitative_analysis=None,
                        report_sections=st.session_state.get("report_sections"),
                    )
                    st.success("DOCX generado")
                    st.download_button(
                        label="Descargar DOCX",
                        data=docx_bytes,
                        file_name=f"informe_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_docx",
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.exception("Error generando DOCX")

    with tabs[3]:
        st.markdown("### Descargar como PDF")
        st.info("Informe con portada Movimer, analisis con graficos integrados.")

        if st.button("Generar PDF", key="btn_pdf"):
            with st.spinner("Generando PDF..."):
                try:
                    pdf_gen = PDFReportGenerator(
                        client_name=client_name,
                        period=period,
                        report_title="Informe Ejecutivo",
                        company_logo_path=company_logo,
                        client_logo_path=client_logo,
                    )
                    pdf_bytes = pdf_gen.generate(
                        quantitative_analysis="",
                        qualitative_analysis=st.session_state.qualitative_results[
                            "analysis"
                        ],
                        metadata=st.session_state.processed_data["metadata"]["_global"],
                        cost_info=st.session_state.cost_summary,
                        report_sections=st.session_state.get("report_sections"),
                    )
                    st.success("PDF generado")
                    st.download_button(
                        label="Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"informe_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        key="download_pdf",
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.exception("Error generando PDF")

    with tabs[4]:
        st.markdown("### Descargar como PPTX")
        st.info("Presentación ejecutiva con portada, secciones y gráficos integrados.")

        if st.button("Generar PPTX", key="btn_pptx"):
            with st.spinner("Generando PPTX..."):
                try:
                    pptx_gen = PPTXReportGenerator(
                        client_name=client_name,
                        period=period,
                        report_title="Informe Ejecutivo",
                    )
                    pptx_bytes = pptx_gen.generate(
                        analysis_text=st.session_state.qualitative_results["analysis"],
                        metadata={
                            "total_records": st.session_state.processed_data[
                                "metadata"
                            ]["_global"]["total_rows"],
                            **st.session_state.cost_summary,
                        },
                        cost_info=st.session_state.cost_summary,
                        report_sections=st.session_state.get("report_sections"),
                    )
                    st.success("PPTX generado")
                    st.download_button(
                        label="Descargar PPTX",
                        data=pptx_bytes,
                        file_name=f"informe_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        key="download_pptx",
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.exception("Error generando PPTX")

    # Reiniciar
    st.markdown("---")
    if st.button("Analizar Otro Archivo"):
        session_state.reset_session_state()
        st.rerun()

# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    """
<div style='text-align: center; padding: 2rem 0;'>
    <p style='color: #575757; font-family: Open Sans, sans-serif; font-size: 0.85rem;'>
        Movimer &middot; Analisis cuantitativo + Estrategia con IA + Visualizaciones
    </p>
</div>
""",
    unsafe_allow_html=True,
)
