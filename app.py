import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import requests
import tempfile
import zipfile
import calendar
from datetime import datetime, timedelta
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Produção 2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Customizado com design moderno
st.markdown("""
<style>
    /* Importar fontes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variáveis de cores */
    :root {
        --primary-color: #1e40af;
        --secondary-color: #3b82f6;
        --accent-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
    }
    
    /* Reset e configurações globais */
    .main {
        font-family: 'Inter', sans-serif;
        background-color: var(--background-color);
    }
    
    /* Header estilizado */
    .dashboard-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;
        z-index: 1;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Cards modernos */
    .metric-card {
        background: var(--card-background);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
        border-color: var(--secondary-color);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--accent-color) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    /* Métricas estilizadas */
    div[data-testid="metric-container"] {
        background: var(--card-background);
        border: 1px solid var(--border-color);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
        border-color: var(--secondary-color);
    }
    
    div[data-testid="metric-container"] > div {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    div[data-testid="metric-container"] label {
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 2rem;
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background-color: var(--card-background);
        border-right: 1px solid var(--border-color);
    }
    
    /* Filtros estilizados */
    .stSelectbox > div > div {
        background-color: var(--card-background);
        border: 2px solid var(--border-color);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--secondary-color);
    }
    
    /* Date Range Picker customizado */
    .date-range-container {
        background: var(--card-background);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .date-range-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .date-range-icon {
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.3);
        background: linear-gradient(135deg, var(--secondary-color) 0%, var(--accent-color) 100%);
    }
    
    /* Download button especial */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
    }
    
    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
        border-bottom: 2px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary-color);
        background-color: rgba(30, 64, 175, 0.05);
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--primary-color);
        background-color: rgba(30, 64, 175, 0.1);
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
    }
    
    /* Expander customizado */
    .streamlit-expanderHeader {
        background-color: var(--card-background);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        font-weight: 600;
        color: var(--text-primary);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--secondary-color);
        background-color: rgba(59, 130, 246, 0.05);
    }
    
    /* Footer moderno */
    .footer {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-top: 3rem;
        text-align: center;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .footer p {
        margin: 0.5rem 0;
        opacity: 0.9;
    }
    
    /* Animações suaves */
    * {
        transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .dashboard-header h1 {
            font-size: 1.8rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
    }
    
    /* Ocultar elementos desnecessários do Streamlit */
    #MainMenu, .stDeployButton, footer {
        visibility: hidden;
    }
    
    /* Progress bar customizada */
    .stProgress > div > div > div > div {
        background-color: var(--primary-color);
        background-image: linear-gradient(45deg, var(--primary-color) 25%, var(--accent-color) 25%, var(--accent-color) 50%, var(--primary-color) 50%, var(--primary-color) 75%, var(--accent-color) 75%, var(--accent-color));
        background-size: 1rem 1rem;
        animation: progress-bar-stripes 1s linear infinite;
    }
    
    @keyframes progress-bar-stripes {
        0% { background-position: 0 0; }
        100% { background-position: 1rem 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# Traduções
translations = {
    'pt': {
        'title': 'Dashboard de Produção',
        'subtitle': 'Análise completa e inteligente de dados de produção',
        'select_language': 'Idioma',
        'select_file': 'Selecione o arquivo',
        'select_sheet': 'Selecione a planilha',
        'filters': 'Filtros',
        'period_filter': 'Filtro de Período',
        'select_all': 'Selecionar Todos',
        'clear_all': 'Limpar Seleção',
        'product': 'Produto',
        'operator': 'Operador',
        'shift': 'Turno',
        'order': 'Ordem',
        'machine': 'Máquina',
        'overview': 'Visão Geral',
        'temporal_analysis': 'Análise Temporal',
        'comparative_analysis': 'Análise Comparativa',
        'advanced_analysis': 'Análise Avançada',
        'predictions': 'Previsões',
        'total_production': 'Produção Total',
        'total_operators': 'Total de Operadores',
        'total_machines': 'Total de Máquinas',
        'total_products': 'Total de Produtos',
        'average_production': 'Média de Produção',
        'efficiency': 'Eficiência',
        'download_filtered': 'Baixar Dados Filtrados',
        'daily_production': 'Produção Diária',
        'hourly_production': 'Produção por Hora',
        'monthly_production': 'Produção Mensal',
        'production_by_product': 'Produção por Produto',
        'production_by_operator': 'Produção por Operador',
        'production_by_machine': 'Produção por Máquina',
        'production_by_shift': 'Produção por Turno',
        'correlation_analysis': 'Análise de Correlação',
        'pareto_products': 'Análise de Pareto - Produtos',
        'pareto_cumulative': '% Acumulado',
        'production_forecast': 'Previsão de Produção',
        'forecast_settings': 'Configurações da Previsão',
        'forecast_days': 'Dias para previsão',
        'generate_forecast': 'Gerar Previsão',
        'forecast_result': 'Resultado da Previsão',
        'download_file': 'Baixar Arquivo',
        'select_date_range': 'Selecione o Período',
        'quick_ranges': 'Períodos Rápidos',
        'last_7_days': 'Últimos 7 dias',
        'last_30_days': 'Últimos 30 dias',
        'last_90_days': 'Últimos 90 dias',
        'this_month': 'Este mês',
        'last_month': 'Mês passado',
        'this_year': 'Este ano',
        'custom_range': 'Período personalizado',
        'apply_filters': 'Aplicar Filtros',
        'reset_filters': 'Resetar Filtros',
        'loading': 'Carregando...',
        'no_data': 'Sem dados disponíveis',
        'error': 'Erro ao processar dados'
    },
    'en': {
        'title': 'Production Dashboard',
        'subtitle': 'Complete and intelligent production data analysis',
        'select_language': 'Language',
        'select_file': 'Select file',
        'select_sheet': 'Select sheet',
        'filters': 'Filters',
        'period_filter': 'Period Filter',
        'select_all': 'Select All',
        'clear_all': 'Clear Selection',
        'product': 'Product',
        'operator': 'Operator',
        'shift': 'Shift',
        'order': 'Order',
        'machine': 'Machine',
        'overview': 'Overview',
        'temporal_analysis': 'Temporal Analysis',
        'comparative_analysis': 'Comparative Analysis',
        'advanced_analysis': 'Advanced Analysis',
        'predictions': 'Predictions',
        'total_production': 'Total Production',
        'total_operators': 'Total Operators',
        'total_machines': 'Total Machines',
        'total_products': 'Total Products',
        'average_production': 'Average Production',
        'efficiency': 'Efficiency',
        'download_filtered': 'Download Filtered Data',
        'daily_production': 'Daily Production',
        'hourly_production': 'Hourly Production',
        'monthly_production': 'Monthly Production',
        'production_by_product': 'Production by Product',
        'production_by_operator': 'Production by Operator',
        'production_by_machine': 'Production by Machine',
        'production_by_shift': 'Production by Shift',
        'correlation_analysis': 'Correlation Analysis',
        'pareto_products': 'Pareto Analysis - Products',
        'pareto_cumulative': 'Cumulative %',
        'production_forecast': 'Production Forecast',
        'forecast_settings': 'Forecast Settings',
        'forecast_days': 'Days to forecast',
        'generate_forecast': 'Generate Forecast',
        'forecast_result': 'Forecast Result',
        'download_file': 'Download File',
        'select_date_range': 'Select Date Range',
        'quick_ranges': 'Quick Ranges',
        'last_7_days': 'Last 7 days',
        'last_30_days': 'Last 30 days',
        'last_90_days': 'Last 90 days',
        'this_month': 'This month',
        'last_month': 'Last month',
        'this_year': 'This year',
        'custom_range': 'Custom range',
        'apply_filters': 'Apply Filters',
        'reset_filters': 'Reset Filters',
        'loading': 'Loading...',
        'no_data': 'No data available',
        'error': 'Error processing data'
    }
}

def t(key):
    return translations[st.session_state.lang].get(key, key)

# Inicializar estado da sessão
if 'lang' not in st.session_state:
    st.session_state.lang = 'pt'

# Header moderno
st.markdown(f"""
<div class="dashboard-header">
    <h1>📊 {t('title')}</h1>
    <p>{t('subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data(file_path, sheet_name=None):
    try:
        if file_path.name.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Conversão de colunas de data
        date_columns = ['Data', 'Date', 'data', 'date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

# Função para aplicar filtro de data
def apply_date_filter(df, date_column, date_range):
    if date_column and date_column in df.columns:
        mask = (df[date_column] >= pd.to_datetime(date_range[0])) & (df[date_column] <= pd.to_datetime(date_range[1]))
        return df.loc[mask]
    return df

# Função para criar gráficos
def create_chart(df, chart_type, x_col, y_col, color_col=None):
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c", "#34495e", "#f1c40f"]
    
    if chart_type == "Linha":
        fig = px.line(df, x=x_col, y=y_col, color=color_col, 
                      color_discrete_sequence=colors,
                      template="plotly_white")
    elif chart_type == "Barra":
        fig = px.bar(df, x=x_col, y=y_col, color=color_col,
                     color_discrete_sequence=colors,
                     template="plotly_white")
    elif chart_type == "Dispersão":
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                        color_discrete_sequence=colors,
                        template="plotly_white")
    elif chart_type == "Pizza":
        fig = px.pie(df, values=y_col, names=x_col,
                     color_discrete_sequence=colors,
                     template="plotly_white")
    elif chart_type == "Área":
        fig = px.area(df, x=x_col, y=y_col, color=color_col,
                      color_discrete_sequence=colors,
                      template="plotly_white")
    elif chart_type == "Box Plot":
        fig = px.box(df, x=x_col, y=y_col, color=color_col,
                     color_discrete_sequence=colors,
                     template="plotly_white")
    elif chart_type == "Histograma":
        fig = px.histogram(df, x=x_col, color=color_col,
                          color_discrete_sequence=colors,
                          template="plotly_white")
    elif chart_type == "Violin":
        fig = px.violin(df, x=x_col, y=y_col, color=color_col,
                       color_discrete_sequence=colors,
                       template="plotly_white")
    else:
        return None
    
    # Estilização do gráfico
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Poppins",
        title_font_size=20,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Poppins"
        )
    )
    
    return fig

# Função para análise estatística
def statistical_analysis(df, column):
    stats = {
        'Média': df[column].mean(),
        'Mediana': df[column].median(),
        'Moda': df[column].mode().iloc[0] if not df[column].mode().empty else None,
        'Desvio Padrão': df[column].std(),
        'Variância': df[column].var(),
        'Mínimo': df[column].min(),
        'Máximo': df[column].max(),
        'Amplitude': df[column].max() - df[column].min(),
        'Coeficiente de Variação': (df[column].std() / df[column].mean()) * 100 if df[column].mean() != 0 else 0,
        'Assimetria': df[column].skew(),
        'Curtose': df[column].kurtosis()
    }
    return stats

# Função para previsão com Prophet
def forecast_prophet(df, date_col, value_col, periods=30):
    prophet_df = df[[date_col, value_col]].copy()
    prophet_df.columns = ['ds', 'y']
    
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )
    
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return model, forecast

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <i class="fas fa-chart-line" style="font-size: 2em; color: #3498db;"></i>
        <h2 style="margin: 10px 0;">Dashboard Avançado</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload de arquivo
    st.markdown("### 📁 Upload de Dados")
    uploaded_file = st.file_uploader(
        "Escolha um arquivo",
        type=['csv', 'xlsx', 'xls'],
        help="Formatos suportados: CSV, Excel"
    )
    
    if uploaded_file:
        # Para arquivos Excel, permite seleção de aba
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_name = st.selectbox(
                "📊 Selecione a aba",
                excel_file.sheet_names,
                help="Escolha qual planilha do Excel você deseja analisar"
            )
            df = load_data(uploaded_file, sheet_name)
        else:
            df = load_data(uploaded_file)
            sheet_name = None
        
        if df is not None:
            st.success(f"✅ Arquivo carregado: {len(df)} linhas")
            
            # Date Range Picker Avançado
            st.markdown("### 📅 Filtro de Data")
            
            # Identificar colunas de data
            date_columns = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            
            if date_columns:
                selected_date_col = st.selectbox(
                    "Selecione a coluna de data",
                    date_columns,
                    help="Escolha qual coluna de data usar para filtrar"
                )
                
                # Presets de data
                date_preset = st.selectbox(
                    "Período rápido",
                    ["Personalizado", "Últimos 7 dias", "Últimos 30 dias", 
                     "Últimos 3 meses", "Últimos 6 meses", "Último ano", 
                     "Este mês", "Mês passado", "Este ano"],
                    help="Selecione um período pré-definido ou escolha datas personalizadas"
                )
                
                # Calcular datas baseado no preset
                today = pd.Timestamp.now().normalize()
                
                if date_preset == "Últimos 7 dias":
                    start_date = today - pd.Timedelta(days=7)
                    end_date = today
                elif date_preset == "Últimos 30 dias":
                    start_date = today - pd.Timedelta(days=30)
                    end_date = today
                elif date_preset == "Últimos 3 meses":
                    start_date = today - pd.DateOffset(months=3)
                    end_date = today
                elif date_preset == "Últimos 6 meses":
                    start_date = today - pd.DateOffset(months=6)
                    end_date = today
                elif date_preset == "Último ano":
                    start_date = today - pd.DateOffset(years=1)
                    end_date = today
                elif date_preset == "Este mês":
                    start_date = today.replace(day=1)
                    end_date = today
                elif date_preset == "Mês passado":
                    first_day_last_month = (today.replace(day=1) - pd.Timedelta(days=1)).replace(day=1)
                    last_day_last_month = today.replace(day=1) - pd.Timedelta(days=1)
                    start_date = first_day_last_month
                    end_date = last_day_last_month
                elif date_preset == "Este ano":
                    start_date = today.replace(month=1, day=1)
                    end_date = today
                else:  # Personalizado
                    min_date = df[selected_date_col].min()
                    max_date = df[selected_date_col].max()
                    start_date = min_date
                    end_date = max_date
                
                # Date range picker
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Data inicial",
                        value=start_date,
                        min_value=df[selected_date_col].min(),
                        max_value=df[selected_date_col].max()
                    )
                with col2:
                    end_date = st.date_input(
                        "Data final",
                        value=end_date,
                        min_value=df[selected_date_col].min(),
                        max_value=df[selected_date_col].max()
                    )
                
                # Aplicar filtro
                date_range = (start_date, end_date)
                df_filtered = apply_date_filter(df, selected_date_col, date_range)
                
                # Mostrar resumo do filtro
                st.info(f"📊 Mostrando {len(df_filtered)} de {len(df)} registros")
            else:
                df_filtered = df
                st.warning("⚠️ Nenhuma coluna de data encontrada")
            
            # Filtros adicionais
            st.markdown("### 🔍 Filtros Adicionais")
            
            # Seleção de colunas para análise
            numeric_columns = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = df_filtered.select_dtypes(include=['object']).columns.tolist()
            
            # Filtros por categoria
            if categorical_columns:
                filter_col = st.selectbox(
                    "Filtrar por categoria",
                    ["Nenhum"] + categorical_columns
                )
                
                if filter_col != "Nenhum":
                    unique_values = df_filtered[filter_col].unique()
                    selected_values = st.multiselect(
                        f"Valores de {filter_col}",
                        unique_values,
                        default=unique_values
                    )
                    df_filtered = df_filtered[df_filtered[filter_col].isin(selected_values)]

# Conteúdo principal
if uploaded_file and df is not None:
    # Header com KPIs
    st.markdown("""
    <div class="main-header">
        <h1>📊 Análise de Dados Avançada</h1>
        <p>Dashboard interativo com análises estatísticas e previsões</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs principais
    if numeric_columns:
        st.markdown("### 📈 Indicadores Principais")
        
        kpi_col = st.selectbox(
            "Selecione a métrica para KPIs",
            numeric_columns
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = df_filtered[kpi_col].sum()
            st.metric(
                label="Total",
                value=f"{total:,.2f}",
                delta=f"{len(df_filtered)} registros"
            )
        
        with col2:
            media = df_filtered[kpi_col].mean()
            st.metric(
                label="Média",
                value=f"{media:,.2f}",
                delta=f"±{df_filtered[kpi_col].std():,.2f}"
            )
        
        with col3:
            maximo = df_filtered[kpi_col].max()
            st.metric(
                label="Máximo",
                value=f"{maximo:,.2f}"
            )
        
        with col4:
            minimo = df_filtered[kpi_col].min()
            st.metric(
                label="Mínimo",
                value=f"{minimo:,.2f}"
            )
    
    # Tabs para diferentes análises
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visualizações", 
        "📈 Análise Estatística", 
        "🔮 Previsões", 
        "📋 Dados", 
        "💾 Download"
    ])
    
    with tab1:
        st.markdown("### 📊 Visualização de Dados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            chart_type = st.selectbox(
                "Tipo de gráfico",
                ["Linha", "Barra", "Dispersão", "Pizza", "Área", "Box Plot", "Histograma", "Violin"]
            )
        
        with col2:
            if chart_type in ["Pizza", "Histograma"]:
                x_axis = st.selectbox("Selecione a coluna", df_filtered.columns)
                y_axis = None
            else:
                x_axis = st.selectbox("Eixo X", df_filtered.columns)
        
        with col3:
            if chart_type not in ["Pizza", "Histograma"]:
                y_axis = st.selectbox("Eixo Y", numeric_columns if numeric_columns else df_filtered.columns)
            
            color_by = st.selectbox(
                "Colorir por (opcional)",
                ["Nenhum"] + categorical_columns
            )
            color_by = None if color_by == "Nenhum" else color_by
        
        # Criar e exibir gráfico
        if st.button("Gerar Visualização", type="primary"):
            with st.spinner("Criando visualização..."):
                fig = create_chart(df_filtered, chart_type, x_axis, y_axis, color_by)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Erro ao criar gráfico")
        
        # Análise de correlação
        if len(numeric_columns) > 1:
            st.markdown("### 🔗 Matriz de Correlação")
            
            if st.checkbox("Mostrar matriz de correlação"):
                corr_matrix = df_filtered[numeric_columns].corr()
                
                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu',
                    zmid=0,
                    text=corr_matrix.values.round(2),
                    texttemplate='%{text}',
                    textfont={"size": 10},
                    hoverongaps=False
                ))
                
                fig_corr.update_layout(
                    title="Matriz de Correlação",
                    height=600,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab2:
        st.markdown("### 📊 Análise Estatística Detalhada")
        
        if numeric_columns:
            selected_col = st.selectbox(
                "Selecione a coluna para análise",
                numeric_columns
            )
            
            # Estatísticas descritivas
            stats = statistical_analysis(df_filtered, selected_col)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Medidas de Tendência Central")
                st.write(f"**Média:** {stats['Média']:.2f}")
                st.write(f"**Mediana:** {stats['Mediana']:.2f}")
                if stats['Moda'] is not None:
                    st.write(f"**Moda:** {stats['Moda']:.2f}")
                
                st.markdown("#### Medidas de Dispersão")
                st.write(f"**Desvio Padrão:** {stats['Desvio Padrão']:.2f}")
                st.write(f"**Variância:** {stats['Variância']:.2f}")
                st.write(f"**Coef. de Variação:** {stats['Coeficiente de Variação']:.2f}%")
            
            with col2:
                st.markdown("#### Medidas de Posição")
                st.write(f"**Mínimo:** {stats['Mínimo']:.2f}")
                st.write(f"**Máximo:** {stats['Máximo']:.2f}")
                st.write(f"**Amplitude:** {stats['Amplitude']:.2f}")
                
                st.markdown("#### Medidas de Forma")
                st.write(f"**Assimetria:** {stats['Assimetria']:.2f}")
                st.write(f"**Curtose:** {stats['Curtose']:.2f}")
            
            # Gráfico de distribuição
            st.markdown("#### Distribuição dos Dados")
            
            fig_dist = go.Figure()
            
            # Histograma
            fig_dist.add_trace(go.Histogram(
                x=df_filtered[selected_col],
                name="Histograma",
                opacity=0.7,
                marker_color='#3498db'
            ))
            
            # Linha de densidade (KDE aproximado)
            from scipy import stats as scipy_stats
            kde_data = scipy_stats.gaussian_kde(df_filtered[selected_col].dropna())
            x_range = np.linspace(df_filtered[selected_col].min(), df_filtered[selected_col].max(), 100)
            
            fig_dist.add_trace(go.Scatter(
                x=x_range,
                y=kde_data(x_range) * len(df_filtered[selected_col]) * (x_range[1] - x_range[0]),
                mode='lines',
                name='Densidade',
                line=dict(color='#e74c3c', width=3),
                yaxis='y2'
            ))
            
            fig_dist.update_layout(
                title=f"Distribuição de {selected_col}",
                xaxis_title=selected_col,
                yaxis_title="Frequência",
                yaxis2=dict(
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                template="plotly_white",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Box plot com outliers
            st.markdown("#### Análise de Outliers")
            
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(
                y=df_filtered[selected_col],
                name=selected_col,
                boxpoints='outliers',
                marker_color='#3498db',
                line_color='#2c3e50'
            ))
            
            fig_box.update_layout(
                title=f"Box Plot - {selected_col}",
                yaxis_title=selected_col,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.markdown("### 🔮 Previsão de Séries Temporais")
        
        if date_columns and numeric_columns:
            col1, col2 = st.columns(2)
            
            with col1:
                date_col_forecast = st.selectbox(
                    "Coluna de data",
                    date_columns
                )
            
            with col2:
                value_col_forecast = st.selectbox(
                    "Coluna de valores",
                    numeric_columns
                )
            
            periods = st.slider(
                "Períodos para previsão (dias)",
                min_value=7,
                max_value=365,
                value=30,
                step=7
            )
            
            if st.button("Gerar Previsão", type="primary"):
                with st.spinner("Gerando previsão..."):
                    try:
                        # Preparar dados
                        forecast_df = df_filtered[[date_col_forecast, value_col_forecast]].copy()
                        forecast_df = forecast_df.dropna()
                        
                        if len(forecast_df) < 10:
                            st.error("Dados insuficientes para previsão (mínimo 10 registros)")
                        else:
                            # Fazer previsão
                            model, forecast = forecast_prophet(
                                forecast_df, 
                                date_col_forecast, 
                                value_col_forecast, 
                                periods
                            )
                            
                            # Criar gráfico
                            fig_forecast = go.Figure()
                            
                            # Dados históricos
                            fig_forecast.add_trace(go.Scatter(
                                x=forecast_df[date_col_forecast],
                                y=forecast_df[value_col_forecast],
                                mode='markers',
                                name='Dados Reais',
                                marker=dict(color='#3498db', size=6)
                            ))
                            
                            # Previsão
                            fig_forecast.add_trace(go.Scatter(
                                x=forecast['ds'],
                                y=forecast['yhat'],
                                mode='lines',
                                name='Previsão',
                                line=dict(color='#e74c3c', width=2)
                            ))
                            
                            # Intervalo de confiança
                            fig_forecast.add_trace(go.Scatter(
                                x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
                                y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
                                fill='toself',
                                fillcolor='rgba(231, 76, 60, 0.2)',
                                line=dict(color='rgba(255,255,255,0)'),
                                name='Intervalo de Confiança',
                                showlegend=True
                            ))
                            
                            fig_forecast.update_layout(
                                title=f"Previsão de {value_col_forecast}",
                                xaxis_title="Data",
                                yaxis_title=value_col_forecast,
                                template="plotly_white",
                                hovermode='x unified'
                            )
                            
                            st.plotly_chart(fig_forecast, use_container_width=True)
                            
                            # Métricas da previsão
                            st.markdown("#### 📊 Métricas da Previsão")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                last_real = forecast_df[value_col_forecast].iloc[-1]
                                st.metric(
                                    "Último Valor Real",
                                    f"{last_real:.2f}"
                                )
                            
                            with col2:
                                last_forecast = forecast['yhat'].iloc[-1]
                                st.metric(
                                    "Última Previsão",
                                    f"{last_forecast:.2f}",
                                    delta=f"{((last_forecast - last_real) / last_real * 100):.1f}%"
                                )
                            
                            with col3:
                                trend = forecast['trend'].iloc[-1] - forecast['trend'].iloc[-periods]
                                st.metric(
                                    "Tendência",
                                    "Crescente" if trend > 0 else "Decrescente",
                                    delta=f"{abs(trend):.2f}"
                                )
                            
                    except Exception as e:
                        st.error(f"Erro ao gerar previsão: {str(e)}")
        else:
            st.warning("⚠️ Selecione colunas de data e valores numéricos para gerar previsões")
    
    with tab4:
        st.markdown("### 📋 Visualização dos Dados")
        
        # Opções de visualização
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_index = st.checkbox("Mostrar índice", value=False)
        
        with col2:
            num_rows = st.number_input(
                "Número de linhas",
                min_value=10,
                max_value=len(df_filtered),
                value=min(100, len(df_filtered))
            )
        
        with col3:
            sort_by = st.selectbox(
                "Ordenar por",
                ["Nenhum"] + list(df_filtered.columns)
            )
        
        # Aplicar ordenação se selecionada
        if sort_by != "Nenhum":
            ascending = st.checkbox("Ordem crescente", value=True)
            df_display = df_filtered.sort_values(by=sort_by, ascending=ascending)
        else:
            df_display = df_filtered
        
        # Exibir dados
        st.dataframe(
            df_display.head(num_rows),
            use_container_width=True,
            hide_index=not show_index
        )
        
        # Informações sobre os dados
        st.markdown("#### 📊 Informações do Dataset")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Total de linhas:** {len(df_filtered)}")
            st.write(f"**Total de colunas:** {len(df_filtered.columns)}")
            st.write(f"**Tamanho em memória:** {df_filtered.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        with col2:
            st.write(f"**Colunas numéricas:** {len(numeric_columns)}")
            st.write(f"**Colunas categóricas:** {len(categorical_columns)}")
            st.write(f"**Valores nulos:** {df_filtered.isnull().sum().sum()}")
    
    with tab5:
        st.markdown("### 💾 Download de Dados e Relatórios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 Dados Filtrados")
            
            # CSV
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f'dados_filtrados_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
            
            # Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_filtered.to_excel(writer, sheet_name='Dados', index=False)
            
            st.download_button(
                label="📥 Download Excel",
                data=buffer.getvalue(),
                file_name=f'dados_filtrados_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        with col2:
            st.markdown("#### 📊 Relatório de Análise")
            
            if st.button("Gerar Relatório PDF", type="primary"):
                st.info("🚧 Funcionalidade em desenvolvimento")
                # Aqui você pode adicionar a geração de PDF com reportlab ou similar
else:
    # Página inicial quando nenhum arquivo foi carregado
    st.markdown("""
    <div class="welcome-container">
        <h1>👋 Bem-vindo ao Dashboard Avançado!</h1>
        <p>Este é um dashboard completo para análise de dados com recursos avançados:</p>
        
        <div class="feature-grid">
            <div class="feature-card">
                <i class="fas fa-calendar-alt" style="font-size: 2em; color: #3498db;"></i>
                <h3>Date Range Picker</h3>
                <p>Filtro avançado de datas com presets customizados</p>
            </div>
            
            <div class="feature-card">
                <i class="fas fa-chart-bar" style="font-size: 2em; color: #e74c3c;"></i>
                <h3>Visualizações Interativas</h3>
                <p>Múltiplos tipos de gráficos com Plotly</p>
            </div>
            
            <div class="feature-card">
                <i class="fas fa-calculator" style="font-size: 2em; color: #2ecc71;"></i>
                <h3>Análise Estatística</h3>
                <p>Estatísticas descritivas completas</p>
            </div>
            
            <div class="feature-card">
                <i class="fas fa-magic" style="font-size: 2em; color: #9b59b6;"></i>
                <h3>Previsões ML</h3>
                <p>Previsão de séries temporais com Prophet</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 40px;">
            <p style="font-size: 1.2em;">👈 Comece fazendo upload de um arquivo na barra lateral</p>
        </div>
    </div>
    
    <style>
    .welcome-container {
        text-align: center;
        padding: 40px;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 40px;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .feature-card h3 {
        margin: 15px 0 10px 0;
    }
    
    .feature-card p {
        margin: 0;
        font-size: 0.9em;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>© 2025 Dashboard Avançado | Desenvolvido por Matheus Martins Lopes usando Streamlit</p>
    <p><small>Versão 2.0.0 | Última atualização: 27/05/2025</small></p>
</div>
""", unsafe_allow_html=True)
