# GUÍA DE DESPLIEGUE
## Generador de Informes Ejecutivos con IA

---

## Requisitos previos

- **Python 3.8+** (recomendado 3.11)
- **API Key de Anthropic** — obtener en [console.anthropic.com](https://console.anthropic.com)
- **Git** (opcional, para clonar el repositorio)

---

## OPCIÓN 1: Ejecución en local

### Inicio rápido (Mac/Linux)

```bash
chmod +x start.sh
./start.sh
```

El script crea automáticamente el entorno virtual, instala dependencias y lanza la aplicación.

### Instalación manual

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate          # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar API Key (elegir una opción)

# Opción A: Variable de entorno
export ANTHROPIC_API_KEY='sk-ant-...'

# Opción B: Fichero de secrets de Streamlit
mkdir -p .streamlit
echo 'ANTHROPIC_API_KEY = "sk-ant-..."' > .streamlit/secrets.toml

# Opción C: Introducir manualmente en la interfaz web

# 4. Lanzar la aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

### Cambiar puerto

```bash
streamlit run app.py --server.port 8080
```

---

## OPCIÓN 2: Docker

### Construir y ejecutar

```bash
# Construir la imagen
docker build -t informe-ia .

# Ejecutar (pasando la API Key como variable de entorno)
docker run -d \
  -e ANTHROPIC_API_KEY='sk-ant-...' \
  -p 8501:8501 \
  --name informe-ia \
  informe-ia
```

La aplicación estará en `http://localhost:8501`.

### Con Docker Compose

Crear un fichero `.env` en la raíz del proyecto:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Ejecutar:

```bash
docker-compose up -d
```

Para detener:

```bash
docker-compose down
```

### Actualizar la imagen

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## OPCIÓN 3: Streamlit Cloud (gratuito)

### Pasos

1. Subir el código a un repositorio en **GitHub** (público o privado).
2. Ir a [share.streamlit.io](https://share.streamlit.io) y conectar la cuenta de GitHub.
3. Crear nueva app:
   - **Repository:** seleccionar el repo.
   - **Branch:** `main`.
   - **Main file path:** `app.py`.
4. En **Advanced settings → Secrets**, añadir:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Pulsar **Deploy**.

La app se actualizará automáticamente con cada `git push` a `main`.

### Límites del plan Community

- 1 app por cuenta.
- La app "duerme" tras ~7 días sin uso y se reactiva al acceder.
- Recursos limitados (1 GB RAM aprox.).

---

## OPCIÓN 4: Heroku

### Requisitos

- Cuenta en [heroku.com](https://heroku.com).
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) instalado.

### Despliegue

```bash
# Crear app en Heroku
heroku create mi-informe-ia

# Configurar API Key
heroku config:set ANTHROPIC_API_KEY='sk-ant-...'

# Desplegar
git push heroku main

# Abrir en el navegador
heroku open
```

El fichero `Procfile` incluido ya configura el comando de inicio.

### Ver logs

```bash
heroku logs --tail
```

---

## OPCIÓN 5: VPS / Servidor propio (Ubuntu/Debian)

### Instalación

```bash
# 1. Instalar Python y dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# 2. Clonar o copiar el proyecto
git clone <url-del-repo> /opt/informe-ia
cd /opt/informe-ia

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configurar API Key
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> /opt/informe-ia/.env
```

### Ejecutar como servicio (systemd)

Crear `/etc/systemd/system/informe-ia.service`:

```ini
[Unit]
Description=Informe IA — Generador de Informes Ejecutivos
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/informe-ia
EnvironmentFile=/opt/informe-ia/.env
ExecStart=/opt/informe-ia/venv/bin/streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activar y arrancar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable informe-ia
sudo systemctl start informe-ia
```

### Con Nginx como reverse proxy (HTTPS)

```nginx
server {
    listen 80;
    server_name informes.midominio.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # WebSocket (necesario para Streamlit)
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

Para HTTPS, añadir certificado con Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d informes.midominio.com
```

---

## OPCIÓN 6: AWS / GCP / Azure (Docker)

Para cualquier proveedor cloud con soporte Docker:

```bash
# 1. Construir y subir imagen a registry
docker build -t informe-ia .
docker tag informe-ia <registry-url>/informe-ia:latest
docker push <registry-url>/informe-ia:latest

# 2. Desplegar con las variables de entorno
#    - ANTHROPIC_API_KEY=sk-ant-...
#    - Puerto expuesto: 8501
```

### Servicios recomendados por proveedor

| Proveedor | Servicio | Notas |
|---|---|---|
| AWS | ECS Fargate / App Runner | Serverless, sin gestión de servidores |
| GCP | Cloud Run | Escala a cero, pago por uso |
| Azure | Container Apps | Similar a Cloud Run |

---

## Verificación post-despliegue

Tras desplegar, verificar:

1. **La app carga:** Acceder a la URL y comprobar que aparece la interfaz.
2. **API Key funciona:** En el panel lateral debe aparecer "API Key configurada".
3. **Subida de archivo:** Cargar un CSV/Excel pequeño de prueba y verificar la vista previa.
4. **Generación de informe:** Ejecutar un análisis completo y descargar PDF/DOCX/PPTX.

### Health check

```bash
curl -f http://localhost:8501/_stcore/health
# Respuesta esperada: "ok"
```

---

## Solución de problemas

| Problema | Solución |
|---|---|
| `Invalid API Key` | Verificar clave en [console.anthropic.com](https://console.anthropic.com) |
| `ModuleNotFoundError` | Ejecutar `pip install -r requirements.txt` |
| Error al leer archivo | Comprobar que sea .xlsx/.xls/.csv con cabeceras en la primera fila |
| Error al generar PDF | `pip install --upgrade reportlab pillow` |
| Puerto 8501 en uso | `streamlit run app.py --server.port 8502` |
| App no carga tras deploy | Verificar que el puerto 8501 está abierto en el firewall |
| WebSocket error en Nginx | Añadir configuración de `proxy_set_header Upgrade` |

---

## Ejecutar tests (verificación de integridad)

```bash
pip install pytest
python -m pytest tests/ -v
```

Resultado esperado: `39 passed`.

---

*Guía de despliegue — Generador de Informes Ejecutivos con IA — Movimer Group*
