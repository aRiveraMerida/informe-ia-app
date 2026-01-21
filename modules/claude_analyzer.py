# -*- coding: utf-8 -*-
"""
Modulo de integracion con Claude API.
Maneja analisis cualitativo y tracking de costes.
"""
import anthropic
import base64
import os
import sys
import pandas as pd
from io import BytesIO
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import warnings

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Configure stdout/stderr for UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

logger = logging.getLogger(__name__)


@dataclass
class CostEstimate:
    """Estimacion de costes de una llamada a la API."""
    input_tokens: int
    output_tokens: int
    model: str
    estimated_cost_usd: float
    
    def __str__(self):
        return f"${self.estimated_cost_usd:.4f} ({self.input_tokens} in + {self.output_tokens} out tokens)"


class ClaudeAnalyzer:
    """Gestiona analisis cualitativo con Claude y tracking de costes."""
    
    PRICING = {
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
        "claude-haiku-4-20250514": {"input": 0.80, "output": 4.00},
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("API key no proporcionada")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.cost_history: List[CostEstimate] = []
        
    def analyze_data(
        self,
        file_content: bytes,
        filename: str,
        quantitative_analysis: str,
        report_metadata: Dict[str, Any],
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 16000
    ) -> Dict[str, Any]:
        """Analiza datos con Claude y retorna analisis cualitativo."""
        try:
            file_text = self._convert_file_to_text(file_content, filename)
            
            prompt = self._build_analysis_prompt(
                quantitative_analysis,
                report_metadata,
                file_text
            )
            
            logger.info("Llamando a Claude %s...", model)
            
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = ""
            for block in message.content:
                if block.type == "text":
                    response_text += block.text
            
            cost_estimate = self._calculate_cost(
                message.usage.input_tokens,
                message.usage.output_tokens,
                model
            )
            
            self.cost_history.append(cost_estimate)
            
            logger.info("Analisis completado. Coste: %s", cost_estimate)
            
            return {
                'success': True,
                'analysis': response_text,
                'cost': cost_estimate,
                'tokens': {
                    'input': message.usage.input_tokens,
                    'output': message.usage.output_tokens
                },
                'model': model
            }
            
        except anthropic.APIError as e:
            error_msg = str(e)
            logger.error("Error de API: %s", repr(error_msg))
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'api_error'
            }
        except Exception as e:
            error_msg = str(e)
            logger.error("Error inesperado: %s", repr(error_msg))
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'unknown'
            }
    
    def _convert_file_to_text(self, file_content: bytes, filename: str) -> str:
        """Convierte archivos Excel/CSV a representacion textual."""
        try:
            buffer = BytesIO(file_content)
            
            if filename.endswith('.csv'):
                df = pd.read_csv(buffer)
                return self._dataframe_to_markdown(df, "Datos")
            
            elif filename.endswith(('.xlsx', '.xls')):
                excel_file = pd.ExcelFile(buffer)
                text_parts = []
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    if not df.empty:
                        text_parts.append(self._dataframe_to_markdown(df, sheet_name))
                
                return "\n\n".join(text_parts)
            
            else:
                return f"[Archivo no soportado: {filename}]"
                
        except Exception as e:
            error_msg = str(e)
            logger.error("Error convirtiendo archivo a texto: %s", repr(error_msg))
            return f"[Error leyendo archivo: {error_msg}]"
    
    def _dataframe_to_markdown(self, df: pd.DataFrame, sheet_name: str) -> str:
        """Convierte un DataFrame a formato markdown tabular COMPLETO."""
        # IMPORTANTE: Incluir TODOS los datos, sin truncar
        # Claude puede manejar contextos grandes (200K tokens)
        max_rows = 2000  # Aumentado significativamente
        
        df_copy = df.copy()
        
        # Clean data: replace NaN and convert all to string safely
        df_copy = df_copy.fillna('')
        
        # Ensure all string columns are properly encoded
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object':
                df_copy[col] = df_copy[col].astype(str)
        
        text = f"## HOJA: {sheet_name}\n"
        text += f"**Total filas: {len(df)} | Total columnas: {len(df.columns)}**\n\n"
        text += f"**Columnas:** {', '.join(df.columns.tolist())}\n\n"
        
        # Incluir estadisticas resumidas por columna
        text += "### RESUMEN ESTADISTICO POR COLUMNA:\n"
        for col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                if df[col].dtype in ['int64', 'float64']:
                    text += f"- **{col}**: Min={col_data.min()}, Max={col_data.max()}, Media={col_data.mean():.2f}\n"
                else:
                    value_counts = col_data.value_counts()
                    if len(value_counts) <= 20:  # Si hay pocas categorias, mostrar todas
                        text += f"- **{col}**: {dict(value_counts)}\n"
                    else:
                        top_5 = value_counts.head(5).to_dict()
                        text += f"- **{col}**: Top 5: {top_5} (+ {len(value_counts)-5} mas)\n"
        
        text += "\n### DATOS COMPLETOS:\n"
        
        if len(df) > max_rows:
            df_display = df_copy.head(max_rows)
            text += f"**(Mostrando primeras {max_rows} de {len(df)} filas)**\n\n"
        else:
            df_display = df_copy
        
        try:
            text += df_display.to_markdown(index=False)
        except Exception:
            text += df_display.to_string(index=False)
        
        return text
    
    def _build_analysis_prompt(
        self,
        quantitative_analysis: str,
        metadata: Dict[str, Any],
        file_text: str = ""
    ) -> str:
        """Construye prompt estructurado para analisis cualitativo."""
        
        client_name = metadata.get('client_name', 'Cliente')
        period = metadata.get('period', 'Periodo no especificado')
        report_type = metadata.get('report_type', 'general')
        total_records = metadata.get('total_records', 0)
        
        prompt = f"""Eres un consultor senior de datos especializado en generar INFORMES EJECUTIVOS para concesionarios de automoviles y empresas de servicios.

# CONTEXTO DEL ANALISIS
- **Cliente:** {client_name}
- **Periodo:** {period}
- **Tipo de informe:** {report_type}
- **Total registros analizados:** {total_records}

---

# DATOS COMPLETOS DEL ARCHIVO (ANALIZA TODOS)

{file_text}

---

# ANALISIS CUANTITATIVO PREVIO (YA CALCULADO)

{quantitative_analysis}

---

# TU TAREA: GENERAR INFORME EJECUTIVO PROFESIONAL

DEBES generar un informe en formato Markdown con la siguiente estructura EXACTA.
**IMPORTANTE:** Todos los numeros, porcentajes y datos DEBEN provenir de los datos proporcionados arriba. NO inventes datos.

---

# INFORME EJECUTIVO
## Analisis de [descripcion segun tipo de datos]

**Cliente:** {client_name}
**Periodo:** {period}
**Registros analizados:** {total_records}
**Fecha del informe:** [fecha actual]

---

## 1. RESUMEN EJECUTIVO

[Parrafo de 3-4 lineas resumiendo los hallazgos principales con datos concretos]

### Indicadores Clave de Rendimiento

| KPI | Valor | Estado |
|-----|-------|--------|
| Tasa de contactabilidad efectiva | XX% (N de M) | [Bueno/Regular/Critico] |
| Tasa de conversion (compra) | XX% (N de M contactados) | [Bueno/Regular/Critico] |
| Satisfaccion con el trato | XX% SI | [Bueno/Regular/Critico] |
| Intencion de compra futura | XX% | [Bueno/Regular/Critico] |
| Interes en volver al concesionario | XX% | [Bueno/Regular/Critico] |

---

## 2. ANALISIS DE CONTACTABILIDAD

### Resultado de las llamadas

| Resultado | Cantidad | Porcentaje |
|-----------|----------|------------|
| ENCUESTA REALIZADA | N | XX% |
| NO CONTESTA NUNCA | N | XX% |
| EL CLIENTE NO COLABORA | N | XX% |
| SI CONTESTA, NO SE LOCALIZA AL TITULAR | N | XX% |
| [otros resultados] | N | XX% |

**Hallazgos:**
- [Insight especifico con dato]
- [Patron detectado]

---

## 3. ANALISIS DE SATISFACCION Y EXPERIENCIA

### Pregunta 1: Trato recibido por el personal

| Respuesta | Cantidad | Porcentaje |
|-----------|----------|------------|
| SI | N | XX% |
| NO | N | XX% |

### Clientes que YA compraron vehiculo

| Ha comprado? | Cantidad | Porcentaje |
|--------------|----------|------------|
| SI | N | XX% |
| NO | N | XX% |

**De los que SI compraron:**

| Donde compro | Cantidad | Porcentaje |
|--------------|----------|------------|
| ARAGON CAR / CUPRA ARAGON CAR | N | XX% |
| Otro concesionario | N | XX% |
| Otra marca | N | XX% |

**Modelos mas vendidos en ARAGON CAR:**
| Modelo | Cantidad |
|--------|----------|
| [modelo] | N |

---

## 4. ANALISIS COMPETITIVO

### Marcas de interes mencionadas

| Marca | Menciones | Porcentaje |
|-------|-----------|------------|
| CUPRA | N | XX% |
| SEAT | N | XX% |
| [otras marcas] | N | XX% |

### Motivos de fuga (clientes que compraron en otro lado)

| Motivo | Cantidad |
|--------|----------|
| [motivo 1] | N |
| [motivo 2] | N |

---

## 5. INTENCION DE COMPRA FUTURA

### Sigue pensando en cambiarse de coche?

| Respuesta | Cantidad | Porcentaje |
|-----------|----------|------------|
| SI | N | XX% |
| NO | N | XX% |

### Plazo de compra estimado

| Plazo | Cantidad | Porcentaje |
|-------|----------|------------|
| MENOS DE 3 MESES | N | XX% |
| MENOS DE 6 MESES | N | XX% |
| MENOS DE 1 ANO | N | XX% |
| NO SABE / OTROS | N | XX% |

### Interes en volver al concesionario

| Respuesta | Cantidad | Porcentaje |
|-----------|----------|------------|
| SI | N | XX% |
| NO | N | XX% |

---

## 6. BRECHAS CRITICAS IDENTIFICADAS

[Si hay contradicciones en los datos, analizar aqui. Ejemplo: Alta satisfaccion pero baja conversion]

**Brecha detectada:** [descripcion]
- Dato 1: [valor]
- Dato 2: [valor contradictorio]
- **Impacto potencial:** [analisis]
- **Hipotesis:** [explicacion posible]

---

## 7. CONCLUSIONES Y RECOMENDACIONES

### Fortalezas identificadas
1. [Fortaleza] - Dato: [numero concreto]
2. [Fortaleza] - Dato: [numero concreto]
3. [Fortaleza] - Dato: [numero concreto]

### Areas criticas de mejora
1. **[Problema]:** [descripcion] - Impacto: [estimacion]
2. **[Problema]:** [descripcion] - Impacto: [estimacion]

### Plan de accion recomendado

**Inmediato (0-30 dias):**
- [Accion especifica con objetivo medible]
- [Accion especifica]

**Corto plazo (1-3 meses):**
- [Iniciativa tactica]
- [Iniciativa tactica]

**Medio plazo (3-6 meses):**
- [Transformacion estrategica]

---

## REGLAS QUE DEBES SEGUIR:

1. **USA SOLO DATOS REALES** - Cada numero debe venir de los datos proporcionados
2. **CALCULA PORCENTAJES** - Siempre muestra cantidad absoluta Y porcentaje
3. **SE ESPECIFICO** - Usa nombres reales de modelos, concesionarios, vendedores
4. **IDENTIFICA PATRONES** - Busca tendencias en los comentarios de clientes
5. **DETECTA BRECHAS** - Si hay contradicciones, analiza por que
6. **RECOMENDACIONES ACCIONABLES** - No generes recomendaciones genericas

**GENERA EL INFORME AHORA.**"""

        return prompt
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> CostEstimate:
        """Calcula el coste de una llamada a la API."""
        pricing = self.PRICING.get(model, self.PRICING["claude-sonnet-4-20250514"])
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return CostEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            estimated_cost_usd=total_cost
        )
    
    def get_total_cost(self) -> float:
        """Retorna el coste total acumulado en la sesion."""
        return sum(cost.estimated_cost_usd for cost in self.cost_history)
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Retorna resumen de costes de la sesion."""
        if not self.cost_history:
            return {
                'total_calls': 0,
                'total_cost_usd': 0.0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'models_used': []
            }
        
        return {
            'total_calls': len(self.cost_history),
            'total_cost_usd': self.get_total_cost(),
            'total_input_tokens': sum(c.input_tokens for c in self.cost_history),
            'total_output_tokens': sum(c.output_tokens for c in self.cost_history),
            'models_used': list(set(c.model for c in self.cost_history)),
            'cost_breakdown': [
                {
                    'model': c.model,
                    'input_tokens': c.input_tokens,
                    'output_tokens': c.output_tokens,
                    'cost_usd': c.estimated_cost_usd
                }
                for c in self.cost_history
            ]
        }
    
    def estimate_cost_before_call(
        self,
        file_size_bytes: int,
        model: str = "claude-sonnet-4-20250514",
        estimated_output_tokens: int = 8000
    ) -> float:
        """Estima el coste antes de hacer una llamada."""
        estimated_input_tokens = int(file_size_bytes / 3)
        
        pricing = self.PRICING.get(model, self.PRICING["claude-sonnet-4-20250514"])
        
        input_cost = (estimated_input_tokens / 1_000_000) * pricing["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
