# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

Spanish-language Streamlit application that generates executive reports from Excel/CSV data using a dual analysis approach:

1. **Deterministic quantitative analysis** — KPIs, correlations, trends, anomaly detection (no AI)
2. **AI-powered strategic analysis** — Claude API for qualitative insights, recommendations, and narrative generation

Output formats: PDF (branded), DOCX (editable), PPTX (presentation).

## Build & Run Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Quick start (handles venv + deps + API key)
./start.sh

# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_data_processor.py -v

# Docker
docker build -t informe-ia .
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -p 8501:8501 informe-ia

# Docker Compose
docker-compose up -d
```

## Environment Variables

- `ANTHROPIC_API_KEY` — **Required** for Claude API integration. Can also be set via `.streamlit/secrets.toml` or the UI input field. Priority: secrets.toml > env var > UI input.

## Architecture

```
app.py                          # Main Streamlit entry point (UI + orchestration)
modules/
├── config.py                   # Centralized config: models, pricing, report types, theme colors
├── styles.py                   # CSS styles for Streamlit UI (Movimer branding)
├── session_state.py            # Session state management helpers
├── data_processor.py           # DataProcessor: Excel/CSV parsing, type inference, cleaning
├── validators.py               # DataQualityReport: data quality scoring and issue detection
├── quantitative_analyzer.py    # QuantitativeAnalyzer: deterministic KPIs, correlations, trends
├── claude_analyzer.py          # ClaudeAnalyzer: Claude API streaming + cost tracking
├── prompt_manager.py           # Prompt templating with variable substitution
├── chart_generator.py          # ChartGenerator: matplotlib charts (bar, line, pie, etc.)
├── report_chart_extractor.py   # Extract tables from markdown reports, generate charts
├── pdf_generator.py            # PDFReportGenerator: ReportLab PDF with branding
├── docx_generator.py           # DOCXReportGenerator: python-docx Word export
└── pptx_generator.py           # PPTXReportGenerator: python-pptx PowerPoint export
prompts/                        # Specialized prompt templates per report type (7 domains)
tests/                          # pytest test suite (39 tests)
.streamlit/                     # Streamlit config and secrets template
```

### Data Flow

1. **DataProcessor** — Normalizes uploaded file, detects column types (numeric/categorical/temporal), handles multi-sheet Excel
2. **Validators** — Scores data quality, detects missing values, duplicates, empty sheets
3. **QuantitativeAnalyzer** — Calculates KPIs, aggregations, distributions, trends, correlations, anomalies (deterministic, no AI)
4. **PromptManager** — Builds specialized prompt from template + quantitative results + data summary
5. **ClaudeAnalyzer** — Sends prompt to Claude API, streams response, tracks cost
6. **Report Generators** — Renders markdown report to PDF/DOCX/PPTX with charts and branding

### Key Design Patterns

- **Session state**: All analysis state managed via `st.session_state` (no database, stateless by design)
- **In-memory processing**: All file processing happens in memory (no disk persistence for uploaded data)
- **Cost tracking**: Per-API-call cost estimation stored in `ClaudeAnalyzer.cost_history`
- **Streaming**: Claude responses streamed in real-time for UX
- **Template extensibility**: New report types added by creating a `.txt` file in `prompts/` — no code changes needed

## Code Conventions

- **Language**: Spanish UI strings, comments, and documentation. Code identifiers (variables, functions, classes) are in English.
- **Naming**: Modules in `snake_case`, classes in `PascalCase`, constants in `UPPER_SNAKE_CASE`, private members with leading underscore
- **Type hints**: Used throughout (`Dict[str, Any]`, `Optional[str]`, `List[bytes]`)
- **Docstrings**: Google-style
- **Logging**: Python `logging` module, one logger per module (`logger = logging.getLogger(__name__)`)
- **Error handling**: Specific exception types (no bare `except`), with logging
- **Imports order**: stdlib → third-party → local modules
- **UTF-8**: Explicitly handled (see `sys.stdout.reconfigure` in `claude_analyzer.py`)
- **Pandas warnings**: Suppressed globally in data processing modules

## Claude API Integration

Models defined in `modules/config.py`:

| Model | ID | Use Case |
|---|---|---|
| Sonnet 4 | `claude-sonnet-4-20250514` | Default, best balance |
| Opus 4 | `claude-opus-4-20250514` | Highest quality |
| Haiku 4 | `claude-haiku-4-20250514` | Most economical |

Pricing tracked per call with `CostEstimate` dataclass. Data is converted to markdown text before sending to Claude.

## Prompt Templates

Located in `prompts/` directory with variable substitution:

- `{client_name}`, `{period}`, `{report_type}` — User-provided metadata
- `{total_records}`, `{data_summary}`, `{quantitative_analysis}` — Auto-generated from data

Available templates: `ventas_kpis.txt`, `satisfaccion_cliente.txt`, `encuestas.txt`, `operaciones.txt`, `marketing.txt`, `recursos_humanos.txt`, `financiero.txt`. A default generic prompt is used when no template matches.

## Testing

- **Framework**: pytest
- **Test count**: 39 tests across 5 files
- **Pattern**: Class-based test organization (e.g., `TestCSVProcessing`, `TestExcelProcessing`)
- **Data**: Tests generate their own test data via helper functions (`_make_csv`, `_make_xlsx`)
- **No mocking**: Direct integration testing against module interfaces
- **Run**: `python -m pytest tests/ -v`

## Deployment

- **Local**: `streamlit run app.py` (port 8501)
- **Docker**: `Dockerfile` with Python 3.11-slim, health check on `/_stcore/health`
- **Docker Compose**: `docker-compose.yml` with volume mounting, restart policy
- **Heroku**: `Procfile` with dynamic `$PORT`
- **Streamlit Cloud**: Auto-deploys from GitHub; secrets via dashboard

## Streamlit Configuration

Configured in `.streamlit/config.toml`:
- Max upload size: 200MB
- Theme: Custom Movimer green (#70ae00)
- CORS and XSRF protection disabled for deployment compatibility
- Headless mode enabled
