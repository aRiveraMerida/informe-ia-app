# -*- coding: utf-8 -*-
"""
Modulo de procesamiento y normalizacion de datos.
Detecta estructura, infiere tipos, maneja multiples hojas XLSX.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from io import BytesIO
import logging
import warnings

# Suprimir TODOS los warnings de pandas (incluidos los de fechas)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*Could not infer format.*')

logger = logging.getLogger(__name__)


class DataProcessor:
    """Procesa y normaliza datos de archivos XLSX/CSV."""
    
    def __init__(self, file_content: bytes, filename: str):
        self.file_content = file_content
        self.filename = filename
        self.sheets_data: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, Any] = {}
        
    def process(self) -> Dict[str, Any]:
        """Procesa el archivo y retorna datos estructurados."""
        try:
            if self.filename.endswith('.csv'):
                self._process_csv()
            else:
                self._process_excel()
            
            self._analyze_structure()
            self._generate_metadata()
            
            return {
                'sheets': self.sheets_data,
                'metadata': self.metadata,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {
                'sheets': {},
                'metadata': {},
                'success': False,
                'error': str(e)
            }
    
    def _process_csv(self):
        """Procesa archivo CSV."""
        df = pd.read_csv(BytesIO(self.file_content))
        self.sheets_data['Sheet1'] = df
        
    def _process_excel(self):
        """Procesa archivo Excel con múltiples hojas."""
        excel_file = pd.ExcelFile(BytesIO(self.file_content))
        
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Filtrar hojas vacías o sin datos relevantes
                if not df.empty and len(df.columns) > 0:
                    # Detectar y eliminar filas de encabezado múltiples
                    df = self._clean_dataframe(df)
                    if not df.empty:
                        self.sheets_data[sheet_name] = df
            except Exception as e:
                logger.warning(f"Error reading sheet {sheet_name}: {e}")
                continue
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y normaliza DataFrame."""
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        # Eliminar columnas completamente vacías
        df = df.dropna(axis=1, how='all')
        
        # Renombrar columnas sin nombre
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            for i, col in enumerate(unnamed_cols):
                df = df.rename(columns={col: f'Column_{i+1}'})
        
        # Inferir tipos de datos
        df = self._infer_types(df)
        
        return df
    
    def _infer_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Infiere tipos de datos de columnas."""
        for col in df.columns:
            # Intentar convertir a numérico
            try:
                numeric_result = pd.to_numeric(df[col], errors='coerce')
                # Solo aplicar si la conversión tuvo éxito en al menos algunos valores
                if numeric_result.notna().any():
                    df[col] = numeric_result
            except:
                pass
            
            # Intentar convertir a datetime (con formato inferido silenciosamente)
            if df[col].dtype == 'object':
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        datetime_result = pd.to_datetime(
                            df[col], 
                            errors='coerce', 
                            dayfirst=True,
                            format='mixed'  # Esto evita el warning de formato
                        )
                    # Solo aplicar si la conversión tuvo éxito en al menos algunos valores
                    if datetime_result.notna().any() and datetime_result.notna().sum() > len(df) * 0.5:
                        df[col] = datetime_result
                except:
                    pass
        
        return df
    
    def _analyze_structure(self):
        """Analiza estructura de datos."""
        for sheet_name, df in self.sheets_data.items():
            self.metadata[sheet_name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'column_types': {col: str(df[col].dtype) for col in df.columns},
                'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(df.select_dtypes(include=['object']).columns),
                'datetime_columns': list(df.select_dtypes(include=['datetime']).columns),
                'missing_values': df.isnull().sum().to_dict(),
                'completeness_pct': round((df.count().sum() / (len(df) * len(df.columns))) * 100, 2)
            }
    
    def _generate_metadata(self):
        """Genera metadatos globales."""
        total_rows = sum(meta['rows'] for meta in self.metadata.values())
        total_cols = sum(meta['columns'] for meta in self.metadata.values())
        
        self.metadata['_global'] = {
            'filename': self.filename,
            'total_sheets': len(self.sheets_data),
            'total_rows': total_rows,
            'total_columns': total_cols,
            'sheet_names': list(self.sheets_data.keys())
        }
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calcula estadísticas resumidas de todas las hojas."""
        summary = {}
        
        for sheet_name, df in self.sheets_data.items():
            sheet_summary = {}
            
            # Estadísticas numéricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                sheet_summary['numeric_stats'] = df[numeric_cols].describe().to_dict()
            
            # Distribuciones categóricas
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                sheet_summary['categorical_distributions'] = {}
                for col in categorical_cols:
                    value_counts = df[col].value_counts().head(10).to_dict()
                    sheet_summary['categorical_distributions'][col] = value_counts
            
            summary[sheet_name] = sheet_summary
        
        return summary
    
    def get_sample_data(self, n: int = 5) -> Dict[str, pd.DataFrame]:
        """Retorna muestra de datos de cada hoja."""
        samples = {}
        for sheet_name, df in self.sheets_data.items():
            samples[sheet_name] = df.head(n)
        return samples
