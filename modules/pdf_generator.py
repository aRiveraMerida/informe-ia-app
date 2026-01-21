# -*- coding: utf-8 -*-
"""
Módulo de generación de PDFs profesionales.
Incluye portada personalizable, logos, secciones estructuradas.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Genera PDFs profesionales con estructura completa."""
    
    def __init__(
        self,
        client_name: str,
        period: str,
        report_title: str = "Informe Ejecutivo de Análisis de Datos",
        company_logo_path: Optional[str] = None,
        client_logo_path: Optional[str] = None
    ):
        self.client_name = client_name
        self.period = period
        self.report_title = report_title
        self.company_logo_path = company_logo_path
        self.client_logo_path = client_logo_path
        
        # Buffer para el PDF
        self.buffer = BytesIO()
        
        # Estilos
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el documento."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F4E78'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2E5C8A'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Heading personalizado
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1F4E78'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2E5C8A'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body text justificado
        self.styles.add(ParagraphStyle(
            name='JustifiedBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        # Metadata
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_RIGHT
        ))
    
    def generate(
        self,
        quantitative_analysis: str,
        qualitative_analysis: str,
        metadata: Dict[str, Any],
        cost_info: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Genera el PDF completo.
        
        Args:
            quantitative_analysis: Texto del análisis cuantitativo
            qualitative_analysis: Texto del análisis cualitativo de Claude
            metadata: Metadata adicional del informe
            cost_info: Información de costes (opcional)
            
        Returns:
            Bytes del PDF generado
        """
        # Crear documento
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Construir story (contenido)
        story = []
        
        # 1. Portada
        story.extend(self._build_cover_page())
        story.append(PageBreak())
        
        # 2. Metadata y resumen ejecutivo
        story.extend(self._build_metadata_section(metadata))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Análisis cuantitativo
        story.append(Paragraph("ANÁLISIS CUANTITATIVO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        story.extend(self._parse_markdown_to_flowables(quantitative_analysis))
        story.append(PageBreak())
        
        # 4. Análisis cualitativo (Claude)
        story.append(Paragraph("ANÁLISIS ESTRATÉGICO Y RECOMENDACIONES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        story.extend(self._parse_markdown_to_flowables(qualitative_analysis))
        
        # 5. Información de generación (pie)
        if cost_info:
            story.append(PageBreak())
            story.extend(self._build_generation_info(cost_info))
        
        # Construir PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        
        # Retornar bytes
        pdf_bytes = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_bytes
    
    def _build_cover_page(self) -> List:
        """Construye la portada del informe."""
        elements = []
        
        # Logo de la empresa (si existe)
        if self.company_logo_path:
            try:
                logo = Image(self.company_logo_path, width=2*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.5*inch))
            except Exception as e:
                logger.warning(f"No se pudo cargar logo de empresa: {e}")
        
        # Espaciado superior
        elements.append(Spacer(1, 2*inch))
        
        # Título
        elements.append(Paragraph(self.report_title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Cliente
        elements.append(Paragraph(
            f"<b>Cliente:</b> {self.client_name}",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Periodo
        elements.append(Paragraph(
            f"<b>Periodo:</b> {self.period}",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Fecha de generación
        fecha = datetime.now().strftime("%d/%m/%Y")
        elements.append(Paragraph(
            f"Fecha de generación: {fecha}",
            self.styles['Metadata']
        ))
        
        return elements
    
    def _build_metadata_section(self, metadata: Dict[str, Any]) -> List:
        """Construye sección de metadata."""
        elements = []
        
        elements.append(Paragraph("Resumen Ejecutivo", self.styles['CustomHeading2']))
        
        # Tabla de metadata
        data = [
            ['Atributo', 'Valor'],
            ['Cliente', self.client_name],
            ['Periodo analizado', self.period],
            ['Fecha de generación', datetime.now().strftime("%d/%m/%Y %H:%M")],
        ]
        
        # Agregar metadata adicional
        if 'total_sheets' in metadata:
            data.append(['Hojas analizadas', str(metadata['total_sheets'])])
        if 'total_records' in metadata:
            data.append(['Registros totales', f"{metadata['total_records']:,}"])
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_generation_info(self, cost_info: Dict[str, Any]) -> List:
        """Construye sección de información de generación."""
        elements = []
        
        elements.append(Paragraph("Información de Generación", self.styles['CustomHeading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        info_text = f"""
        Este informe ha sido generado automáticamente utilizando IA generativa.
        <br/><br/>
        <b>Modelo utilizado:</b> {cost_info.get('model', 'N/A')}<br/>
        <b>Tokens procesados:</b> {cost_info.get('total_input_tokens', 0):,} (entrada) + {cost_info.get('total_output_tokens', 0):,} (salida)<br/>
        <b>Coste estimado:</b> ${cost_info.get('total_cost_usd', 0):.4f} USD<br/><br/>
        <i>Generado por Warp IA el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}</i>
        """
        
        elements.append(Paragraph(info_text, self.styles['Normal']))
        
        return elements
    
    def _parse_markdown_to_flowables(self, markdown_text: str) -> List:
        """
        Convierte texto markdown a flowables de ReportLab.
        Maneja headings, bullets, tablas markdown básicas.
        """
        elements = []
        lines = markdown_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Headings
            if line.startswith('###'):
                text = line.replace('###', '').strip()
                elements.append(Paragraph(text, self.styles['CustomHeading3']))
            elif line.startswith('##'):
                text = line.replace('##', '').strip()
                elements.append(Paragraph(text, self.styles['CustomHeading2']))
            elif line.startswith('#'):
                text = line.replace('#', '').strip()
                elements.append(Paragraph(text, self.styles['CustomTitle']))
            
            # Bullets
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                text = self._markdown_to_html(text)
                elements.append(Paragraph(f"• {text}", self.styles['BodyText']))
            
            # Tablas markdown (simple)
            elif '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                table_data, rows_consumed = self._parse_markdown_table(lines[i:])
                if table_data:
                    table = self._create_table(table_data)
                    elements.append(table)
                    elements.append(Spacer(1, 0.2*inch))
                i += rows_consumed - 1
            
            # Texto normal
            elif line:
                text = self._markdown_to_html(line)
                elements.append(Paragraph(text, self.styles['JustifiedBody']))
            
            # Espacio
            else:
                elements.append(Spacer(1, 0.1*inch))
            
            i += 1
        
        return elements
    
    def _parse_markdown_table(self, lines: List[str]) -> tuple:
        """Parsea una tabla markdown y retorna los datos."""
        table_data = []
        rows_consumed = 0
        
        # Header
        if len(lines) < 2:
            return None, 0
        
        header = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        table_data.append(header)
        rows_consumed = 2  # Header + separator
        
        # Rows
        for i in range(2, len(lines)):
            if not lines[i].strip() or '|' not in lines[i]:
                break
            row = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
            if row:
                table_data.append(row)
                rows_consumed += 1
        
        return table_data, rows_consumed
    
    def _create_table(self, data: List[List[str]]) -> Table:
        """Crea una tabla formateada."""
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        return table
    
    def _markdown_to_html(self, text: str) -> str:
        """Convierte markdown básico a HTML para ReportLab."""
        # Bold
        import re
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        
        return text
    
    def _add_footer(self, canvas, doc):
        """Agrega pie de página con logo del cliente."""
        canvas.saveState()
        
        # Logo del cliente (si existe)
        if self.client_logo_path:
            try:
                canvas.drawImage(
                    self.client_logo_path,
                    30, 30,
                    width=1*inch,
                    height=0.5*inch,
                    preserveAspectRatio=True
                )
            except Exception as e:
                logger.warning(f"No se pudo cargar logo de cliente: {e}")
        
        # Número de página
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(doc.pagesize[0] - 30, 30, text)
        
        canvas.restoreState()
