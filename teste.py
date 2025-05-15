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
        duracoes_minutos,
        nbins=20,
        labels={'value': 'Duração (minutos)', 'count': 'Frequência'},
        title="Distribuição da Duração das Paradas",
        color_discrete_sequence=['#3498db'],
        opacity=0.7
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
    
    # Adiciona linha vertical para a média
    media_minutos = duracoes_minutos.mean()
    fig.add_vline(
        x=media_minutos,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média: {media_minutos:.1f} min",
        annotation_position="top right"
    )
    
    return fig

# ----- FUNÇÕES DE EXPORTAÇÃO -----
@st.cache_data
def get_download_link(df, filename, text):
    """Gera um link para download de um DataFrame como arquivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=True, sheet_name='Dados')
        # Ajusta as colunas para melhor visualização
        worksheet = writer.sheets['Dados']
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(i+1, i+1, max_len)
    
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-button">{text}</a>'
    return href

# ----- FUNÇÃO PRINCIPAL DE ANÁLISE -----
def analisar_dados(df, maquina_selecionada, periodo_selecionado):
    """Realiza a análise completa dos dados com base nos filtros selecionados."""
    # Filtra os dados com base nas seleções
    dados_filtrados = df.copy()
    
    if maquina_selecionada != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina_selecionada]
    
    if periodo_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['Ano-Mês'] == periodo_selecionado]
    
    # Verifica se há dados após a filtragem
    if dados_filtrados.empty:
        st.warning("⚠️ Não há dados disponíveis para os filtros selecionados.")
        return
    
    # Calcula o tempo programado (assumindo 24 horas por dia)
    # Pode ser ajustado conforme necessário
    dias_no_periodo = (dados_filtrados['Inicio'].max() - dados_filtrados['Inicio'].min()).days + 1
    tempo_programado = pd.Timedelta(days=dias_no_periodo)
    
    # Calcula métricas principais
    disponibilidade = calcular_disponibilidade(dados_filtrados, tempo_programado)
    eficiencia = eficiencia_operacional(dados_filtrados, tempo_programado)
    tempo_medio = tempo_medio_paradas(dados_filtrados)
    total_paradas = len(dados_filtrados)
    duracao_total = dados_filtrados['Duração'].sum()
    
    # Identifica paradas críticas
    paradas_criticas, percentual_criticas = indice_paradas_criticas(dados_filtrados)
    
    # Calcula indicadores adicionais
    areas_responsaveis = indice_paradas_por_area(dados_filtrados)
    pareto = pareto_causas_parada(dados_filtrados)
    frequentes = paradas_mais_frequentes(dados_filtrados)
    ocorrencias = taxa_ocorrencia_paradas(dados_filtrados)
    duracao_mensal = duracao_total_por_mes(dados_filtrados)
    tempo_por_area = tempo_total_paradas_area(dados_filtrados)
    
    # Exibe as métricas principais
    st.markdown('<div class="metrics-container" style="display: flex; justify-content: space-between; flex-wrap: wrap;">', unsafe_allow_html=True)
    
    # Métrica 1: Disponibilidade
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Disponibilidade</div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: {'#28a745' if disponibilidade >= 90 else '#ffc107' if disponibilidade >= 75 else '#dc3545'};">{disponibilidade:.1f}%</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">Tempo disponível para operação</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Métrica 2: Eficiência Operacional
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Eficiência Operacional</div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: {'#28a745' if eficiencia >= 90 else '#ffc107' if eficiencia >= 75 else '#dc3545'};">{eficiencia:.1f}%</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">Aproveitamento do tempo disponível</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Métrica 3: Tempo Médio de Parada
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Tempo Médio de Parada</div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #17a2b8;">{formatar_duracao(tempo_medio)}</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">Duração média por ocorrência</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Métrica 4: Total de Paradas
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Total de Paradas</div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #6f42c1;">{total_paradas}</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">Número de ocorrências no período</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Segunda linha de métricas
    st.markdown('<div class="metrics-container" style="display: flex; justify-content: space-between; flex-wrap: wrap;">', unsafe_allow_html=True)
    
    # Métrica 5: Duração Total
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Duração Total</div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #e83e8c;">{formatar_duracao(duracao_total)}</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">Tempo total de paradas no período</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Métrica 6: Paradas Críticas
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Paradas Críticas (>1h)</div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: {'#dc3545' if percentual_criticas > 20 else '#ffc107' if percentual_criticas > 10 else '#28a745'};">{len(paradas_criticas)}</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">{percentual_criticas:.1f}% do total de paradas</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Métrica 7: Período Analisado
    periodo_texto = obter_nome_mes(periodo_selecionado) if periodo_selecionado != "Todos" else "Todos os Meses"
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Período Analisado</div>
            <div class="metric-value" style="font-size: 1.8rem; font-weight: bold; color: #20c997;">{periodo_texto}</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">{dias_no_periodo} dias analisados</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Métrica 8: Máquina Analisada
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="metric-label" style="font-size: 1rem; color: #6c757d;">Máquina Analisada</div>
            <div class="metric-value" style="font-size: 1.8rem; font-weight: bold; color: #fd7e14;">{maquina_selecionada}</div>
            <div class="metric-description" style="font-size: 0.8rem; color: #6c757d;">Equipamento em análise</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráficos de análise
    st.markdown('<div class="section-title">Análise de Paradas</div>', unsafe_allow_html=True)
    
    # Primeira linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Pareto
        fig_pareto = criar_grafico_pareto(pareto)
        if fig_pareto:
            st.plotly_chart(fig_pareto, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de Pareto.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Pizza por Áreas
        fig_areas = criar_grafico_pizza_areas(areas_responsaveis)
        if fig_areas:
            st.plotly_chart(fig_areas, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de áreas responsáveis.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Segunda linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Ocorrências por Mês
        fig_ocorrencias = criar_grafico_ocorrencias(ocorrencias)
        if fig_ocorrencias:
            st.plotly_chart(fig_ocorrencias, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de ocorrências mensais.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Duração Total por Mês
        fig_duracao = criar_grafico_duracao_mensal(duracao_mensal)
        if fig_duracao:
            st.plotly_chart(fig_duracao, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de duração mensal.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Terceira linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Tempo por Área
        fig_tempo_area = criar_grafico_tempo_area(tempo_por_area)
        if fig_tempo_area:
            st.plotly_chart(fig_tempo_area, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de tempo por área.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Paradas Críticas
        if not paradas_criticas.empty:
            top_criticas = paradas_criticas.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
            fig_criticas = criar_grafico_paradas_criticas(top_criticas)
            if fig_criticas:
                st.plotly_chart(fig_criticas, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de paradas críticas.")
        else:
            st.info("Não foram identificadas paradas críticas (>1h) no período.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quarta linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Distribuição de Duração
        fig_distribuicao = criar_grafico_distribuicao_duracao(dados_filtrados)
        if fig_distribuicao:
            st.plotly_chart(fig_distribuicao, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o histograma de duração.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gráfico de Pizza de Áreas Críticas
        fig_areas_criticas = criar_grafico_pizza_areas_criticas(paradas_criticas)
        if fig_areas_criticas:
            st.plotly_chart(fig_areas_criticas, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de áreas responsáveis por paradas críticas.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise e recomendações
    st.markdown('<div class="section-title">Conclusões e Recomendações</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        
        # Conclusões com base nos dados
        st.markdown("### 📋 Principais Conclusões")
        
        conclusoes = []
        
        # Análise de disponibilidade
        if disponibilidade < 75:
            conclusoes.append(f"A disponibilidade está **criticamente baixa** ({disponibilidade:.1f}%), indicando problemas significativos que afetam a operação.")
        elif disponibilidade < 90:
            conclusoes.append(f"A disponibilidade está **abaixo do ideal** ({disponibilidade:.1f}%), com oportunidades de melhoria.")
        else:
            conclusoes.append(f"A disponibilidade está em um **bom nível** ({disponibilidade:.1f}%), mas ainda pode ser aprimorada.")
        
        # Análise de paradas críticas
        if len(paradas_criticas) > 0:
            percentual = len(paradas_criticas) / total_paradas * 100
            if percentual > 20:
                conclusoes.append(f"**Alta incidência de paradas críticas** ({percentual:.1f}% do total), indicando falhas graves que precisam de atenção imediata.")
            else:
                conclusoes.append(f"Foram identificadas {len(paradas_criticas)} paradas críticas ({percentual:.1f}% do total), que devem ser priorizadas.")
        
        # Análise de tempo médio
        tempo_medio_minutos = tempo_medio.total_seconds() / 60 if not pd.isna(tempo_medio) else 0
        if tempo_medio_minutos > 60:
            conclusoes.append(f"O tempo médio de parada está **muito alto** ({formatar_duracao(tempo_medio)}), sugerindo dificuldades na resolução de problemas.")
        elif tempo_medio_minutos > 30:
            conclusoes.append(f"O tempo médio de parada ({formatar_duracao(tempo_medio)}) indica oportunidades para melhorar os procedimentos de manutenção.")
        
        # Análise de áreas responsáveis
        if not areas_responsaveis.empty:
            area_principal = areas_responsaveis.idxmax()
            percentual_area = areas_responsaveis.max()
            conclusoes.append(f"A área de **{area_principal}** é responsável por {percentual_area:.1f}% das paradas, sendo o principal ponto de atenção.")
        
        # Análise de causas principais
        if not pareto.empty:
            causa_principal = pareto.idxmax()
            tempo_causa = pareto.max().total_seconds() / 3600
            conclusoes.append(f"A causa **'{causa_principal}'** é responsável por {tempo_causa:.1f} horas de parada, sendo a principal a ser tratada.")
        
        # Exibe as conclusões
        for conclusao in conclusoes:
            st.markdown(f"- {conclusao}")
        
        # Recomendações
        st.markdown("### 🚀 Recomendações")
        
        recomendacoes = []
        
        # Recomendações com base na disponibilidade
        if disponibilidade < 90:
            recomendacoes.append("Implementar um programa de manutenção preventiva mais rigoroso para aumentar a disponibilidade dos equipamentos.")
        
        # Recomendações com base nas paradas críticas
        if len(paradas_criticas) > 0:
            recomendacoes.append("Criar um plano de ação específico para as paradas críticas, com foco nas causas mais frequentes e de maior duração.")
        
        # Recomendações com base no tempo médio
        if tempo_medio_minutos > 30:
            recomendacoes.append("Revisar os procedimentos de resposta a paradas, buscando reduzir o tempo médio de resolução.")
        
        # Recomendações com base nas áreas responsáveis
        if not areas_responsaveis.empty:
            area_principal = areas_responsaveis.idxmax()
            recomendacoes.append(f"Realizar treinamentos específicos para a equipe de {area_principal}, focando na prevenção e rápida resolução de problemas.")
        
        # Recomendações com base nas causas principais
        if not pareto.empty:
            causa_principal = pareto.idxmax()
            recomendacoes.append(f"Desenvolver um projeto de melhoria focado na causa '{causa_principal}', que representa o maior impacto no tempo de parada.")
        
        # Recomendações gerais
        recomendacoes.append("Implementar indicadores de desempenho (KPIs) para monitoramento contínuo da eficiência e disponibilidade dos equipamentos.")
        recomendacoes.append("Realizar análises de causa raiz para as paradas mais frequentes, envolvendo equipes multidisciplinares.")
        
        # Exibe as recomendações
        for recomendacao in recomendacoes:
            st.markdown(f"- {recomendacao}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão para download do relatório completo
    st.markdown(
        get_download_link(dados_filtrados, 'relatorio_paradas.xlsx', '📥 Baixar relatório completo'),
        unsafe_allow_html=True
    )

# ----- FUNÇÃO PRINCIPAL DA APLICAÇÃO -----
def main():
    """Função principal que controla o fluxo da aplicação."""
    # Inicializa o estado da sessão se necessário
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    if 'first_load' not in st.session_state:
        st.session_state.first_load = False
    
    # Menu de navegação
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Dados", "Sobre"],
        icons=["speedometer2", "table", "info-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#2a9d8f", "font-size": "16px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "padding": "10px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#2a9d8f", "color": "white"},
        }
    )
    
    if selected == "Dashboard":
        st.markdown('<div class="main-title">Análise de Eficiência de Máquinas</div>', unsafe_allow_html=True)
        
        # Upload de arquivo
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("### 📤 Upload de Dados")
            
            uploaded_file = st.file_uploader("Selecione um arquivo Excel com os dados de paradas", type=["xlsx", "xls"])
            
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)
                    
                    # Verifica se o arquivo tem as colunas necessárias
                    colunas_necessarias = ['Máquina', 'Inicio', 'Fim', 'Duração']
                    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
                    
                    if colunas_faltantes:
                        st.error(f"⚠️ O arquivo não contém as colunas necessárias: {', '.join(colunas_faltantes)}")
                    else:
                        # Processa os dados
                        df_processado = processar_dados(df)
                        
                        # Armazena no estado da sessão
                        st.session_state.df = df_processado
                        
                        st.success(f"✅ Dados carregados com sucesso! ({len(df_processado)} registros)")
                        
                        # Exibe uma prévia dos dados
                        st.markdown("### 👁️ Prévia dos Dados")
                        st.dataframe(
                            df_processado.head(5),
                            use_container_width=True,
                            hide_index=True
                        )
                except Exception as e:
                    st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Filtros e análise
        if st.session_state.df is not None:
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                st.markdown("### 🔍 Filtros de Análise")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtro de máquina
                    maquinas_disponiveis = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    maquina_selecionada = st.selectbox("Selecione a Máquina:", maquinas_disponiveis)
                
                with col2:
                    # Filtro de período (substituindo o filtro de mês)
                    periodos_disponiveis = ["Todos"] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                    periodo_selecionado = st.selectbox("Selecione o Período:", periodos_disponiveis)
                
                # Botão para analisar
                if st.button("Analisar Dados", type="primary"):
                    analisar_dados(st.session_state.df, maquina_selecionada, periodo_selecionado)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Realiza a análise com os filtros padrão na primeira carga
            if not st.session_state.first_load and st.session_state.df is not None:
                st.session_state.first_load = True
                analisar_dados(st.session_state.df, "Todas", "Todos")
    
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
                    # Filtro de mês
                    meses_para_filtro = ["Todos"] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                    mes_filtro = st.selectbox("Filtrar por Mês:", meses_para_filtro)
                
                # Aplica os filtros
                dados_filtrados = st.session_state.df.copy()
                
                if maquina_filtro != "Todas":
                    dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina_filtro]
                
                if mes_filtro != "Todos":
                    dados_filtrados = dados_filtrados[dados_filtrados['Ano-Mês'] == mes_filtro]
                
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

# Executa a aplicação
if __name__ == "__main__":
    main()
