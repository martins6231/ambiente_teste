import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import requests
import tempfile
import zipfile
# from prophet import Prophet  # Comentado
import calendar
from datetime import datetime, date, timedelta
import streamlit_date_picker as date_picker

st.set_page_config(
    page_title="Dashboard de Produção",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado com melhorias de UX/UI
st.markdown("""
<style>
    /* Reset e variáveis CSS */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --background-color: #f0f2f6;
        --text-color: #262730;
        --card-background: #ffffff;
        --shadow: 0 2px 4px rgba(0,0,0,0.1);
        --shadow-hover: 0 4px 8px rgba(0,0,0,0.15);
        --border-radius: 10px;
        --transition: all 0.3s ease;
    }
    
    /* Modo escuro */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --text-color: #fafafa;
            --card-background: #262730;
            --shadow: 0 2px 4px rgba(255,255,255,0.1);
        }
    }
    
    /* Container principal */
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Cards e containers */
    .metric-card {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        transition: var(--transition);
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }
    
    /* Cabeçalho melhorado */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow);
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Métricas estilizadas */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .metric-delta.positive {
        background-color: #d4edda;
        color: #155724;
    }
    
    .metric-delta.negative {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    /* Filtro de data estilizado */
    .date-filter-container {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin-bottom: 2rem;
    }
    
    .date-filter-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        font-weight: 600;
        color: var(--primary-color);
    }
    
    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--card-background);
        padding: 0.5rem;
        border-radius: var(--border-radius);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: var(--transition);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(31, 119, 180, 0.1);
    }
    
    /* Botões melhorados */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 6px;
        font-weight: 600;
        transition: var(--transition);
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        background-color: #1557a0;
        box-shadow: var(--shadow-hover);
        transform: translateY(-1px);
    }
    
    /* Inputs e selectbox */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 6px;
        border: 2px solid #e0e0e0;
        transition: var(--transition);
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }
    
    /* Tabelas estilizadas */
    .dataframe {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow);
    }
    
    /* Footer melhorado */
    .footer {
        background: var(--card-background);
        padding: 2rem;
        text-align: center;
        margin-top: 4rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .dashboard-header h1 {
            font-size: 1.8rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Traduções
translations = {
    'pt': {
        'dashboard_title': 'Dashboard de Produção Avançado',
        'dashboard_subtitle': 'Análise completa e visualização de dados em tempo real',
        'upload_file': 'Carregar arquivo de dados',
        'select_sheet': 'Selecionar planilha',
        'date_filter': '📅 Filtro de Data Avançado',
        'quick_select': 'Seleção Rápida:',
        'last_7_days': 'Últimos 7 dias',
        'last_30_days': 'Últimos 30 dias',
        'last_90_days': 'Últimos 90 dias',
        'this_month': 'Este mês',
        'last_month': 'Mês passado',
        'this_year': 'Este ano',
        'custom_range': 'Período personalizado',
        'apply_filter': 'Aplicar Filtro',
        'clear_filter': 'Limpar Filtro',
        'overview': '📊 Visão Geral',
        'analysis': '📈 Análises',
        'comparisons': '🔄 Comparações',
        'predictions': '🔮 Previsões',
        'export': '💾 Exportar',
        'settings': '⚙️ Configurações',
        'key_metrics': 'Métricas Principais',
        'trend_analysis': 'Análise de Tendências',
        'distribution': 'Distribuição',
        'correlation': 'Correlação',
        'export_pdf': 'Exportar PDF',
        'export_excel': 'Exportar Excel',
        'export_csv': 'Exportar CSV',
        'theme': 'Tema',
        'language': 'Idioma',
        'update_interval': 'Intervalo de Atualização',
        'notifications': 'Notificações',
        'total_production': 'Produção Total',
        'average_efficiency': 'Eficiência Média',
        'active_machines': 'Máquinas Ativas',
        'quality_rate': 'Taxa de Qualidade',
        'no_data': 'Nenhum dado disponível',
        'select_columns': 'Selecionar colunas para análise',
        'download_file': 'Baixar arquivo',
        'generating_report': 'Gerando relatório...',
        'report_generated': 'Relatório gerado com sucesso!',
        'error_loading': 'Erro ao carregar arquivo',
        'welcome': 'Bem-vindo ao Dashboard',
        'features': 'Recursos Disponíveis',
        'real_time': 'Análise em Tempo Real',
        'custom_viz': 'Visualizações Personalizadas',
        'data_export': 'Exportação de Dados',
        'predictive': 'Análise Preditiva'
    },
    'en': {
        'dashboard_title': 'Advanced Production Dashboard',
        'dashboard_subtitle': 'Complete analysis and real-time data visualization',
        'upload_file': 'Upload data file',
        'select_sheet': 'Select worksheet',
        'date_filter': '📅 Advanced Date Filter',
        'quick_select': 'Quick Select:',
        'last_7_days': 'Last 7 days',
        'last_30_days': 'Last 30 days',
        'last_90_days': 'Last 90 days',
        'this_month': 'This month',
        'last_month': 'Last month',
        'this_year': 'This year',
        'custom_range': 'Custom range',
        'apply_filter': 'Apply Filter',
        'clear_filter': 'Clear Filter',
        'overview': '📊 Overview',
        'analysis': '📈 Analysis',
        'comparisons': '🔄 Comparisons',
        'predictions': '🔮 Predictions',
        'export': '💾 Export',
        'settings': '⚙️ Settings',
        'key_metrics': 'Key Metrics',
        'trend_analysis': 'Trend Analysis',
        'distribution': 'Distribution',
        'correlation': 'Correlation',
        'export_pdf': 'Export PDF',
        'export_excel': 'Export Excel',
        'export_csv': 'Export CSV',
        'theme': 'Theme',
        'language': 'Language',
        'update_interval': 'Update Interval',
        'notifications': 'Notifications',
        'total_production': 'Total Production',
        'average_efficiency': 'Average Efficiency',
        'active_machines': 'Active Machines',
        'quality_rate': 'Quality Rate',
        'no_data': 'No data available',
        'select_columns': 'Select columns for analysis',
        'download_file': 'Download file',
        'generating_report': 'Generating report...',
        'report_generated': 'Report generated successfully!',
        'error_loading': 'Error loading file',
        'welcome': 'Welcome to Dashboard',
        'features': 'Available Features',
        'real_time': 'Real-time Analysis',
        'custom_viz': 'Custom Visualizations',
        'data_export': 'Data Export',
        'predictive': 'Predictive Analysis'
    }
}

# Estado da sessão
if 'language' not in st.session_state:
    st.session_state.language = 'pt'
if 'df' not in st.session_state:
    st.session_state.df = None
if 'date_filter_applied' not in st.session_state:
    st.session_state.date_filter_applied = False
if 'start_date' not in st.session_state:
    st.session_state.start_date = None
if 'end_date' not in st.session_state:
    st.session_state.end_date = None

def t(key):
    return translations[st.session_state.language].get(key, key)

# Função para carregar dados
@st.cache_data
def load_data(file_path, sheet_name=None):
    try:
        if file_path.name.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Conversão de colunas de data
        date_columns = ['Data', 'Date', 'data', 'date', 'DATE', 'DATA']
        for col in df.columns:
            if any(date_col in col for date_col in date_columns):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        return df
    except Exception as e:
        st.error(f"{t('error_loading')}: {str(e)}")
        return None

# Função para aplicar filtro de data
def apply_date_filter(df, date_column, start_date, end_date):
    if date_column in df.columns:
        mask = (df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))
        return df.loc[mask]
    return df

# Função para criar métricas
def create_metric_card(label, value, delta=None, delta_color="normal"):
    delta_class = "positive" if delta_color == "normal" and delta and delta > 0 else "negative" if delta and delta < 0 else ""
    delta_symbol = "↑" if delta and delta > 0 else "↓" if delta and delta < 0 else ""
    
    return f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-delta {delta_class}">{delta_symbol} {abs(delta):.1f}%</div>' if delta is not None else ''}
    </div>
    """

# Cabeçalho
st.markdown(f"""
<div class="dashboard-header">
    <h1>{t('dashboard_title')}</h1>
    <p>{t('dashboard_subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📁 " + t('upload_file'))
    uploaded_file = st.file_uploader(
        "",
        type=['csv', 'xlsx', 'xls'],
        help="Arraste ou selecione um arquivo CSV ou Excel"
    )
    
    if uploaded_file:
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            xl_file = pd.ExcelFile(uploaded_file)
            sheet_name = st.selectbox(t('select_sheet'), xl_file.sheet_names)
            df = load_data(uploaded_file, sheet_name)
        else:
            df = load_data(uploaded_file)
        
        if df is not None:
            st.session_state.df = df
            st.success(f"✅ Arquivo carregado: {len(df)} registros")
    
    # Configurações
    st.markdown("### ⚙️ Configurações")
    st.session_state.language = st.selectbox(
        t('language'),
        options=['pt', 'en'],
        format_func=lambda x: 'Português' if x == 'pt' else 'English'
    )

# Conteúdo principal
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Date Range Picker Avançado
    date_columns = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
    
    if date_columns:
        with st.container():
            st.markdown(f"""
            <div class="date-filter-container">
                <div class="date-filter-header">
                    {t('date_filter')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                selected_date_col = st.selectbox(
                    "Coluna de data",
                    date_columns,
                    key="date_column_selector"
                )
            
            with col2:
                # Seleção rápida
                quick_select = st.selectbox(
                    t('quick_select'),
                    [t('custom_range'), t('last_7_days'), t('last_30_days'), 
                     t('last_90_days'), t('this_month'), t('last_month'), t('this_year')]
                )
                
                # Calcular datas baseado na seleção
                today = datetime.now().date()
                
                if quick_select == t('last_7_days'):
                    default_start = today - timedelta(days=7)
                    default_end = today
                elif quick_select == t('last_30_days'):
                    default_start = today - timedelta(days=30)
                    default_end = today
                elif quick_select == t('last_90_days'):
                    default_start = today - timedelta(days=90)
                    default_end = today
                elif quick_select == t('this_month'):
                    default_start = today.replace(day=1)
                    default_end = today
                elif quick_select == t('last_month'):
                    first_day_current = today.replace(day=1)
                    default_end = first_day_current - timedelta(days=1)
                    default_start = default_end.replace(day=1)
                elif quick_select == t('this_year'):
                    default_start = today.replace(month=1, day=1)
                    default_end = today
                else:  # custom_range
                    default_start = df[selected_date_col].min().date() if not pd.isna(df[selected_date_col].min()) else today - timedelta(days=30)
                    default_end = df[selected_date_col].max().date() if not pd.isna(df[selected_date_col].max()) else today
            
            with col3:
                col3_1, col3_2 = st.columns(2)
                with col3_1:
                    if st.button(t('apply_filter'), type="primary", use_container_width=True):
                        st.session_state.date_filter_applied = True
                        st.session_state.start_date = default_start
                        st.session_state.end_date = default_end
                
                with col3_2:
                    if st.button(t('clear_filter'), use_container_width=True):
                        st.session_state.date_filter_applied = False
                        st.session_state.start_date = None
                        st.session_state.end_date = None
            
            # Seletor de datas customizado
            if quick_select == t('custom_range'):
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Data inicial",
                        value=default_start,
                        max_value=default_end
                    )
                with col2:
                    end_date = st.date_input(
                        "Data final",
                        value=default_end,
                        min_value=default_start
                    )
                
                if start_date and end_date:
                    default_start = start_date
                    default_end = end_date
    
    # Aplicar filtro se necessário
    if st.session_state.date_filter_applied and date_columns:
        df_filtered = apply_date_filter(
            df, 
            selected_date_col, 
            st.session_state.start_date, 
            st.session_state.end_date
        )
        st.info(f"🔍 Filtro aplicado: {st.session_state.start_date} até {st.session_state.end_date} ({len(df_filtered)} registros)")
    else:
        df_filtered = df
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t('overview'), t('analysis'), t('comparisons'), 
        t('predictions'), t('export')
    ])
    
    with tab1:
        st.markdown(f"### {t('key_metrics')}")
        
        # Calcular métricas
        numeric_columns = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_columns:
            col1, col2, col3, col4 = st.columns(4)
            
            # Métricas exemplo (adaptar conforme dados reais)
            with col1:
                if len(numeric_columns) > 0:
                    total = df_filtered[numeric_columns[0]].sum()
                    st.markdown(create_metric_card(
                        t('total_production'),
                        f"{total:,.0f}",
                        delta=5.2
                    ), unsafe_allow_html=True)
            
            with col2:
                if len(numeric_columns) > 0:
                    avg = df_filtered[numeric_columns[0]].mean()
                    st.markdown(create_metric_card(
                        t('average_efficiency'),
                        f"{avg:.1f}%",
                        delta=-2.1
                    ), unsafe_allow_html=True)
            
            with col3:
                st.markdown(create_metric_card(
                    t('active_machines'),
                    f"{len(df_filtered)}",
                    delta=0
                ), unsafe_allow_html=True)
            
            with col4:
                quality = np.random.uniform(94, 99)
                st.markdown(create_metric_card(
                    t('quality_rate'),
                    f"{quality:.1f}%",
                    delta=1.8
                ), unsafe_allow_html=True)
        
        # Gráficos principais
        st.markdown(f"### {t('trend_analysis')}")
        
        if date_columns and numeric_columns:
            # Gráfico de linha temporal
            fig_line = px.line(
                df_filtered,
                x=date_columns[0],
                y=numeric_columns[0] if numeric_columns else None,
                title=f"{numeric_columns[0]} ao longo do tempo",
                template="plotly_white"
            )
            fig_line.update_layout(
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Distribuição
        col1, col2 = st.columns(2)
        
        with col1:
            if numeric_columns:
                fig_hist = px.histogram(
                    df_filtered,
                    x=numeric_columns[0],
                    title=f"Distribuição de {numeric_columns[0]}",
                    template="plotly_white",
                    color_discrete_sequence=['#1f77b4']
                )
                st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            if len(numeric_columns) > 1:
                fig_scatter = px.scatter(
                    df_filtered,
                    x=numeric_columns[0],
                    y=numeric_columns[1],
                    title=f"{numeric_columns[0]} vs {numeric_columns[1]}",
                    template="plotly_white",
                    trendline="ols"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab2:
        st.markdown(f"### {t('analysis')}")
        
        # Seleção de colunas para análise
        selected_columns = st.multiselect(
            t('select_columns'),
            options=numeric_columns,
            default=numeric_columns[:3] if len(numeric_columns) >= 3 else numeric_columns
        )
        
        if selected_columns:
            # Estatísticas descritivas
            st.markdown("#### 📊 Estatísticas Descritivas")
            stats_df = df_filtered[selected_columns].describe()
            st.dataframe(
                stats_df.style.format("{:.2f}").background_gradient(cmap='Blues'),
                use_container_width=True
            )
            
            # Matriz de correlação
            if len(selected_columns) > 1:
                st.markdown("#### 🔗 Matriz de Correlação")
                corr_matrix = df_filtered[selected_columns].corr()
                
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale='RdBu_r',
                    title="Correlação entre variáveis"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            
            # Box plots
            st.markdown("#### 📦 Análise de Outliers")
            fig_box = go.Figure()
            for col in selected_columns:
                fig_box.add_trace(go.Box(
                    y=df_filtered[col],
                    name=col,
                    boxpoints='outliers'
                ))
            fig_box.update_layout(
                title="Box Plot - Identificação de Outliers",
                showlegend=True,
                template="plotly_white"
            )
            st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.markdown(f"### {t('comparisons')}")
        
        # Comparação temporal
        if date_columns:
            st.markdown("#### 📅 Comparação Temporal")
            
            # Agrupar por período
            period_type = st.radio(
                "Agrupar por:",
                ["Dia", "Semana", "Mês", "Trimestre", "Ano"],
                horizontal=True
            )
            
            period_map = {
                "Dia": "D",
                "Semana": "W",
                "Mês": "M",
                "Trimestre": "Q",
                "Ano": "Y"
            }
            
            if numeric_columns:
                df_period = df_filtered.set_index(date_columns[0]).resample(period_map[period_type])[numeric_columns[0]].agg(['sum', 'mean', 'count'])
                
                fig_comparison = go.Figure()
                fig_comparison.add_trace(go.Bar(
                    x=df_period.index,
                    y=df_period['sum'],
                    name='Total',
                    yaxis='y'
                ))
                fig_comparison.add_trace(go.Scatter(
                    x=df_period.index,
                    y=df_period['mean'],
                    name='Média',
                    yaxis='y2',
                    line=dict(color='red', width=3)
                ))
                
                fig_comparison.update_layout(
                    title=f"Comparação por {period_type}",
                    yaxis=dict(title="Total", side="left"),
                    yaxis2=dict(title="Média", overlaying="y", side="right"),
                    hovermode='x unified',
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Comparação de categorias
        categorical_columns = df_filtered.select_dtypes(include=['object']).columns.tolist()
        if categorical_columns and numeric_columns:
            st.markdown("#### 🏷️ Comparação por Categoria")
            
            cat_col = st.selectbox("Selecione a categoria:", categorical_columns)
            num_col = st.selectbox("Selecione a métrica:", numeric_columns)
            
            df_grouped = df_filtered.groupby(cat_col)[num_col].agg(['sum', 'mean', 'count']).reset_index()
            
            fig_cat = px.bar(
                df_grouped,
                x=cat_col,
                y='sum',
                title=f"Total de {num_col} por {cat_col}",
                template="plotly_white",
                text='sum'
            )
            fig_cat.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            st.plotly_chart(fig_cat, use_container_width=True)
    
    with tab4:
        st.markdown(f"### {t('predictions')}")
        
        # Análise de tendência simples (sem Prophet)
        if date_columns and numeric_columns:
            st.markdown("#### 📈 Análise de Tendência")
            
            # Preparar dados
            trend_data = df_filtered[[date_columns[0], numeric_columns[0]]].copy()
            trend_data = trend_data.sort_values(date_columns[0])
            trend_data = trend_data.set_index(date_columns[0])
            
            # Calcular média móvel
            window_size = st.slider("Período da média móvel (dias):", 7, 90, 30)
            trend_data['MA'] = trend_data[numeric_columns[0]].rolling(window=window_size).mean()
            
            # Calcular tendência linear
            from sklearn.linear_model import LinearRegression
            trend_data['days'] = (trend_data.index - trend_data.index[0]).days
            
            # Remover NaN para regressão
            clean_data = trend_data.dropna()
            if len(clean_data) > 1:
                X = clean_data[['days']]
                y = clean_data[numeric_columns[0]]
                
                model = LinearRegression()
                model.fit(X, y)
                trend_data['trend'] = model.predict(trend_data[['days']])
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend_data.index,
                    y=trend_data[numeric_columns[0]],
                    mode='lines',
                    name='Valores Reais',
                    line=dict(color='#1f77b4')
                ))
                fig.add_trace(go.Scatter(
                    x=trend_data.index,
                    y=trend_data['trend'],
                    mode='lines',
                    name='Tendência',
                    line=dict(color='#ff7f0e', dash='dash')
                ))
                
                fig.update_layout(
                    title='Análise de Tendência Temporal',
                    xaxis_title='Data',
                    yaxis_title='Valor',
                    template='plotly_white',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Estatísticas da tendência
                slope = model.coef_[0]
                if slope > 0:
                    st.success(f"📈 Tendência de crescimento: +{slope:.2f} por dia")
                else:
                    st.warning(f"📉 Tendência de queda: {slope:.2f} por dia")

# Página de Análise Preditiva
elif page == t("predictive_analysis"):
    st.title(f"🔮 {t('predictive_analysis')}")
    
    if df is not None:
        st.info("💡 Análise preditiva simplificada usando regressão linear")
        
        # Seleção de variáveis
        col1, col2 = st.columns(2)
        
        with col1:
            target_col = st.selectbox(
                "Variável alvo (Y)",
                numeric_columns,
                help="Variável que você deseja prever"
            )
        
        with col2:
            feature_cols = st.multiselect(
                "Variáveis preditoras (X)",
                [col for col in numeric_columns if col != target_col],
                help="Variáveis usadas para fazer a previsão"
            )
        
        if feature_cols and target_col:
            # Preparar dados
            X = df[feature_cols].dropna()
            y = df[target_col].dropna()
            
            # Alinhar índices
            common_idx = X.index.intersection(y.index)
            X = X.loc[common_idx]
            y = y.loc[common_idx]
            
            if len(X) > 10:
                # Dividir dados
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = y[:split_idx], y[split_idx:]
                
                # Treinar modelo
                model = LinearRegression()
                model.fit(X_train, y_train)
                
                # Fazer previsões
                y_pred = model.predict(X_test)
                
                # Visualizar resultados
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=y_test,
                    y=y_pred,
                    mode='markers',
                    name='Previsões',
                    marker=dict(
                        size=8,
                        color='#1f77b4',
                        line=dict(width=1, color='white')
                    )
                ))
                
                # Linha de referência perfeita
                min_val = min(y_test.min(), y_pred.min())
                max_val = max(y_test.max(), y_pred.max())
                fig.add_trace(go.Scatter(
                    x=[min_val, max_val],
                    y=[min_val, max_val],
                    mode='lines',
                    name='Previsão Perfeita',
                    line=dict(color='red', dash='dash')
                ))
                
                fig.update_layout(
                    title='Valores Reais vs Previstos',
                    xaxis_title='Valores Reais',
                    yaxis_title='Valores Previstos',
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Métricas do modelo
                from sklearn.metrics import r2_score, mean_absolute_error
                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("R² Score", f"{r2:.3f}")
                with col2:
                    st.metric("Erro Médio Absoluto", f"{mae:.2f}")
                with col3:
                    st.metric("Amostras de Teste", len(y_test))
                
                # Importância das variáveis
                st.subheader("📊 Importância das Variáveis")
                importance_df = pd.DataFrame({
                    'Variável': feature_cols,
                    'Coeficiente': model.coef_
                }).sort_values('Coeficiente', key=abs, ascending=False)
                
                fig_imp = px.bar(
                    importance_df,
                    x='Coeficiente',
                    y='Variável',
                    orientation='h',
                    title='Coeficientes do Modelo',
                    color='Coeficiente',
                    color_continuous_scale='RdBu_r'
                )
                st.plotly_chart(fig_imp, use_container_width=True)
                
                # Previsão manual
                st.subheader("🎯 Fazer Nova Previsão")
                with st.form("prediction_form"):
                    input_values = {}
                    cols = st.columns(len(feature_cols))
                    
                    for i, col in enumerate(feature_cols):
                        with cols[i]:
                            input_values[col] = st.number_input(
                                col,
                                value=float(X[col].mean()),
                                help=f"Média: {X[col].mean():.2f}"
                            )
                    
                    if st.form_submit_button("Prever", type="primary"):
                        input_df = pd.DataFrame([input_values])
                        prediction = model.predict(input_df)[0]
                        st.success(f"**Previsão para {target_col}: {prediction:.2f}**")

# Página de Comparação
elif page == t("comparison"):
    st.title(f"🔄 {t('comparison')}")
    
    if df is not None:
        st.info("Compare diferentes categorias ou períodos de tempo")
        
        # Tipo de comparação
        comp_type = st.radio(
            "Tipo de Comparação",
            ["Por Categoria", "Por Período"],
            horizontal=True
        )
        
        if comp_type == "Por Categoria":
            # Seleção de categoria
            cat_columns = df.select_dtypes(include=['object']).columns.tolist()
            if cat_columns:
                cat_col = st.selectbox("Selecione a categoria", cat_columns)
                
                # Seleção de métrica
                metric_col = st.selectbox("Selecione a métrica", numeric_columns)
                
                # Agregação
                agg_func = st.selectbox(
                    "Função de agregação",
                    ["Soma", "Média", "Mediana", "Máximo", "Mínimo"]
                )
                
                agg_map = {
                    "Soma": "sum",
                    "Média": "mean",
                    "Mediana": "median",
                    "Máximo": "max",
                    "Mínimo": "min"
                }
                
                # Calcular agregação
                comparison_df = df.groupby(cat_col)[metric_col].agg(agg_map[agg_func]).reset_index()
                comparison_df = comparison_df.sort_values(metric_col, ascending=False)
                
                # Visualização
                fig = px.bar(
                    comparison_df,
                    x=cat_col,
                    y=metric_col,
                    title=f"{agg_func} de {metric_col} por {cat_col}",
                    color=metric_col,
                    color_continuous_scale='Viridis',
                    text=metric_col
                )
                
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_layout(
                    xaxis_tickangle=-45,
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela resumo
                st.subheader("📊 Resumo Estatístico")
                st.dataframe(
                    comparison_df.style.highlight_max(subset=[metric_col], color='lightgreen')
                    .highlight_min(subset=[metric_col], color='lightcoral'),
                    use_container_width=True
                )
                
        else:  # Por Período
            if date_columns:
                date_col = date_columns[0]
                
                # Seleção de métrica
                metric_col = st.selectbox("Selecione a métrica", numeric_columns)
                
                # Granularidade temporal
                granularity = st.selectbox(
                    "Granularidade",
                    ["Diário", "Semanal", "Mensal", "Trimestral", "Anual"]
                )
                
                # Preparar dados temporais
                temp_df = df[[date_col, metric_col]].copy()
                temp_df[date_col] = pd.to_datetime(temp_df[date_col])
                temp_df = temp_df.set_index(date_col)
                
                # Resample baseado na granularidade
                resample_map = {
                    "Diário": "D",
                    "Semanal": "W",
                    "Mensal": "M",
                    "Trimestral": "Q",
                    "Anual": "Y"
                }
                
                resampled = temp_df.resample(resample_map[granularity]).agg({
                    metric_col: ['sum', 'mean', 'count']
                })
                
                # Visualização
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=resampled.index,
                    y=resampled[(metric_col, 'sum')],
                    name='Soma',
                    marker_color='lightblue'
                ))
                
                fig.add_trace(go.Scatter(
                    x=resampled.index,
                    y=resampled[(metric_col, 'mean')],
                    name='Média',
                    mode='lines+markers',
                    yaxis='y2',
                    line=dict(color='red', width=2)
                ))
                
                fig.update_layout(
                    title=f'Análise {granularity} de {metric_col}',
                    xaxis_title='Período',
                    yaxis_title='Soma',
                    yaxis2=dict(
                        title='Média',
                        overlaying='y',
                        side='right'
                    ),
                    hovermode='x unified',
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Análise de variação
                st.subheader("📈 Análise de Variação")
                resampled['variacao_pct'] = resampled[(metric_col, 'sum')].pct_change() * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    maior_aumento = resampled['variacao_pct'].max()
                    st.metric("Maior Aumento", f"{maior_aumento:.1f}%")
                with col2:
                    maior_queda = resampled['variacao_pct'].min()
                    st.metric("Maior Queda", f"{maior_queda:.1f}%")
                with col3:
                    variacao_media = resampled['variacao_pct'].mean()
                    st.metric("Variação Média", f"{variacao_media:.1f}%")

# Página de Exportação
elif page == t("export"):
    st.title(f"💾 {t('export')}")
    
    if df is not None:
        st.info("Exporte seus dados e análises em diferentes formatos")
        
        # Opções de exportação
        export_type = st.selectbox(
            "O que você deseja exportar?",
            ["Dados Completos", "Dados Filtrados", "Relatório de Análise"]
        )
        
        if export_type == "Dados Completos":
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name="dados_completos.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Dados', index=False)
                buffer.seek(0)
                
                st.download_button(
                    label="📊 Download Excel",
                    data=buffer,
                    file_name="dados_completos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        elif export_type == "Dados Filtrados":
            # Aplicar filtros antes de exportar
            st.subheader("Aplicar Filtros")
            
            # Filtros de colunas
            selected_cols = st.multiselect(
                "Selecione as colunas",
                df.columns.tolist(),
                default=df.columns.tolist()
            )
            
            filtered_df = df[selected_cols]
            
            # Preview
            st.subheader("Preview dos Dados")
            st.dataframe(filtered_df.head(10), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV Filtrado",
                    data=csv,
                    file_name="dados_filtrados.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    filtered_df.to_excel(writer, sheet_name='Dados Filtrados', index=False)
                buffer.seek(0)
                
                st.download_button(
                    label="📊 Download Excel Filtrado",
                    data=buffer,
                    file_name="dados_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Rodapé
st.markdown("""
<div class="footer">
    <p>© 2025 Dashboard Produção | Desenvolvido por Matheus Martins Lopes</p>
    <p><small>Versão 2.0.0 | Última atualização: Maio 2025</small></p>
</div>
""", unsafe_allow_html=True)
