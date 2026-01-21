# -*- coding: utf-8 -*-
"""
Módulo de análisis cuantitativo determinista.
Calcula KPIs, agregados, tendencias sin usar IA.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class QuantitativeAnalyzer:
    """Realiza análisis cuantitativo automático de datos."""
    
    def __init__(self, sheets_data: Dict[str, pd.DataFrame], metadata: Dict[str, Any]):
        self.sheets_data = sheets_data
        self.metadata = metadata
        self.kpis = {}
        
    def analyze(self) -> Dict[str, Any]:
        """Ejecuta análisis completo y retorna resultados."""
        results = {
            'kpis': {},
            'aggregations': {},
            'trends': {},
            'distributions': {},
            'correlations': {},
            'anomalies': {}
        }
        
        for sheet_name, df in self.sheets_data.items():
            logger.info(f"Analyzing sheet: {sheet_name}")
            
            results['kpis'][sheet_name] = self._calculate_kpis(df, sheet_name)
            results['aggregations'][sheet_name] = self._calculate_aggregations(df)
            results['distributions'][sheet_name] = self._analyze_distributions(df)
            results['correlations'][sheet_name] = self._calculate_correlations(df)
            results['trends'][sheet_name] = self._detect_trends(df)
            results['anomalies'][sheet_name] = self._detect_anomalies(df)
        
        # KPIs globales
        results['global_kpis'] = self._calculate_global_kpis()
        
        return results
    
    def _calculate_kpis(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Calcula KPIs automáticos basados en estructura de datos."""
        kpis = {}
        
        # KPIs básicos
        kpis['total_records'] = len(df)
        kpis['completeness_rate'] = round((df.count().sum() / (len(df) * len(df.columns))) * 100, 2)
        kpis['missing_values_total'] = df.isnull().sum().sum()
        
        # KPIs numéricos
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            for col in numeric_cols:
                col_key = f"{col}_stats"
                kpis[col_key] = {
                    'mean': round(df[col].mean(), 2) if df[col].notna().any() else None,
                    'median': round(df[col].median(), 2) if df[col].notna().any() else None,
                    'std': round(df[col].std(), 2) if df[col].notna().any() else None,
                    'min': round(df[col].min(), 2) if df[col].notna().any() else None,
                    'max': round(df[col].max(), 2) if df[col].notna().any() else None,
                    'sum': round(df[col].sum(), 2) if df[col].notna().any() else None,
                }
        
        # KPIs categóricos
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            kpis['categorical_summary'] = {}
            for col in categorical_cols:
                unique_values = df[col].nunique()
                mode_value = df[col].mode()[0] if len(df[col].mode()) > 0 else None
                kpis['categorical_summary'][col] = {
                    'unique_values': unique_values,
                    'most_common': mode_value,
                    'diversity_score': round((unique_values / len(df)) * 100, 2) if len(df) > 0 else 0
                }
        
        # Detectar KPIs específicos por nombre de columna
        kpis.update(self._detect_domain_specific_kpis(df))
        
        return kpis
    
    def _detect_domain_specific_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta KPIs específicos del dominio basado en nombres de columnas."""
        domain_kpis = {}
        
        # Normalizar nombres de columnas
        col_lower = {col: col.lower() for col in df.columns}
        
        # Satisfacción / NPS
        for col, col_name_lower in col_lower.items():
            if any(keyword in col_name_lower for keyword in ['satisf', 'satisfaction', 'nps', 'score', 'rating', 'calificacion']):
                if pd.api.types.is_numeric_dtype(df[col]):
                    values = df[col].dropna()
                    if len(values) > 0:
                        domain_kpis['satisfaction_metrics'] = domain_kpis.get('satisfaction_metrics', {})
                        domain_kpis['satisfaction_metrics'][col] = {
                            'average_score': round(values.mean(), 2),
                            'score_distribution': values.value_counts().to_dict(),
                            'positive_rate': round((values >= values.median()).sum() / len(values) * 100, 2)
                        }
        
        # Ventas / Revenue
        for col, col_name_lower in col_lower.items():
            if any(keyword in col_name_lower for keyword in ['venta', 'sales', 'revenue', 'ingreso', 'precio', 'price', 'amount']):
                if pd.api.types.is_numeric_dtype(df[col]):
                    values = df[col].dropna()
                    if len(values) > 0:
                        domain_kpis['sales_metrics'] = domain_kpis.get('sales_metrics', {})
                        domain_kpis['sales_metrics'][col] = {
                            'total': round(values.sum(), 2),
                            'average': round(values.mean(), 2),
                            'median': round(values.median(), 2),
                            'top_10_pct': round(values.quantile(0.9), 2)
                        }
        
        # Tasas de conversión / porcentajes
        for col, col_name_lower in col_lower.items():
            if any(keyword in col_name_lower for keyword in ['tasa', 'rate', 'conversion', '%', 'porcentaje', 'percentage']):
                if pd.api.types.is_numeric_dtype(df[col]):
                    values = df[col].dropna()
                    if len(values) > 0:
                        domain_kpis['conversion_metrics'] = domain_kpis.get('conversion_metrics', {})
                        domain_kpis['conversion_metrics'][col] = {
                            'average_rate': round(values.mean(), 2),
                            'best_rate': round(values.max(), 2),
                            'worst_rate': round(values.min(), 2)
                        }
        
        return domain_kpis
    
    def _calculate_aggregations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula agregaciones por categorías."""
        aggregations = {}
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            for cat_col in categorical_cols:
                # Limitar a categorías con valores razonables
                if df[cat_col].nunique() <= 50:
                    aggregations[cat_col] = {}
                    for num_col in numeric_cols:
                        grouped = df.groupby(cat_col)[num_col].agg(['mean', 'sum', 'count']).round(2)
                        aggregations[cat_col][num_col] = grouped.to_dict()
        
        return aggregations
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza distribuciones de variables."""
        distributions = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            values = df[col].dropna()
            if len(values) > 0:
                distributions[col] = {
                    'quartiles': {
                        'Q1': round(values.quantile(0.25), 2),
                        'Q2': round(values.quantile(0.5), 2),
                        'Q3': round(values.quantile(0.75), 2)
                    },
                    'skewness': round(values.skew(), 2) if len(values) > 2 else None,
                    'kurtosis': round(values.kurtosis(), 2) if len(values) > 3 else None
                }
        
        return distributions
    
    def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula correlaciones entre variables numéricas."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {}
        
        try:
            corr_matrix = df[numeric_cols].corr().round(2)
            
            # Encontrar correlaciones significativas (|r| > 0.5)
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5 and not pd.isna(corr_value):
                        strong_correlations.append({
                            'var1': corr_matrix.columns[i],
                            'var2': corr_matrix.columns[j],
                            'correlation': float(corr_value)
                        })
            
            return {
                'correlation_matrix': corr_matrix.to_dict(),
                'strong_correlations': strong_correlations
            }
        except Exception as e:
            logger.warning(f"Error calculating correlations: {e}")
            return {}
    
    def _detect_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta tendencias temporales si hay columnas de fecha."""
        trends = {}
        
        datetime_cols = df.select_dtypes(include=['datetime']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            date_col = datetime_cols[0]
            df_sorted = df.sort_values(date_col)
            
            for num_col in numeric_cols:
                values = df_sorted[num_col].dropna()
                if len(values) > 2:
                    # Calcular tendencia simple
                    x = np.arange(len(values))
                    try:
                        slope = np.polyfit(x, values, 1)[0]
                        trends[num_col] = {
                            'trend': 'increasing' if slope > 0 else 'decreasing',
                            'slope': round(float(slope), 4)
                        }
                    except:
                        pass
        
        return trends
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta valores anómalos usando IQR."""
        anomalies = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            values = df[col].dropna()
            if len(values) > 4:
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = values[(values < lower_bound) | (values > upper_bound)]
                
                if len(outliers) > 0:
                    anomalies[col] = {
                        'count': len(outliers),
                        'percentage': round((len(outliers) / len(values)) * 100, 2),
                        'bounds': {
                            'lower': round(lower_bound, 2),
                            'upper': round(upper_bound, 2)
                        }
                    }
        
        return anomalies
    
    def _calculate_global_kpis(self) -> Dict[str, Any]:
        """Calcula KPIs globales de todo el dataset."""
        total_records = sum(len(df) for df in self.sheets_data.values())
        total_columns = sum(len(df.columns) for df in self.sheets_data.values())
        
        return {
            'total_sheets': len(self.sheets_data),
            'total_records': total_records,
            'total_columns': total_columns,
            'avg_records_per_sheet': round(total_records / len(self.sheets_data), 2) if len(self.sheets_data) > 0 else 0
        }
    
    def format_for_report(self) -> str:
        """Formatea resultados del analisis para incluir en el reporte."""
        analysis = self.analyze()
        
        report = "## ANALISIS CUANTITATIVO DETERMINISTA (CALCULADO AUTOMATICAMENTE)\n\n"
        
        # KPIs globales
        report += "### METRICAS GLOBALES\n"
        for key, value in analysis['global_kpis'].items():
            report += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        report += "\n"
        
        # KPIs por hoja
        for sheet_name, df in self.sheets_data.items():
            report += f"### ANALISIS DE HOJA: '{sheet_name}'\n\n"
            report += f"**Total registros**: {len(df)}\n\n"
            
            # Analizar TODAS las columnas categoricas con value_counts
            report += "#### DISTRIBUCION POR COLUMNAS CATEGORICAS\n\n"
            
            for col in df.columns:
                col_data = df[col].dropna()
                if len(col_data) == 0:
                    continue
                    
                # Para columnas tipo objeto (categoricas)
                if df[col].dtype == 'object' or str(df[col].dtype) == 'object':
                    value_counts = col_data.value_counts()
                    total = len(col_data)
                    
                    # Solo mostrar si hay menos de 30 categorias unicas
                    if len(value_counts) <= 30 and len(value_counts) > 0:
                        report += f"**{col}:**\n"
                        report += "| Valor | Cantidad | Porcentaje |\n"
                        report += "|-------|----------|------------|\n"
                        for val, count in value_counts.items():
                            pct = (count / total) * 100
                            # Truncar valores muy largos
                            val_str = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
                            report += f"| {val_str} | {count} | {pct:.1f}% |\n"
                        report += "\n"
            
            # Detectar columnas especificas de encuestas
            report += self._analyze_survey_specific_columns(df)
        
        return report
    
    def _analyze_survey_specific_columns(self, df: pd.DataFrame) -> str:
        """Analiza columnas especificas de encuestas de satisfaccion."""
        report = ""
        
        # Buscar columna de resultado de llamada
        result_cols = [col for col in df.columns if 'resultado' in col.lower() or 'llamada' in col.lower()]
        if result_cols:
            col = result_cols[-1]  # Tomar la ultima (suele ser la de resultado)
            value_counts = df[col].value_counts()
            total = len(df)
            encuestas_realizadas = value_counts.get('ENCUESTA REALIZADA', 0)
            
            report += "#### ANALISIS DE CONTACTABILIDAD\n\n"
            report += f"- **Total intentos de contacto**: {total}\n"
            report += f"- **Encuestas completadas**: {encuestas_realizadas} ({(encuestas_realizadas/total*100):.1f}%)\n"
            report += f"- **Tasa de no contacto**: {(total - encuestas_realizadas)} ({((total-encuestas_realizadas)/total*100):.1f}%)\n\n"
        
        # Buscar columna de "ha comprado"
        compra_cols = [col for col in df.columns if 'comprado' in col.lower() or 'compra' in col.lower()]
        if compra_cols:
            col = compra_cols[0]
            value_counts = df[col].dropna().value_counts()
            if len(value_counts) > 0:
                total_respuestas = value_counts.sum()
                compras_si = value_counts.get('SI', 0)
                report += "#### ANALISIS DE CONVERSION\n\n"
                report += f"- **Clientes que SI compraron**: {compras_si} ({(compras_si/total_respuestas*100):.1f}%)\n"
                report += f"- **Clientes que NO compraron**: {value_counts.get('NO', 0)} ({(value_counts.get('NO', 0)/total_respuestas*100):.1f}%)\n\n"
        
        # Buscar columna de trato/satisfaccion
        satisf_cols = [col for col in df.columns if 'trato' in col.lower() or 'correcto' in col.lower() or 'satisf' in col.lower()]
        if satisf_cols:
            col = satisf_cols[0]
            value_counts = df[col].dropna().value_counts()
            if len(value_counts) > 0:
                total_respuestas = value_counts.sum()
                satisfechos = value_counts.get('SI', 0)
                report += "#### SATISFACCION CON EL TRATO\n\n"
                report += f"- **Clientes satisfechos (SI)**: {satisfechos} ({(satisfechos/total_respuestas*100):.1f}%)\n"
                report += f"- **Clientes no satisfechos (NO)**: {value_counts.get('NO', 0)} ({(value_counts.get('NO', 0)/total_respuestas*100):.1f}%)\n\n"
        
        # Buscar columna de intencion de cambio
        cambio_cols = [col for col in df.columns if 'sigue pensando' in col.lower() or 'cambiar' in col.lower() or 'proximamente' in col.lower()]
        if cambio_cols:
            col = cambio_cols[0]
            value_counts = df[col].dropna().value_counts()
            if len(value_counts) > 0:
                total_respuestas = value_counts.sum()
                quieren_cambiar = value_counts.get('SI', 0)
                report += "#### INTENCION DE COMPRA FUTURA\n\n"
                report += f"- **SI piensan cambiar de coche**: {quieren_cambiar} ({(quieren_cambiar/total_respuestas*100):.1f}%)\n"
                report += f"- **NO piensan cambiar**: {value_counts.get('NO', 0)} ({(value_counts.get('NO', 0)/total_respuestas*100):.1f}%)\n\n"
        
        # Buscar columna de plazo
        plazo_cols = [col for col in df.columns if 'plazo' in col.lower() or 'meses' in col.lower()]
        if plazo_cols:
            col = plazo_cols[0]
            value_counts = df[col].dropna().value_counts()
            if len(value_counts) > 0:
                report += "#### PLAZO DE COMPRA ESTIMADO\n\n"
                report += "| Plazo | Cantidad | Porcentaje |\n"
                report += "|-------|----------|------------|\n"
                total_respuestas = value_counts.sum()
                for val, count in value_counts.items():
                    report += f"| {val} | {count} | {(count/total_respuestas*100):.1f}% |\n"
                report += "\n"
        
        # Buscar columna de interes en volver
        volver_cols = [col for col in df.columns if 'pasarse' in col.lower() or 'volver' in col.lower() or 'nuevamente' in col.lower()]
        if volver_cols:
            col = volver_cols[0]
            value_counts = df[col].dropna().value_counts()
            if len(value_counts) > 0:
                total_respuestas = value_counts.sum()
                quieren_volver = value_counts.get('SI', 0)
                report += "#### INTERES EN VOLVER AL CONCESIONARIO\n\n"
                report += f"- **SI les interesa volver**: {quieren_volver} ({(quieren_volver/total_respuestas*100):.1f}%)\n"
                report += f"- **NO les interesa**: {value_counts.get('NO', 0)} ({(value_counts.get('NO', 0)/total_respuestas*100):.1f}%)\n\n"
        
        # Buscar modelos comprados
        modelo_cols = [col for col in df.columns if 'modelo' in col.lower()]
        if modelo_cols:
            # Buscar la columna que tenga "4" en el nombre (suele ser el modelo del competidor) o la segunda
            for col in modelo_cols:
                value_counts = df[col].dropna().value_counts()
                if len(value_counts) > 0 and len(value_counts) < 50:
                    report += f"#### MODELOS MENCIONADOS ({col})\n\n"
                    report += "| Modelo | Cantidad |\n"
                    report += "|--------|----------|\n"
                    for val, count in value_counts.head(15).items():
                        report += f"| {val} | {count} |\n"
                    report += "\n"
        
        # Buscar concesionario donde compro
        conces_cols = [col for col in df.columns if 'concesionario' in col.lower() and 'comprado' in col.lower()]
        if conces_cols:
            col = conces_cols[0]
            value_counts = df[col].dropna().value_counts()
            if len(value_counts) > 0:
                report += "#### CONCESIONARIOS DONDE COMPRARON\n\n"
                report += "| Concesionario | Cantidad |\n"
                report += "|---------------|----------|\n"
                for val, count in value_counts.head(10).items():
                    val_str = str(val)[:40] + "..." if len(str(val)) > 40 else str(val)
                    report += f"| {val_str} | {count} |\n"
                report += "\n"
        
        # Buscar marcas de interes
        marcas_cols = [col for col in df.columns if 'marcas' in col.lower() and 'interesado' in col.lower()]
        if marcas_cols:
            col = marcas_cols[0]
            # Contar menciones de marcas (pueden estar separadas por coma)
            all_marcas = []
            for val in df[col].dropna():
                if isinstance(val, str):
                    # Separar por comas y limpiar
                    marcas = [m.strip().upper() for m in str(val).replace(' Y ', ', ').replace(',', ', ').split(', ') if m.strip()]
                    all_marcas.extend(marcas)
            
            if all_marcas:
                from collections import Counter
                marca_counts = Counter(all_marcas)
                report += "#### MARCAS DE INTERES MENCIONADAS\n\n"
                report += "| Marca | Menciones |\n"
                report += "|-------|-----------|\n"
                for marca, count in marca_counts.most_common(15):
                    report += f"| {marca} | {count} |\n"
                report += "\n"
        
        return report
