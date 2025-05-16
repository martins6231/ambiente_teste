import pandas as pd
import numpy as np
from datetime import datetime

def preprocess_data(df):
    """
    Preprocess the input dataframe to standardize column names and data types.
    
    Args:
        df: Input pandas DataFrame
    
    Returns:
        Preprocessed pandas DataFrame
    """
    # Make a copy to avoid modifying the original
    df_processed = df.copy()
    
    # Standardize machine names if needed
    machine_mapping = {
        78: "PET",
        79: "TETRA 1000",
        80: "TETRA 200",
        89: "SIG 1000",
        91: "SIG 200"
    }
    
    # Check if 'Máquina' column exists
    if 'Máquina' in df_processed.columns:
        df_processed['Máquina'] = df_processed['Máquina'].replace(machine_mapping)
    
    # Convert date columns to datetime
    date_columns = ['Inicio', 'Fim']
    for col in date_columns:
        if col in df_processed.columns:
            df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')
    
    # Process duration column
    if 'Duração' in df_processed.columns:
        try:
            # Try to convert duration to timedelta
            df_processed['Duração'] = pd.to_timedelta(df_processed['Duração'])
        except:
            # If that fails, try parsing specific formats
            def parse_duration(duration_str):
                try:
                    if isinstance(duration_str, str):
                        parts = duration_str.split(':')
                        if len(parts) == 3:
                            hours, minutes, seconds = map(int, parts)
                            return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    return pd.NaT
                except:
                    return pd.NaT
            
            df_processed['Duração'] = df_processed['Duração'].apply(parse_duration)
    
    # Create additional date-related columns
    if 'Inicio' in df_processed.columns:
        df_processed['Ano'] = df_processed['Inicio'].dt.year
        df_processed['Mês'] = df_processed['Inicio'].dt.month
        df_processed['Mês_Nome'] = df_processed['Inicio'].dt.strftime('%B')
        df_processed['Ano-Mês'] = df_processed['Inicio'].dt.strftime('%Y-%m')
        
        # Add day of week and hour for the new analyses
        df_processed['Dia_Semana'] = df_processed['Inicio'].dt.dayofweek  # 0=Monday, 6=Sunday
        df_processed['Hora_Dia'] = df_processed['Inicio'].dt.hour
    
    # Drop rows with missing values in essential columns
    essential_columns = [col for col in ['Máquina', 'Inicio', 'Fim', 'Duração'] if col in df_processed.columns]
    if essential_columns:
        df_processed = df_processed.dropna(subset=essential_columns)
    
    return df_processed

def calculate_metrics(df, tempo_programado):
    """
    Calculate key metrics from the processed dataframe.
    
    Args:
        df: Processed pandas DataFrame
        tempo_programado: Time delta representing total scheduled time
    
    Returns:
        Dictionary of metrics
    """
    metrics = {}
    
    # Calculate availability
    tempo_total_parado = df['Duração'].sum()
    disponibilidade = (tempo_programado - tempo_total_parado) / tempo_programado * 100
    metrics['disponibilidade'] = max(0, min(100, disponibilidade))
    
    # Calculate operational efficiency
    tempo_operacao = tempo_programado - tempo_total_parado
    eficiencia = tempo_operacao / tempo_programado * 100
    metrics['eficiencia'] = max(0, min(100, eficiencia))
    
    # Average downtime
    metrics['tmp'] = df['Duração'].mean()
    
    # Critical stops (more than 1 hour)
    limite = pd.Timedelta(hours=1)
    paradas_criticas = df[df['Duração'] > limite]
    percentual_criticas = len(paradas_criticas) / len(df) * 100 if len(df) > 0 else 0
    metrics['paradas_criticas'] = paradas_criticas
    metrics['percentual_criticas'] = percentual_criticas
    
    # Store processed data for additional metrics
    if 'Área Responsável' in df.columns:
        metrics['area_counts'] = df.groupby('Área Responsável')['Duração'].sum()
    
    if 'Parada' in df.columns:
        metrics['pareto'] = df.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
        metrics['frequencia_categorias'] = df['Parada'].value_counts()
    
    # Store occurrence rate by month if data spans multiple months
    metrics['ocorrencias'] = df.groupby('Ano-Mês').size()
    
    return metrics