# Despliegue en Streamlit Cloud

## Pasos para desplegar la aplicacion

### 1. Preparar el repositorio en GitHub

```bash
cd /Users/ariveramerida/Desktop/informe-ia-app

# Inicializar git (si no existe)
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Preparar para despliegue en Streamlit Cloud"

# Crear repositorio en GitHub y conectar
# Ve a github.com y crea un nuevo repositorio llamado "informe-ia-app"
# Luego ejecuta:
git remote add origin https://github.com/TU_USUARIO/informe-ia-app.git
git branch -M main
git push -u origin main
```

### 2. Desplegar en Streamlit Cloud

1. Ve a **[share.streamlit.io](https://share.streamlit.io)**
2. Haz click en **"New app"**
3. Conecta tu cuenta de GitHub (si no lo has hecho)
4. Selecciona:
   - **Repository**: `TU_USUARIO/informe-ia-app`
   - **Branch**: `main`
   - **Main file path**: `app_pro.py`

### 3. Configurar la API Key (IMPORTANTE)

1. En la pagina de despliegue, click en **"Advanced settings"**
2. En la seccion **"Secrets"**, pega:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-TU_API_KEY_AQUI"
```

3. Click en **"Deploy!"**

### 4. Obtener tu API Key de Anthropic

1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta o inicia sesion
3. Ve a **API Keys** en el menu lateral
4. Click en **"Create Key"**
5. Copia la key (empieza con `sk-ant-api03-...`)

## Archivos necesarios para el despliegue

La aplicacion necesita estos archivos:

```
informe-ia-app/
├── app_pro.py              # Archivo principal (OBLIGATORIO)
├── requirements.txt        # Dependencias (OBLIGATORIO)
├── modules/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── quantitative_analyzer.py
│   ├── claude_analyzer.py
│   ├── pdf_generator.py
│   └── docx_generator.py
└── .streamlit/
    └── config.toml         # Configuracion del tema
```

## Verificacion post-despliegue

Una vez desplegado:

1. Abre la URL de tu app (ej: `https://tu-usuario-informe-ia-app.streamlit.app`)
2. Verifica que aparece "API Key configurada" en el sidebar
3. Sube un archivo de prueba
4. Genera un informe

## Troubleshooting

### Error: "ModuleNotFoundError"
- Verifica que `requirements.txt` tiene todas las dependencias
- Redespliega la app

### Error: "API Key no configurada"
- Ve a Settings > Secrets en tu app de Streamlit Cloud
- Verifica que la key esta correctamente pegada

### Error: "Internal Server Error"
- Revisa los logs en Streamlit Cloud (Manage app > Logs)
- Verifica que el archivo principal es `app_pro.py`

## Costes

- **Streamlit Cloud**: GRATIS (plan Community)
- **Anthropic API**: Pago por uso (~$0.10-0.30 por informe con Sonnet)

## Actualizaciones

Para actualizar la app desplegada:

```bash
git add .
git commit -m "Actualizar app"
git push
```

Streamlit Cloud detectara los cambios y redesplegara automaticamente.
