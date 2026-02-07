# -*- coding: utf-8 -*-
"""
Estilos CSS centralizados — Branding Movimer.
Colores: #70ae00 (verde), #8cc000 (verde claro), #000 (texto), #f6f6f6 (fondo).
Tipografía: Open Sans / Oswald.
"""

APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&family=Oswald:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
        letter-spacing: 0.02em;
    }
    h1, h2, h3, h4, h5, h6,
    .main-header, .sub-header,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        font-family: 'Oswald', sans-serif;
        text-transform: uppercase;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #70ae00;
        letter-spacing: 3px;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #575757;
        letter-spacing: 1px;
        margin-bottom: 2rem;
        font-family: 'Open Sans', sans-serif;
        text-transform: none;
    }
    .metric-card {
        background: #70ae00;
        padding: 1.5rem;
        border-radius: 4px;
        color: white;
        text-align: center;
    }
    .cost-box {
        background: #f7f5e7;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #70ae00;
        margin: 1rem 0;
    }
    .success-box {
        background: #eaf5e0;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #70ae00;
    }
    .prompt-info {
        background: #f6f6f6;
        padding: 0.8rem;
        border-radius: 4px;
        border-left: 4px solid #70ae00;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .chart-config-card {
        background: #f6f6f6;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #d4d4d4;
        margin: 0.5rem 0;
    }
    .stButton>button {
        background: #70ae00;
        color: white;
        font-family: 'Open Sans', sans-serif;
        font-weight: 600;
        padding: 0.6rem 1.8rem;
        border-radius: 4px;
        border: 2px solid #70ae00;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.85rem;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: transparent;
        color: #70ae00;
        border: 2px solid #70ae00;
    }
    .section-divider {
        border-top: 1px solid #70ae00;
        margin: 2rem 0;
        opacity: 0.4;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-family: 'Oswald', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: #70ae00 !important;
        color: #70ae00 !important;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f6f6f6;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #000;
        font-family: 'Oswald', sans-serif;
    }
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #70ae00;
    }
    /* Dividers */
    hr {
        border-color: #d4d4d4 !important;
    }
    /* Logo container */
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    .logo-container img {
        max-width: 180px;
    }
</style>
"""
