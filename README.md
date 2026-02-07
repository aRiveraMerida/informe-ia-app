# Generador de Informes Ejecutivos con IA

Aplicación Streamlit que transforma datos Excel/CSV en informes ejecutivos profesionales combinando análisis cuantitativo determinista con análisis estratégico de IA (Claude). Exporta a PDF, DOCX y PPTX.

## Requisitos

- Python 3.8+
- API Key de [Anthropic](https://console.anthropic.com)

## Inicio rápido

```bash
./start.sh
```

El script crea el entorno virtual, instala dependencias y lanza la aplicación.

## Instalación manual

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

## Configuración

### API Key

Se puede configurar de tres formas (en orden de prioridad):

1. **Streamlit Secrets** — en `.streamlit/secrets.toml`:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
2. **Variable de entorno**:
   ```bash
   export ANTHROPIC_API_KEY='sk-ant-...'
   ```
3. **Campo en la UI** — panel lateral de la aplicación.

### Modelos disponibles

| Modelo | Input ($/MTok) | Output ($/MTok) | Uso |
|--------|---------------|-----------------|-----|
| Sonnet 4 | 3.00 | 15.00 | Balance calidad/precio (recomendado) |
| Opus 4 | 15.00 | 75.00 | Máxima calidad |
| Haiku 4 | 0.80 | 4.00 | Más económico |

## Estructura del proyecto

```
app.py                          # Aplicación principal Streamlit
modules/
├── config.py                   # Configuración: modelos, precios, tema
├── styles.py                   # CSS de la aplicación
├── session_state.py            # Gestión de estado de sesión
├── prompt_manager.py           # Plantillas de prompts editables
├── data_processor.py           # Lectura y normalización de Excel/CSV
├── quantitative_analyzer.py    # KPIs, correlaciones, tendencias (sin IA)
├── claude_analyzer.py          # Análisis con Claude (streaming) + costes
├── chart_generator.py          # Gráficos matplotlib
├── report_chart_extractor.py   # Extracción de gráficos del informe
├── validators.py               # Validación de calidad de datos
├── pdf_generator.py            # Generación de PDF (ReportLab)
├── docx_generator.py           # Generación de DOCX (python-docx)
└── pptx_generator.py           # Generación de PPTX (python-pptx)
prompts/                        # Plantillas de prompt por tipo de informe
tests/                          # Tests automatizados (pytest)
requirements.txt
start.sh                        # Script de inicio rápido
Dockerfile                      # Despliegue Docker
docker-compose.yml
Procfile                        # Despliegue Heroku
.streamlit/config.toml          # Configuración de Streamlit
LogoMovimer.png                 # Logo corporativo
```

## Despliegue

### Streamlit Cloud (gratuito)

1. Sube el repositorio a GitHub.
2. Ve a [share.streamlit.io](https://share.streamlit.io) y conecta tu cuenta.
3. Crea nueva app seleccionando el repositorio, branch `main`, archivo `app.py`.
4. En **Advanced settings → Secrets**, añade:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Haz clic en **Deploy**.

La app se actualizará automáticamente con cada `git push`.

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t informe-ia .
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -p 8501:8501 informe-ia
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
```

### Heroku

```bash
heroku create mi-informe-ia
heroku config:set ANTHROPIC_API_KEY=sk-ant-...
git push heroku main
```

### Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `Invalid API Key` | Verificar clave en [console.anthropic.com](https://console.anthropic.com) |
| Error al leer archivo | Comprobar que sea .xlsx/.xls/.csv con cabeceras en la primera fila |
| Error al generar PDF | `pip install --upgrade reportlab pillow` |
| Puerto en uso | `streamlit run app.py --server.port 8502` |

## Seguridad

- La API Key nunca se persiste en disco.
- Los archivos se procesan en memoria, sin almacenamiento.
- Conexión cifrada con la API de Anthropic.
- Sin telemetría ni tracking externo.
