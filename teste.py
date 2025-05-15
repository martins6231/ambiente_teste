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
def formatar_periodo(data_inicio, data_fim):
    """Formata um período de datas para exibição amigável."""
    meses_pt = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    if data_inicio == data_fim:
        return f"{data_inicio.day} de {meses_pt[data_inicio.month]} de {data_inicio.year}"
    
    if data_inicio.year == data_fim.year and data_inicio.month == data_fim.month:
        return f"{data_inicio.day} a {data_fim.day} de {meses_pt[data_inicio.month]} de {data_inicio.year}"
    
    if data_inicio.year == data_fim.year:
        return f"{data_inicio.day} de {meses_pt[data_inicio.month]} a {data_fim.day} de {meses_pt[data_fim.month]} de {data_inicio.year}"
    
    return f"{data_inicio.day}/{data_inicio.month}/{data_inicio.year} a {data_fim.day}/{data_fim.month}/{data_fim.year}"

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
    df_processado['Data'] = df_processado['Inicio'].dt.date  # Adiciona coluna de data para facilitar a filtragem por período
    
    # Remove registros com valores ausentes nas colunas essenciais
    df_processado = df_processado.dropna(subset=['Máquina', 'Inicio', 'Fim', 'Duração'])
    
    return df_processado

# ... outras funções permanecem iguais ...

def analisar_dados(df, maquina_selecionada, data_inicio, data_fim):
    """Realiza a análise completa dos dados com base nos filtros selecionados."""
    # Filtra os dados conforme seleção
    dados_filtrados = df.copy()
    
    if maquina_selecionada != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina_selecionada]
    
    # Filtra pelo intervalo de datas
    dados_filtrados = dados_filtrados[(dados_filtrados['Inicio'].dt.date >= data_inicio) & 
                                     (dados_filtrados['Inicio'].dt.date <= data_fim)]
    
    # Define o tempo programado com base no período selecionado
    dias_no_periodo = (data_fim - data_inicio).days + 1
    tempo_programado_horas = dias_no_periodo * 24
    tempo_programado = pd.Timedelta(hours=tempo_programado_horas)
    
    # Verifica se há dados após a filtragem
    if dados_filtrados.empty:
        st.warning(f"⚠️ Não foram encontrados dados para a máquina '{maquina_selecionada}' no período selecionado.")
        return
    
    # Exibe informações sobre os filtros aplicados
    st.markdown('<div class="section-title">Análise de Eficiência</div>', unsafe_allow_html=True)
    
    # Formata o período para exibição
    periodo_formatado = formatar_periodo(data_inicio, data_fim)
    
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown(f"### 📊 Resultados para {maquina_selecionada if maquina_selecionada != 'Todas' else 'Todas as Máquinas'}")
        st.markdown(f"**Período analisado:** {periodo_formatado}")
        st.markdown(f"**Total de registros:** {len(dados_filtrados)}")
        st.markdown(f"**Tempo programado:** {tempo_programado_horas} horas ({dias_no_periodo} dias)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Calcula os indicadores
    disponibilidade = calcular_disponibilidade(dados_filtrados, tempo_programado)
    tmp = tempo_medio_paradas(dados_filtrados)
    tmp_horas = tmp.total_seconds() / 3600
    
    # Calcula o número total de paradas e a duração total
    total_paradas = len(dados_filtrados)
    duracao_total = dados_filtrados['Duração'].sum()
    duracao_total_horas = duracao_total.total_seconds() / 3600
    
    # Calcula a eficiência operacional
    eficiencia = eficiencia_operacional(dados_filtrados, tempo_programado)
    
    # Identifica paradas críticas (>1h)
    paradas_criticas, percentual_criticas = indice_paradas_criticas(dados_filtrados)
    
    # Exibe os indicadores principais
    with st.container():
        st.markdown('<div class="metrics-container content-box">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{disponibilidade:.1f}%</p>', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Disponibilidade</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{tmp_horas:.2f}h</p>', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Tempo Médio de Parada</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{total_paradas}</p>', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Total de Paradas</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{duracao_total_horas:.1f}h</p>', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Duração Total</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Exibe indicadores secundários
    with st.container():
        st.markdown('<div class="metrics-container content-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{eficiencia:.1f}%</p>', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Eficiência Operacional</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{percentual_criticas:.1f}%</p>', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Índice de Paradas Críticas (>1h)</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise de causas de paradas (Pareto)
    with st.container():
        st.markdown('<div class="section-title">Análise de Causas</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if 'Parada' in dados_filtrados.columns:
                pareto = pareto_causas_parada(dados_filtrados)
                fig_pareto = criar_grafico_pareto(pareto)
                if fig_pareto:
                    st.plotly_chart(fig_pareto, use_container_width=True)
                else:
                    st.info("Dados insuficientes para gerar o gráfico de Pareto.")
            else:
                st.info("Coluna 'Parada' não encontrada nos dados.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if 'Área Responsável' in dados_filtrados.columns:
                indice_areas = indice_paradas_por_area(dados_filtrados)
                fig_pizza = criar_grafico_pizza_areas(indice_areas)
                if fig_pizza:
                    st.plotly_chart(fig_pizza, use_container_width=True)
                else:
                    st.info("Dados insuficientes para gerar o gráfico de áreas responsáveis.")
            else:
                st.info("Coluna 'Área Responsável' não encontrada nos dados.")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise de tendências
    with st.container():
        st.markdown('<div class="section-title">Análise de Tendências</div>', unsafe_allow_html=True)
        
        # Agrupa os dados por data para análise de tendências no período selecionado
        ocorrencias_diarias = dados_filtrados.groupby(dados_filtrados['Inicio'].dt.date).size()
        duracao_diaria = dados_filtrados.groupby(dados_filtrados['Inicio'].dt.date)['Duração'].sum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Cria gráfico de ocorrências diárias
            if len(ocorrencias_diarias) > 1:
                fig_ocorrencias = px.line(
                    x=ocorrencias_diarias.index,
                    y=ocorrencias_diarias.values,
                    markers=True,
                    labels={'x': 'Data', 'y': 'Número de Paradas'},
                    title="Ocorrências de Paradas por Dia",
                    color_discrete_sequence=['#2ecc71']
                )
                
                # Adiciona área sob a linha
                fig_ocorrencias.add_trace(
                    go.Scatter(
                        x=ocorrencias_diarias.index,
                        y=ocorrencias_diarias.values,
                        fill='tozeroy',
                        fillcolor='rgba(46, 204, 113, 0.2)',
                        line=dict(color='rgba(46, 204, 113, 0)'),
                        showlegend=False
                    )
                )
                
                fig_ocorrencias.update_layout(
                    xaxis_tickangle=-45,
                    autosize=True,
                    margin=dict(l=50, r=50, t=80, b=100),
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis_title="Número de Paradas",
                    xaxis_title="Data",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_ocorrencias, use_container_width=True)
            else:
                st.info("Dados insuficientes para análise de tendências diárias.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Cria gráfico de duração diária
            if len(duracao_diaria) > 1:
                # Converte para horas
                duracao_diaria_horas = duracao_diaria.apply(lambda x: x.total_seconds() / 3600)
                
                fig_duracao = px.line(
                    x=duracao_diaria_horas.index,
                    y=duracao_diaria_horas.values,
                    markers=True,
                    labels={'x': 'Data', 'y': 'Duração Total (horas)'},
                    title="Duração Total de Paradas por Dia",
                    color_discrete_sequence=['#e74c3c']
                )
                
                # Adiciona área sob a linha
                fig_duracao.add_trace(
                    go.Scatter(
                        x=duracao_diaria_horas.index,
                        y=duracao_diaria_horas.values,
                        fill='tozeroy',
                        fillcolor='rgba(231, 76, 60, 0.2)',
                        line=dict(color='rgba(231, 76, 60, 0)'),
                        showlegend=False
                    )
                )
                
                fig_duracao.update_layout(
                    xaxis_tickangle=-45,
                    autosize=True,
                    margin=dict(l=50, r=50, t=80, b=100),
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis_title="Duração Total (horas)",
                    xaxis_title="Data",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_duracao, use_container_width=True)
            else:
                st.info("Dados insuficientes para análise de tendências diárias.")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise detalhada
    with st.container():
        st.markdown('<div class="section-title">Análise Detalhada</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🔍 Paradas Críticas", "📊 Tempo por Área", "📈 Distribuição de Duração"])
        
        with tab1:
            if not paradas_criticas.empty:
                # Agrupa paradas críticas por tipo
                if 'Parada' in paradas_criticas.columns:
                    top_criticas = paradas_criticas.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
                    fig_criticas = criar_grafico_paradas_criticas(top_criticas)
                    if fig_criticas:
                        st.plotly_chart(fig_criticas, use_container_width=True)
                    
                    # Exibe tabela de paradas críticas
                    st.markdown("#### Detalhamento de Paradas Críticas (>1h)")
                    
                    # Prepara os dados para exibição
                    paradas_criticas_display = paradas_criticas.copy()
                    paradas_criticas_display['Duração (h)'] = paradas_criticas_display['Duração'].apply(lambda x: round(x.total_seconds() / 3600, 2))
                    paradas_criticas_display['Início'] = paradas_criticas_display['Inicio'].dt.strftime('%d/%m/%Y %H:%M')
                    paradas_criticas_display['Fim'] = paradas_criticas_display['Fim'].dt.strftime('%d/%m/%Y %H:%M')
                    
                    # Seleciona e ordena as colunas para exibição
                    colunas_display = ['Máquina', 'Parada', 'Início', 'Fim', 'Duração (h)']
                    if 'Área Responsável' in paradas_criticas_display.columns:
                        colunas_display.insert(2, 'Área Responsável')
                    
                    st.dataframe(
                        paradas_criticas_display[colunas_display].sort_values('Duração (h)', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Gráfico de distribuição por área
                    if 'Área Responsável' in paradas_criticas.columns:
                        fig_areas_criticas = criar_grafico_pizza_areas_criticas(paradas_criticas)
                        if fig_areas_criticas:
                            st.plotly_chart(fig_areas_criticas, use_container_width=True)
                else:
                    st.info("Coluna 'Parada' não encontrada nos dados.")
            else:
                st.info("Não foram encontradas paradas críticas (>1h) no período selecionado.")
        
        with tab2:
            if 'Área Responsável' in dados_filtrados.columns:
                tempo_area = tempo_total_paradas_area(dados_filtrados)
                fig_tempo_area = criar_grafico_tempo_area(tempo_area)
                if fig_tempo_area:
                    st.plotly_chart(fig_tempo_area, use_container_width=True)
                
                # Tabela de tempo por área
                st.markdown("#### Detalhamento de Tempo por Área")
                
                # Prepara os dados para exibição
                tempo_area_df = pd.DataFrame({
                    'Área Responsável': tempo_area.index,
                    'Duração Total (h)': tempo_area.apply(lambda x: round(x.total_seconds() / 3600, 2)),
                    'Número de Paradas': dados_filtrados.groupby('Área Responsável').size()
                }).sort_values('Duração Total (h)', ascending=False)
                
                # Calcula o tempo médio por área
                tempo_area_df['Duração Média (h)'] = tempo_area_df['Duração Total (h)'] / tempo_area_df['Número de Paradas']
                tempo_area_df['Duração Média (h)'] = tempo_area_df['Duração Média (h)'].round(2)
                
                # Calcula o percentual do tempo total
                tempo_area_df['% do Tempo Total'] = (tempo_area_df['Duração Total (h)'] / tempo_area_df['Duração Total (h)'].sum() * 100).round(1)
                
                st.dataframe(
                    tempo_area_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Coluna 'Área Responsável' não encontrada nos dados.")
        
        with tab3:
            # Cria histograma da distribuição de duração
            fig_dist = criar_grafico_distribuicao_duracao(dados_filtrados)
            if fig_dist:
                st.plotly_chart(fig_dist, use_container_width=True)
            
            # Estatísticas de duração
            st.markdown("#### Estatísticas de Duração")
            
            # Calcula estatísticas
            duracao_segundos = dados_filtrados['Duração'].apply(lambda x: x.total_seconds())
            duracao_minutos = duracao_segundos / 60
            duracao_horas = duracao_segundos / 3600
            
            estatisticas = {
                'Mínima': duracao_minutos.min(),
                'Média': duracao_minutos.mean(),
                'Mediana': duracao_minutos.median(),
                'Máxima': duracao_minutos.max(),
                'Desvio Padrão': duracao_minutos.std()
            }
            
            # Cria DataFrame para exibição
            estatisticas_df = pd.DataFrame({
                'Estatística': list(estatisticas.keys()),
                'Valor (minutos)': [round(v, 2) for v in estatisticas.values()],
                'Valor (horas)': [round(v/60, 2) for v in estatisticas.values()]
            })
            
            st.dataframe(
                estatisticas_df,
                use_container_width=True,
                hide_index=True
            )
    
    # Recomendações
    with st.container():
        st.markdown('<div class="section-title">Recomendações</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            
            # Identifica as principais áreas e causas para recomendações
            principais_areas = []
            if 'Área Responsável' in dados_filtrados.columns:
                principais_areas = tempo_total_paradas_area(dados_filtrados).sort_values(ascending=False).head(2).index.tolist()
            
            principais_causas = []
            if 'Parada' in dados_filtrados.columns:
                principais_causas = pareto_causas_parada(dados_filtrados).sort_values(ascending=False).head(3).index.tolist()
            
            # Gera recomendações com base nos dados analisados
            st.markdown("### 💡 Recomendações baseadas na análise")
            
            recomendacoes = []
            
            # Recomendações baseadas na disponibilidade
            if disponibilidade < 85:
                recomendacoes.append(f"**Atenção à disponibilidade**: A disponibilidade está em {disponibilidade:.1f}%, abaixo do ideal (>90%). Priorize ações para reduzir o tempo total de paradas.")
            
            # Recomendações baseadas no tempo médio de parada
            if tmp_horas > 1:
                recomendacoes.append(f"**Reduzir tempo médio de parada**: O tempo médio de parada está em {tmp_horas:.2f}h, considerado alto. Implemente procedimentos mais eficientes para resolução de problemas.")
            
            # Recomendações baseadas nas áreas responsáveis
            if principais_areas:
                areas_str = " e ".join(principais_areas)
                recomendacoes.append(f"**Foco em áreas críticas**: As áreas de {areas_str} são responsáveis pela maior parte do tempo de parada. Desenvolva planos de ação específicos para estas áreas.")
            
            # Recomendações baseadas nas causas de parada
            if principais_causas:
                causas_str = ", ".join(principais_causas)
                recomendacoes.append(f"**Atacar causas principais**: As principais causas de parada são: {causas_str}. Implemente contramedidas específicas para estas causas.")
            
            # Recomendações baseadas no percentual de paradas críticas
            if percentual_criticas > 20:
                recomendacoes.append(f"**Reduzir paradas críticas**: {percentual_criticas:.1f}% das paradas são consideradas críticas (>1h). Estabeleça protocolos de resposta rápida para evitar que paradas se estendam.")
            
            # Exibe as recomendações
            if recomendacoes:
                for rec in recomendacoes:
                    st.markdown(f"- {rec}")
            else:
                st.markdown("- Os indicadores analisados estão dentro dos parâmetros esperados. Continue monitorando e aplicando as boas práticas atuais.")
            
            # Adiciona recomendação genérica sobre análise contínua
            st.markdown("- **Análise contínua**: Mantenha o monitoramento regular dos indicadores e estabeleça metas de melhoria contínua.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão para exportar relatório
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # Botão para exportar dados filtrados
            st.markdown(
                get_download_link(dados_filtrados, 'dados_filtrados.xlsx', '📥 Exportar Dados Filtrados'),
                unsafe_allow_html=True
            )
        
        with col2:
            # Botão para exportar resumo por área
            if 'Área Responsável' in dados_filtrados.columns:
                resumo_area = dados_filtrados.groupby('Área Responsável').agg({
                    'Duração': ['count', 'sum', 'mean']
                })
                resumo_area.columns = ['Número de Paradas', 'Duração Total', 'Duração Média']
                
                st.markdown(
                    get_download_link(resumo_area.reset_index(), 'resumo_areas.xlsx', '📥 Exportar Resumo por Área'),
                    unsafe_allow_html=True
                )
            else:
                st.markdown("Coluna 'Área Responsável' não disponível")
        
        with col3:
            # Botão para exportar paradas críticas
            if not paradas_criticas.empty:
                st.markdown(
                    get_download_link(paradas_criticas, 'paradas_criticas.xlsx', '📥 Exportar Paradas Críticas'),
                    unsafe_allow_html=True
                )
            else:
                st.markdown("Sem paradas críticas no período")
        
                st.markdown('</div>', unsafe_allow_html=True)

# ... outras funções permanecem iguais ...

# ----- FUNÇÃO PRINCIPAL -----
def main():
    """Função principal que controla o fluxo da aplicação."""
    # Inicializa o estado da sessão se necessário
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    if 'first_load' not in st.session_state:
        st.session_state.first_load = False
    
    # Menu lateral
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu Principal",
            options=["Dashboard", "Dados", "Sobre"],
            icons=["speedometer2", "table", "info-circle"],
            menu_icon="gear",
            default_index=0
        )
    
    # Título principal
    st.markdown('<div class="main-title">Análise de Eficiência de Máquinas</div>', unsafe_allow_html=True)
    
    if selected == "Dashboard":
        # Seção de upload de arquivo
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("### 📁 Carregar Dados")
            
            uploaded_file = st.file_uploader("Selecione um arquivo Excel com os dados de paradas:", type=["xlsx", "xls"])
            
            if uploaded_file is not None:
                with st.spinner("Carregando e processando dados..."):
                    try:
                        # Carrega o arquivo Excel
                        df_raw = pd.read_excel(uploaded_file)
                        
                        # Processa os dados
                        df_processed = processar_dados(df_raw)
                        
                        # Atualiza o estado da sessão
                        st.session_state.df = df_processed
                        
                        # Exibe mensagem de sucesso
                        st.success(f"✅ Dados carregados com sucesso! {len(df_processed)} registros encontrados.")
                        
                        # Exibe informações básicas sobre os dados
                        if df_processed is not None and not df_processed.empty:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total de Registros", len(df_processed))
                            
                            with col2:
                                maquinas_unicas = df_processed['Máquina'].nunique()
                                st.metric("Máquinas Diferentes", maquinas_unicas)
                            
                            with col3:
                                periodo = f"{df_processed['Inicio'].min().strftime('%d/%m/%Y')} a {df_processed['Inicio'].max().strftime('%d/%m/%Y')}"
                                st.metric("Período dos Dados", periodo)
                    
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo: {str(e)}")
                        st.session_state.df = None
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Se houver dados carregados, exibe os filtros e a análise
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
                    # Filtro de período
                    st.markdown("Selecione o Período:")
                    data_min = st.session_state.df['Inicio'].min().date()
                    data_max = st.session_state.df['Inicio'].max().date()
                    
                    # Define valores padrão para o período (último mês disponível)
                    data_fim_padrao = data_max
                    data_inicio_padrao = max(data_min, data_max - pd.Timedelta(days=30))
                    
                    # Widgets de seleção de data
                    data_inicio = st.date_input("Data de Início", 
                                               value=data_inicio_padrao, 
                                               min_value=data_min, 
                                               max_value=data_max)
                    
                    data_fim = st.date_input("Data de Fim", 
                                            value=data_fim_padrao, 
                                            min_value=data_min, 
                                            max_value=data_max)
                    
                    # Verifica se a data de início é posterior à data de fim
                    if data_inicio > data_fim:
                        st.warning("⚠️ A data de início não pode ser posterior à data de fim. Ajustando automaticamente.")
                        data_inicio = data_fim
                
                # Botão para analisar
                if st.button("Analisar", key="btn_analisar"):
                    with st.spinner("Analisando dados..."):
                        analisar_dados(st.session_state.df, maquina_selecionada, data_inicio, data_fim)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Realiza a análise com os filtros padrão na primeira carga
            if not st.session_state.first_load and st.session_state.df is not None:
                st.session_state.first_load = True
                # Usa o último mês disponível como período padrão para a primeira análise
                data_max = st.session_state.df['Inicio'].max().date()
                data_inicio_padrao = max(data_min, data_max - pd.Timedelta(days=30))
                analisar_dados(st.session_state.df, "Todas", data_inicio_padrao, data_max)
    
    elif selected == "Dados":
        if st.session_state.df is not None:
            st.markdown('<div class="section-title">Visualização dos Dados</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                # Opções de filtro para visualização
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Filtro de máquina
                    maquinas_para_filtro = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    maquina_filtro = st.selectbox("Filtrar por Máquina:", maquinas_para_filtro)
                
                with col2:
                    # Filtro de data inicial
                    data_min = st.session_state.df['Inicio'].min().date()
                    data_max = st.session_state.df['Inicio'].max().date()
                    data_inicio_filtro = st.date_input("Data Inicial:", 
                                                     value=data_min,
                                                     min_value=data_min,
                                                     max_value=data_max,
                                                     key="data_inicio_filtro")
                
                with col3:
                    # Filtro de data final
                    data_fim_filtro = st.date_input("Data Final:", 
                                                   value=data_max,
                                                   min_value=data_min,
                                                   max_value=data_max,
                                                   key="data_fim_filtro")
                
                # Aplica os filtros
                dados_filtrados = st.session_state.df.copy()
                
                if maquina_filtro != "Todas":
                    dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina_filtro]
                
                # Filtra por período
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
                - Filtragem por máquina e período personalizado
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
