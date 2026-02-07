# -*- coding: utf-8 -*-
"""
Generador de PDFs profesionales — Estilo Movimer.
Portada con logo, tablas limpias, footer corporativo, sin anexo cuantitativo.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any, List
import pathlib
import re
import logging

logger = logging.getLogger(__name__)

# Colores Movimer
_GREEN = colors.HexColor('#70ae00')
_GREEN_DARK = colors.HexColor('#3d6b00')
_GRAY_TEXT = colors.HexColor('#575757')
_GRAY_LIGHT = colors.HexColor('#f6f6f6')
_GRAY_LINE = colors.HexColor('#d4d4d4')
_BLACK = colors.HexColor('#000000')
_WHITE = colors.white

# Ruta al logo (relativa al paquete modules/)
_LOGO_PATH = pathlib.Path(__file__).parent.parent / "LogoMovimer.png"


class PDFReportGenerator:
    """Genera PDFs profesionales estilo Movimer."""

    def __init__(
        self,
        client_name: str,
        period: str,
        report_title: str = "Informe Ejecutivo",
        company_logo_path: Optional[str] = None,
        client_logo_path: Optional[str] = None,
    ):
        self.client_name = client_name
        self.period = period
        self.report_title = report_title
        self.company_logo_path = company_logo_path
        self.client_logo_path = client_logo_path
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    # ─── Estilos ──────────────────────────────────────────────────────────────

    def _setup_custom_styles(self):
        """Estilos personalizados Movimer."""
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=_BLACK,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        ))
        self.styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=_GRAY_TEXT,
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica',
        ))
        self.styles.add(ParagraphStyle(
            name='CoverMeta',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=_GRAY_TEXT,
            alignment=TA_CENTER,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=_GREEN,
            spaceAfter=10,
            spaceBefore=16,
            fontName='Helvetica-Bold',
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=_GREEN_DARK,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
        ))
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=_GREEN_DARK,
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold',
        ))
        self.styles.add(ParagraphStyle(
            name='Body',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14,
        ))
        bullet = self.styles['Bullet']
        bullet.parent = self.styles['BodyText']
        bullet.fontSize = 10
        bullet.leftIndent = 18
        bullet.spaceAfter = 4
        bullet.leading = 13
        self.styles.add(ParagraphStyle(
            name='SmallGray',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=_GRAY_TEXT,
            alignment=TA_CENTER,
            spaceAfter=4,
        ))

    # ─── Generación principal ─────────────────────────────────────────────────

    def generate(
        self,
        quantitative_analysis: str,
        qualitative_analysis: str,
        metadata: Dict[str, Any],
        cost_info: Optional[Dict[str, Any]] = None,
        chart_images: Optional[List[tuple]] = None,
        report_sections: Optional[List] = None,
    ) -> bytes:
        """
        Genera PDF unificado profesional.

        Estructura:
          1. Portada con logo Movimer
          2. Informe ejecutivo (secciones con gráficos inline)
          3. Nota de generación compacta
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60,
        )

        story = []

        # 1. Portada
        story.extend(self._build_cover_page())
        story.append(PageBreak())

        # 2. Informe ejecutivo con gráficos inline
        if report_sections:
            story.extend(self._build_sections_with_charts(report_sections))
        else:
            story.extend(self._parse_markdown_to_flowables(qualitative_analysis))
            if chart_images:
                story.append(PageBreak())
                story.extend(self._build_charts_section(chart_images))

        # 3. Nota de generación compacta (sin PageBreak)
        if cost_info:
            story.extend(self._build_generation_note(cost_info))

        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

        pdf_bytes = self.buffer.getvalue()
        self.buffer.close()
        return pdf_bytes

    # ─── Portada ──────────────────────────────────────────────────────────────

    def _build_cover_page(self) -> List:
        elements = []

        # Logo Movimer centrado
        if _LOGO_PATH.exists():
            try:
                logo = Image(str(_LOGO_PATH), width=2.5 * inch, height=1.2 * inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
            except Exception as e:
                logger.warning("No se pudo cargar logo Movimer: %s", e)

        elements.append(Spacer(1, 1.5 * inch))

        # Título
        elements.append(Paragraph(self.report_title.upper(), self.styles['CoverTitle']))
        elements.append(Spacer(1, 0.3 * inch))

        # Línea verde
        elements.append(HRFlowable(
            width="40%", thickness=2, color=_GREEN,
            spaceAfter=20, spaceBefore=10, hAlign='CENTER',
        ))

        # Cliente
        elements.append(Paragraph(self.client_name, self.styles['CoverSubtitle']))
        elements.append(Spacer(1, 0.3 * inch))

        # Periodo y fecha
        elements.append(Paragraph(f"Periodo: {self.period}", self.styles['CoverMeta']))
        fecha = datetime.now().strftime("%d/%m/%Y")
        elements.append(Paragraph(f"Fecha: {fecha}", self.styles['CoverMeta']))

        elements.append(Spacer(1, 1.5 * inch))

        # Logo del cliente (si existe)
        if self.client_logo_path:
            try:
                cl_logo = Image(self.client_logo_path, width=1.5 * inch, height=0.75 * inch)
                cl_logo.hAlign = 'CENTER'
                elements.append(cl_logo)
            except Exception as e:
                logger.warning("No se pudo cargar logo de cliente: %s", e)

        # Logo empresa subido por usuario (si existe)
        if self.company_logo_path:
            try:
                co_logo = Image(self.company_logo_path, width=1.5 * inch, height=0.75 * inch)
                co_logo.hAlign = 'CENTER'
                elements.append(co_logo)
            except Exception as e:
                logger.warning("No se pudo cargar logo de empresa: %s", e)

        return elements

    # ─── Secciones con gráficos ───────────────────────────────────────────────

    def _build_sections_with_charts(self, report_sections: List) -> List:
        elements = []
        for section in report_sections:
            if section.heading:
                elements.append(Paragraph(section.heading, self.styles['SectionHeading']))
                elements.append(Spacer(1, 0.05 * inch))
            if section.text:
                elements.extend(self._parse_markdown_to_flowables(section.text))
            if section.chart_images:
                elements.append(Spacer(1, 0.1 * inch))
                for chart_title, png_bytes in section.chart_images:
                    try:
                        img_buffer = BytesIO(png_bytes)
                        img = Image(img_buffer, width=5.8 * inch, height=3.5 * inch)
                        img.hAlign = 'CENTER'
                        elements.append(img)
                        elements.append(Paragraph(
                            f"<i>{chart_title}</i>", self.styles['SmallGray'],
                        ))
                    except Exception as e:
                        logger.warning("No se pudo insertar gráfico '%s': %s", chart_title, e)
                elements.append(Spacer(1, 0.1 * inch))
        return elements

    # ─── Nota de generación compacta ──────────────────────────────────────────

    def _build_generation_note(self, cost_info: Dict[str, Any]) -> List:
        elements = []
        elements.append(Spacer(1, 0.4 * inch))
        elements.append(HRFlowable(
            width="100%", thickness=0.5, color=_GRAY_LINE,
            spaceAfter=8, spaceBefore=8,
        ))
        model = cost_info.get('model', 'N/A')
        tokens_in = cost_info.get('total_input_tokens', 0)
        tokens_out = cost_info.get('total_output_tokens', 0)
        cost = cost_info.get('total_cost_usd', 0)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        note = (
            f"Informe generado con IA  |  Modelo: {model}  |  "
            f"Tokens: {tokens_in:,}+{tokens_out:,}  |  "
            f"Coste: ${cost:.4f}  |  {fecha}"
        )
        elements.append(Paragraph(note, self.styles['SmallGray']))
        return elements

    # ─── Parser markdown → flowables ──────────────────────────────────────────

    def _parse_markdown_to_flowables(self, markdown_text: str) -> List:
        elements = []
        lines = markdown_text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Ignorar separadores markdown
            if line in ('---', '___', '***', '----', '-----'):
                i += 1
                continue

            # Headings
            if line.startswith('### '):
                text = line[4:].strip()
                elements.append(Paragraph(text, self.styles['SubHeading']))
            elif line.startswith('## '):
                text = line[3:].strip()
                elements.append(Paragraph(text, self.styles['SectionHeading']))
            elif line.startswith('# '):
                text = line[2:].strip()
                elements.append(Paragraph(text, self.styles['SectionTitle']))

            # Bullets
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                text = self._md_to_html(text)
                elements.append(Paragraph(f"• {text}", self.styles['Bullet']))

            # Tablas markdown
            elif '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                table_data, rows_consumed = self._parse_markdown_table(lines[i:])
                if table_data:
                    table = self._create_table(table_data)
                    elements.append(table)
                    elements.append(Spacer(1, 0.15 * inch))
                i += rows_consumed - 1

            # Texto normal
            elif line:
                text = self._md_to_html(line)
                elements.append(Paragraph(text, self.styles['Body']))

            # Espacio
            else:
                elements.append(Spacer(1, 0.06 * inch))

            i += 1
        return elements

    # ─── Tablas estilo Movimer ────────────────────────────────────────────────

    def _parse_markdown_table(self, lines: List[str]) -> tuple:
        table_data = []
        rows_consumed = 0

        if len(lines) < 2:
            return None, 0

        header = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        table_data.append(header)
        rows_consumed = 2  # header + separator

        for idx in range(2, len(lines)):
            if not lines[idx].strip() or '|' not in lines[idx]:
                break
            row = [cell.strip() for cell in lines[idx].split('|') if cell.strip()]
            if row:
                table_data.append(row)
                rows_consumed += 1

        return table_data, rows_consumed

    def _create_table(self, data: List[List[str]]) -> Table:
        """Tabla limpia estilo Movimer: header verde, líneas finas, sin grid pesado."""
        if not data:
            return Table([[""]])

        # Calcular ancho disponible
        page_width = A4[0] - 120  # 60pt margen cada lado
        n_cols = max(len(row) for row in data)
        col_width = page_width / n_cols

        # Envolver texto largo en Paragraph
        styled_data = []
        for i, row in enumerate(data):
            styled_row = []
            for cell in row:
                if i == 0:
                    # Header: verde, negrita
                    styled_row.append(Paragraph(
                        f"<b>{cell}</b>",
                        ParagraphStyle('_th', parent=self.styles['Normal'],
                                       fontSize=9, textColor=_GREEN_DARK,
                                       alignment=TA_CENTER),
                    ))
                else:
                    styled_row.append(Paragraph(
                        cell,
                        ParagraphStyle('_td', parent=self.styles['Normal'],
                                       fontSize=9, alignment=TA_CENTER),
                    ))
            # Pad row if needed
            while len(styled_row) < n_cols:
                styled_row.append("")
            styled_data.append(styled_row)

        table = Table(styled_data, colWidths=[col_width] * n_cols)

        style_cmds = [
            # Header: línea inferior verde
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, _GREEN),
            # Todas las filas: línea inferior gris fina
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, _GRAY_LINE),
            # Alineación y padding
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]

        # Filas alternas: fondo gris muy claro
        for row_idx in range(1, len(styled_data)):
            if row_idx % 2 == 0:
                style_cmds.append(
                    ('BACKGROUND', (0, row_idx), (-1, row_idx), _GRAY_LIGHT)
                )

        table.setStyle(TableStyle(style_cmds))
        return table

    # ─── Footer profesional ───────────────────────────────────────────────────

    def _add_footer(self, canvas, doc):
        canvas.saveState()
        page_w = doc.pagesize[0]

        # Línea verde
        y_line = 42
        canvas.setStrokeColor(_GREEN)
        canvas.setLineWidth(0.8)
        canvas.line(40, y_line, page_w - 40, y_line)

        # "movimer" a la izquierda
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(_GRAY_TEXT)
        canvas.drawString(42, 30, "movimer.com")

        # Página a la derecha
        page_num = canvas.getPageNumber()
        canvas.drawRightString(page_w - 42, 30, f"Página {page_num}")

        canvas.restoreState()

    # ─── Sección de gráficos legacy ───────────────────────────────────────────

    def _build_charts_section(self, chart_images: List[tuple]) -> List:
        elements = []
        for title, png_bytes in chart_images:
            elements.append(Paragraph(title, self.styles['SubHeading']))
            elements.append(Spacer(1, 0.1 * inch))
            try:
                img_buffer = BytesIO(png_bytes)
                img = Image(img_buffer, width=6 * inch, height=3.6 * inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 0.3 * inch))
            except Exception as e:
                logger.warning("No se pudo insertar gráfico '%s': %s", title, e)
        return elements

    # ─── Utilidades ───────────────────────────────────────────────────────────

    @staticmethod
    def _md_to_html(text: str) -> str:
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        return text
