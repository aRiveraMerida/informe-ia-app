# -*- coding: utf-8 -*-
"""
Módulo de integración con Claude API.
Maneja análisis cualitativo y tracking de costes.
Genérico para cualquier tipo de dataset.
"""
import anthropic
import os
import sys
import pandas as pd
from io import BytesIO
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import warnings

from .config import MODEL_PRICING, MAX_ROWS_MARKDOWN
from .prompt_manager import get_prompt, render_prompt, DEFAULT_PROMPT

warnings.filterwarnings("ignore", category=UserWarning)

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

logger = logging.getLogger(__name__)


@dataclass
class CostEstimate:
    """Estimación de costes de una llamada a la API."""
    input_tokens: int
    output_tokens: int
    model: str
    estimated_cost_usd: float

    def __str__(self) -> str:
        return f"${self.estimated_cost_usd:.4f} ({self.input_tokens} in + {self.output_tokens} out tokens)"


class ClaudeAnalyzer:
    """Gestiona análisis cualitativo con Claude y tracking de costes."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
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
        max_tokens: int = 16000,
        custom_prompt: Optional[str] = None,
        stream_callback=None,
    ) -> Dict[str, Any]:
        """Analiza datos con Claude y retorna análisis cualitativo.

        Args:
            custom_prompt: Prompt personalizado del usuario. Si es None o vacío,
                           se usa el prompt por defecto genérico.
        """
        try:
            file_text = self._convert_file_to_text(file_content, filename)

            report_type = report_metadata.get("report_type", "Análisis General")
            prompt_template = get_prompt(custom_prompt, report_type=report_type)
            prompt = render_prompt(
                template=prompt_template,
                client_name=report_metadata.get("client_name", "Cliente"),
                period=report_metadata.get("period", "Periodo no especificado"),
                report_type=report_type,
                total_records=report_metadata.get("total_records", 0),
                data_summary=file_text,
                quantitative_analysis=quantitative_analysis,
            )

            logger.info("Llamando a Claude %s...", model)

            if stream_callback is not None:
                return self._analyze_streaming(
                    prompt, model, max_tokens, stream_callback
                )

            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = ""
            for block in message.content:
                if block.type == "text":
                    response_text += block.text

            cost_estimate = self._calculate_cost(
                message.usage.input_tokens, message.usage.output_tokens, model
            )
            self.cost_history.append(cost_estimate)

            logger.info("Análisis completado. Coste: %s", cost_estimate)

            return {
                "success": True,
                "analysis": response_text,
                "cost": cost_estimate,
                "tokens": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens,
                },
                "model": model,
            }

        except anthropic.APIError as e:
            logger.error("Error de API: %s", repr(str(e)))
            return {"success": False, "error": str(e), "error_type": "api_error"}
        except Exception as e:
            logger.error("Error inesperado: %s", repr(str(e)))
            return {"success": False, "error": str(e), "error_type": "unknown"}

    # ─── Streaming ───────────────────────────────────────────────────────

    def _analyze_streaming(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        stream_callback,
    ) -> Dict[str, Any]:
        """Ejecuta análisis con streaming, invocando stream_callback(chunk) por cada fragmento."""
        try:
            response_text = ""
            input_tokens = 0
            output_tokens = 0

            with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    response_text += text
                    stream_callback(text)

                # Obtener uso de tokens del mensaje final
                final_message = stream.get_final_message()
                input_tokens = final_message.usage.input_tokens
                output_tokens = final_message.usage.output_tokens

            cost_estimate = self._calculate_cost(input_tokens, output_tokens, model)
            self.cost_history.append(cost_estimate)
            logger.info("Análisis streaming completado. Coste: %s", cost_estimate)

            return {
                "success": True,
                "analysis": response_text,
                "cost": cost_estimate,
                "tokens": {"input": input_tokens, "output": output_tokens},
                "model": model,
            }

        except anthropic.APIError as e:
            logger.error("Error de API streaming: %s", repr(str(e)))
            return {"success": False, "error": str(e), "error_type": "api_error"}
        except Exception as e:
            logger.error("Error inesperado streaming: %s", repr(str(e)))
            return {"success": False, "error": str(e), "error_type": "unknown"}

    # ─── Conversión de archivos ─────────────────────────────────────────

    def _convert_file_to_text(self, file_content: bytes, filename: str) -> str:
        """Convierte archivos Excel/CSV a representación textual."""
        try:
            buffer = BytesIO(file_content)

            if filename.endswith(".csv"):
                df = pd.read_csv(buffer)
                return self._dataframe_to_markdown(df, "Datos")

            elif filename.endswith((".xlsx", ".xls")):
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
            logger.error("Error convirtiendo archivo a texto: %s", repr(str(e)))
            return f"[Error leyendo archivo: {e}]"

    def _dataframe_to_markdown(self, df: pd.DataFrame, sheet_name: str) -> str:
        """Convierte un DataFrame a formato markdown tabular."""
        df_copy = df.copy()
        df_copy = df_copy.fillna("")

        for col in df_copy.columns:
            if df_copy[col].dtype == "object":
                df_copy[col] = df_copy[col].astype(str)

        text = f"## HOJA: {sheet_name}\n"
        text += f"**Total filas: {len(df)} | Total columnas: {len(df.columns)}**\n\n"
        text += f"**Columnas:** {', '.join(df.columns.tolist())}\n\n"

        # Resumen estadístico por columna
        text += "### RESUMEN ESTADÍSTICO POR COLUMNA:\n"
        for col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            if df[col].dtype in ["int64", "float64"]:
                text += f"- **{col}**: Min={col_data.min()}, Max={col_data.max()}, Media={col_data.mean():.2f}\n"
            else:
                value_counts = col_data.value_counts()
                if len(value_counts) <= 20:
                    text += f"- **{col}**: {dict(value_counts)}\n"
                else:
                    top_5 = value_counts.head(5).to_dict()
                    text += f"- **{col}**: Top 5: {top_5} (+ {len(value_counts) - 5} más)\n"

        text += "\n### DATOS COMPLETOS:\n"

        if len(df) > MAX_ROWS_MARKDOWN:
            df_display = df_copy.head(MAX_ROWS_MARKDOWN)
            text += f"**(Mostrando primeras {MAX_ROWS_MARKDOWN} de {len(df)} filas)**\n\n"
        else:
            df_display = df_copy

        try:
            text += df_display.to_markdown(index=False)
        except Exception:
            text += df_display.to_string(index=False)

        return text

    # ─── Costes ─────────────────────────────────────────────────────────────

    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> CostEstimate:
        """Calcula el coste de una llamada a la API."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["claude-sonnet-4-20250514"])

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return CostEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            estimated_cost_usd=input_cost + output_cost,
        )

    def get_total_cost(self) -> float:
        """Retorna el coste total acumulado en la sesión."""
        return sum(cost.estimated_cost_usd for cost in self.cost_history)

    def get_cost_summary(self) -> Dict[str, Any]:
        """Retorna resumen de costes de la sesión."""
        if not self.cost_history:
            return {
                "total_calls": 0,
                "total_cost_usd": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "models_used": [],
            }

        return {
            "total_calls": len(self.cost_history),
            "total_cost_usd": self.get_total_cost(),
            "total_input_tokens": sum(c.input_tokens for c in self.cost_history),
            "total_output_tokens": sum(c.output_tokens for c in self.cost_history),
            "models_used": list(set(c.model for c in self.cost_history)),
            "cost_breakdown": [
                {
                    "model": c.model,
                    "input_tokens": c.input_tokens,
                    "output_tokens": c.output_tokens,
                    "cost_usd": c.estimated_cost_usd,
                }
                for c in self.cost_history
            ],
        }

    def estimate_cost_before_call(
        self,
        file_size_bytes: int,
        model: str = "claude-sonnet-4-20250514",
        estimated_output_tokens: int = 8000,
    ) -> float:
        """Estima el coste antes de hacer una llamada."""
        estimated_input_tokens = int(file_size_bytes / 3)
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["claude-sonnet-4-20250514"])

        input_cost = (estimated_input_tokens / 1_000_000) * pricing["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
