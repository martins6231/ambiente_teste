import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64
from streamlit_option_menu import option_menu

# ----- CONFIGURAÇÃO DA PÁGINA -----
st.set_page_config(
    page_title="Análise de Eficiência de Máquinas",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- ESTILOS CSS OTIMIZADOS -----
def aplicar_estilos():
    """Aplica estilos CSS otimizados e melhorados para a aplicação."""
    st.markdown(
        """
        <style>
        body {
            font-family: 'Arial', sans-serif;
        }

        /* Principal */
        .main-container {
            max-width: 1200px;
            padding: 1rem;
            margin: auto;
        }

        /* Títulos */
        .main-title, .section-title {
            text-transform: uppercase;
            text-align: center;
            margin-bottom: 20px;
            font-family: 'Verdana', sans-serif;
            color: #20232a;
        }

        .main-title {
            font-size: 3rem;
            color: #264653;
        }

        .section-title {
            font-size: 2rem;
            color: #2a9d8f;
        }

        /* Botões de Ação */
        .stButton > button {
            background-color: #2a9d8f;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 12px 24px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s ease;
        }

        .stButton > button:hover {
            background-color: #21867a;
        }

        /* Caixas de Conteúdo */
        .content-box {
            background-color: #ffffff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .metrics-container .metric-box {
            border-top: 3px solid #2a9d8f;
            transition: transform 0.3s ease;
        }

        .metric-value {
            font-size: 2rem;
            color: #1d3557;
        }

        .metric-label {
            color: #457b9d;
        }

        /* Gráficos */
        .chart-container {
            background-color: #f7f9fb;
            padding: 20px;
            margin-top: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        /* Upload de Arquivos */
        .uploadedFile {
            border: 1px dashed #2a9d8f;
            border-radius: 5px;
            padding: 0.5rem;
        }

        /* Responsividade */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            .section-title {
                font-size: 1.5rem;
            }
            .metrics-container {
                flex-direction: column;
                align-items: center;
            }
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

# Aplica os estilos CSS
aplicar_estilos()

# ----- FUNÇÕES AUXILIARES -----
@st.cache_data
def formatar_duracao(duracao):
    """Formata uma duração (timedelta) para exibição amigável."""
    if pd.isna(duracao):
        return "00:00:00"
    
    total_segundos = int(duracao.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

@st.cache_data
def obter_nome_mes(mes_ano):
    """Converte o formato 'YYYY-MM' para um nome de mês legível."""
    if mes_ano == 'Todos':
        return 'Todos os Meses'
    
    try:
        data = datetime.strptime(mes_ano, '%Y-%m')
        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return f"{meses_pt[data.month]} {data.year}"
    except:
        return mes_ano

@st.cache_data
def processar_dados(df):
    """Processa e limpa os dados do DataFrame."""
    # Cria uma cópia para evitar SettingWithCopyWarning
    df_processado = df.copy()
    
    # Mapeamento de máquinas com tratamento para códigos desconhecidos
    machine_mapping = {
        78: "PET",
        79: "TETRA 1000",
        80: "TETRA 200",
        89: "SIG 1000",
        91: "SIG 200"
    }
    
    if 'Máquina' in df_processado.columns:
        # Preserva o código original se não estiver no mapeamento
        df_processado['Máquina'] = df_processado['Máquina'].apply(
            lambda x: machine_mapping.get(x, f"Máquina {x}")
        )
    
    # Converte as colunas de tempo para o formato datetime
    for col in ['Inicio', 'Fim']:
        if col in df_processado.columns:
            df_processado[col] = pd.to_datetime(df_processado[col], errors='coerce')
    
    # Processa a coluna de duração
    if 'Duração' in df_processado.columns:
        # Tenta converter a coluna Duração para timedelta
        try:
            df_processado['Duração'] = pd.to_timedelta(df_processado['Duração'])
        except:
            # Se falhar, tenta extrair horas, minutos e segundos e criar um timedelta
            if isinstance(df_processado['Duração'].iloc[0], str):
                def parse_duration(duration_str):
                    try:
                        parts = duration_str.split(':')
                        if len(parts) == 3:
                            hours, minutes, seconds = map(int, parts)
                            return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
                        else:
                            return pd.NaT
                    except:
                        return pd.NaT
                
                df_processado['Duração'] = df_processado['Duração'].apply(parse_duration)
    
    # Adiciona colunas de ano, mês e ano-mês para facilitar a filtragem
    df_processado['Ano'] = df_processado['Inicio'].dt.year
    df_processado['Mês'] = df_processado['Inicio'].dt.month
    df_processado['Mês_Nome'] = df_processado['Inicio'].dt.strftime('%B')  # Nome do mês
    df_processado['Ano-Mês'] = df_processado['Inicio'].dt.strftime('%Y-%m')
    
    # Remove registros com valores ausentes nas colunas essenciais
    df_processado = df_processado.dropna(subset=['Máquina', 'Inicio', 'Fim', 'Duração'])
    
    return df_processado

# ----- FUNÇÕES DE CÁLCULO DE INDICADORES -----
@st.cache_data
def calcular_disponibilidade(df, tempo_programado):
    """Calcula a taxa de disponibilidade."""
    tempo_total_parado = df['Duração'].sum()
    disponibilidade = (tempo_programado - tempo_total_parado) / tempo_programado * 100
    return max(0, min(100, disponibilidade))

@st.cache_data
def indice_paradas_por_area(df):
    """Calcula o índice de paradas por área responsável."""
    if 'Área Responsável' in df.columns:
        area_counts = df['Área Responsável'].value_counts(normalize=True) * 100
        return area_counts
    else:
        return pd.Series()

@st.cache_data
def pareto_causas_parada(df):
    """Identifica as principais causas de paradas (Pareto) por duração total."""
    if 'Parada' in df.columns:
        pareto = df.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
        return pareto
    else:
        return pd.Series()

@st.cache_data
def paradas_mais_frequentes(df):
    """Identifica as paradas mais frequentes por contagem."""
    if 'Parada' in df.columns:
        frequentes = df['Parada'].value_counts().head(10)
        return frequentes
    else:
        return pd.Series()

@st.cache_data
def tempo_medio_paradas(df):
    """Calcula o tempo médio de parada (TMP)."""
    tmp = df['Duração'].mean()
    return tmp

@st.cache_data
def taxa_ocorrencia_paradas(df):
    """Calcula a taxa de ocorrência de paradas (número total de paradas por mês)."""
    ocorrencias_mensais = df.groupby('Ano-Mês').size()
    return ocorrencias_mensais

@st.cache_data
def duracao_total_por_mes(df):
    """Calcula a duração total de paradas por mês."""
    duracao_mensal = df.groupby('Ano-Mês')['Duração'].sum()
    return duracao_mensal

@st.cache_data
def tempo_total_paradas_area(df):
    """Calcula o tempo total de paradas por área."""
    if 'Área Responsável' in df.columns:
        tempo_por_area = df.groupby('Área Responsável')['Duração'].sum()
        return tempo_por_area
    else:
        return pd.Series()

@st.cache_data
def frequencia_categorias_paradas(df):
    """Calcula a frequência de paradas por categoria."""
    if 'Parada' in df.columns:
        frequencia = df['Parada'].value_counts()
        return frequencia
    else:
        return pd.Series()

@st.cache_data
def eficiencia_operacional(df, tempo_programado):
    """Calcula a eficiência operacional."""
    tempo_operacao = tempo_programado - df['Duração'].sum()
    eficiencia = tempo_operacao / tempo_programado * 100
    return max(0, min(100, eficiencia))

@st.cache_data
def indice_paradas_criticas(df, limite_horas=1):
    """Identifica paradas críticas (com duração maior que o limite especificado)."""
    limite = pd.Timedelta(hours=limite_horas)
    paradas_criticas = df[df['Duração'] > limite]
    percentual_criticas = len(paradas_criticas) / len(df) * 100 if len(df) > 0 else 0
    return paradas_criticas, percentual_criticas

# ----- FUNÇÕES DE VISUALIZAÇÃO -----
@st.cache_data
def criar_grafico_pareto(pareto):
    """Cria um gráfico de Pareto com Plotly."""
    if pareto.empty:
        return None
    
    # Converte durações para horas
    pareto_horas = pareto.apply(lambda x: x.total_seconds() / 3600)
    
    fig = px.bar(
        x=pareto_horas.index,
        y=pareto_horas.values,
        labels={'x': 'Causa de Parada', 'y': 'Duração Total (horas)'},
        title="Pareto de Causas de Paradas (Top 10 por Duração)",
        color_discrete_sequence=['#3498db'],
        text=pareto_horas.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h', 
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Duração Total (horas)",
        xaxis_title="Causa de Parada",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_pizza_areas(indice_paradas):
    """Cria um gráfico de pizza para áreas responsáveis com Plotly."""
    if indice_paradas.empty:
        return None
    
    fig = px.pie(
        values=indice_paradas.values,
        names=indice_paradas.index,
        title="Índice de Paradas por Área Responsável",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4  # Cria um gráfico de donut para melhor visualização
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if i == indice_paradas.values.argmax() else 0 for i in range(len(indice_paradas))]  # Destaca o maior valor
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_ocorrencias(ocorrencias):
    """Cria um gráfico de linha para ocorrências mensais com Plotly."""
    if ocorrencias.empty or len(ocorrencias) <= 1:
        return None
    
    fig = px.line(
        x=ocorrencias.index,
        y=ocorrencias.values,
        markers=True,
        labels={'x': 'Mês', 'y': 'Número de Paradas'},
        title="Taxa de Ocorrência de Paradas por Mês",
        color_discrete_sequence=['#2ecc71']
    )
    
    # Adiciona área sob a linha para melhor visualização de tendências
    fig.add_trace(
        go.Scatter(
            x=ocorrencias.index,
            y=ocorrencias.values,
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)',
            line=dict(color='rgba(46, 204, 113, 0)'),
            showlegend=False
        )
    )
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(ocorrencias):
        fig.add_annotation(
            x=ocorrencias.index[i],
            y=v,
            text=str(v),
            showarrow=False,
            yshift=10,
            font=dict(color="#2c3e50")
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Número de Paradas",
        xaxis_title="Mês",
        hovermode="x unified",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_duracao_mensal(duracao_mensal):
    """Cria um gráfico de linha para duração total de paradas por mês."""
    if duracao_mensal.empty or len(duracao_mensal) <= 1:
        return None
    
    # Converte durações para horas
    duracao_horas = duracao_mensal.apply(lambda x: x.total_seconds() / 3600)
    
    fig = px.line(
        x=duracao_horas.index,
        y=duracao_horas.values,
        markers=True,
        labels={'x': 'Mês', 'y': 'Duração Total (horas)'},
        title="Duração Total de Paradas por Mês",
        color_discrete_sequence=['#e74c3c']
    )
    
    # Adiciona área sob a linha para melhor visualização de tendências
    fig.add_trace(
        go.Scatter(
            x=duracao_horas.index,
            y=duracao_horas.values,
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)',
            line=dict(color='rgba(231, 76, 60, 0)'),
            showlegend=False
        )
    )
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(duracao_horas):
        fig.add_annotation(
            x=duracao_horas.index[i],
            y=v,
            text=f"{v:.1f}h",
            showarrow=False,
            yshift=10,
            font=dict(color="#2c3e50")
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Duração Total (horas)",
        xaxis_title="Mês",
        hovermode="x unified",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_tempo_area(tempo_area):
    """Cria um gráfico de barras horizontais para tempo por área com Plotly."""
    if tempo_area.empty:
        return None
    
    # Converte durações para horas
    tempo_area_horas = tempo_area.apply(lambda x: x.total_seconds() / 3600)
    
    # Ordena os dados para melhor visualização
    tempo_area_horas = tempo_area_horas.sort_values(ascending=True)
    
    fig = px.bar(
        y=tempo_area_horas.index,
        x=tempo_area_horas.values,
        orientation='h',
        labels={'y': 'Área Responsável', 'x': 'Duração Total (horas)'},
        title="Tempo Total de Paradas por Área",
        color_discrete_sequence=['#e74c3c'],
        text=tempo_area_horas.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h', 
        textposition='outside'
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Duração Total (horas)",
        yaxis_title="Área Responsável",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_paradas_criticas(top_criticas):
    """Cria um gráfico de barras horizontais para paradas críticas com Plotly."""
    if top_criticas.empty:
        return None
    
    # Converte durações para horas
    top_criticas_horas = top_criticas.apply(lambda x: x.total_seconds() / 3600)
    
    # Ordena os dados para melhor visualização
    top_criticas_horas = top_criticas_horas.sort_values(ascending=True)
    
    fig = px.bar(
        y=top_criticas_horas.index,
        x=top_criticas_horas.values,
        orientation='h',
        labels={'y': 'Tipo de Parada', 'x': 'Duração Total (horas)'},
        title="Top 10 Paradas Críticas (>1h)",
        color_discrete_sequence=['#9b59b6'],
        text=top_criticas_horas.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h', 
        textposition='outside'
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Duração Total (horas)",
        yaxis_title="Tipo de Parada",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_pizza_areas_criticas(paradas_criticas):
    """Cria um gráfico de pizza para áreas responsáveis por paradas críticas."""
    if 'Área Responsável' not in paradas_criticas.columns or paradas_criticas.empty:
        return None
    
    areas_criticas = paradas_criticas['Área Responsável'].value_counts()
    
    fig = px.pie(
        values=areas_criticas.values,
        names=areas_criticas.index,
        title="Distribuição de Paradas Críticas por Área",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hole=0.4  # Cria um gráfico de donut para melhor visualização
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_distribuicao_duracao(df):
    """Cria um histograma da distribuição de duração das paradas."""
    if df.empty:
        return None
    
    # Converte durações para minutos para melhor visualização
    duracoes_minutos = df['Duração'].apply(lambda x: x.total_seconds() / 60)
    
    fig = px.histogram(
        x=duracoes_minutos,
        nbins=20,
        labels={'x': 'Duração (minutos)', 'y': 'Frequência'},
        title="Distribuição da Duração das Paradas",
        color_discrete_sequence=['#3498db']
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Duração (minutos)",
        yaxis_title="Frequência",
        bargap=0.1,
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

# ----- FUNÇÕES DE EXPORTAÇÃO -----
def get_download_link(df, filename, link_text):
    """Gera um link para download de um DataFrame como arquivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=True)
    
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# ----- FUNÇÕES DE ANÁLISE -----
def analisar_dados(df, maquina, data_inicio, data_fim):
    """Realiza a análise dos dados com base nos filtros selecionados."""
    st.markdown('<div class="section-title">Análise de Eficiência</div>', unsafe_allow_html=True)
    
    # Filtra os dados conforme seleção
    dados_filtrados = df.copy()
    
    if maquina != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina]
    
    # Filtro por período (substituindo o filtro por mês)
    dados_filtrados = dados_filtrados[(dados_filtrados['Inicio'].dt.date >= data_inicio) & 
                                      (dados_filtrados['Inicio'].dt.date <= data_fim)]
    
    # Exibe a informação sobre o filtro aplicado
    periodo_texto = f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    st.markdown(f"<h3 style='text-align: center;'>{maquina} | {periodo_texto}</h3>", unsafe_allow_html=True)
    
    # Verifica se há dados após a filtragem
    if dados_filtrados.empty:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
        return
    
    # Define tempo programado (assume 24 horas por dia para simplificar)
    num_dias = (dados_filtrados['Inicio'].max() - dados_filtrados['Inicio'].min()).days + 1
    tempo_programado = pd.Timedelta(hours=24 * num_dias)
    
    # Cálculos para métricas
    total_paradas = len(dados_filtrados)
    tempo_total_parado = dados_filtrados['Duração'].sum()
    tempo_medio = tempo_medio_paradas(dados_filtrados)
    disponibilidade = calcular_disponibilidade(dados_filtrados, tempo_programado)
    
    # Calcula o tempo médio entre falhas (MTBF) se houver mais de uma parada
    if total_paradas > 1:
        # Ordena as paradas por hora de início
        paradas_ordenadas = dados_filtrados.sort_values('Inicio')
        # Calcula a diferença entre o início de cada parada
        diferencas = paradas_ordenadas['Inicio'].diff().dropna()
        # Remove diferenças muito pequenas (menos de 1 minuto) que podem ser registros duplicados
        diferencas = diferencas[diferencas > pd.Timedelta(minutes=1)]
        mtbf = diferencas.mean() if not diferencas.empty else pd.Timedelta(hours=0)
    else:
        mtbf = pd.Timedelta(hours=0)
    
    # Calcula as paradas críticas (acima de 1 hora)
    paradas_criticas, percentual_criticas = indice_paradas_criticas(dados_filtrados)
    
    # Exibe as métricas principais
    st.markdown('<div class="content-box metrics-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{total_paradas}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Total de Paradas</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{formatar_duracao(tempo_total_parado)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Tempo Total Parado</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{disponibilidade:.1f}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Disponibilidade</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{formatar_duracao(tempo_medio)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Tempo Médio de Parada</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Segunda linha de métricas
    st.markdown('<div class="content-box metrics-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{formatar_duracao(mtbf)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Tempo Médio Entre Falhas</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{len(paradas_criticas)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Paradas Críticas (>1h)</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{percentual_criticas:.1f}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">% de Paradas Críticas</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calcula dados para gráficos
    pareto = pareto_causas_parada(dados_filtrados)
    indice_areas = indice_paradas_por_area(dados_filtrados)
    ocorrencias = taxa_ocorrencia_paradas(dados_filtrados)
    duracao_mensal = duracao_total_por_mes(dados_filtrados)
    tempo_areas = tempo_total_paradas_area(dados_filtrados)
    
    # Top paradas críticas
    if not paradas_criticas.empty and 'Parada' in paradas_criticas.columns:
        top_criticas = paradas_criticas.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
    else:
        top_criticas = pd.Series()
    
    # ----- VISUALIZAÇÕES -----
    st.markdown('<div class="section-title">Análise de Causas e Tendências</div>', unsafe_allow_html=True)
    
    # Primeira linha de gráficos
    st.markdown('<div class="content-box chart-container">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Pareto de Causas", "🍩 Índice por Área"])
    
    with tab1:
        fig_pareto = criar_grafico_pareto(pareto)
        if fig_pareto:
            st.plotly_chart(fig_pareto, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de Pareto.")
    
    with tab2:
        fig_areas = criar_grafico_pizza_areas(indice_areas)
        if fig_areas:
            st.plotly_chart(fig_areas, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de áreas.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Segunda linha de gráficos
    st.markdown('<div class="content-box chart-container">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📈 Ocorrências por Mês", "📉 Duração por Mês"])
    
    with tab1:
        fig_ocorrencias = criar_grafico_ocorrencias(ocorrencias)
        if fig_ocorrencias:
            st.plotly_chart(fig_ocorrencias, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de ocorrências por mês.")
    
    with tab2:
        fig_duracao = criar_grafico_duracao_mensal(duracao_mensal)
        if fig_duracao:
            st.plotly_chart(fig_duracao, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de duração por mês.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Terceira linha de gráficos
    st.markdown('<div class="content-box chart-container">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["⏱️ Tempo por Área", "⚠️ Paradas Críticas"])
    
    with tab1:
        fig_tempo_areas = criar_grafico_tempo_area(tempo_areas)
        if fig_tempo_areas:
            st.plotly_chart(fig_tempo_areas, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de tempo por área.")
    
    with tab2:
        fig_paradas_criticas = criar_grafico_paradas_criticas(top_criticas)
        if fig_paradas_criticas:
            st.plotly_chart(fig_paradas_criticas, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de paradas críticas.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quarta linha com análises adicionais
    st.markdown('<div class="section-title">Análises Adicionais</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box chart-container">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Distribuição de Duração", "🔍 Áreas Críticas"])
    
    with tab1:
        fig_distribuicao = criar_grafico_distribuicao_duracao(dados_filtrados)
        if fig_distribuicao:
            st.plotly_chart(fig_distribuicao, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o histograma de distribuição.")
    
    with tab2:
        fig_areas_criticas = criar_grafico_pizza_areas_criticas(paradas_criticas)
        if fig_areas_criticas:
            st.plotly_chart(fig_areas_criticas, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de áreas críticas.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recomendações baseadas na análise
    st.markdown('<div class="section-title">Insights e Recomendações</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # Principais problemas identificados
    if not pareto.empty:
        st.markdown("### 🔍 Principais Problemas Identificados")
        
        # Top 3 causas de parada
        top3_causas = pareto.head(3)
        st.markdown("#### Top 3 Causas de Parada por Duração:")
        for causa, duracao in top3_causas.items():
            horas = duracao.total_seconds() / 3600
            st.markdown(f"- **{causa}**: {horas:.1f} horas ({(horas / (tempo_total_parado.total_seconds() / 3600) * 100):.1f}% do tempo total)")
    
    # Recomendações
    st.markdown("### 💡 Recomendações")
    
    if not pareto.empty:
        top_causa = pareto.index[0]
        st.markdown(f"1. **Priorizar a resolução** da causa principal de paradas: **{top_causa}**")
    
    if not indice_areas.empty:
        top_area = indice_areas.index[0]
        st.markdown(f"2. **Analisar processos e treinamentos** da área com maior índice de paradas: **{top_area}**")
    
    if not paradas_criticas.empty:
        st.markdown(f"3. **Desenvolver planos de contingência** para reduzir o número de paradas críticas (acima de 1 hora)")
    
    st.markdown("4. **Implementar manutenção preventiva** em componentes críticos para aumentar o MTBF")
    
    st.markdown("5. **Revisar procedimentos operacionais** para reduzir o tempo médio de parada")
    
    # Link para download dos dados analisados
    st.markdown("### 📥 Exportar Dados Analisados")
    
    st.markdown(
        get_download_link(dados_filtrados, 'analise_paradas.xlsx', '📥 Baixar dados analisados'),
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----- INICIALIZAÇÃO DA SESSÃO -----
# Inicializa variáveis de estado da sessão
if 'df' not in st.session_state:
    st.session_state.df = None
if 'first_load' not in st.session_state:
    st.session_state.first_load = False

# ----- INTERFACE PRINCIPAL -----
def main():
    """Função principal que controla o fluxo da aplicação."""
    # Título principal
    st.markdown('<div class="main-title">Análise de Eficiência de Máquinas</div>', unsafe_allow_html=True)
    
    # Menu de navegação
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Dados", "Sobre"],
        icons=["speedometer2", "table", "info-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "margin": "0!important"},
            "icon": {"color": "#2a9d8f", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "padding": "10px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#2a9d8f", "color": "white"},
        }
    )
    
    if selected == "Dashboard":
        # Seção de upload de arquivo
        st.markdown('<div class="section-title">Importação de Dados</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown(
                """
                Faça o upload de um arquivo Excel contendo os registros de paradas de máquinas. 
                O arquivo deve conter as colunas: Máquina, Inicio, Fim, Duração, Parada e Área Responsável.
                """
            )
            
            uploaded_file = st.file_uploader("Selecione um arquivo Excel", type=['xlsx', 'xls'])
            
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)
                    st.session_state.df = processar_dados(df)
                    st.success(f"✅ Arquivo carregado com sucesso! {len(st.session_state.df)} registros encontrados.")
                except Exception as e:
                    st.error(f"❌ Erro ao carregar o arquivo: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Seção de filtros e análise
        if st.session_state.df is not None:
            st.markdown('<div class="section-title">Filtros</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtro de máquina
                    maquinas = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    maquina_selecionada = st.selectbox("Selecione uma Máquina:", maquinas)
                
                with col2:
                    # Filtro de período (substituindo o filtro de mês)
                    st.markdown("**Selecione o período:**")
                    col2a, col2b = st.columns(2)
                    with col2a:
                        data_inicio = st.date_input("Data Inicial", 
                                                 value=st.session_state.df['Inicio'].min().date() if st.session_state.df is not None else None,
                                                 min_value=st.session_state.df['Inicio'].min().date() if st.session_state.df is not None else None,
                                                 max_value=st.session_state.df['Inicio'].max().date() if st.session_state.df is not None else None)
                    with col2b:
                        data_fim = st.date_input("Data Final", 
                                               value=st.session_state.df['Inicio'].max().date() if st.session_state.df is not None else None,
                                               min_value=st.session_state.df['Inicio'].min().date() if st.session_state.df is not None else None,
                                               max_value=st.session_state.df['Inicio'].max().date() if st.session_state.df is not None else None)
                
                # Botão para realizar a análise
                if st.button("Analisar Dados", type="primary", use_container_width=True):
                    if st.session_state.df is not None:
                        analisar_dados(st.session_state.df, maquina_selecionada, data_inicio, data_fim)
                    else:
                        st.error("⚠️ Nenhum dado foi carregado. Por favor, faça o upload de um arquivo Excel.")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Realiza a análise com os filtros padrão na primeira carga
            if not st.session_state.first_load and st.session_state.df is not None:
                st.session_state.first_load = True
                data_inicio_padrao = st.session_state.df['Inicio'].min().date()
                data_fim_padrao = st.session_state.df['Inicio'].max().date()
                analisar_dados(st.session_state.df, "Todas", data_inicio_padrao, data_fim_padrao)
    
    elif selected == "Dados":
        if st.session_state.df is not None:
            st.markdown('<div class="section-title">Visualização dos Dados</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                # Opções de filtro para visualização
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtro de máquina
                    maquinas_para_filtro = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    maquina_filtro = st.selectbox("Filtrar por Máquina:", maquinas_para_filtro)
                
                with col2:
                    # Filtro de período (substituindo o filtro de mês)
                    st.markdown("**Selecione o período:**")
                    col2a, col2b = st.columns(2)
                    with col2a:
                        data_inicio_filtro = st.date_input("Data Inicial (Filtro)", 
                                                        value=st.session_state.df['Inicio'].min().date(),
                                                        min_value=st.session_state.df['Inicio'].min().date(),
                                                        max_value=st.session_state.df['Inicio'].max().date())
                    with col2b:
                        data_fim_filtro = st.date_input("Data Final (Filtro)", 
                                                     value=st.session_state.df['Inicio'].max().date(),
                                                     min_value=st.session_state.df['Inicio'].min().date(),
                                                     max_value=st.session_state.df['Inicio'].max().date())
                
                # Aplica os filtros
                dados_filtrados = st.session_state.df.copy()
                
                if maquina_filtro != "Todas":
                    dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina_filtro]
                
                # Filtro por período (substituindo o filtro por mês)
                dados_filtrados = dados_filtrados[(dados_filtrados['Inicio'].dt.date >= data_inicio_filtro) & 
                                                 (dados_filtrados['Inicio'].dt.date <= data_fim_filtro)]
                
                # Exibe os dados filtrados
                st.markdown(f"**Mostrando {len(dados_filtrados)} registros**")
                st.dataframe(
                    dados_filtrados,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # Botão para download dos dados
                st.markdown(
                    get_download_link(dados_filtrados, 'dados_filtrados.xlsx', '📥 Baixar dados filtrados'),
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Estatísticas básicas
            st.markdown('<div class="section-title">Estatísticas Básicas</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                # Resumo por máquina
                resumo_maquina = dados_filtrados.groupby('Máquina').agg({
                    'Duração': ['count', 'sum', 'mean']
                })
                resumo_maquina.columns = ['Número de Paradas', 'Duração Total', 'Duração Média']
                
                # Converte para horas
                resumo_maquina['Duração Total (horas)'] = resumo_maquina['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
                resumo_maquina['Duração Média (horas)'] = resumo_maquina['Duração Média'].apply(lambda x: x.total_seconds() / 3600)
                
                st.dataframe(
                    resumo_maquina[['Número de Paradas', 'Duração Total (horas)', 'Duração Média (horas)']],
                    column_config={
                        "Número de Paradas": st.column_config.NumberColumn("Número de Paradas", format="%d"),
                        "Duração Total (horas)": st.column_config.NumberColumn("Duração Total (horas)", format="%.2f"),
                        "Duração Média (horas)": st.column_config.NumberColumn("Duração Média (horas)", format="%.2f")
                    },
                    use_container_width=True
                )
                
                # Gráfico de resumo por máquina
                if len(resumo_maquina) > 1:  # Só cria o gráfico se houver mais de uma máquina
                    fig_resumo = px.bar(
                        resumo_maquina.reset_index(),
                        x='Máquina',
                        y='Duração Total (horas)',
                        color='Máquina',
                        title="Duração Total de Paradas por Máquina",
                        labels={'Duração Total (horas)': 'Duração Total (horas)', 'Máquina': 'Máquina'},
                        text='Duração Total (horas)'
                    )
                    
                    fig_resumo.update_traces(
                        texttemplate='%{text:.1f}h', 
                        textposition='outside'
                    )
                    
                    fig_resumo.update_layout(
                        xaxis_tickangle=0,
                        autosize=True,
                        margin=dict(l=50, r=50, t=80, b=50),
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_resumo, use_container_width=True)
                
                # Botão para download do resumo
                st.markdown(
                    get_download_link(resumo_maquina.reset_index(), 'resumo_maquinas.xlsx', '📥 Baixar resumo por máquina'),
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Distribuição de paradas por dia da semana
            st.markdown('<div class="section-title">Análises Adicionais</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                
                tab1, tab2 = st.tabs(["📅 Distribuição por Dia da Semana", "🕒 Distribuição por Hora do Dia"])
                
                with tab1:
                    # Adiciona coluna de dia da semana
                    dados_filtrados['Dia da Semana'] = dados_filtrados['Inicio'].dt.day_name()
                    
                    # Ordem dos dias da semana
                    ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    nomes_dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                    
                    # Mapeamento para nomes em português
                    mapeamento_dias = dict(zip(ordem_dias, nomes_dias_pt))
                    dados_filtrados['Dia da Semana PT'] = dados_filtrados['Dia da Semana'].map(mapeamento_dias)
                    
                    # Agrupa por dia da semana
                    paradas_por_dia = dados_filtrados.groupby('Dia da Semana PT').agg({
                        'Duração': ['count', 'sum']
                    })
                    paradas_por_dia.columns = ['Número de Paradas', 'Duração Total']
                    
                    # Converte para horas
                    paradas_por_dia['Duração (horas)'] = paradas_por_dia['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
                    
                    # Reordena o índice de acordo com os dias da semana
                    if not paradas_por_dia.empty:
                        paradas_por_dia = paradas_por_dia.reindex(nomes_dias_pt)
                        
                        # Cria o gráfico
                        fig_dias = px.bar(
                            paradas_por_dia.reset_index(),
                            x='Dia da Semana PT',
                            y='Número de Paradas',
                            title="Distribuição de Paradas por Dia da Semana",
                            labels={'Número de Paradas': 'Número de Paradas', 'Dia da Semana PT': 'Dia da Semana'},
                            text='Número de Paradas',
                            color='Dia da Semana PT',
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        
                        fig_dias.update_traces(
                            texttemplate='%{text}', 
                            textposition='outside'
                        )
                        
                        fig_dias.update_layout(
                            xaxis_tickangle=0,
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=50),
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_dias, use_container_width=True)
                        
                        # Exibe a tabela
                        st.dataframe(
                            paradas_por_dia[['Número de Paradas', 'Duração (horas)']],
                            column_config={
                                "Número de Paradas": st.column_config.NumberColumn("Número de Paradas", format="%d"),
                                "Duração (horas)": st.column_config.NumberColumn("Duração (horas)", format="%.2f")
                            },
                            use_container_width=True
                        )
                    else:
                        st.info("Dados insuficientes para análise por dia da semana.")
                
                with tab2:
                    # Adiciona coluna de hora do dia
                    dados_filtrados['Hora do Dia'] = dados_filtrados['Inicio'].dt.hour
                    
                    # Agrupa por hora do dia
                    paradas_por_hora = dados_filtrados.groupby('Hora do Dia').agg({
                        'Duração': ['count', 'sum']
                    })
                    paradas_por_hora.columns = ['Número de Paradas', 'Duração Total']
                    
                    # Converte para horas
                    paradas_por_hora['Duração (horas)'] = paradas_por_hora['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
                    
                    # Cria o gráfico
                    if not paradas_por_hora.empty:
                        fig_horas = px.line(
                            paradas_por_hora.reset_index(),
                            x='Hora do Dia',
                            y='Número de Paradas',
                            title="Distribuição de Paradas por Hora do Dia",
                            labels={'Número de Paradas': 'Número de Paradas', 'Hora do Dia': 'Hora do Dia'},
                            markers=True
                        )
                        
                        # Adiciona área sob a linha
                        fig_horas.add_trace(
                            go.Scatter(
                                x=paradas_por_hora.reset_index()['Hora do Dia'],
                                y=paradas_por_hora['Número de Paradas'],
                                fill='tozeroy',
                                fillcolor='rgba(52, 152, 219, 0.2)',
                                line=dict(color='rgba(52, 152, 219, 0)'),
                                showlegend=False
                            )
                        )
                        
                        fig_horas.update_layout(
                            xaxis=dict(
                                tickmode='array',
                                tickvals=list(range(0, 24)),
                                ticktext=[f"{h}:00" for h in range(0, 24)]
                            ),
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=50),
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_horas, use_container_width=True)
                        
                        # Exibe a tabela
                        st.dataframe(
                            paradas_por_hora[['Número de Paradas', 'Duração (horas)']],
                            column_config={
                                "Número de Paradas": st.column_config.NumberColumn("Número de Paradas", format="%d"),
                                "Duração (horas)": st.column_config.NumberColumn("Duração (horas)", format="%.2f")
                            },
                            use_container_width=True
                        )
                    else:
                        st.info("Dados insuficientes para análise por hora do dia.")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
                        st.warning("⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel.")
    
    elif selected == "Sobre":
        st.markdown('<div class="section-title">Sobre a Aplicação</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image("https://img.icons8.com/fluency/240/factory.png", width=150)
            
            with col2:
                st.markdown("""
                # Análise de Eficiência de Máquinas
                
                Esta aplicação foi desenvolvida para analisar dados de paradas de máquinas e calcular indicadores de eficiência, 
                fornecendo insights valiosos para melhorar a produtividade e reduzir o tempo de inatividade.
                """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Funcionalidades
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## ✨ Funcionalidades")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📊 Análise de Dados
                - Visualização de indicadores de disponibilidade e eficiência
                - Identificação das principais causas de paradas
                - Análise da distribuição de paradas por área responsável
                - Acompanhamento da evolução das paradas ao longo do tempo
                """)
            
            with col2:
                st.markdown("""
                ### 🔍 Recursos Adicionais
                - Filtragem por máquina e período
                - Exportação de dados para análise detalhada
                - Visualizações interativas e responsivas
                - Recomendações automáticas baseadas nos dados
                """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Como usar
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 🚀 Como Usar")
            
            st.markdown("""
            1. **Upload de Dados**: Na página "Dashboard", faça o upload de um arquivo Excel contendo os registros de paradas.
            2. **Filtros**: Selecione a máquina e o período desejados para análise.
            3. **Análise**: Visualize os gráficos, tabelas e conclusões geradas automaticamente.
            4. **Exportação**: Use os botões de download para exportar tabelas e dados para análise detalhada.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Formato dos dados
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 📋 Formato dos Dados")
            
            st.markdown("""
            O arquivo Excel deve conter as seguintes colunas:
            
            - **Máquina**: Identificador da máquina (será convertido conforme mapeamento)
            - **Inicio**: Data e hora de início da parada
            - **Fim**: Data e hora de fim da parada
            - **Duração**: Tempo de duração da parada (HH:MM:SS)
            - **Parada**: Descrição do tipo de parada
            - **Área Responsável**: Área responsável pela parada
            """)
            
            # Exemplo de dados
            st.markdown("### Exemplo de Dados")
            
            exemplo_dados = pd.DataFrame({
                'Máquina': [78, 79, 80, 89, 91],
                'Inicio': pd.date_range(start='2023-01-01', periods=5, freq='D'),
                'Fim': pd.date_range(start='2023-01-01 02:00:00', periods=5, freq='D'),
                'Duração': ['02:00:00', '02:00:00', '02:00:00', '02:00:00', '02:00:00'],
                'Parada': ['Manutenção', 'Erro de Configuração', 'Falta de Insumos', 'Falha Elétrica', 'Troca de Produto'],
                'Área Responsável': ['Manutenção', 'Operação', 'Logística', 'Manutenção', 'Produção']
            })
            
            st.dataframe(exemplo_dados, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tecnologias utilizadas
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 🛠️ Tecnologias Utilizadas")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                ### Frontend
                - **Streamlit**: Framework para criação de aplicações web
                - **Plotly**: Biblioteca para criação de gráficos interativos
                - **HTML/CSS**: Estilização e formatação da interface
                """)
            
            with col2:
                st.markdown("""
                ### Análise de Dados
                - **Pandas**: Manipulação e análise de dados
                - **NumPy**: Computação numérica
                - **Matplotlib/Seaborn**: Visualização de dados
                """)
            
            with col3:
                st.markdown("""
                ### Infraestrutura
                - **Streamlit Cloud**: Hospedagem da aplicação
                - **GitHub**: Controle de versão
                - **Python**: Linguagem de programação
                """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Requisitos do sistema
        with st.expander("📦 Requisitos do Sistema"):
            st.code("""
            # requirements.txt
            streamlit>=1.22.0
            pandas>=2.0.1
            numpy>=1.26.0
            matplotlib>=3.7.1
            seaborn>=0.12.2
            plotly>=5.14.1
            openpyxl>=3.1.2
            xlsxwriter>=3.1.0
            streamlit-option-menu>=0.3.2
            """)
    
    # Rodapé
    st.markdown("""
    <div class="footer">
        <p>© 2023-2025 Análise de Eficiência de Máquinas | Desenvolvido com ❤️ usando Streamlit</p>
        <p><small>Versão 2.1.0 | Última atualização: Maio 2025</small></p>
    </div>
    """, unsafe_allow_html=True)

# Função para criar links de download
def get_download_link(df, filename, text):
    """Gera um link de download para um DataFrame."""
    # Cria um buffer na memória para salvar o arquivo Excel
    output = io.BytesIO()
    
    # Cria um escritor Excel
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Escreve o DataFrame no buffer
    df.to_excel(writer, index=False, sheet_name='Dados')
    
    # Salva o conteúdo no buffer
    writer.close()
    
    # Converte o buffer para base64
    b64 = base64.b64encode(output.getvalue()).decode()
    
    # Cria o link de download
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-button">{text}</a>'
    
    return href

# Função para analisar dados (modificada para usar período)
def analisar_dados(df, maquina, data_inicio, data_fim):
    """Realiza a análise dos dados com base nos filtros selecionados."""
    st.markdown('<div class="section-title">Análise de Eficiência</div>', unsafe_allow_html=True)
    
    # Filtra os dados conforme seleção
    dados_filtrados = df.copy()
    
    if maquina != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina]
    
    # Filtro por período (substituindo o filtro por mês)
    dados_filtrados = dados_filtrados[(dados_filtrados['Inicio'].dt.date >= data_inicio) & 
                                      (dados_filtrados['Inicio'].dt.date <= data_fim)]
    
    # Verifica se existem dados após a filtragem
    if dados_filtrados.empty:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste os filtros.")
        return
    
    # Exibe informações sobre a seleção atual
    periodo_texto = f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    st.markdown(f"<h3 style='text-align: center;'>{maquina} | {periodo_texto}</h3>", unsafe_allow_html=True)
    
    # Contagem de registros e estatísticas básicas
    st.markdown(f"**Total de registros analisados: {len(dados_filtrados)}**")
    
    # Calcula tempo total de paradas
    tempo_total_horas = dados_filtrados['Duração'].sum().total_seconds() / 3600
    
    # Calcula tempo médio de parada
    tempo_medio = tempo_medio_paradas(dados_filtrados)
    
    # Suposição: assume um tempo programado de operação (24h por dia para o período selecionado)
    # Ajuste conforme a realidade da operação
    dias_periodo = (data_fim - data_inicio).days + 1
    tempo_programado_horas = dias_periodo * 24  # 24 horas por dia
    tempo_programado = pd.Timedelta(hours=tempo_programado_horas)
    
    # Calcula disponibilidade e eficiência
    disponibilidade = calcular_disponibilidade(dados_filtrados, tempo_programado)
    eficiencia = eficiencia_operacional(dados_filtrados, tempo_programado)
    
    # Identifica paradas críticas
    paradas_criticas, percentual_criticas = indice_paradas_criticas(dados_filtrados)
    
    # Métricas em cards
    st.markdown('<div class="metrics-container" style="display: flex; justify-content: space-between; margin-bottom: 20px;">', unsafe_allow_html=True)
    
    # Card 1: Disponibilidade
    st.markdown(f"""
    <div class="metric-box" style="flex: 1; background-color: #f8f9fa; padding: 20px; margin: 0 10px; border-radius: 10px; text-align: center;">
        <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: {'#2ecc71' if disponibilidade >= 80 else '#e74c3c'};">{disponibilidade:.1f}%</div>
        <div class="metric-label" style="font-size: 1rem; color: #7f8c8d;">Disponibilidade</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Card 2: Tempo Total de Paradas
    st.markdown(f"""
    <div class="metric-box" style="flex: 1; background-color: #f8f9fa; padding: 20px; margin: 0 10px; border-radius: 10px; text-align: center;">
        <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #3498db;">{tempo_total_horas:.1f}h</div>
        <div class="metric-label" style="font-size: 1rem; color: #7f8c8d;">Tempo Total de Paradas</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Card 3: Tempo Médio de Parada
    st.markdown(f"""
    <div class="metric-box" style="flex: 1; background-color: #f8f9fa; padding: 20px; margin: 0 10px; border-radius: 10px; text-align: center;">
        <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #9b59b6;">{formatar_duracao(tempo_medio)}</div>
        <div class="metric-label" style="font-size: 1rem; color: #7f8c8d;">Tempo Médio de Parada</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Card 4: % Paradas Críticas
    st.markdown(f"""
    <div class="metric-box" style="flex: 1; background-color: #f8f9fa; padding: 20px; margin: 0 10px; border-radius: 10px; text-align: center;">
        <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: {'#e74c3c' if percentual_criticas > 20 else '#f39c12'};">{percentual_criticas:.1f}%</div>
        <div class="metric-label" style="font-size: 1rem; color: #7f8c8d;">Paradas Críticas (>1h)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráficos de análise
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de Pareto de causas de paradas
        pareto = pareto_causas_parada(dados_filtrados)
        fig_pareto = criar_grafico_pareto(pareto)
        if fig_pareto:
            st.plotly_chart(fig_pareto, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de Pareto.")
        
        # Gráfico de paradas por área
        if 'Área Responsável' in dados_filtrados.columns:
            indice_areas = indice_paradas_por_area(dados_filtrados)
            fig_areas = criar_grafico_pizza_areas(indice_areas)
            if fig_areas:
                st.plotly_chart(fig_areas, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de áreas responsáveis.")
    
    with col2:
        # Gráfico de tempo total de paradas por área
        if 'Área Responsável' in dados_filtrados.columns:
            tempo_areas = tempo_total_paradas_area(dados_filtrados)
            fig_tempo_areas = criar_grafico_tempo_area(tempo_areas)
            if fig_tempo_areas:
                st.plotly_chart(fig_tempo_areas, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de tempo por área.")
        
        # Gráfico das principais paradas críticas
        if not paradas_criticas.empty:
            top_criticas = paradas_criticas.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
            fig_criticas = criar_grafico_paradas_criticas(top_criticas)
            if fig_criticas:
                st.plotly_chart(fig_criticas, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de paradas críticas.")
    
    # Histórico mensal (caso aplicável)
    st.markdown("### 📈 Histórico de Paradas")
    
    tab1, tab2 = st.tabs(["🔢 Ocorrências Mensais", "⏱️ Duração Mensal"])
    
    with tab1:
        # Filtra por máquina, mas mantém todos os meses para análise de tendência
        dados_historico = df.copy()
        if maquina != "Todas":
            dados_historico = dados_historico[dados_historico['Máquina'] == maquina]
        
        dados_historico = dados_historico[(dados_historico['Inicio'].dt.date >= data_inicio) & 
                                         (dados_historico['Inicio'].dt.date <= data_fim)]
        
        # Verifica se há pelo menos dois meses de dados para análise de tendência
        ocorrencias = taxa_ocorrencia_paradas(dados_historico)
        fig_ocorrencias = criar_grafico_ocorrencias(ocorrencias)
        if fig_ocorrencias:
            st.plotly_chart(fig_ocorrencias, use_container_width=True)
        else:
            st.info("É necessário ter dados de pelo menos dois meses para exibir a tendência de ocorrências.")
    
    with tab2:
        # Gráfico de duração total por mês
        duracao_mensal = duracao_total_por_mes(dados_historico)
        fig_duracao = criar_grafico_duracao_mensal(duracao_mensal)
        if fig_duracao:
            st.plotly_chart(fig_duracao, use_container_width=True)
        else:
            st.info("É necessário ter dados de pelo menos dois meses para exibir a tendência de duração.")
    
    # Recomendações baseadas na análise
    st.markdown("### 🔍 Insights e Recomendações")
    
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        
        # Principais insights
        insights = []
        
        if disponibilidade < 80:
            insights.append("A disponibilidade está abaixo do ideal (80%).")
        
        if percentual_criticas > 20:
            insights.append(f"Há um percentual elevado de paradas críticas ({percentual_criticas:.1f}%).")
        
        if not pareto.empty:
            top_causa = pareto.index[0]
            duracao_top = pareto.iloc[0].total_seconds() / 3600
            insights.append(f"A principal causa de parada é '{top_causa}' com {duracao_top:.1f} horas.")
        
        if 'Área Responsável' in dados_filtrados.columns and not indice_areas.empty:
            top_area = indice_areas.index[0]
            percentual_top = indice_areas.iloc[0]
            insights.append(f"A área com maior índice de paradas é '{top_area}' ({percentual_top:.1f}%).")
        
        # Exibe os insights
        if insights:
            st.markdown("#### 📊 Principais Insights:")
            for insight in insights:
                st.markdown(f"- {insight}")
        
        # Recomendações
        st.markdown("#### 🚀 Recomendações:")
        
        recomendacoes = []
        
        if disponibilidade < 80:
            recomendacoes.append("Implementar um programa de manutenção preventiva para reduzir paradas não programadas.")
        
        if percentual_criticas > 20:
            recomendacoes.append("Focar na redução das paradas críticas (>1h) para melhorar a disponibilidade.")
        
        if not pareto.empty:
            recomendacoes.append(f"Criar um plano de ação específico para a causa '{pareto.index[0]}' que representa a maior parte do tempo de parada.")
        
        if 'Área Responsável' in dados_filtrados.columns and not indice_areas.empty:
            recomendacoes.append(f"Realizar treinamento específico para a equipe da área '{indice_areas.index[0]}' para reduzir a incidência de paradas.")
        
        # Exibe as recomendações
        if recomendacoes:
            for i, rec in enumerate(recomendacoes):
                st.markdown(f"{i+1}. {rec}")
        else:
            st.info("Dados insuficientes para gerar recomendações específicas.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão para download dos dados analisados
    st.markdown(
        get_download_link(dados_filtrados, 'analise_paradas.xlsx', '📥 Baixar dados analisados'),
        unsafe_allow_html=True
    )

# Executa a aplicação
if __name__ == "__main__":
    main()
