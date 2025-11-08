"""
Módulo de Preprocesamiento de Datos para Ciencia de Datos
Autor: Gabriela Ocampo
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from typing import List, Union, Optional
import warnings
warnings.filterwarnings('ignore')


class PreprocessingPipeline:
    """
    Clase para realizar preprocesamiento completo de datasets.
    Incluye manejo de valores nulos, normalización, codificación y limpieza.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el pipeline con un DataFrame.
        
        Args:
            df: DataFrame de pandas a preprocesar
        """
        self.df = df.copy()
        self.original_shape = df.shape
        self.transformations_log = []
        
    def info_dataset(self) -> dict:
        """
        Obtiene información general del dataset.
        
        Returns:
            Diccionario con información del dataset
        """
        info = {
            'shape': self.df.shape,
            'columnas': list(self.df.columns),
            'tipos_datos': self.df.dtypes.to_dict(),
            'valores_nulos': self.df.isnull().sum().to_dict(),
            'duplicados': self.df.duplicated().sum(),
            'memoria_mb': self.df.memory_usage(deep=True).sum() / 1024**2
        }
        return info
    
    def detectar_valores_nulos(self) -> pd.DataFrame:
        """
        Detecta y analiza valores nulos en el dataset.
        
        Returns:
            DataFrame con análisis de valores nulos
        """
        nulos = pd.DataFrame({
            'columna': self.df.columns,
            'valores_nulos': self.df.isnull().sum().values,
            'porcentaje': (self.df.isnull().sum().values / len(self.df) * 100).round(2)
        })
        nulos = nulos[nulos['valores_nulos'] > 0].sort_values('porcentaje', ascending=False)
        return nulos
    
    def manejar_valores_nulos(self, 
                             estrategia: str = 'eliminar',
                             columnas: Optional[List[str]] = None,
                             valor_relleno: Optional[Union[int, float, str]] = None) -> 'PreprocessingPipeline':
        """
        Maneja valores nulos según la estrategia especificada.
        
        Args:
            estrategia: 'eliminar', 'media', 'mediana', 'moda', 'constante', 'ffill', 'bfill'
            columnas: Lista de columnas a procesar. Si es None, procesa todas
            valor_relleno: Valor para usar con estrategia 'constante'
            
        Returns:
            self para encadenamiento de métodos
        """
        cols = columnas if columnas else self.df.columns.tolist()
        
        if estrategia == 'eliminar':
            before = len(self.df)
            self.df = self.df.dropna(subset=cols)
            self.transformations_log.append(
                f"Eliminadas {before - len(self.df)} filas con valores nulos"
            )
            
        elif estrategia == 'media':
            for col in cols:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
            self.transformations_log.append(f"Rellenados nulos con media en {cols}")
            
        elif estrategia == 'mediana':
            for col in cols:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
            self.transformations_log.append(f"Rellenados nulos con mediana en {cols}")
            
        elif estrategia == 'moda':
            for col in cols:
                self.df[col].fillna(self.df[col].mode()[0], inplace=True)
            self.transformations_log.append(f"Rellenados nulos con moda en {cols}")
            
        elif estrategia == 'constante':
            for col in cols:
                self.df[col].fillna(valor_relleno, inplace=True)
            self.transformations_log.append(
                f"Rellenados nulos con constante '{valor_relleno}' en {cols}"
            )
            
        elif estrategia == 'ffill':
            self.df[cols] = self.df[cols].fillna(method='ffill')
            self.transformations_log.append(f"Rellenados nulos con forward fill en {cols}")
            
        elif estrategia == 'bfill':
            self.df[cols] = self.df[cols].fillna(method='bfill')
            self.transformations_log.append(f"Rellenados nulos con backward fill en {cols}")
        
        return self
    
    def eliminar_duplicados(self, 
                           subset: Optional[List[str]] = None,
                           keep: str = 'first') -> 'PreprocessingPipeline':
        """
        Elimina filas duplicadas del dataset.
        
        Args:
            subset: Columnas a considerar para detectar duplicados
            keep: 'first', 'last' o False
            
        Returns:
            self para encadenamiento de métodos
        """
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed = before - len(self.df)
        self.transformations_log.append(f"Eliminadas {removed} filas duplicadas")
        return self
    
    def normalizar_columnas(self, 
                           columnas: List[str],
                           metodo: str = 'standard') -> 'PreprocessingPipeline':
        """
        Normaliza columnas numéricas.
        
        Args:
            columnas: Lista de columnas a normalizar
            metodo: 'standard' (z-score) o 'minmax' (0-1)
            
        Returns:
            self para encadenamiento de métodos
        """
        if metodo == 'standard':
            scaler = StandardScaler()
            self.df[columnas] = scaler.fit_transform(self.df[columnas])
            self.transformations_log.append(
                f"Normalización estándar aplicada a {columnas}"
            )
            
        elif metodo == 'minmax':
            scaler = MinMaxScaler()
            self.df[columnas] = scaler.fit_transform(self.df[columnas])
            self.transformations_log.append(
                f"Normalización MinMax aplicada a {columnas}"
            )
        
        return self
    
    def codificar_categoricas(self, 
                             columnas: List[str],
                             metodo: str = 'label') -> 'PreprocessingPipeline':
        """
        Codifica variables categóricas.
        
        Args:
            columnas: Lista de columnas a codificar
            metodo: 'label' (LabelEncoder) u 'onehot' (OneHotEncoder)
            
        Returns:
            self para encadenamiento de métodos
        """
        if metodo == 'label':
            for col in columnas:
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col].astype(str))
            self.transformations_log.append(
                f"Label encoding aplicado a {columnas}"
            )
            
        elif metodo == 'onehot':
            self.df = pd.get_dummies(self.df, columns=columnas, prefix=columnas)
            self.transformations_log.append(
                f"One-hot encoding aplicado a {columnas}"
            )
        
        return self
    
    def detectar_outliers(self, 
                         columnas: List[str],
                         metodo: str = 'iqr') -> pd.DataFrame:
        """
        Detecta outliers en columnas numéricas.
        
        Args:
            columnas: Lista de columnas a analizar
            metodo: 'iqr' (rango intercuartílico) o 'zscore'
            
        Returns:
            DataFrame con información de outliers
        """
        outliers_info = []
        
        for col in columnas:
            if metodo == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = self.df[(self.df[col] < lower_bound) | 
                                  (self.df[col] > upper_bound)]
                
            elif metodo == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / 
                                 self.df[col].std())
                outliers = self.df[z_scores > 3]
            
            outliers_info.append({
                'columna': col,
                'cantidad_outliers': len(outliers),
                'porcentaje': (len(outliers) / len(self.df) * 100).round(2)
            })
        
        return pd.DataFrame(outliers_info)
    
    def eliminar_outliers(self, 
                         columnas: List[str],
                         metodo: str = 'iqr') -> 'PreprocessingPipeline':
        """
        Elimina outliers del dataset.
        
        Args:
            columnas: Lista de columnas a procesar
            metodo: 'iqr' o 'zscore'
            
        Returns:
            self para encadenamiento de métodos
        """
        before = len(self.df)
        
        for col in columnas:
            if metodo == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                self.df = self.df[(self.df[col] >= lower_bound) & 
                                 (self.df[col] <= upper_bound)]
            
            elif metodo == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / 
                                 self.df[col].std())
                self.df = self.df[z_scores <= 3]
        
        removed = before - len(self.df)
        self.transformations_log.append(
            f"Eliminados {removed} outliers usando método {metodo}"
        )
        return self
    
    def convertir_tipos(self, conversiones: dict) -> 'PreprocessingPipeline':
        """
        Convierte tipos de datos de columnas.
        
        Args:
            conversiones: Diccionario {columna: tipo_deseado}
            
        Returns:
            self para encadenamiento de métodos
        """
        for col, dtype in conversiones.items():
            self.df[col] = self.df[col].astype(dtype)
        self.transformations_log.append(
            f"Tipos de datos convertidos: {conversiones}"
        )
        return self
    
    def obtener_dataframe(self) -> pd.DataFrame:
        """
        Obtiene el DataFrame procesado.
        
        Returns:
            DataFrame procesado
        """
        return self.df
    
    def resumen_transformaciones(self) -> dict:
        """
        Obtiene un resumen de todas las transformaciones realizadas.
        
        Returns:
            Diccionario con información del procesamiento
        """
        return {
            'shape_original': self.original_shape,
            'shape_final': self.df.shape,
            'filas_eliminadas': self.original_shape[0] - self.df.shape[0],
            'columnas_agregadas': self.df.shape[1] - self.original_shape[1],
            'transformaciones': self.transformations_log
        }
    
    def guardar_dataset(self, 
                       ruta: str,
                       formato: str = 'csv') -> None:
        """
        Guarda el dataset procesado.
        
        Args:
            ruta: Ruta donde guardar el archivo
            formato: 'csv', 'excel' o 'json'
        """
        if formato == 'csv':
            self.df.to_csv(ruta, index=False)
        elif formato == 'excel':
            self.df.to_excel(ruta, index=False)
        elif formato == 'json':
            self.df.to_json(ruta, orient='records', indent=2)
        
        self.transformations_log.append(f"Dataset guardado en {ruta}")


# Función auxiliar para uso rápido
def preprocesar_dataset(df: pd.DataFrame,
                       eliminar_nulos: bool = True,
                       eliminar_duplicados: bool = True,
                       normalizar: bool = False,
                       columnas_normalizar: List[str] = None) -> pd.DataFrame:
    """
    Función auxiliar para preprocesamiento rápido.
    
    Args:
        df: DataFrame a procesar
        eliminar_nulos: Si eliminar filas con nulos
        eliminar_duplicados: Si eliminar duplicados
        normalizar: Si normalizar columnas numéricas
        columnas_normalizar: Columnas específicas a normalizar
        
    Returns:
        DataFrame procesado
    """
    pipeline = PreprocessingPipeline(df)
    
    if eliminar_nulos:
        pipeline.manejar_valores_nulos(estrategia='eliminar')
    
    if eliminar_duplicados:
        pipeline.eliminar_duplicados()
    
    if normalizar and columnas_normalizar:
        pipeline.normalizar_columnas(columnas_normalizar, metodo='standard')
    
    return pipeline.obtener_dataframe()


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 60)
    print("MÓDULO DE PREPROCESAMIENTO DE DATOS")
    print("=" * 60)
    
    # Crear dataset de ejemplo
    data = {
        'edad': [25, 30, np.nan, 35, 40, 28, 32, 30],
        'salario': [50000, 60000, 55000, np.nan, 70000, 52000, 58000, 60000],
        'ciudad': ['Quito', 'Guayaquil', 'Cuenca', 'Quito', 'Quito', 
                   'Guayaquil', 'Cuenca', 'Quito'],
        'departamento': ['IT', 'HR', 'IT', 'Sales', 'IT', 'HR', 'IT', 'HR']
    }
    
    df = pd.DataFrame(data)
    
    # Crear pipeline
    pipeline = PreprocessingPipeline(df)
    
    # Mostrar información inicial
    print("\nInformación inicial del dataset:")
    info = pipeline.info_dataset()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Procesar
    print("\n" + "=" * 60)
    print("APLICANDO TRANSFORMACIONES...")
    print("=" * 60)
    
    pipeline.manejar_valores_nulos(estrategia='media')\
            .eliminar_duplicados()\
            .codificar_categoricas(['ciudad', 'departamento'], metodo='label')
    
    # Mostrar resumen
    print("\nResumen de transformaciones:")
    resumen = pipeline.resumen_transformaciones()
    for key, value in resumen.items():
        print(f"\n{key}:")
        if isinstance(value, list):
            for item in value:
                print(f"  - {item}")
        else:
            print(f"  {value}")
    
    print("\n" + "=" * 60)
    print("Dataset procesado:")
    print(pipeline.obtener_dataframe())
    print("=" * 60)

    #Si puedes soñarlo, puedes programarlo :)