# 🚀 Guía de Despliegue

## Opciones de Deployment

### 1. 🏠 Desarrollo Local

```bash
# Clonar/descargar archivos
cd generador-informes-ia

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar app básica
streamlit run app.py

# O ejecutar app avanzada
streamlit run app_advanced.py
```

La app se abrirá en `http://localhost:8501`

---

### 2. ☁️ Streamlit Cloud (GRATIS)

**Ventajas:**
- Hosting gratuito
- Deploy automático desde GitHub
- HTTPS incluido
- Sin gestión de servidor

**Pasos:**

1. **Crear repositorio en GitHub**
   - Sube los archivos: `app.py`, `requirements.txt`, `README.md`, `.streamlit/config.toml`
   - Asegúrate de que sean públicos

2. **Ir a Streamlit Cloud**
   - Visita [share.streamlit.io](https://share.streamlit.io)
   - Inicia sesión con GitHub

3. **Crear nueva app**
   - Selecciona tu repositorio
   - Branch: `main` (o el que uses)
   - Main file: `app.py`
   - Click "Deploy"

4. **Configurar secrets (opcional)**
   - En el dashboard, ve a "Settings" → "Secrets"
   - Añade tu API key si quieres pre-configurarla
   ```toml
   ANTHROPIC_API_KEY = "tu-api-key-aqui"
   ```

5. **Compartir**
   - Tu app estará en: `https://tu-usuario-tu-repo.streamlit.app`

---

### 3. 🐳 Docker (Producción)

**Crear Dockerfile:**

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

**Construir y ejecutar:**

```bash
# Construir imagen
docker build -t informe-ia .

# Ejecutar contenedor
docker run -p 8501:8501 informe-ia
```

**Docker Compose:**

```yaml
version: '3.8'
services:
  streamlit-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
```

---

### 4. ⚡ Vercel (Serverless)

**Crear `vercel.json`:**

```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

**Deploy:**

```bash
npm i -g vercel
vercel --prod
```

---

### 5. 🌊 Heroku

**Crear `Procfile`:**

```
web: sh setup.sh && streamlit run app.py
```

**Crear `setup.sh`:**

```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**Deploy:**

```bash
heroku create tu-app-nombre
git push heroku main
```

---

### 6. 🔥 AWS / GCP / Azure

#### AWS EC2

```bash
# SSH a instancia
ssh -i key.pem ubuntu@ip-address

# Instalar Python y dependencias
sudo apt update
sudo apt install python3-pip

# Clonar repo
git clone tu-repo.git
cd tu-repo

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar con nohup
nohup streamlit run app.py --server.port 8501 &
```

#### Con PM2 (recomendado para producción)

```bash
# Instalar PM2
npm install -g pm2

# Crear ecosystem.config.js
module.exports = {
  apps: [{
    name: 'informe-ia',
    script: 'streamlit',
    args: 'run app.py --server.port 8501',
    interpreter: 'python3'
  }]
}

# Iniciar
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 🔐 Gestión de API Keys en Producción

### Opción 1: Variables de Entorno

```python
import os
api_key = os.getenv('ANTHROPIC_API_KEY', '')
```

### Opción 2: Streamlit Secrets

En `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

En el código:

```python
import streamlit as st
api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
```

### Opción 3: Vault/Secrets Manager

Para empresas, usa AWS Secrets Manager, Google Secret Manager, o HashiCorp Vault.

---

## 📊 Monitoreo y Logs

### Streamlit Cloud
- Logs automáticos en el dashboard
- Métricas de uso incluidas

### Producción Custom
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("App iniciada")
```

---

## 🔒 Seguridad en Producción

1. **HTTPS**: Siempre usa SSL/TLS
2. **Rate Limiting**: Limita requests por usuario
3. **Autenticación**: Añade login si es necesario
4. **Sanitización**: Valida inputs de usuario
5. **API Keys**: Nunca las expongas en código

```python
# Ejemplo de rate limiting
import streamlit as st
from datetime import datetime, timedelta

if 'last_request' not in st.session_state:
    st.session_state.last_request = datetime.now() - timedelta(minutes=1)

if datetime.now() - st.session_state.last_request < timedelta(seconds=10):
    st.error("Por favor espera 10 segundos entre requests")
else:
    st.session_state.last_request = datetime.now()
    # Procesar request
```

---

## 🎯 Optimización de Performance

1. **Caché de Streamlit**
```python
@st.cache_data
def load_data(file):
    return pd.read_excel(file)
```

2. **Compresión de assets**
3. **CDN para archivos estáticos**
4. **Lazy loading de componentes**

---

## ✅ Checklist de Deployment

- [ ] Código en repositorio Git
- [ ] `requirements.txt` actualizado
- [ ] Variables de entorno configuradas
- [ ] API keys seguras (no en código)
- [ ] HTTPS configurado
- [ ] Logs implementados
- [ ] Monitoreo activo
- [ ] Backup de datos (si aplica)
- [ ] Documentación actualizada
- [ ] Pruebas en staging
- [ ] Plan de rollback definido

---

## 🆘 Troubleshooting Común

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### "Port already in use"
```bash
# Cambiar puerto
streamlit run app.py --server.port 8502
```

### "API Key invalid"
- Verifica en https://console.anthropic.com
- Revisa variables de entorno
- Confirma formato: `sk-ant-...`

### App lenta
- Usa `@st.cache_data` para datos
- Optimiza queries a API
- Reduce tamaño de uploads

---

**¿Necesitas ayuda?** Consulta la [documentación de Streamlit](https://docs.streamlit.io) o contacta soporte.
