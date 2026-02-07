"""
Módulos de análisis y generación de informes con IA.
"""
from .data_processor import DataProcessor
from .quantitative_analyzer import QuantitativeAnalyzer
from .claude_analyzer import ClaudeAnalyzer, CostEstimate
from .pdf_generator import PDFReportGenerator
from .docx_generator import DOCXReportGenerator
from .pptx_generator import PPTXReportGenerator
from .chart_generator import ChartGenerator, ChartConfig
from .report_chart_extractor import ReportSection, generate_charts_for_report
from .validators import validate_quality, DataQualityReport
from . import prompt_manager
from . import config
from . import styles
from . import session_state

__all__ = [
    "DataProcessor",
    "QuantitativeAnalyzer",
    "ClaudeAnalyzer",
    "CostEstimate",
    "PDFReportGenerator",
    "DOCXReportGenerator",
    "PPTXReportGenerator",
    "ChartGenerator",
    "ChartConfig",
    "ReportSection",
    "generate_charts_for_report",
    "validate_quality",
    "DataQualityReport",
    "prompt_manager",
    "config",
    "styles",
    "session_state",
]
