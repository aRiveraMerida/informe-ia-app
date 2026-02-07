# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Spanish-language Streamlit application that generates executive reports from Excel/CSV data using a dual analysis approach:
1. **Deterministic quantitative analysis** (KPIs, correlations, trends)
2. **AI-powered strategic analysis** using Claude API (insights, recommendations)

Output formats: PDF, DOCX and PPTX with customizable branding.

## Build & Run Commands

```bash
# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Quick start script (handles venv setup + dependencies + API key config)
./start.sh
```

## Environment Variables

- `ANTHROPIC_API_KEY` - Required for Claude API integration. Can also be set via Streamlit secrets or UI input.

## Architecture

```
app.py                        # Main Streamlit entry point
modules/
├── config.py                 # Centralized config: models, pricing, chart types, theme
├── styles.py                 # CSS styles extracted from app
├── session_state.py          # Session state management helpers
├── prompt_manager.py         # Editable prompt templates with variable substitution
├── chart_generator.py        # ChartGenerator: matplotlib charts (bar, line, pie, scatter, etc.)
├── data_processor.py         # DataProcessor: Excel/CSV parsing, type inference, cleaning
├── quantitative_analyzer.py  # QuantitativeAnalyzer: Generic deterministic KPIs, correlations
├── claude_analyzer.py        # ClaudeAnalyzer: Claude API + streaming + cost tracking
├── validators.py             # DataQualityReport: data quality scoring and issue detection
├── pdf_generator.py          # PDFReportGenerator: ReportLab PDF with chart images
├── docx_generator.py         # DOCXReportGenerator: python-docx Word with chart images
└── pptx_generator.py         # PPTXReportGenerator: python-pptx PowerPoint with charts
prompts/                      # Specialized prompt templates per report type
tests/                        # Automated tests (pytest, 39 tests)
```

### Data Flow
1. `DataProcessor` → normalizes uploaded file, detects types, handles multi-sheet Excel
2. `QuantitativeAnalyzer` → calculates KPIs without AI (deterministic)
3. `ClaudeAnalyzer` → sends data + quant analysis to Claude for strategic insights
4. `PDFReportGenerator` / `DOCXReportGenerator` / `PPTXReportGenerator` → renders final report with markdown parsing

### Key Design Patterns
- Session state management via `st.session_state` for analysis results and file content
- Cost tracking per API call stored in `ClaudeAnalyzer.cost_history`
- All file processing happens in-memory (no disk persistence for security)
- Streamlit config in `.streamlit/config.toml` sets theme and server options

## Claude API Integration

Models available (defined in `claude_analyzer.py`):
- `claude-sonnet-4-20250514` - Default, best balance
- `claude-opus-4-20250514` - Highest quality
- `claude-haiku-4-20250514` - Most economical

Pricing tracked per-call with `CostEstimate` dataclass. The analyzer converts Excel/CSV to markdown text before sending to Claude.

## Code Conventions

- Spanish UI strings and comments throughout
- UTF-8 encoding explicitly handled (see `sys.stdout.reconfigure` in claude_analyzer.py)
- Pandas warnings suppressed globally in data processing modules
- Logging via Python's `logging` module (INFO level default)

## Streamlit Deployment

For Streamlit Cloud:
- API key via `Settings > Secrets` as `ANTHROPIC_API_KEY`
- Max upload size: 200MB (configured in `.streamlit/config.toml`)
- CORS and XSRF protection disabled for compatibility
