import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import locale
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Configurações da página com design moderno
st.set_page_config(
    page_title="Dashboard de Produção - Britvic",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar UX/UI
st.markdown("""
    <style>
    /* Tema principal com cores modernas */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
        --background-color: #f0f2f6;
        --card-background: #ffffff;
        --text-color: #262730;
        --border-radius: 10px;
        --box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Container principal com margem e padding otimizados */
    .main {
        padding: 1rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Cards modernos com sombra suave */
    .stMetric {
        background-color: var(--card-background);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background-color: #f8f9fa;
        padding: 2rem 1rem;
    }
    
    /* Headers com estilo consistente */
    h1, h2, h3 {
        color: var(--text-color);
        font-weight: 600;
    }
    
    /* Botões estilizados */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1557a0;
        transform: translateY(-1px);
    }
    
    /* Date Range Picker customizado */
    .date-range-container {
        background-color: var(--card-background);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
        box-shadow: var(--box-shadow);
    }
    
    /* Tabs estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--background-color);
        padding: 0.5rem;
        border-radius: var(--border-radius);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: white;
        border-radius: 5px;
        color: var(--text-color);
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Métricas responsivas */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        .stMetric {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Configuração de localização
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        pass

# Estado da sessão para controle de idioma
if 'language' not in st.session_state:
    st.session_state.language = 'pt'

# Dicionário de traduções aprimorado
translations = {
    'pt': {
        'title': '🏭 Dashboard de Produção',
        'subtitle': 'Monitoramento e Análise em Tempo Real',
        'filters': '🔍 Filtros',
        'date_range': '📅 Período de Análise',
        'quick_ranges': 'Períodos Rápidos:',
        'last_7_days': 'Últimos 7 dias',
        'last_30_days': 'Últimos 30 dias',
        'last_90_days': 'Últimos 90 dias',
        'current_month': 'Mês atual',
        'current_year': 'Ano atual',
        'custom_range': 'Período personalizado',
        'start_date': 'Data inicial',
        'end_date': 'Data final',
        'line': 'Linha de Produção',
        'shift': 'Turno',
        'product': 'Produto',
        'all': 'Todos',
        'overview': '📊 Visão Geral',
        'efficiency': '⚡ Eficiência',
        'quality': '✅ Qualidade',
        'predictions': '🔮 Previsões',
        'total_production': 'Produção Total',
        'average_efficiency': 'Eficiência Média',
        'quality_rate': 'Taxa de Qualidade',
        'units_produced': 'Unidades Produzidas',
        'production_trend': 'Tendência de Produção',
        'efficiency_by_line': 'Eficiência por Linha',
        'daily_production': 'Produção Diária',
        'quality_analysis': 'Análise de Qualidade',
        'defects_by_type': 'Defeitos por Tipo',
        'quality_trend': 'Tendência de Qualidade',
        'predictive_model': 'Modelo Preditivo',
        'model_accuracy': 'Precisão do Modelo',
        'mae': 'Erro Médio Absoluto',
        'r2': 'R² Score',
        'predicted_vs_actual': 'Previsto vs Real',
        'insights': '💡 Insights Automáticos',
        'top_insights': 'Principais Descobertas',
        'download_report': '📥 Baixar Relatório',
        'generating_report': 'Gerando relatório...',
        'report_generated': 'Relatório gerado com sucesso!',
        'morning': 'Manhã',
        'afternoon': 'Tarde',
        'night': 'Noite'
    },
    'en': {
        'title': '🏭 Production Dashboard',
        'subtitle': 'Real-time Monitoring and Analysis',
        'filters': '🔍 Filters',
        'date_range': '📅 Analysis Period',
        'quick_ranges': 'Quick Ranges:',
        'last_7_days': 'Last 7 days',
        'last_30_days': 'Last 30 days',
        'last_90_days': 'Last 90 days',
        'current_month': 'Current month',
        'current_year': 'Current year',
        'custom_range': 'Custom range',
        'start_date': 'Start date',
        'end_date': 'End date',
        'line': 'Production Line',
        'shift': 'Shift',
        'product': 'Product',
        'all': 'All',
        'overview': '📊 Overview',
        'efficiency': '⚡ Efficiency',
        'quality': '✅ Quality',
        'predictions': '🔮 Predictions',
        'total_production': 'Total Production',
        'average_efficiency': 'Average Efficiency',
        'quality_rate': 'Quality Rate',
        'units_produced': 'Units Produced',
        'production_trend': 'Production Trend',
        'efficiency_by_line': 'Efficiency by Line',
        'daily_production': 'Daily Production',
        'quality_analysis': 'Quality Analysis',
        'defects_by_type': 'Defects by Type',
        'quality_trend': 'Quality Trend',
        'predictive_model': 'Predictive Model',
        'model_accuracy': 'Model Accuracy',
        'mae': 'Mean Absolute Error',
        'r2': 'R² Score',
        'predicted_vs_actual': 'Predicted vs Actual',
        'insights': '💡 Automatic Insights',
        'top_insights': 'Key Findings',
        'download_report': '📥 Download Report',
        'generating_report': 'Generating report...',
        'report_generated': 'Report generated successfully!',
        'morning': 'Morning',
        'afternoon': 'Afternoon',
        'night': 'Night'
    }
}

def t(key):
    """Função de tradução"""
    return translations[st.session_state.language].get(key, key)

@st.cache_data
def generate_sample_data():
    """Gera dados de exemplo para o dashboard"""
    np.random.seed(42)
    
    # Datas dos últimos 365 dias
    dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
    
    # Configuração dos dados
    lines = ['Linha A', 'Linha B', 'Linha C', 'Linha D']
    products = ['Produto 1', 'Produto 2', 'Produto 3', 'Produto 4', 'Produto 5']
    shifts = ['morning', 'afternoon', 'night']
    
    data = []
    
    for date in dates:
        for line in lines:
            for shift in shifts:
                # Produção base com sazonalidade
                base_production = 1000 + np.sin(date.dayofyear * 2 * np.pi / 365) * 200
                
                # Variação por linha
                line_factor = {'Linha A': 1.2, 'Linha B': 1.0, 'Linha C': 0.9, 'Linha D': 1.1}[line]
                
                # Variação por turno
                shift_factor = {'morning': 0.9, 'afternoon': 1.0, 'night': 0.8}[shift]
                
                production = int(base_production * line_factor * shift_factor + np.random.normal(0, 100))
                production = max(0, production)
                
                # Eficiência (com tendência positiva ao longo do tempo)
                base_efficiency = 75 + (date - dates[0]).days / 365 * 5
                efficiency = min(100, max(0, base_efficiency + np.random.normal(0, 5)))
                
                # Qualidade
                quality = min(100, max(0, 95 + np.random.normal(0, 2)))
                
                # Defeitos
                defects = max(0, int(production * (100 - quality) / 100))
                
                data.append({
                    'date': date,
                    'production_line': line,
                    'shift': shift,
                    'product': np.random.choice(products),
                    'units_produced': production,
                    'efficiency': efficiency,
                    'quality_rate': quality,
                    'defects': defects,
                    'downtime_minutes': max(0, int(np.random.exponential(10))),
                    'energy_consumption': production * 0.5 + np.random.normal(0, 50)
                })
    
    return pd.DataFrame(data)

# NOVA FUNÇÃO: Date Range Picker aprimorado
def render_date_range_picker(df):
    """
    Renderiza um seletor de intervalo de datas moderno e intuitivo
    Retorna as datas selecionadas
    """
    with st.container():
        st.markdown(f"### {t('date_range')}")
        
        # Container estilizado para o date picker
        st.markdown('<div class="date-range-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Seleção rápida de períodos
            st.markdown(f"**{t('quick_ranges')}**")
            
            quick_range = st.radio(
                "",
                options=['last_7_days', 'last_30_days', 'last_90_days', 
                        'current_month', 'current_year', 'custom_range'],
                format_func=lambda x: t(x),
                key='quick_range_selector',
                label_visibility="collapsed"
            )
            
        with col2:
            # Cálculo automático de datas baseado na seleção rápida
            today = datetime.now().date()
            
            if quick_range == 'last_7_days':
                default_start = today - timedelta(days=7)
                default_end = today
            elif quick_range == 'last_30_days':
                default_start = today - timedelta(days=30)
                default_end = today
            elif quick_range == 'last_90_days':
                default_start = today - timedelta(days=90)
                default_end = today
            elif quick_range == 'current_month':
                default_start = today.replace(day=1)
                default_end = today
            elif quick_range == 'current_year':
                default_start = today.replace(month=1, day=1)
                default_end = today
            else:  # custom_range
                default_start = df['date'].min().date()
                default_end = df['date'].max().date()
            
            # Seletores de data com validação
            col_start, col_end = st.columns(2)
            
            with col_start:
                start_date = st.date_input(
                    t('start_date'),
                    value=default_start,
                    min_value=df['date'].min().date(),
                    max_value=df['date'].max().date(),
                    key='start_date_picker',
                    disabled=(quick_range != 'custom_range')
                )
            
            with col_end:
                end_date = st.date_input(
                    t('end_date'),
                    value=default_end,
                    min_value=df['date'].min().date(),
                    max_value=df['date'].max().date(),
                    key='end_date_picker',
                    disabled=(quick_range != 'custom_range')
                )
            
            # Validação de intervalo
            if start_date > end_date:
                st.error("⚠️ A data inicial deve ser anterior à data final!")
                start_date, end_date = end_date, start_date
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mostrar período selecionado
        days_selected = (end_date - start_date).days + 1
        st.info(f"📅 Período selecionado: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')} ({days_selected} dias)")
        
    return pd.Timestamp(start_date), pd.Timestamp(end_date)

def generate_insights(df_filtered):
    """Gera insights automáticos baseados nos dados filtrados"""
    insights = []
    
    # Insight 1: Linha mais eficiente
    efficiency_by_line = df_filtered.groupby('production_line')['efficiency'].mean()
    best_line = efficiency_by_line.idxmax()
    best_efficiency = efficiency_by_line.max()
    insights.append(f"🏆 {best_line} é a linha mais eficiente com {best_efficiency:.1f}% de eficiência média")
    
    # Insight 2: Tendência de produção
    daily_production = df_filtered.groupby('date')['units_produced'].sum()
    if len(daily_production) > 1:
        trend = (daily_production.iloc[-1] - daily_production.iloc[0]) / daily_production.iloc[0] * 100
        trend_text = "aumentou" if trend > 0 else "diminuiu"
        insights.append(f"📈 A produção {trend_text} {abs(trend):.1f}% no período selecionado")
    
    # Insight 3: Melhor turno
    production_by_shift = df_filtered.groupby('shift')['units_produced'].sum()
    best_shift = production_by_shift.idxmax()
    shift_names = {'morning': t('morning'), 'afternoon': t('afternoon'), 'night': t('night')}
    insights.append(f"⏰ O turno da {shift_names.get(best_shift, best_shift)} produz mais unidades")
    
    # Insight 4: Taxa de defeitos
    defect_rate = (df_filtered['defects'].sum() / df_filtered['units_produced'].sum() * 100)
    insights.append(f"🔧 Taxa média de defeitos: {defect_rate:.2f}%")
    
    return insights

def main():
    """Função principal do dashboard"""
    # Header com seletor de idioma
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title(t('title'))
        st.markdown(f"*{t('subtitle')}*")
    with col2:
        lang = st.selectbox(
            "🌐",
            options=['pt', 'en'],
            format_func=lambda x: '🇧🇷 PT' if x == 'pt' else '🇺🇸 EN',
            key='language_selector',
            label_visibility="collapsed"
        )
        st.session_state.language = lang
    
    # Carrega dados
    df = generate_sample_data()
    
    # Sidebar com filtros
    with st.sidebar:
        st.header(t('filters'))
        
        # NOVO: Date Range Picker integrado
        start_date, end_date = render_date_range_picker(df)
        
        st.markdown("---")
        
        # Outros filtros existentes com design aprimorado
        selected_lines = st.multiselect(
            t('line'),
            options=df['production_line'].unique(),
            default=df['production_line'].unique(),
            key='line_filter'
        )
        
        selected_shifts = st.multiselect(
            t('shift'),
            options=df['shift'].unique(),
            default=df['shift'].unique(),
            format_func=lambda x: t(x),
            key='shift_filter'
        )
        
        selected_products = st.multiselect(
            t('product'),
            options=df['product'].unique(),
            default=df['product'].unique()[:3],
            key='product_filter'
        )
    
    # Aplicar filtros incluindo o novo filtro de data
    df_filtered = df[
        (df['date'] >= start_date) & 
        (df['date'] <= end_date) &
        (df['production_line'].isin(selected_lines)) &
        (df['shift'].isin(selected_shifts)) &
        (df['product'].isin(selected_products))
    ].copy()
    
    # Adiciona colunas de análise
    df_filtered['date_str'] = df_filtered['date'].dt.strftime('%Y-%m-%d')
    df_filtered['month'] = df_filtered['date'].dt.to_period('M').astype(str)
    df_filtered['shift_name'] = df_filtered['shift'].map({
        'morning': t('morning'), 
        'afternoon': t('afternoon'), 
        'night': t('night')
    })
    
    # Tabs principais com design moderno
    tabs = st.tabs([t('overview'), t('efficiency'), t('quality'), t('predictions')])
    
    # Tab 1: Visão Geral
    with tabs[0]:
        # KPIs em cards modernos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_production = df_filtered['units_produced'].sum()
            st.metric(
                t('total_production'),
                f"{total_production:,.0f}",
                f"{t('units_produced').lower()}"
            )
        
        with col2:
            avg_efficiency = df_filtered['efficiency'].mean()
            st.metric(
                t('average_efficiency'),
                f"{avg_efficiency:.1f}%",
                f"+{avg_efficiency-70:.1f}%" if avg_efficiency > 70 else f"{avg_efficiency-70:.1f}%"
            )
        
        with col3:
            avg_quality = df_filtered['quality_rate'].mean()
            st.metric(
                t('quality_rate'),
                f"{avg_quality:.1f}%",
                f"+{avg_quality-90:.1f}%" if avg_quality > 90 else f"{avg_quality-90:.1f}%"
            )
        
        with col4:
            total_defects = df_filtered['defects'].sum()
            defect_rate = (total_defects / total_production * 100) if total_production > 0 else 0
            st.metric(
                "Taxa de Defeitos",
                f"{defect_rate:.2f}%",
                f"-{5-defect_rate:.2f}%" if defect_rate < 5 else f"+{defect_rate-5:.2f}%",
                delta_color="inverse"
            )
        
        st.markdown("---")
        
        # Gráficos principais com layout responsivo
        col1, col2 = st.columns(2)
        
        with col1:
            # Tendência de produção com média móvel
            daily_prod = df_filtered.groupby('date_str')['units_produced'].sum().reset_index()
            daily_prod['MA7'] = daily_prod['units_produced'].rolling(window=7, min_periods=1).mean()
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=daily_prod['date_str'],
                y=daily_prod['units_produced'],
                mode='lines',
                name='Produção Diária',
                line=dict(color='#1f77b4', width=2),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)'
            ))
            fig_trend.add_trace(go.Scatter(
                x=daily_prod['date_str'],
                y=daily_prod['MA7'],
                mode='lines',
                name='Média Móvel (7 dias)',
                line=dict(color='#ff7f0e', width=3, dash='dot')
            ))
            fig_trend.update_layout(
                title=t('production_trend'),
                xaxis_title="Data",
                yaxis_title=t('units_produced'),
                hovermode='x unified',
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Eficiência por linha com cores personalizadas
            eff_by_line = df_filtered.groupby('production_line')['efficiency'].mean().reset_index()
            eff_by_line = eff_by_line.sort_values('efficiency', ascending=True)
            
            fig_eff = px.bar(
                eff_by_line,
                x='efficiency',
                y='production_line',
                orientation='h',
                title=t('efficiency_by_line'),
                color='efficiency',
                color_continuous_scale='RdYlGn',
                range_color=[70, 100]
            )
            fig_eff.update_traces(
                texttemplate='%{x:.1f}%',
                textposition='outside'
            )
            fig_eff.update_layout(
                xaxis_title="Eficiência (%)",
                yaxis_title="",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_eff, use_container_width=True)
        
        # Produção por produto - gráfico interativo
        st.subheader("📊 Produção por Produto")
        prod_by_product = df_filtered.groupby(['date_str', 'product'])['units_produced'].sum().reset_index()
        
        fig_product = px.area(
            prod_by_product,
            x='date_str',
            y='units_produced',
            color='product',
            title="Evolução da Produção por Produto",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_product.update_layout(
            xaxis_title="Data",
            yaxis_title=t('units_produced'),
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_product, use_container_width=True)
    
    # Tab 2: Análise de Eficiência
    with tabs[1]:
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap de eficiência
            pivot_eff = df_filtered.pivot_table(
                values='efficiency',
                index='production_line',
                columns='shift_name',
                aggfunc='mean'
            )
            
            fig_heatmap = px.imshow(
                pivot_eff,
                labels=dict(x="Turno", y="Linha", color="Eficiência (%)"),
                title="Mapa de Calor - Eficiência por Linha e Turno",
                color_continuous_scale='RdYlGn',
                aspect="auto"
            )
            fig_heatmap.update_traces(
                text=pivot_eff.values.round(1),
                texttemplate='%{text}%',
                textfont={"size": 12}
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # Box plot de eficiência
            fig_box = px.box(
                df_filtered,
                x='production_line',
                y='efficiency',
                color='shift_name',
                title="Distribuição de Eficiência",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_box.update_layout(
                xaxis_title="Linha de Produção",
                yaxis_title="Eficiência (%)",
                showlegend=True
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Análise temporal de eficiência
        st.subheader("⏰ Análise Temporal de Eficiência")
        
        # Eficiência por hora do dia (simulada)
        df_filtered['hour'] = pd.to_datetime(df_filtered['date']).dt.hour
        hourly_eff = df_filtered.groupby(['hour', 'shift_name'])['efficiency'].mean().reset_index()
        
        fig_hourly = px.line(
            hourly_eff,
            x='hour',
            y='efficiency',
            color='shift_name',
            title="Padrão de Eficiência ao Longo do Dia",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_hourly.update_layout(
            xaxis_title="Hora do Dia",
            yaxis_title="Eficiência Média (%)",
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            hovermode='x unified'
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Tab 3: Análise de Qualidade
    with tabs[2]:
        st.subheader(t('quality_analysis'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Defeitos por tipo (simulado)
            defect_types = ['Dimensional', 'Visual', 'Funcional', 'Embalagem', 'Outros']
            defect_counts = [
                int(df_filtered['defects'].sum() * p) 
                for p in [0.3, 0.25, 0.2, 0.15, 0.1]
            ]
            
            fig_defects = go.Figure(data=[
                go.Pie(
                    labels=defect_types,
                    values=defect_counts,
                    hole=0.4,
                    marker_colors=px.colors.sequential.RdBu
                )
            ])
            fig_defects.update_layout(
                title=t('defects_by_type'),
                annotations=[dict(text='Defeitos', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig_defects, use_container_width=True)
        
        with col2:
            # Tendência de qualidade
            quality_trend = df_filtered.groupby('date_str')['quality_rate'].mean().reset_index()
            
            fig_quality = go.Figure()
            fig_quality.add_trace(go.Scatter(
                x=quality_trend['date_str'],
                y=quality_trend['quality_rate'],
                mode='lines+markers',
                name='Taxa de Qualidade',
                line=dict(color='green', width=3),
                marker=dict(size=8)
            ))
            
            # Linha de meta
            fig_quality.add_hline(
                y=95, 
                line_dash="dash", 
                line_color="red",
                annotation_text="Meta: 95%"
            )
            
            fig_quality.update_layout(
                title=t('quality_trend'),
                xaxis_title="Data",
                yaxis_title="Taxa de Qualidade (%)",
                yaxis=dict(range=[90, 100]),
                hovermode='x unified'
            )
            st.plotly_chart(fig_quality, use_container_width=True)
        
        # Análise de correlação
        st.subheader("🔍 Análise de Correlação")
        
        # Correlação entre variáveis
        correlation_data = df_filtered[['efficiency', 'quality_rate', 'units_produced', 'downtime_minutes']].corr()
        
        fig_corr = px.imshow(
            correlation_data,
            labels=dict(color="Correlação"),
            title="Matriz de Correlação",
            color_continuous_scale='RdBu',
            zmin=-1,
            zmax=1
        )
        fig_corr.update_traces(
            text=correlation_data.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 14}
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Tab 4: Modelo Preditivo
    with tabs[3]:
        st.subheader(t('predictive_model'))
        
        # Preparação dos dados para o modelo
        df_model = df_filtered.copy()
        df_model['day_of_week'] = pd.to_datetime(df_model['date']).dt.dayofweek
        df_model['month'] = pd.to_datetime(df_model['date']).dt.month
        df_model['line_encoded'] = pd.Categorical(df_model['production_line']).codes
        df_model['shift_encoded'] = pd.Categorical(df_model['shift']).codes
        
        # Features e target
        features = ['efficiency', 'line_encoded', 'shift_encoded', 'day_of_week', 'month']
        X = df_model[features]
        y = df_model['units_produced']
        
        # Divisão treino/teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Treinamento do modelo
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Previsões
        y_pred = model.predict(X_test)
        
        # Métricas
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(t('model_accuracy'), f"{(1 - mae/y_test.mean())*100:.1f}%")
        
        with col2:
            st.metric(t('mae'), f"{mae:.0f} unidades")
        
        with col3:
            st.metric(t('r2'), f"{r2:.3f}")
        
        # Gráfico de previsão vs real
        fig_pred = go.Figure()
        
        # Scatter plot
        fig_pred.add_trace(go.Scatter(
            x=y_test,
            y=y_pred,
            mode='markers',
            name='Previsões',
            marker=dict(
                color='blue',
                size=8,
                opacity=0.6,
                line=dict(width=1, color='DarkSlateGrey')
            )
        ))
        
        # Linha de referência perfeita
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        fig_pred.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Previsão Perfeita',
            line=dict(color='red', dash='dash')
        ))
        
        fig_pred.update_layout(
            title=t('predicted_vs_actual'),
            xaxis_title="Produção Real",
            yaxis_title="Produção Prevista",
            hovermode='closest'
        )
        st.plotly_chart(fig_pred, use_container_width=True)
        
        # Feature importance
        st.subheader("🎯 Importância das Variáveis")
        
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=True)
        
        fig_importance = px.bar(
            feature_importance,
            x='importance',
            y='feature',
            orientation='h',
            title="Importância das Features no Modelo",
            color='importance',
            color_continuous_scale='Viridis'
        )
        fig_importance.update_traces(
            texttemplate='%{x:.3f}',
            textposition='outside'
        )
        st.plotly_chart(fig_importance, use_container_width=True)
    
    # Seção de Insights com design moderno
    st.markdown("---")
    with st.expander(t('insights'), expanded=True):
        st.subheader(t('top_insights'))
        insights = generate_insights(df_filtered)
        for i, insight in enumerate(insights, 1):
            st.markdown(f"{i}. {insight}")
    
    # Botão de download com feedback visual
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(t('download_report'), type="primary", use_container_width=True):
            with st.spinner(t('generating_report')):
                # Simulação de geração de relatório
                import time
                time.sleep(2)
                
                # Criar CSV para download
                csv = df_filtered.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name=f"relatorio_producao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.success(t('report_generated'))
    
    # Footer com informações adicionais
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>Dashboard de Produção v2.0 | Desenvolvido com Streamlit</p>
            <p>Última atualização: {} | Dados em tempo real</p>
        </div>
        """.format(datetime.now().strftime('%d/%m/%Y %H:%M')),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
