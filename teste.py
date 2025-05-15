import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64
from streamlit_option_menu import option_menu
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
import plotly.figure_factory as ff
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

# Suprimir avisos
warnings.filterwarnings("ignore")

# ----- CONFIGURAÇÃO DA PÁGINA -----
st.set_page_config(
    page_title="Análise de Eficiência de Máquinas 3.0",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----- ESTILOS CSS OTIMIZADOS -----
def aplicar_estilos():
    """Aplica estilos CSS otimizados e melhorados para a aplicação."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f8f9fa;
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
            font-family: 'Poppins', sans-serif;
            color: #20232a;
        }

        .main-title {
            font-size: 2.5rem;
            color: #264653;
            font-weight: 600;
            letter-spacing: 1px;
        }

        .section-title {
            font-size: 1.8rem;
            color: #2a9d8f;
            font-weight: 600;
            border-bottom: 2px solid #2a9d8f;
            padding-bottom: 5px;
            width: fit-content;
            margin: 0 auto 20px auto;
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
            transition: all 0.3s ease;
            font-weight: 500;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .stButton > button:hover {
            background-color: #21867a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        /* Caixas de Conteúdo */
        .content-box {
            background-color: #ffffff;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border-left: 4px solid #2a9d8f;
        }

        .content-box:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
            transform: translateY(-3px);
        }

        .metrics-container .metric-box {
            border-top: 3px solid #2a9d8f;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            padding: 15px;
            border-radius: 8px;
            background-color: #f8f9fa;
            margin-bottom: 15px;
        }

        .metrics-container .metric-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }

        .metric-value {
            font-size: 2.2rem;
            color: #1d3557;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .metric-label {
            color: #457b9d;
            font-size: 1rem;
            font-weight: 500;
        }

        /* Gráficos */
        .chart-container {
            background-color: #f7f9fb;
            padding: 25px;
            margin-top: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border: 1px solid #e9ecef;
        }

        .chart-container:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }

        /* Upload de Arquivos */
        .uploadedFile {
            border: 2px dashed #2a9d8f;
            border-radius: 8px;
            padding: 1rem;
            background-color: #f0f9f8;
            transition: all 0.3s ease;
        }

        .uploadedFile:hover {
            background-color: #e6f5f3;
            border-color: #21867a;
        }

        /* Abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #f0f2f6;
            border-radius: 5px 5px 0 0;
            padding: 10px 20px;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background-color: #2a9d8f;
            color: white;
        }

        /* Alertas e Notificações */
        .stAlert {
            border-radius: 8px;
            border-left: 5px solid;
            padding: 15px;
            margin-bottom: 20px;
        }

        .stAlert.info {
            background-color: #e6f3f8;
            border-left-color: #3498db;
        }

        .stAlert.warning {
            background-color: #fef6e7;
            border-left-color: #f39c12;
        }

        .stAlert.error {
            background-color: #fae9e8;
            border-left-color: #e74c3c;
        }

        .stAlert.success {
            background-color: #e8f6ef;
            border-left-color: #2ecc71;
        }

        /* Rodapé */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9rem;
            border-top: 1px solid #dee2e6;
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
            .content-box {
                padding: 15px;
            }
        }

        /* Tooltip personalizado */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        /* Animação de carregamento */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 3px 8px;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 10px;
            margin-right: 5px;
        }

        .badge-primary {
            background-color: #2a9d8f;
            color: white;
        }

        .badge-warning {
            background-color: #f39c12;
            color: white;
        }

        .badge-danger {
            background-color: #e74c3c;
            color: white;
        }

        .badge-success {
            background-color: #2ecc71;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----- FUNÇÕES AUXILIARES MELHORADAS -----
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
    if mes_ano == "Todos":
        return "Todos os Meses"

    try:
        data = datetime.strptime(mes_ano, "%Y-%m")
        meses_pt = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }
        return f"{meses_pt[data.month]} {data.year}"
    except:
        return mes_ano


@st.cache_data
def processar_dados(df):
    """Processa e limpa os dados do DataFrame com tratamento de erros aprimorado."""
    try:
        # Cria uma cópia para evitar SettingWithCopyWarning
        df_processado = df.copy()

        # Verifica colunas obrigatórias
        colunas_obrigatorias = ["Máquina", "Inicio", "Fim", "Duração"]
        colunas_faltantes = [
            col
            for col in colunas_obrigatorias
            if col not in df_processado.columns
        ]

        if colunas_faltantes:
            st.error(
                f"Erro: Colunas obrigatórias faltando: {', '.join(colunas_faltantes)}"
            )
            return None

        # Mapeamento de máquinas com tratamento para códigos desconhecidos
        machine_mapping = {
            78: "PET",
            79: "TETRA 1000",
            80: "TETRA 200",
            89: "SIG 1000",
            91: "SIG 200",
        }

        # Tratamento da coluna Máquina
        if "Máquina" in df_processado.columns:
            # Converte para numérico se possível
            try:
                df_processado["Máquina"] = pd.to_numeric(
                    df_processado["Máquina"], errors="ignore"
                )
            except:
                pass

            # Aplica o mapeamento
            df_processado["Máquina"] = df_processado["Máquina"].apply(
                lambda x: machine_mapping.get(x, f"Máquina {x}")
            )

        # Converte as colunas de tempo para o formato datetime
        for col in ["Inicio", "Fim"]:
            if col in df_processado.columns:
                df_processado[col] = pd.to_datetime(
                    df_processado[col], errors="coerce"
                )

        # Processa a coluna de duração
        if "Duração" in df_processado.columns:
            # Verifica o tipo de dados da coluna Duração
            if df_processado["Duração"].dtype == "timedelta64[ns]":
                # Já está no formato correto
                pass
            elif isinstance(df_processado["Duração"].iloc[0], str):
                # Tenta converter strings no formato HH:MM:SS para timedelta
                def parse_duration(duration_str):
                    try:
                        if pd.isna(duration_str) or duration_str == "":
                            return pd.NaT

                        # Tenta o formato HH:MM:SS
                        parts = duration_str.split(":")
                        if len(parts) == 3:
                            hours, minutes, seconds = map(int, parts)
                            return pd.Timedelta(
                                hours=hours, minutes=minutes, seconds=seconds
                            )
                        # Tenta outros formatos comuns
                        elif len(parts) == 2:
                            minutes, seconds = map(int, parts)
                            return pd.Timedelta(
                                minutes=minutes, seconds=seconds
                            )
                        else:
                            # Tenta converter diretamente
                            return pd.to_timedelta(duration_str)
                    except:
                        return pd.NaT

                df_processado["Duração"] = df_processado["Duração"].apply(
                    parse_duration
                )
            else:
                # Tenta converter diretamente para timedelta
                try:
                    df_processado["Duração"] = pd.to_timedelta(
                        df_processado["Duração"]
                    )
                except:
                    st.warning(
                        "Aviso: Não foi possível converter a coluna 'Duração' para o formato correto."
                    )

        # Calcula a duração se estiver faltando mas tiver Inicio e Fim
        duracoes_invalidas = df_processado["Duração"].isna()
        if (
            duracoes_invalidas.any()
            and not df_processado["Inicio"].isna().any()
            and not df_processado["Fim"].isna().any()
        ):
            df_processado.loc[duracoes_invalidas, "Duração"] = (
                df_processado.loc[duracoes_invalidas, "Fim"]
                - df_processado.loc[duracoes_invalidas, "Inicio"]
            )

        # Adiciona colunas de ano, mês e ano-mês para facilitar a filtragem
        df_processado["Ano"] = df_processado["Inicio"].dt.year
        df_processado["Mês"] = df_processado["Inicio"].dt.month
        df_processado["Mês_Nome"] = df_processado["Inicio"].dt.strftime(
            "%B"
        )  # Nome do mês
        df_processado["Ano-Mês"] = df_processado["Inicio"].dt.strftime("%Y-%m")
        df_processado["Dia da Semana"] = df_processado["Inicio"].dt.day_name()
        df_processado["Hora do Dia"] = df_processado["Inicio"].dt.hour
        df_processado["Semana do Ano"] = (
            df_processado["Inicio"].dt.isocalendar().week
        )

        # Adiciona coluna de duração em horas para facilitar análises
        df_processado["Duração (horas)"] = (
            df_processado["Duração"].dt.total_seconds() / 3600
        )

        # Remove registros com valores ausentes nas colunas essenciais
        df_processado = df_processado.dropna(
            subset=["Máquina", "Inicio", "Fim", "Duração"]
        )

        # Verifica se há dados válidos após o processamento
        if len(df_processado) == 0:
            st.error(
                "Erro: Nenhum dado válido após o processamento. Verifique o formato do arquivo."
            )
            return None

        return df_processado

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
        return None


# ----- FUNÇÕES DE EXPORTAÇÃO MELHORADAS -----
def get_download_link(df, filename, link_text):
    """Gera um link para download de um DataFrame como arquivo Excel."""
    try:
        # Cria um buffer para o arquivo Excel
        output = BytesIO()

        # Cria um escritor Excel
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Dados", index=False)

            # Acessa a planilha para formatação
            workbook = writer.book
            worksheet = writer.sheets["Dados"]

            # Formata cabeçalhos
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "top",
                    "fg_color": "#D7E4BC",
                    "border": 1,
                }
            )

            # Aplica formato aos cabeçalhos
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Ajusta largura das colunas
            for i, col in enumerate(df.columns):
                column_width = max(
                    df[col].astype(str).map(len).max(), len(col) + 2
                )
                worksheet.set_column(i, i, column_width)

        # Obtém os dados do buffer
        output.seek(0)
        excel_data = output.read()

        # Codifica os dados em base64
        b64 = base64.b64encode(excel_data).decode()

        # Cria o link de download
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-button">{link_text}</a>'
        return href
    except Exception as e:
        st.error(f"Erro ao gerar link de download: {str(e)}")
        return f"<p>Erro ao gerar download: {str(e)}</p>"


def exportar_pdf(fig, titulo, nome_arquivo):
    """Exporta um gráfico como PDF."""
    try:
        # Implementação futura
        pass
    except Exception as e:
        st.error(f"Erro ao exportar PDF: {str(e)}")


# ----- NOVAS FUNÇÕES DE ANÁLISE PREDITIVA -----
@st.cache_data
def preparar_dados_previsao(df):
    """Prepara os dados para modelos de previsão."""
    try:
        if df is None or len(df) < 10:  # Verifica se há dados suficientes
            return None, None, None, None

        # Agrupa dados por dia
        df_diario = df.copy()
        df_diario["Data"] = df_diario["Inicio"].dt.date

        # Calcula métricas diárias
        dados_diarios = (
            df_diario.groupby("Data")
            .agg({"Duração": ["count", "sum"], "Duração (horas)": "sum"})
            .reset_index()
        )

        dados_diarios.columns = [
            "Data",
            "Num_Paradas",
            "Duracao_Total",
            "Horas_Paradas",
        ]

        # Converte Data para datetime e cria features temporais
        dados_diarios["Data"] = pd.to_datetime(dados_diarios["Data"])
        dados_diarios["DiaSemana"] = dados_diarios["Data"].dt.dayofweek
        dados_diarios["Mes"] = dados_diarios["Data"].dt.month
        dados_diarios["DiaMes"] = dados_diarios["Data"].dt.day

        # Adiciona dias sequenciais para tendência
        dados_diarios["Dia_Sequencial"] = range(len(dados_diarios))

        # Cria média móvel de 3 dias para cada métrica
        dados_diarios["MM3_Num_Paradas"] = (
            dados_diarios["Num_Paradas"]
            .rolling(window=3, min_periods=1)
            .mean()
        )
        dados_diarios["MM3_Horas_Paradas"] = (
            dados_diarios["Horas_Paradas"]
            .rolling(window=3, min_periods=1)
            .mean()
        )

        # Features para o modelo
        features = [
            "DiaSemana",
            "Mes",
            "DiaMes",
            "Dia_Sequencial",
            "MM3_Num_Paradas",
            "MM3_Horas_Paradas",
        ]

        # Divide em conjunto de treino e teste (80% treino, 20% teste)
        train_size = int(len(dados_diarios) * 0.8)
        train_data = dados_diarios.iloc[:train_size]
        test_data = dados_diarios.iloc[train_size:]

        return dados_diarios, features, train_data, test_data

    except Exception as e:
        st.error(f"Erro ao preparar dados para previsão: {str(e)}")
        return None, None, None, None


@st.cache_data
def treinar_modelo_previsao(train_data, features, target):
    """Treina um modelo de previsão usando Random Forest."""
    try:
        if train_data is None or len(train_data) < 5:
            return None, None

        # Prepara dados de treino
        X_train = train_data[features]
        y_train = train_data[target]

        # Treina o modelo
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Avalia no conjunto de treino
        y_pred_train = model.predict(X_train)
        train_mae = mean_absolute_error(y_train, y_pred_train)
        train_r2 = r2_score(y_train, y_pred_train)

        return model, (train_mae, train_r2)

    except Exception as e:
        st.error(f"Erro ao treinar modelo de previsão: {str(e)}")
        return None, None


@st.cache_data
def avaliar_modelo_previsao(model, test_data, features, target):
    """Avalia o modelo de previsão no conjunto de teste."""
    try:
        if model is None or test_data is None or len(test_data) < 3:
            return None, None

        # Prepara dados de teste
        X_test = test_data[features]
        y_test = test_data[target]

        # Faz previsões
        y_pred = model.predict(X_test)

        # Calcula métricas
        test_mae = mean_absolute_error(y_test, y_pred)
        test_r2 = r2_score(y_test, y_pred)

        # Prepara dados para visualização
        resultados = pd.DataFrame(
            {"Data": test_data["Data"], "Real": y_test, "Previsto": y_pred}
        )

        return resultados, (test_mae, test_r2)

    except Exception as e:
        st.error(f"Erro ao avaliar modelo de previsão: {str(e)}")
        return None, None


@st.cache_data
def fazer_previsao_futura(model, dados_diarios, features, dias_futuros=7):
    """Faz previsão para os próximos dias."""
    try:
        if model is None or dados_diarios is None or len(dados_diarios) < 5:
            return None

        # Obtém o último dia dos dados
        ultimo_dia = dados_diarios["Data"].max()

        # Cria dataframe para dias futuros
        datas_futuras = [
            ultimo_dia + timedelta(days=i + 1) for i in range(dias_futuros)
        ]
        df_futuro = pd.DataFrame({"Data": datas_futuras})

        # Adiciona features temporais
        df_futuro["DiaSemana"] = df_futuro["Data"].dt.dayofweek
        df_futuro["Mes"] = df_futuro["Data"].dt.month
        df_futuro["DiaMes"] = df_futuro["Data"].dt.day

        # Adiciona dias sequenciais (continuando a sequência)
        ultimo_dia_seq = dados_diarios["Dia_Sequencial"].max()
        df_futuro["Dia_Sequencial"] = range(
            ultimo_dia_seq + 1, ultimo_dia_seq + 1 + dias_futuros
        )

        # Obtém as médias móveis mais recentes
        ultima_mm3_paradas = dados_diarios["MM3_Num_Paradas"].iloc[-1]
        ultima_mm3_horas = dados_diarios["MM3_Horas_Paradas"].iloc[-1]

        # Inicializa as médias móveis no dataframe futuro
        df_futuro["MM3_Num_Paradas"] = ultima_mm3_paradas
        df_futuro["MM3_Horas_Paradas"] = ultima_mm3_horas

        # Faz previsões para cada dia futuro
        previsoes_num_paradas = []
        previsoes_horas_paradas = []

        # Modelo para número de paradas
        modelo_num_paradas = model[0]
        # Modelo para horas de paradas
        modelo_horas_paradas = model[1]

        # Para cada dia futuro, faz a previsão e atualiza a média móvel
        for i in range(dias_futuros):
            # Obtém as features para o dia atual
            X_futuro = df_futuro.iloc[i : i + 1][features]

            # Faz a previsão
            prev_num_paradas = modelo_num_paradas.predict(X_futuro)[0]
            prev_horas_paradas = modelo_horas_paradas.predict(X_futuro)[0]

            # Armazena as previsões
            previsoes_num_paradas.append(prev_num_paradas)
            previsoes_horas_paradas.append(prev_horas_paradas)

            # Atualiza a média móvel para o próximo dia se não for o último
            if i < dias_futuros - 1:
                # Calcula nova média móvel (média dos 2 últimos dias reais + dia previsto)
                if i == 0:
                    # Para o primeiro dia futuro, usa os 2 últimos dias reais + previsão
                    ultimos_num_paradas = list(
                        dados_diarios["Num_Paradas"].iloc[-2:]
                    ) + [prev_num_paradas]
                    ultimos_horas_paradas = list(
                        dados_diarios["Horas_Paradas"].iloc[-2:]
                    ) + [prev_horas_paradas]
                elif i == 1:
                    # Para o segundo dia futuro, usa o último dia real + 2 previsões
                    ultimos_num_paradas = [
                        dados_diarios["Num_Paradas"].iloc[-1]
                    ] + previsoes_num_paradas
                    ultimos_horas_paradas = [
                        dados_diarios["Horas_Paradas"].iloc[-1]
                    ] + previsoes_horas_paradas
                else:
                    # Para os demais dias, usa apenas as previsões
                    ultimos_num_paradas = previsoes_num_paradas[i - 2 : i + 1]
                    ultimos_horas_paradas = previsoes_horas_paradas[
                        i - 2 : i + 1
                    ]

                # Atualiza as médias móveis
                df_futuro.loc[i + 1, "MM3_Num_Paradas"] = sum(
                    ultimos_num_paradas
                ) / len(ultimos_num_paradas)
                df_futuro.loc[i + 1, "MM3_Horas_Paradas"] = sum(
                    ultimos_horas_paradas
                ) / len(ultimos_horas_paradas)

        # Adiciona as previsões ao dataframe
        df_futuro["Previsao_Num_Paradas"] = previsoes_num_paradas
        df_futuro["Previsao_Horas_Paradas"] = previsoes_horas_paradas

        return df_futuro

    except Exception as e:
        st.error(f"Erro ao fazer previsão futura: {str(e)}")
        return None


# ----- FUNÇÕES DE ANÁLISE DE TENDÊNCIAS -----
@st.cache_data
def calcular_tendencias(df, coluna, periodo="mensal"):
    """Calcula tendências ao longo do tempo para uma métrica específica."""
    try:
        if df is None or len(df) < 5:
            return None, None

        # Cria cópia para evitar modificações no dataframe original
        df_tendencia = df.copy()

        # Define o agrupamento com base no período
        if periodo == "mensal":
            df_tendencia["Periodo"] = df_tendencia["Inicio"].dt.strftime(
                "%Y-%m"
            )
        elif periodo == "semanal":
            df_tendencia["Periodo"] = df_tendencia["Inicio"].dt.strftime(
                "%Y-%U"
            )
        elif periodo == "diario":
            df_tendencia["Periodo"] = df_tendencia["Inicio"].dt.strftime(
                "%Y-%m-%d"
            )
        else:
            df_tendencia["Periodo"] = df_tendencia["Inicio"].dt.strftime(
                "%Y-%m"
            )

        # Agrupa os dados pelo período
        if coluna == "Contagem":
            # Conta o número de ocorrências
            dados_agrupados = (
                df_tendencia.groupby("Periodo")
                .size()
                .reset_index(name="Valor")
            )
        elif coluna == "Duração":
            # Soma a duração das paradas
            dados_agrupados = (
                df_tendencia.groupby("Periodo")["Duração"]
                .sum()
                .reset_index(name="Valor")
            )
            # Converte para horas
            dados_agrupados["Valor"] = (
                dados_agrupados["Valor"].dt.total_seconds() / 3600
            )
        else:
            # Para outras colunas, calcula a média
            dados_agrupados = (
                df_tendencia.groupby("Periodo")[coluna]
                .mean()
                .reset_index(name="Valor")
            )

        # Ordena por período
        dados_agrupados = dados_agrupados.sort_values("Periodo")

        # Calcula a tendência usando regressão linear
        X = np.arange(len(dados_agrupados)).reshape(-1, 1)
        y = dados_agrupados["Valor"].values

        modelo = LinearRegression()
        modelo.fit(X, y)

        # Calcula valores previstos e tendência
        y_pred = modelo.predict(X)

        # Determina a direção da tendência
        coeficiente = modelo.coef_[0]

        if abs(coeficiente) < 0.01:
            direcao = "estável"
        elif coeficiente > 0:
            direcao = "crescente"
        else:
            direcao = "decrescente"

        # Calcula a variação percentual
        if len(y) >= 2 and y[0] != 0:
            variacao_pct = ((y[-1] - y[0]) / y[0]) * 100
        else:
            variacao_pct = 0

        # Retorna os dados e as informações da tendência
        return dados_agrupados, {
            "coeficiente": coeficiente,
            "direcao": direcao,
            "variacao_pct": variacao_pct,
            "valores_previstos": y_pred,
        }

    except Exception as e:
        st.error(f"Erro ao calcular tendências: {str(e)}")
        return None, None


@st.cache_data
def identificar_padroes_ciclicos(df, coluna="Contagem", periodo="mensal"):
    """Identifica padrões cíclicos nos dados."""
    try:
        if (
            df is None or len(df) < 12
        ):  # Precisa de pelo menos 12 pontos para análise cíclica
            return None, None

        # Prepara os dados de forma semelhante à função de tendências
        df_padrao = df.copy()

        # Define o agrupamento com base no período
        if periodo == "mensal":
            df_padrao["Periodo"] = df_padrao["Inicio"].dt.strftime("%Y-%m")
            df_padrao["Mes"] = df_padrao["Inicio"].dt.month
        elif periodo == "semanal":
            df_padrao["Periodo"] = df_padrao["Inicio"].dt.strftime("%Y-%U")
            df_padrao["DiaSemana"] = df_padrao["Inicio"].dt.dayofweek
        elif periodo == "diario":
            df_padrao["Periodo"] = df_padrao["Inicio"].dt.strftime("%Y-%m-%d")
            df_padrao["Hora"] = df_padrao["Inicio"].dt.hour
        else:
            df_padrao["Periodo"] = df_padrao["Inicio"].dt.strftime("%Y-%m")
            df_padrao["Mes"] = df_padrao["Inicio"].dt.month

        # Agrupa os dados pelo período
        if coluna == "Contagem":
            # Conta o número de ocorrências
            dados_agrupados = (
                df_padrao.groupby("Periodo").size().reset_index(name="Valor")
            )
        elif coluna == "Duração":
            # Soma a duração das paradas
            dados_agrupados = (
                df_padrao.groupby("Periodo")["Duração"]
                .sum()
                .reset_index(name="Valor")
            )
            # Converte para horas
            dados_agrupados["Valor"] = (
                dados_agrupados["Valor"].dt.total_seconds() / 3600
            )
        else:
            # Para outras colunas, calcula a média
            dados_agrupados = (
                df_padrao.groupby("Periodo")[coluna]
                .mean()
                .reset_index(name="Valor")
            )

        # Adiciona informações temporais
        if periodo == "mensal":
            dados_agrupados["Ciclo"] = [
                int(p.split("-")[1]) for p in dados_agrupados["Periodo"]
            ]
        elif periodo == "semanal":
            dados_agrupados["Ciclo"] = [
                int(p.split("-")[1]) % 52 for p in dados_agrupados["Periodo"]
            ]
        elif periodo == "diario":
            dados_agrupados["Ciclo"] = [
                datetime.strptime(p, "%Y-%m-%d").weekday()
                for p in dados_agrupados["Periodo"]
            ]

        # Analisa o padrão cíclico
        ciclo_medio = (
            dados_agrupados.groupby("Ciclo")["Valor"].mean().reset_index()
        )

        # Identifica os picos e vales
        if len(ciclo_medio) > 2:
            valor_max = ciclo_medio["Valor"].max()
            valor_min = ciclo_medio["Valor"].min()

            pico = ciclo_medio.loc[
                ciclo_medio["Valor"] == valor_max, "Ciclo"
            ].iloc[0]
            vale = ciclo_medio.loc[
                ciclo_medio["Valor"] == valor_min, "Ciclo"
            ].iloc[0]

            # Mapeia os nomes dos ciclos
            if periodo == "mensal":
                meses = {
                    1: "Janeiro",
                    2: "Fevereiro",
                    3: "Março",
                    4: "Abril",
                    5: "Maio",
                    6: "Junho",
                    7: "Julho",
                    8: "Agosto",
                    9: "Setembro",
                    10: "Outubro",
                    11: "Novembro",
                    12: "Dezembro",
                }
                pico_nome = meses.get(pico, str(pico))
                vale_nome = meses.get(vale, str(vale))
            elif periodo == "semanal":
                dias = {
                    0: "Segunda",
                    1: "Terça",
                    2: "Quarta",
                    3: "Quinta",
                    4: "Sexta",
                    5: "Sábado",
                    6: "Domingo",
                }
                pico_nome = dias.get(pico % 7, str(pico))
                vale_nome = dias.get(vale % 7, str(vale))
            else:
                pico_nome = str(pico)
                vale_nome = str(vale)

            # Calcula a amplitude do ciclo
            amplitude = valor_max - valor_min
            amplitude_pct = (
                (amplitude / valor_min * 100) if valor_min > 0 else 0
            )

            padroes = {
                "pico": pico,
                "pico_nome": pico_nome,
                "vale": vale,
                "vale_nome": vale_nome,
                "amplitude": amplitude,
                "amplitude_pct": amplitude_pct,
            }
        else:
            padroes = None

        return ciclo_medio, padroes

    except Exception as e:
        st.error(f"Erro ao identificar padrões cíclicos: {str(e)}")
        return None, None


# ----- FUNÇÕES DE ANÁLISE DE CORRELAÇÃO -----
@st.cache_data
def analisar_correlacoes(df):
    """Analisa correlações entre diferentes tipos de paradas e áreas responsáveis."""
    try:
        if df is None or len(df) < 10:
            return None

        # Cria uma cópia para evitar modificações no dataframe original
        df_corr = df.copy()

        # Verifica se as colunas necessárias existem
        if (
            "Parada" not in df_corr.columns
            or "Área Responsável" not in df_corr.columns
        ):
            return None

        # Cria uma tabela de contingência entre tipos de parada e áreas responsáveis
        tabela_cont = pd.crosstab(
            df_corr["Parada"],
            df_corr["Área Responsável"],
            values=df_corr["Duração (horas)"],
            aggfunc="sum",
        ).fillna(0)

        # Calcula a matriz de correlação
        matriz_corr = tabela_cont.corr()

        return matriz_corr

    except Exception as e:
        st.error(f"Erro ao analisar correlações: {str(e)}")
        return None


# ----- FUNÇÕES DE DETECÇÃO DE ANOMALIAS -----
@st.cache_data
def detectar_anomalias(
    df, coluna="Duração (horas)", metodo="zscore", limiar=3.0
):
    """Detecta valores anômalos nos dados usando diferentes métodos."""
    try:
        if df is None or len(df) < 10:
            return None, None

        # Cria uma cópia para evitar modificações no dataframe original
        df_anomalias = df.copy()

        # Verifica se a coluna existe
        if coluna not in df_anomalias.columns:
            return None, None

        # Obtém os valores da coluna
        valores = df_anomalias[coluna].values

        # Detecta anomalias com base no método escolhido
        if metodo == "zscore":
            # Método Z-Score
            media = np.mean(valores)
            desvio_padrao = np.std(valores)

            if desvio_padrao == 0:
                return None, None

            z_scores = np.abs((valores - media) / desvio_padrao)
            anomalias = z_scores > limiar

        elif metodo == "iqr":
            # Método IQR (Intervalo Interquartil)
            q1 = np.percentile(valores, 25)
            q3 = np.percentile(valores, 75)
            iqr = q3 - q1

            limite_inferior = q1 - 1.5 * iqr
            limite_superior = q3 + 1.5 * iqr

            anomalias = (valores < limite_inferior) | (
                valores > limite_superior
            )

        else:
            # Método padrão: Z-Score
            media = np.mean(valores)
            desvio_padrao = np.std(valores)

            if desvio_padrao == 0:
                return None, None

            z_scores = np.abs((valores - media) / desvio_padrao)
            anomalias = z_scores > limiar

        # Marca as anomalias no dataframe
        df_anomalias["Anomalia"] = anomalias

        # Filtra apenas as anomalias
        df_anomalias_filtrado = df_anomalias[df_anomalias["Anomalia"]]

        # Calcula estatísticas das anomalias
        num_anomalias = len(df_anomalias_filtrado)
        pct_anomalias = (num_anomalias / len(df_anomalias)) * 100

        estatisticas = {
            "num_anomalias": num_anomalias,
            "pct_anomalias": pct_anomalias,
            "media_anomalias": (
                df_anomalias_filtrado[coluna].mean()
                if num_anomalias > 0
                else 0
            ),
            "max_anomalia": (
                df_anomalias_filtrado[coluna].max() if num_anomalias > 0 else 0
            ),
        }

        return df_anomalias_filtrado, estatisticas

    except Exception as e:
        st.error(f"Erro ao detectar anomalias: {str(e)}")
        return None, None


# ----- FUNÇÕES DE ANÁLISE DE IMPACTO -----
@st.cache_data
def analisar_impacto_paradas(df, tempo_programado=24 * 7):
    """Analisa o impacto das paradas na produção."""
    try:
        if df is None or len(df) < 5:
            return None

        # Cria uma cópia para evitar modificações no dataframe original
        df_impacto = df.copy()

        # Calcula o tempo total de paradas em horas
        tempo_total_parado = df_impacto["Duração (horas)"].sum()

        # Calcula a disponibilidade
        disponibilidade = (
            (tempo_programado - tempo_total_parado) / tempo_programado * 100
        )
        disponibilidade = max(0, min(100, disponibilidade))

        # Calcula o impacto por tipo de parada
        impacto_por_tipo = (
            df_impacto.groupby("Parada")["Duração (horas)"]
            .sum()
            .sort_values(ascending=False)
        )

        # Calcula o impacto por área responsável
        impacto_por_area = (
            df_impacto.groupby("Área Responsável")["Duração (horas)"]
            .sum()
            .sort_values(ascending=False)
        )

        # Calcula o impacto por máquina
        impacto_por_maquina = (
            df_impacto.groupby("Máquina")["Duração (horas)"]
            .sum()
            .sort_values(ascending=False)
        )

        # Calcula o impacto financeiro estimado (assumindo um custo por hora de parada)
        custo_por_hora = (
            1000  # Valor fictício, deve ser ajustado conforme a realidade
        )
        impacto_financeiro = tempo_total_parado * custo_por_hora

        return {
            "tempo_total_parado": tempo_total_parado,
            "disponibilidade": disponibilidade,
            "impacto_por_tipo": impacto_por_tipo,
            "impacto_por_area": impacto_por_area,
            "impacto_por_maquina": impacto_por_maquina,
            "impacto_financeiro": impacto_financeiro,
        }

    except Exception as e:
        st.error(f"Erro ao analisar impacto das paradas: {str(e)}")
        return None


# ----- FUNÇÕES DE RECOMENDAÇÃO -----
@st.cache_data
def gerar_recomendacoes(df, analise_impacto=None):
    """Gera recomendações baseadas nos dados e análises."""
    try:
        if df is None or len(df) < 10:
            return []

        recomendacoes = []

        # Analisa os tipos de paradas mais frequentes
        if "Parada" in df.columns:
            paradas_frequentes = df["Parada"].value_counts().head(3)
            for parada, contagem in paradas_frequentes.items():
                recomendacoes.append(
                    f"Implementar plano de ação para reduzir a ocorrência de '{parada}', "
                    f"que representa {contagem} ocorrências no período analisado."
                )

        # Analisa as áreas com maior tempo de parada
        if "Área Responsável" in df.columns:
            areas_criticas = (
                df.groupby("Área Responsável")["Duração (horas)"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
            )
            for area, duracao in areas_criticas.items():
                recomendacoes.append(
                    f"Revisar processos da área '{area}', responsável por {duracao:.1f} horas "
                    f"de paradas no período analisado."
                )

        # Analisa padrões temporais
        if "Hora do Dia" in df.columns:
            horas_criticas = (
                df.groupby("Hora do Dia")
                .size()
                .sort_values(ascending=False)
                .head(3)
            )
            for hora, contagem in horas_criticas.items():
                recomendacoes.append(
                    f"Reforçar supervisão e suporte durante o horário das {hora}h, "
                    f"quando ocorrem mais paradas ({contagem} ocorrências)."
                )

        # Analisa dias da semana com mais paradas
        if "Dia da Semana" in df.columns:
            dias_criticos = (
                df.groupby("Dia da Semana")
                .size()
                .sort_values(ascending=False)
                .head(2)
            )
            for dia, contagem in dias_criticos.items():
                recomendacoes.append(
                    f"Implementar checklist de verificação preventiva às {dia}s-feiras, "
                    f"dia com maior incidência de paradas ({contagem} ocorrências)."
                )

        # Recomendações baseadas na análise de impacto
        if analise_impacto is not None:
            # Recomendação baseada na disponibilidade
            disponibilidade = analise_impacto.get("disponibilidade", 0)
            if disponibilidade < 85:
                recomendacoes.append(
                    f"Priorizar aumento da disponibilidade (atualmente em {disponibilidade:.1f}%) "
                    f"através de manutenção preventiva e redução de paradas não programadas."
                )

            # Recomendação baseada no impacto financeiro
            impacto_financeiro = analise_impacto.get("impacto_financeiro", 0)
            if impacto_financeiro > 50000:
                recomendacoes.append(
                    f"Desenvolver plano de redução de custos para minimizar o impacto financeiro "
                    f"das paradas (estimado em R$ {impacto_financeiro:,.2f} no período)."
                )

        # Adiciona recomendações gerais
        recomendacoes.append(
            "Implementar sistema de gestão visual para acompanhamento em tempo real das paradas, "
            "facilitando a identificação e resolução rápida de problemas."
        )

        recomendacoes.append(
            "Estabelecer reuniões diárias de análise de paradas com representantes das áreas "
            "responsáveis para identificar causas raiz e implementar ações corretivas."
        )

        return recomendacoes

    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {str(e)}")
        return []


# ----- COMPONENTES DE INTERFACE MELHORADOS -----
def exibir_indicadores(disponibilidade, tmp, eficiencia, percentual_criticas):
    """Exibe indicadores em um layout de cartões melhorado."""
    st.markdown(
        '<div class="metrics-container" style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: space-between;">',
        unsafe_allow_html=True,
    )

    # Cartão de Disponibilidade
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="margin-top: 0; color: #2a9d8f;">Disponibilidade</h3>
            <div class="metric-value">{disponibilidade:.1f}%</div>
            <div class="metric-label">Tempo disponível para produção</div>
            <div style="margin-top: 10px; height: 5px; background-color: #f0f0f0; border-radius: 5px;">
                <div style="width: {min(disponibilidade, 100)}%; height: 100%; background-color: {'#2ecc71' if disponibilidade >= 85 else '#f39c12' if disponibilidade >= 70 else '#e74c3c'}; border-radius: 5px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cartão de Tempo Médio de Parada
    tmp_horas = tmp.total_seconds() / 3600 if pd.notna(tmp) else 0
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="margin-top: 0; color: #2a9d8f;">Tempo Médio de Parada</h3>
            <div class="metric-value">{tmp_horas:.2f}h</div>
            <div class="metric-label">Duração média por ocorrência</div>
            <div style="margin-top: 10px; height: 5px; background-color: #f0f0f0; border-radius: 5px;">
                <div style="width: {min(100 - (tmp_horas * 10), 100)}%; height: 100%; background-color: {'#2ecc71' if tmp_horas < 1 else '#f39c12' if tmp_horas < 2 else '#e74c3c'}; border-radius: 5px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cartão de Eficiência Operacional
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="margin-top: 0; color: #2a9d8f;">Eficiência Operacional</h3>
            <div class="metric-value">{eficiencia:.1f}%</div>
            <div class="metric-label">Produtividade do equipamento</div>
            <div style="margin-top: 10px; height: 5px; background-color: #f0f0f0; border-radius: 5px;">
                <div style="width: {min(eficiencia, 100)}%; height: 100%; background-color: {'#2ecc71' if eficiencia >= 85 else '#f39c12' if eficiencia >= 70 else '#e74c3c'}; border-radius: 5px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cartão de Paradas Críticas
    st.markdown(
        f"""
        <div class="metric-box" style="flex: 1; min-width: 200px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="margin-top: 0; color: #2a9d8f;">Paradas Críticas</h3>
            <div class="metric-value">{percentual_criticas:.1f}%</div>
            <div class="metric-label">Percentual de paradas > 1h</div>
            <div style="margin-top: 10px; height: 5px; background-color: #f0f0f0; border-radius: 5px;">
                <div style="width: {min(100 - percentual_criticas, 100)}%; height: 100%; background-color: {'#2ecc71' if percentual_criticas < 10 else '#f39c12' if percentual_criticas < 20 else '#e74c3c'}; border-radius: 5px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def exibir_previsoes(
    df_previsao, titulo="Previsão de Paradas para os Próximos 7 Dias"
):
    """Exibe as previsões em um formato visual aprimorado."""
    if df_previsao is None or len(df_previsao) == 0:
        st.warning("Não há dados suficientes para gerar previsões.")
        return

    st.markdown(
        f'<h3 style="text-align: center; color: #2a9d8f;">{titulo}</h3>',
        unsafe_allow_html=True,
    )

    # Cria abas para diferentes visualizações
    tab1, tab2 = st.tabs(["📊 Gráfico de Previsão", "📋 Tabela de Previsão"])

    with tab1:
        # Formata as datas para exibição
        df_previsao["Data_Formatada"] = df_previsao["Data"].dt.strftime(
            "%d/%m/%Y"
        )

        # Cria gráfico para número de paradas
        fig_num_paradas = px.bar(
            df_previsao,
            x="Data_Formatada",
            y="Previsao_Num_Paradas",
            title="Previsão de Número de Paradas",
            labels={
                "Previsao_Num_Paradas": "Número de Paradas",
                "Data_Formatada": "Data",
            },
            text_auto=".1f",
            color="Previsao_Num_Paradas",
            color_continuous_scale="Blues",
        )

        fig_num_paradas.update_layout(
            xaxis_tickangle=-45,
            autosize=True,
            margin=dict(l=50, r=50, t=80, b=100),
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig_num_paradas, use_container_width=True)

        # Cria gráfico para horas de paradas
        fig_horas_paradas = px.bar(
            df_previsao,
            x="Data_Formatada",
            y="Previsao_Horas_Paradas",
            title="Previsão de Horas de Paradas",
            labels={
                "Previsao_Horas_Paradas": "Horas de Paradas",
                "Data_Formatada": "Data",
            },
            text_auto=".1f",
            color="Previsao_Horas_Paradas",
            color_continuous_scale="Reds",
        )

        fig_horas_paradas.update_layout(
            xaxis_tickangle=-45,
            autosize=True,
            margin=dict(l=50, r=50, t=80, b=100),
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig_horas_paradas, use_container_width=True)

    with tab2:
        # Prepara os dados para a tabela
        tabela_previsao = df_previsao[
            ["Data", "Previsao_Num_Paradas", "Previsao_Horas_Paradas"]
        ].copy()
        tabela_previsao["Data"] = tabela_previsao["Data"].dt.strftime(
            "%d/%m/%Y"
        )
        tabela_previsao.columns = [
            "Data",
            "Número de Paradas Previsto",
            "Horas de Paradas Previsto",
        ]

        # Exibe a tabela
        st.dataframe(
            tabela_previsao,
            column_config={
                "Data": st.column_config.TextColumn("Data"),
                "Número de Paradas Previsto": st.column_config.NumberColumn(
                    "Número de Paradas", format="%.1f"
                ),
                "Horas de Paradas Previsto": st.column_config.NumberColumn(
                    "Horas de Paradas", format="%.2f"
                ),
            },
            use_container_width=True,
        )

        # Adiciona botão para download da previsão
        st.markdown(
            get_download_link(
                tabela_previsao,
                "previsao_paradas.xlsx",
                "📥 Baixar tabela de previsão",
            ),
            unsafe_allow_html=True,
        )


def exibir_recomendacoes(recomendacoes):
    """Exibe recomendações em um formato visualmente atraente."""
    if not recomendacoes:
        st.info(
            "Não foi possível gerar recomendações com os dados disponíveis."
        )
        return

    st.markdown(
        '<h3 style="text-align: center; color: #2a9d8f;">Recomendações para Melhoria</h3>',
        unsafe_allow_html=True,
    )

    # Exibe cada recomendação em um card
    for i, recomendacao in enumerate(recomendacoes):
        st.markdown(
            f"""
            <div style="background-color: white; padding: 15px; margin-bottom: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); border-left: 4px solid #2a9d8f;">
                <div style="display: flex; align-items: flex-start;">
                    <div style="background-color: #2a9d8f; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; justify-content: center; align-items: center; margin-right: 15px; flex-shrink: 0;">
                        {i+1}
                    </div>
                    <div>
                        {recomendacao}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Adiciona nota sobre as recomendações
    st.markdown(
        """
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #6c757d;">
            <p style="margin: 0; color: #6c757d;"><strong>Nota:</strong> Estas recomendações são baseadas na análise dos dados e devem ser avaliadas pela equipe técnica antes da implementação.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def exibir_anomalias(df_anomalias, estatisticas):
    """Exibe anomalias detectadas em um formato visual aprimorado."""
    if df_anomalias is None or estatisticas is None:
        st.info(
            "Não foi possível detectar anomalias com os dados disponíveis."
        )
        return

    st.markdown(
        '<h3 style="text-align: center; color: #2a9d8f;">Análise de Anomalias</h3>',
        unsafe_allow_html=True,
    )

    # Exibe estatísticas em cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 100%;">
                <h4 style="margin-top: 0; color: #2a9d8f; text-align: center;">Anomalias Detectadas</h4>
                <div style="font-size: 2rem; text-align: center; color: #1d3557;">{estatisticas['num_anomalias']}</div>
                <div style="text-align: center; color: #457b9d;">eventos</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 100%;">
                <h4 style="margin-top: 0; color: #2a9d8f; text-align: center;">Percentual Anômalo</h4>
                <div style="font-size: 2rem; text-align: center; color: #1d3557;">{estatisticas['pct_anomalias']:.1f}%</div>
                <div style="text-align: center; color: #457b9d;">dos eventos</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 100%;">
                <h4 style="margin-top: 0; color: #2a9d8f; text-align: center;">Duração Máxima</h4>
                <div style="font-size: 2rem; text-align: center; color: #1d3557;">{estatisticas['max_anomalia']:.2f}h</div>
                <div style="text-align: center; color: #457b9d;">maior anomalia</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Exibe tabela de anomalias
    if len(df_anomalias) > 0:
        st.markdown(
            "<h4 style='margin-top: 30px;'>Detalhes das Anomalias</h4>",
            unsafe_allow_html=True,
        )

        # Prepara os dados para exibição
        df_exibicao = df_anomalias.copy()

        # Formata as colunas de data
        if "Inicio" in df_exibicao.columns:
            df_exibicao["Inicio"] = df_exibicao["Inicio"].dt.strftime(
                "%d/%m/%Y %H:%M"
            )
        if "Fim" in df_exibicao.columns:
            df_exibicao["Fim"] = df_exibicao["Fim"].dt.strftime(
                "%d/%m/%Y %H:%M"
            )

        # Seleciona as colunas relevantes
        colunas_exibir = [
            "Máquina",
            "Inicio",
            "Fim",
            "Duração (horas)",
            "Parada",
            "Área Responsável",
        ]
        colunas_exibir = [
            col for col in colunas_exibir if col in df_exibicao.columns
        ]

        # Exibe a tabela
        st.dataframe(df_exibicao[colunas_exibir], use_container_width=True)

        # Adiciona botão para download das anomalias
        st.markdown(
            get_download_link(
                df_exibicao[colunas_exibir],
                "anomalias_detectadas.xlsx",
                "📥 Baixar lista de anomalias",
            ),
            unsafe_allow_html=True,
        )

    # Exibe gráfico de anomalias se houver dados suficientes
    if len(df_anomalias) > 0 and "Duração (horas)" in df_anomalias.columns:
        st.markdown(
            "<h4 style='margin-top: 30px;'>Distribuição das Anomalias</h4>",
            unsafe_allow_html=True,
        )

        # Cria gráfico de dispersão
        fig = px.scatter(
            df_anomalias,
            x="Inicio",
            y="Duração (horas)",
            color=(
                "Área Responsável"
                if "Área Responsável" in df_anomalias.columns
                else None
            ),
            size="Duração (horas)",
            hover_name="Parada" if "Parada" in df_anomalias.columns else None,
            title="Distribuição de Anomalias ao Longo do Tempo",
            labels={
                "Inicio": "Data de Início",
                "Duração (horas)": "Duração (horas)",
            },
        )

        fig.update_layout(
            autosize=True,
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig, use_container_width=True)


# ----- FUNÇÕES PARA PÁGINA DE PREVISÃO -----
def pagina_previsao(df):
    """Página dedicada à análise preditiva e previsões."""
    st.markdown(
        '<div class="section-title">Análise Preditiva</div>',
        unsafe_allow_html=True,
    )

    if df is None or len(df) < 10:
        st.warning(
            "⚠️ Dados insuficientes para análise preditiva. É necessário ter pelo menos 10 registros."
        )
        return

    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)

        st.markdown(
            """
        ### 🔮 Previsão de Paradas
        
        Esta seção utiliza modelos de aprendizado de máquina para prever o comportamento futuro das paradas com base nos padrões históricos.
        """
        )

        # Prepara dados para previsão
        dados_diarios, features, train_data, test_data = (
            preparar_dados_previsao(df)
        )

        if (
            dados_diarios is None
            or features is None
            or train_data is None
            or test_data is None
        ):
            st.warning(
                "⚠️ Não foi possível preparar os dados para previsão. Verifique se há dados suficientes."
            )
            st.markdown("</div>", unsafe_allow_html=True)
            return

        # Treina modelos
        with st.spinner("Treinando modelos de previsão..."):
            # Modelo para número de paradas
            modelo_num_paradas, metricas_treino_num = treinar_modelo_previsao(
                train_data, features, "Num_Paradas"
            )

            # Modelo para horas de paradas
            modelo_horas_paradas, metricas_treino_horas = (
                treinar_modelo_previsao(train_data, features, "Horas_Paradas")
            )

            if modelo_num_paradas is None or modelo_horas_paradas is None:
                st.warning(
                    "⚠️ Não foi possível treinar os modelos de previsão."
                )
                st.markdown("</div>", unsafe_allow_html=True)
                return

            # Avalia modelos
            resultados_num_paradas, metricas_teste_num = (
                avaliar_modelo_previsao(
                    modelo_num_paradas, test_data, features, "Num_Paradas"
                )
            )
            resultados_horas_paradas, metricas_teste_horas = (
                avaliar_modelo_previsao(
                    modelo_horas_paradas, test_data, features, "Horas_Paradas"
                )
            )

        # Exibe métricas de avaliação
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Modelo de Número de Paradas")
            if metricas_teste_num is not None:
                st.metric(
                    "Erro Médio Absoluto",
                    f"{metricas_teste_num[0]:.2f} paradas",
                )
                st.metric("Coeficiente R²", f"{metricas_teste_num[1]:.2f}")

            if resultados_num_paradas is not None:
                # Gráfico de comparação entre real e previsto
                fig_num = px.line(
                    resultados_num_paradas,
                    x="Data",
                    y=["Real", "Previsto"],
                    title="Comparação: Número de Paradas (Real vs. Previsto)",
                    labels={
                        "value": "Número de Paradas",
                        "Data": "Data",
                        "variable": "Tipo",
                    },
                )

                fig_num.update_layout(
                    autosize=True,
                    margin=dict(l=50, r=50, t=80, b=50),
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                    ),
                )

                st.plotly_chart(fig_num, use_container_width=True)

        with col2:
            st.markdown("#### Modelo de Horas de Paradas")
            if metricas_teste_horas is not None:
                st.metric(
                    "Erro Médio Absoluto",
                    f"{metricas_teste_horas[0]:.2f} horas",
                )
                st.metric("Coeficiente R²", f"{metricas_teste_horas[1]:.2f}")

            if resultados_horas_paradas is not None:
                # Gráfico de comparação entre real e previsto
                fig_horas = px.line(
                    resultados_horas_paradas,
                    x="Data",
                    y=["Real", "Previsto"],
                    title="Comparação: Horas de Paradas (Real vs. Previsto)",
                    labels={
                        "value": "Horas de Paradas",
                        "Data": "Data",
                        "variable": "Tipo",
                    },
                )

                fig_horas.update_layout(
                    autosize=True,
                    margin=dict(l=50, r=50, t=80, b=50),
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                    ),
                )

                st.plotly_chart(fig_horas, use_container_width=True)

                # Faz previsão para os próximos dias
        st.markdown("### Previsão para os Próximos Dias")

        # Slider para selecionar o número de dias para previsão
        dias_previsao = st.slider(
            "Selecione o número de dias para previsão:",
            min_value=3,
            max_value=30,
            value=7,
            step=1,
        )

        with st.spinner("Gerando previsões..."):
            # Combina os modelos para previsão
            modelos_combinados = (modelo_num_paradas, modelo_horas_paradas)

            # Faz a previsão
            df_previsao = fazer_previsao_futura(
                modelos_combinados, dados_diarios, features, dias_previsao
            )

            if df_previsao is not None:
                # Exibe as previsões
                exibir_previsoes(
                    df_previsao,
                    f"Previsão de Paradas para os Próximos {dias_previsao} Dias",
                )

                # Calcula estatísticas da previsão
                total_paradas_previsto = df_previsao[
                    "Previsao_Num_Paradas"
                ].sum()
                total_horas_previsto = df_previsao[
                    "Previsao_Horas_Paradas"
                ].sum()
                media_paradas_dia = df_previsao["Previsao_Num_Paradas"].mean()
                media_horas_dia = df_previsao["Previsao_Horas_Paradas"].mean()

                # Exibe estatísticas
                st.markdown("#### Resumo da Previsão")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Total de Paradas", f"{total_paradas_previsto:.0f}"
                    )

                with col2:
                    st.metric("Total de Horas", f"{total_horas_previsto:.1f}h")

                with col3:
                    st.metric(
                        "Média Diária (Paradas)", f"{media_paradas_dia:.1f}"
                    )

                with col4:
                    st.metric(
                        "Média Diária (Horas)", f"{media_horas_dia:.1f}h"
                    )

                # Calcula impacto estimado
                st.markdown("#### Impacto Estimado")

                # Assume um custo por hora de parada
                custo_hora_padrao = 1000  # Valor fictício
                custo_hora = st.number_input(
                    "Custo por hora de parada (R$):",
                    min_value=100,
                    value=custo_hora_padrao,
                    step=100,
                )

                impacto_financeiro = total_horas_previsto * custo_hora

                st.markdown(
                    f"""
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #e74c3c;">
                        <h4 style="margin-top: 0; color: #e74c3c;">Impacto Financeiro Estimado</h4>
                        <p style="font-size: 1.5rem; font-weight: bold;">R$ {impacto_financeiro:,.2f}</p>
                        <p>Baseado em {total_horas_previsto:.1f} horas de parada previstas nos próximos {dias_previsao} dias.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Recomendações baseadas na previsão
                st.markdown("#### Recomendações Baseadas na Previsão")

                recomendacoes_previsao = [
                    f"Planejar recursos adicionais para lidar com as {total_paradas_previsto:.0f} paradas previstas nos próximos {dias_previsao} dias.",
                    f"Preparar equipe de manutenção para atender à média de {media_paradas_dia:.1f} paradas por dia.",
                    f"Considerar ajustes no cronograma de produção para compensar as {total_horas_previsto:.1f} horas de parada previstas.",
                    "Realizar verificações preventivas nos equipamentos mais críticos antes do período previsto.",
                ]

                for rec in recomendacoes_previsao:
                    st.markdown(f"- {rec}")
            else:
                st.warning(
                    "⚠️ Não foi possível gerar previsões com os dados disponíveis."
                )

        st.markdown("</div>", unsafe_allow_html=True)


# ----- FUNÇÕES PARA PÁGINA DE TENDÊNCIAS E PADRÕES -----
def pagina_tendencias(df):
    """Página dedicada à análise de tendências e padrões."""
    st.markdown(
        '<div class="section-title">Análise de Tendências e Padrões</div>',
        unsafe_allow_html=True,
    )

    if df is None or len(df) < 10:
        st.warning(
            "⚠️ Dados insuficientes para análise de tendências. É necessário ter pelo menos 10 registros."
        )
        return

    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)

        st.markdown(
            """
        ### 📈 Tendências ao Longo do Tempo
        
        Esta seção analisa como as paradas evoluem ao longo do tempo, identificando tendências de aumento, diminuição ou estabilidade.
        """
        )

        # Seleção de período e métrica
        col1, col2 = st.columns(2)

        with col1:
            periodo = st.selectbox(
                "Selecione o período de análise:",
                ["mensal", "semanal", "diario"],
                index=0,
            )

        with col2:
            metrica = st.selectbox(
                "Selecione a métrica para análise:",
                ["Contagem", "Duração"],
                index=0,
            )

        # Calcula tendências
        with st.spinner("Analisando tendências..."):
            dados_tendencia, info_tendencia = calcular_tendencias(
                df, metrica, periodo
            )

            if dados_tendencia is None or info_tendencia is None:
                st.warning(
                    "⚠️ Não foi possível analisar tendências com os dados disponíveis."
                )
                st.markdown("</div>", unsafe_allow_html=True)
                return

            # Exibe gráfico de tendência
            fig_tendencia = px.line(
                dados_tendencia,
                x="Periodo",
                y="Valor",
                title=f"Tendência de {metrica} de Paradas ({periodo.capitalize()})",
                labels={
                    "Valor": (
                        "Número de Paradas"
                        if metrica == "Contagem"
                        else "Duração (horas)"
                    ),
                    "Periodo": "Período",
                },
                markers=True,
            )

            # Adiciona linha de tendência
            fig_tendencia.add_scatter(
                x=dados_tendencia["Periodo"],
                y=info_tendencia["valores_previstos"],
                mode="lines",
                name="Tendência",
                line=dict(color="red", dash="dash"),
            )

            fig_tendencia.update_layout(
                xaxis_tickangle=-45,
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=100),
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )

            st.plotly_chart(fig_tendencia, use_container_width=True)

            # Exibe informações sobre a tendência
            direcao = info_tendencia["direcao"]
            variacao_pct = info_tendencia["variacao_pct"]

            # Define cor com base na direção da tendência
            cor_tendencia = (
                "#2ecc71"
                if direcao == "decrescente"
                else "#e74c3c" if direcao == "crescente" else "#3498db"
            )

            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 4px solid {cor_tendencia};">
                    <h4 style="margin-top: 0; color: {cor_tendencia};">Análise da Tendência</h4>
                    <p>A tendência de {metrica.lower()} de paradas é <strong>{direcao}</strong> ao longo do período analisado.</p>
                    <p>Variação percentual: <strong>{variacao_pct:.1f}%</strong> entre o primeiro e o último período.</p>
                    <p>Coeficiente angular: <strong>{info_tendencia['coeficiente']:.4f}</strong> ({metrica.lower()} por período).</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Análise de padrões cíclicos
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)

        st.markdown(
            """
        ### 🔄 Padrões Cíclicos
        
        Esta seção identifica padrões que se repetem em determinados períodos, como dias da semana, meses do ano ou horas do dia.
        """
        )

        # Seleção de período e métrica para padrões cíclicos
        col1, col2 = st.columns(2)

        with col1:
            periodo_ciclo = st.selectbox(
                "Selecione o ciclo para análise:",
                ["mensal", "semanal", "diario"],
                index=1,
            )

        with col2:
            metrica_ciclo = st.selectbox(
                "Selecione a métrica para padrões cíclicos:",
                ["Contagem", "Duração"],
                index=0,
            )

        # Calcula padrões cíclicos
        with st.spinner("Analisando padrões cíclicos..."):
            dados_ciclo, info_ciclo = identificar_padroes_ciclicos(
                df, metrica_ciclo, periodo_ciclo
            )

            if dados_ciclo is None or info_ciclo is None:
                st.warning(
                    "⚠️ Não foi possível identificar padrões cíclicos com os dados disponíveis."
                )
                st.markdown("</div>", unsafe_allow_html=True)
                return

            # Exibe gráfico de padrão cíclico
            fig_ciclo = px.bar(
                dados_ciclo,
                x="Ciclo",
                y="Valor",
                title=f"Padrão Cíclico de {metrica_ciclo} de Paradas ({periodo_ciclo.capitalize()})",
                labels={
                    "Valor": (
                        "Número de Paradas"
                        if metrica_ciclo == "Contagem"
                        else "Duração (horas)"
                    ),
                    "Ciclo": "Período",
                },
                text_auto=".1f",
            )

            fig_ciclo.update_layout(
                xaxis_tickangle=0,
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=50),
                plot_bgcolor="rgba(0,0,0,0)",
            )

            # Adiciona linha média
            fig_ciclo.add_hline(
                y=dados_ciclo["Valor"].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text="Média",
                annotation_position="bottom right",
            )

            st.plotly_chart(fig_ciclo, use_container_width=True)

            # Exibe informações sobre o padrão cíclico
            pico_nome = info_ciclo["pico_nome"]
            vale_nome = info_ciclo["vale_nome"]
            amplitude_pct = info_ciclo["amplitude_pct"]

            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #9b59b6;">
                    <h4 style="margin-top: 0; color: #9b59b6;">Análise do Padrão Cíclico</h4>
                    <p>Pico identificado em: <strong>{pico_nome}</strong></p>
                    <p>Vale identificado em: <strong>{vale_nome}</strong></p>
                    <p>Amplitude do ciclo: <strong>{amplitude_pct:.1f}%</strong> entre o pico e o vale.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Recomendações baseadas no padrão cíclico
            st.markdown("#### Recomendações Baseadas no Padrão Cíclico")

            recomendacoes_ciclo = [
                f"Reforçar equipe de manutenção durante {pico_nome}, quando ocorre o pico de {metrica_ciclo.lower()} de paradas.",
                f"Programar manutenções preventivas antes de {pico_nome} para reduzir ocorrências.",
                f"Aproveitar {vale_nome} para realizar treinamentos ou atividades que exijam menor disponibilidade da equipe.",
                "Investigar as causas específicas que levam ao aumento de paradas nos períodos de pico.",
            ]

            for rec in recomendacoes_ciclo:
                st.markdown(f"- {rec}")

        st.markdown("</div>", unsafe_allow_html=True)

    # Análise de correlações
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)

        st.markdown(
            """
        ### 🔗 Correlações entre Variáveis
        
        Esta seção analisa como diferentes variáveis se relacionam, identificando possíveis causas e efeitos.
        """
        )

        # Calcula correlações
        with st.spinner("Analisando correlações..."):
            matriz_corr = analisar_correlacoes(df)

            if matriz_corr is None or matriz_corr.empty:
                st.warning(
                    "⚠️ Não foi possível analisar correlações com os dados disponíveis."
                )
                st.markdown("</div>", unsafe_allow_html=True)
                return

            # Exibe mapa de calor de correlações
            fig_corr = px.imshow(
                matriz_corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title="Matriz de Correlação entre Áreas Responsáveis",
            )

            fig_corr.update_layout(
                autosize=True, margin=dict(l=50, r=50, t=80, b=50)
            )

            st.plotly_chart(fig_corr, use_container_width=True)

            # Identifica correlações fortes
            correlacoes_fortes = []

            for i in range(len(matriz_corr.columns)):
                for j in range(i + 1, len(matriz_corr.columns)):
                    valor = matriz_corr.iloc[i, j]
                    if abs(valor) > 0.7:  # Limiar para correlação forte
                        correlacoes_fortes.append(
                            {
                                "var1": matriz_corr.columns[i],
                                "var2": matriz_corr.columns[j],
                                "corr": valor,
                            }
                        )

            # Exibe correlações fortes
            if correlacoes_fortes:
                st.markdown("#### Correlações Fortes Identificadas")

                for corr in correlacoes_fortes:
                    tipo_corr = "positiva" if corr["corr"] > 0 else "negativa"
                    cor_corr = "#2ecc71" if corr["corr"] > 0 else "#e74c3c"

                    st.markdown(
                        f"""
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid {cor_corr};">
                            <p style="margin: 0;"><strong>{corr['var1']}</strong> e <strong>{corr['var2']}</strong> têm correlação <span style="color: {cor_corr};">{tipo_corr} forte</span> ({corr['corr']:.2f}).</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Recomendações baseadas nas correlações
                st.markdown("#### Recomendações Baseadas nas Correlações")

                recomendacoes_corr = [
                    "Investigar a relação entre áreas com alta correlação positiva para identificar causas comuns.",
                    "Considerar abordagens integradas para resolver problemas em áreas correlacionadas.",
                    "Implementar melhorias que possam beneficiar múltiplas áreas correlacionadas simultaneamente.",
                ]

                for rec in recomendacoes_corr:
                    st.markdown(f"- {rec}")
            else:
                st.info(
                    "Não foram identificadas correlações fortes entre as variáveis analisadas."
                )

        st.markdown("</div>", unsafe_allow_html=True)


# ----- FUNÇÕES PARA PÁGINA DE ANOMALIAS -----
def pagina_anomalias(df):
    """Página dedicada à detecção e análise de anomalias."""
    st.markdown(
        '<div class="section-title">Detecção de Anomalias</div>',
        unsafe_allow_html=True,
    )

    if df is None or len(df) < 10:
        st.warning(
            "⚠️ Dados insuficientes para detecção de anomalias. É necessário ter pelo menos 10 registros."
        )
        return

    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)

        st.markdown(
            """
        ### 🔍 Detecção de Valores Anômalos
        
        Esta seção identifica paradas que apresentam comportamento fora do padrão, como duração excessivamente longa ou curta.
        """
        )

        # Seleção de parâmetros para detecção de anomalias
        col1, col2, col3 = st.columns(3)

        with col1:
            coluna_anomalia = st.selectbox(
                "Selecione a variável para análise:",
                ["Duração (horas)"],
                index=0,
            )

        with col2:
            metodo_anomalia = st.selectbox(
                "Selecione o método de detecção:", ["zscore", "iqr"], index=0
            )

        with col3:
            limiar_anomalia = st.slider(
                "Selecione o limiar de detecção:",
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.1,
            )

        # Detecta anomalias
        with st.spinner("Detectando anomalias..."):
            df_anomalias, estatisticas_anomalias = detectar_anomalias(
                df, coluna_anomalia, metodo_anomalia, limiar_anomalia
            )

            if df_anomalias is None or estatisticas_anomalias is None:
                st.warning(
                    "⚠️ Não foi possível detectar anomalias com os dados disponíveis."
                )
                st.markdown("</div>", unsafe_allow_html=True)
                return

            # Exibe resultados da detecção de anomalias
            exibir_anomalias(df_anomalias, estatisticas_anomalias)

            # Análise aprofundada das anomalias
            if len(df_anomalias) > 0:
                st.markdown("### Análise Aprofundada das Anomalias")

                # Distribuição por tipo de parada
                if "Parada" in df_anomalias.columns:
                    tipos_anomalias = df_anomalias["Parada"].value_counts()

                    fig_tipos = px.pie(
                        values=tipos_anomalias.values,
                        names=tipos_anomalias.index,
                        title="Distribuição de Anomalias por Tipo de Parada",
                        hole=0.4,
                    )

                    fig_tipos.update_layout(
                        autosize=True, margin=dict(l=20, r=20, t=80, b=20)
                    )

                    st.plotly_chart(fig_tipos, use_container_width=True)

                # Distribuição por máquina
                if "Máquina" in df_anomalias.columns:
                    maquinas_anomalias = df_anomalias["Máquina"].value_counts()

                    fig_maquinas = px.bar(
                        x=maquinas_anomalias.index,
                        y=maquinas_anomalias.values,
                        title="Distribuição de Anomalias por Máquina",
                        labels={"x": "Máquina", "y": "Número de Anomalias"},
                        text_auto=True,
                    )

                    fig_maquinas.update_layout(
                        xaxis_tickangle=0,
                        autosize=True,
                        margin=dict(l=50, r=50, t=80, b=50),
                        plot_bgcolor="rgba(0,0,0,0)",
                    )

                    st.plotly_chart(fig_maquinas, use_container_width=True)

                # Recomendações baseadas nas anomalias
                st.markdown("#### Recomendações para Tratamento de Anomalias")

                recomendacoes_anomalias = [
                    f"Investigar em detalhe as {estatisticas_anomalias['num_anomalias']} paradas anômalas identificadas.",
                    "Criar um processo de análise de causa raiz para paradas com duração anormalmente longa.",
                    "Estabelecer limites de alerta para identificar anomalias em tempo real.",
                    "Implementar revisões técnicas específicas para os tipos de parada que apresentam mais anomalias.",
                ]

                for rec in recomendacoes_anomalias:
                    st.markdown(f"- {rec}")

        st.markdown("</div>", unsafe_allow_html=True)


# ----- FUNÇÕES PARA PÁGINA DE IMPACTO -----
def pagina_impacto(df):
    """Página dedicada à análise de impacto das paradas."""
    st.markdown(
        '<div class="section-title">Análise de Impacto</div>',
        unsafe_allow_html=True,
    )

    if df is None or len(df) < 5:
        st.warning(
            "⚠️ Dados insuficientes para análise de impacto. É necessário ter pelo menos 5 registros."
        )
        return

    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)

        st.markdown(
            """
        ### 💰 Impacto Financeiro e Operacional
        
        Esta seção analisa o impacto das paradas na produção e nos resultados financeiros.
        """
        )

        # Configuração de parâmetros para análise de impacto
        col1, col2 = st.columns(2)

        with col1:
            tempo_programado = st.number_input(
                "Tempo programado por semana (horas):",
                min_value=1,
                value=168,
                step=1,
            )

        with col2:
            custo_hora_parada = st.number_input(
                "Custo por hora de parada (R$):",
                min_value=100,
                value=1000,
                step=100,
            )

        # Analisa o impacto
        with st.spinner("Analisando impacto..."):
            analise_impacto = analisar_impacto_paradas(df, tempo_programado)

            if analise_impacto is None:
                st.warning(
                    "⚠️ Não foi possível analisar o impacto com os dados disponíveis."
                )
                st.markdown("</div>", unsafe_allow_html=True)
                return

            # Atualiza o impacto financeiro com o custo por hora informado
            analise_impacto["impacto_financeiro"] = (
                analise_impacto["tempo_total_parado"] * custo_hora_parada
            )

            # Exibe indicadores de impacto
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"""
                    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 100%;">
                        <h4 style="margin-top: 0; color: #2a9d8f; text-align: center;">Tempo Total Parado</h4>
                        <div style="font-size: 2rem; text-align: center; color: #1d3557;">{analise_impacto['tempo_total_parado']:.1f}h</div>
                        <div style="text-align: center; color: #457b9d;">no período analisado</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 100%;">
                        <h4 style="margin-top: 0; color: #2a9d8f; text-align: center;">Disponibilidade</h4>
                        <div style="font-size: 2rem; text-align: center; color: #1d3557;">{analise_impacto['disponibilidade']:.1f}%</div>
                        <div style="text-align: center; color: #457b9d;">do tempo programado</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 100%;">
                        <h4 style="margin-top: 0; color: #2a9d8f; text-align: center;">Impacto Financeiro</h4>
                        <div style="font-size: 2rem; text-align: center; color: #1d3557;">R$ {analise_impacto['impacto_financeiro']:,.2f}</div>
                        <div style="text-align: center; color: #457b9d;">custo estimado</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Gráfico de impacto por tipo de parada
            st.markdown("#### Impacto por Tipo de Parada")

            # Pega os top 10 tipos de parada por impacto
            top_tipos = analise_impacto["impacto_por_tipo"].head(10)

            fig_tipos = px.bar(
                x=top_tipos.index,
                y=top_tipos.values,
                title="Top 10 Tipos de Parada por Impacto",
                labels={"x": "Tipo de Parada", "y": "Duração (horas)"},
                text_auto=".1f",
                color=top_tipos.values,
                color_continuous_scale="Reds",
            )

            fig_tipos.update_layout(
                xaxis_tickangle=-45,
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=100),
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
            )

            st.plotly_chart(fig_tipos, use_container_width=True)

            # Gráfico de impacto por área responsável
            st.markdown("#### Impacto por Área Responsável")

            # Pega todas as áreas responsáveis
            areas = analise_impacto["impacto_por_area"]

            fig_areas = px.pie(
                values=areas.values,
                names=areas.index,
                title="Distribuição do Impacto por Área Responsável",
                hole=0.4,
            )

            fig_areas.update_layout(
                autosize=True, margin=dict(l=20, r=20, t=80, b=20)
            )

            st.plotly_chart(fig_areas, use_container_width=True)

            # Gráfico de impacto por máquina
            st.markdown("#### Impacto por Máquina")

            # Pega todas as máquinas
            maquinas = analise_impacto["impacto_por_maquina"]

            fig_maquinas = px.bar(
                x=maquinas.index,
                y=maquinas.values,
                title="Impacto por Máquina",
                labels={"x": "Máquina", "y": "Duração (horas)"},
                text_auto=".1f",
                color=maquinas.values,
                color_continuous_scale="Blues",
            )

            fig_maquinas.update_layout(
                xaxis_tickangle=0,
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=50),
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
            )

            st.plotly_chart(fig_maquinas, use_container_width=True)

            # Análise de impacto financeiro detalhado
            st.markdown("#### Análise de Impacto Financeiro Detalhado")

            # Calcula o impacto financeiro por tipo de parada
            impacto_financeiro_tipo = top_tipos * custo_hora_parada

            # Cria uma tabela com o impacto financeiro por tipo de parada
            df_impacto_financeiro = pd.DataFrame(
                {
                    "Tipo de Parada": impacto_financeiro_tipo.index,
                    "Duração (horas)": top_tipos.values,
                    "Impacto Financeiro (R$)": impacto_financeiro_tipo.values,
                }
            )

            # Exibe a tabela
            st.dataframe(
                df_impacto_financeiro,
                column_config={
                    "Tipo de Parada": st.column_config.TextColumn(
                        "Tipo de Parada"
                    ),
                    "Duração (horas)": st.column_config.NumberColumn(
                        "Duração (horas)", format="%.1f"
                    ),
                    "Impacto Financeiro (R$)": st.column_config.NumberColumn(
                        "Impacto Financeiro (R$)", format="R$ %.2f"
                    ),
                },
                use_container_width=True,
            )

            # Adiciona botão para download da análise de impacto
            st.markdown(
                get_download_link(
                    df_impacto_financeiro,
                    "analise_impacto.xlsx",
                    "📥 Baixar análise de impacto",
                ),
                unsafe_allow_html=True,
            )

            # Recomendações baseadas na análise de impacto
            st.markdown("#### Recomendações para Redução de Impacto")

            # Gera recomendações
            recomendacoes = gerar_recomendacoes(df, analise_impacto)

            # Exibe recomendações
            exibir_recomendacoes(recomendacoes)

        st.markdown("</div>", unsafe_allow_html=True)


# ----- FUNÇÕES PARA PÁGINA DE RELATÓRIO -----
def pagina_relatorio(df):
    """Página dedicada à geração de relatórios."""
    st.markdown(
        '<div class="section-title">Geração de Relatórios</div>',
        unsafe_allow_html=True,
    )

    if df is None or len(df) < 5:
        st.warning(
            "⚠️ Dados insuficientes para geração de relatórios. É necessário ter pelo menos 5 registros."
        )
        return

    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)

        st.markdown(
            """
        ### 📊 Relatório Executivo
        
        Esta seção permite gerar relatórios executivos com os principais indicadores e análises.
        """
        )

        # Configuração de parâmetros para o relatório
        col1, col2 = st.columns(2)

        with col1:
            maquina_relatorio = st.selectbox(
                "Selecione a máquina para o relatório:",
                ["Todas"] + sorted(df["Máquina"].unique().tolist()),
                index=0,
            )

        with col2:
            periodo_relatorio = st.selectbox(
                "Selecione o período para o relatório:",
                ["Todos"] + sorted(df["Ano-Mês"].unique().tolist()),
                index=0,
            )

        # Botão para gerar o relatório
        if st.button("Gerar Relatório Executivo", key="btn_relatorio"):
            with st.spinner("Gerando relatório executivo..."):
                # Filtra os dados conforme seleção
                df_relatorio = df.copy()

                if maquina_relatorio != "Todas":
                    df_relatorio = df_relatorio[
                        df_relatorio["Máquina"] == maquina_relatorio
                    ]

                if periodo_relatorio != "Todos":
                    df_relatorio = df_relatorio[
                        df_relatorio["Ano-Mês"] == periodo_relatorio
                    ]

                # Verifica se há dados após a filtragem
                if len(df_relatorio) == 0:
                    st.warning(
                        "⚠️ Não há dados disponíveis para os filtros selecionados."
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    return

                # Título do relatório
                titulo_maquina = (
                    "Todas as Máquinas"
                    if maquina_relatorio == "Todas"
                    else maquina_relatorio
                )
                titulo_periodo = (
                    "Todo o Período"
                    if periodo_relatorio == "Todos"
                    else obter_nome_mes(periodo_relatorio)
                )

                st.markdown(
                    f"## Relatório Executivo - {titulo_maquina} - {titulo_periodo}"
                )

                # Resumo dos dados
                st.markdown("### Resumo dos Dados")

                # Calcula métricas resumidas
                total_paradas = len(df_relatorio)
                total_horas = df_relatorio["Duração (horas)"].sum()
                media_duracao = df_relatorio["Duração (horas)"].mean()
                tempo_programado = 24 * 7  # Valor padrão para uma semana
                disponibilidade = (
                    (tempo_programado - total_horas) / tempo_programado * 100
                )
                disponibilidade = max(0, min(100, disponibilidade))

                # Exibe métricas em cards
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total de Paradas", f"{total_paradas}")

                with col2:
                    st.metric("Total de Horas", f"{total_horas:.1f}h")

                with col3:
                    st.metric("Duração Média", f"{media_duracao:.2f}h")

                with col4:
                    st.metric("Disponibilidade", f"{disponibilidade:.1f}%")

                # Gráficos para o relatório
                st.markdown("### Análise Gráfica")

                # Cria abas para diferentes visualizações
                tab1, tab2, tab3 = st.tabs(
                    [
                        "📊 Pareto de Causas",
                        "🔄 Evolução Temporal",
                        "👥 Análise por Área",
                    ]
                )

                with tab1:
                    # Pareto de causas
                    if "Parada" in df_relatorio.columns:
                        pareto = (
                            df_relatorio.groupby("Parada")["Duração (horas)"]
                            .sum()
                            .sort_values(ascending=False)
                            .head(10)
                        )

                        fig_pareto = px.bar(
                            x=pareto.index,
                            y=pareto.values,
                            title="Pareto de Causas de Paradas (Top 10)",
                            labels={
                                "x": "Causa de Parada",
                                "y": "Duração Total (horas)",
                            },
                            text_auto=".1f",
                        )

                        fig_pareto.update_layout(
                            xaxis_tickangle=-45,
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=100),
                            plot_bgcolor="rgba(0,0,0,0)",
                        )

                        st.plotly_chart(fig_pareto, use_container_width=True)

                with tab2:
                    # Evolução temporal
                    if (
                        "Ano-Mês" in df_relatorio.columns
                        and len(df_relatorio["Ano-Mês"].unique()) > 1
                    ):
                        evolucao = df_relatorio.groupby("Ano-Mês")[
                            "Duração (horas)"
                        ].sum()

                        fig_evolucao = px.line(
                            x=evolucao.index,
                            y=evolucao.values,
                            title="Evolução da Duração Total de Paradas",
                            labels={
                                "x": "Período",
                                "y": "Duração Total (horas)",
                            },
                            markers=True,
                        )

                        fig_evolucao.update_layout(
                            xaxis_tickangle=-45,
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=100),
                            plot_bgcolor="rgba(0,0,0,0)",
                        )

                        st.plotly_chart(fig_evolucao, use_container_width=True)
                    else:
                        st.info(
                            "Dados insuficientes para análise de evolução temporal."
                        )

                with tab3:
                    # Análise por área
                    if "Área Responsável" in df_relatorio.columns:
                        areas = (
                            df_relatorio.groupby("Área Responsável")[
                                "Duração (horas)"
                            ]
                            .sum()
                            .sort_values(ascending=False)
                        )

                        fig_areas = px.pie(
                            values=areas.values,
                            names=areas.index,
                            title="Distribuição de Paradas por Área Responsável",
                            hole=0.4,
                        )

                        fig_areas.update_layout(
                            autosize=True, margin=dict(l=20, r=20, t=80, b=20)
                        )

                        st.plotly_chart(fig_areas, use_container_width=True)

                # Tabela detalhada
                st.markdown("### Detalhamento das Paradas")

                # Agrupa por tipo de parada
                if "Parada" in df_relatorio.columns:
                    detalhamento = (
                        df_relatorio.groupby("Parada")
                        .agg({"Duração (horas)": ["count", "sum", "mean"]})
                        .reset_index()
                    )

                    detalhamento.columns = [
                        "Tipo de Parada",
                        "Ocorrências",
                        "Duração Total (h)",
                        "Duração Média (h)",
                    ]

                    # Ordena por duração total
                    detalhamento = detalhamento.sort_values(
                        "Duração Total (h)", ascending=False
                    )

                    # Exibe a tabela
                    st.dataframe(
                        detalhamento,
                        column_config={
                            "Tipo de Parada": st.column_config.TextColumn(
                                "Tipo de Parada"
                            ),
                            "Ocorrências": st.column_config.NumberColumn(
                                "Ocorrências", format="%d"
                            ),
                            "Duração Total (h)": st.column_config.NumberColumn(
                                "Duração Total (h)", format="%.1f"
                            ),
                            "Duração Média (h)": st.column_config.NumberColumn(
                                "Duração Média (h)", format="%.2f"
                            ),
                        },
                        use_container_width=True,
                    )

                    # Adiciona botão para download do detalhamento
                    st.markdown(
                        get_download_link(
                            detalhamento,
                            "detalhamento_paradas.xlsx",
                            "📥 Baixar detalhamento",
                        ),
                        unsafe_allow_html=True,
                    )

                # Conclusões e recomendações
                st.markdown("### Conclusões e Recomendações")

                # Analisa o impacto
                analise_impacto = analisar_impacto_paradas(
                    df_relatorio, tempo_programado
                )

                # Gera recomendações
                recomendacoes = gerar_recomendacoes(
                    df_relatorio, analise_impacto
                )

                # Exibe recomendações
                exibir_recomendacoes(recomendacoes)

                # Adiciona informações sobre o relatório
                st.markdown(
                    f"""
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 30px; border-left: 4px solid #6c757d;">
                        <p style="margin: 0; color: #6c757d;"><strong>Informações do Relatório</strong></p>
                        <p style="margin: 5px 0 0 0; color: #6c757d;">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                        <p style="margin: 5px 0 0 0; color: #6c757d;">Filtros aplicados: Máquina: {titulo_maquina}, Período: {titulo_periodo}</p>
                        <p style="margin: 5px 0 0 0; color: #6c757d;">Total de registros analisados: {total_paradas}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Botão para download completo do relatório (implementação futura)
                st.info(
                    "A funcionalidade de download do relatório completo em PDF será implementada em uma versão futura."
                )

        st.markdown("</div>", unsafe_allow_html=True)


# ----- FUNÇÃO PRINCIPAL MELHORADA -----
def main():
    """Função principal da aplicação."""
    # Aplica estilos
    aplicar_estilos()

    # Título principal
    st.markdown(
        '<div class="main-title">Análise de Eficiência de Máquinas 3.0</div>',
        unsafe_allow_html=True,
    )

    # Menu de navegação
    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Dados",
            "Previsões",
            "Tendências",
            "Anomalias",
            "Impacto",
            "Relatórios",
            "Sobre",
        ],
        icons=[
            "speedometer2",
            "table",
            "graph-up",
            "arrow-repeat",
            "exclamation-triangle",
            "currency-dollar",
            "file-earmark-text",
            "info-circle",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#f0f2f6",
            },
            "icon": {"color": "#2a9d8f", "font-size": "14px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {
                "background-color": "#2a9d8f",
                "color": "white",
            },
        },
    )

    # Inicializa o estado da sessão para armazenar o DataFrame
    if "df" not in st.session_state:
        st.session_state.df = None

    if "first_load" not in st.session_state:
        st.session_state.first_load = True

    # Função para analisar os dados
    def analisar_dados(df, maquina_selecionada, mes_selecionado):
        """Analisa os dados com base nos filtros selecionados."""
        # Filtra os dados
        df_filtrado = df.copy()

        if maquina_selecionada != "Todas":
            df_filtrado = df_filtrado[
                df_filtrado["Máquina"] == maquina_selecionada
            ]

        if mes_selecionado != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["Ano-Mês"] == mes_selecionado
            ]

        # Verifica se há dados após a filtragem
        if len(df_filtrado) == 0:
            st.warning(
                "⚠️ Não há dados disponíveis para os filtros selecionados."
            )
            return

        # Calcula indicadores
        tempo_programado = 24 * 7  # Valor padrão para uma semana

        # Calcula a disponibilidade
        tempo_total_parado = df_filtrado["Duração"].sum()
        disponibilidade = (
            (tempo_programado - tempo_total_parado.total_seconds() / 3600)
            / tempo_programado
            * 100
        )
        disponibilidade = max(0, min(100, disponibilidade))

        # Calcula o tempo médio de parada
        tmp = df_filtrado["Duração"].mean()

        # Calcula a eficiência operacional
        tempo_operacao = (
            tempo_programado - tempo_total_parado.total_seconds() / 3600
        )
        eficiencia = tempo_operacao / tempo_programado * 100
        eficiencia = max(0, min(100, eficiencia))

        # Identifica paradas críticas
        limite = pd.Timedelta(hours=1)
        paradas_criticas = df_filtrado[df_filtrado["Duração"] > limite]
        percentual_criticas = (
            len(paradas_criticas) / len(df_filtrado) * 100
            if len(df_filtrado) > 0
            else 0
        )

        # Exibe indicadores
        exibir_indicadores(
            disponibilidade, tmp, eficiencia, percentual_criticas
        )

        # Cria container para os gráficos
        with st.container():
            st.markdown(
                '<div class="chart-container">', unsafe_allow_html=True
            )

            # Cria abas para diferentes visualizações
            tab1, tab2, tab3, tab4 = st.tabs(
                ["📊 Pareto", "🔄 Tendências", "👥 Áreas", "⚠️ Críticas"]
            )

            with tab1:
                # Pareto de causas de parada
                if "Parada" in df_filtrado.columns:
                    pareto = (
                        df_filtrado.groupby("Parada")["Duração"]
                        .sum()
                        .sort_values(ascending=False)
                        .head(10)
                    )
                    fig_pareto = criar_grafico_pareto(pareto)

                    if fig_pareto is not None:
                        st.plotly_chart(fig_pareto, use_container_width=True)
                    else:
                        st.info(
                            "Dados insuficientes para gerar o gráfico de Pareto."
                        )

            with tab2:
                # Tendências ao longo do tempo
                col1, col2 = st.columns(2)

                with col1:
                    # Taxa de ocorrência de paradas
                    ocorrencias = taxa_ocorrencia_paradas(df_filtrado)
                    fig_ocorrencias = criar_grafico_ocorrencias(ocorrencias)

                    if fig_ocorrencias is not None:
                        st.plotly_chart(
                            fig_ocorrencias, use_container_width=True
                        )
                    else:
                        st.info(
                            "Dados insuficientes para gerar o gráfico de ocorrências."
                        )

                with col2:
                    # Duração total por mês
                    duracao_mensal = duracao_total_por_mes(df_filtrado)
                    fig_duracao = criar_grafico_duracao_mensal(duracao_mensal)

                    if fig_duracao is not None:
                        st.plotly_chart(fig_duracao, use_container_width=True)
                    else:
                        st.info(
                            "Dados insuficientes para gerar o gráfico de duração mensal."
                        )

            with tab3:
                # Análise por área responsável
                col1, col2 = st.columns(2)

                with col1:
                    # Índice de paradas por área
                    if "Área Responsável" in df_filtrado.columns:
                        indice_areas = indice_paradas_por_area(df_filtrado)
                        fig_areas = criar_grafico_pizza_areas(indice_areas)

                        if fig_areas is not None:
                            st.plotly_chart(
                                fig_areas, use_container_width=True
                            )
                        else:
                            st.info(
                                "Dados insuficientes para gerar o gráfico de áreas."
                            )

                with col2:
                    # Tempo total por área
                    if "Área Responsável" in df_filtrado.columns:
                        tempo_areas = tempo_total_paradas_area(df_filtrado)
                        fig_tempo_areas = criar_grafico_tempo_area(tempo_areas)

                        if fig_tempo_areas is not None:
                            st.plotly_chart(
                                fig_tempo_areas, use_container_width=True
                            )
                        else:
                            st.info(
                                "Dados insuficientes para gerar o gráfico de tempo por área."
                            )

            with tab4:
                # Análise de paradas críticas
                col1, col2 = st.columns(2)

                with col1:
                    # Top paradas críticas
                    if len(paradas_criticas) > 0:
                        top_criticas = (
                            paradas_criticas.groupby("Parada")["Duração"]
                            .sum()
                            .sort_values(ascending=False)
                            .head(10)
                        )
                        fig_criticas = criar_grafico_paradas_criticas(
                            top_criticas
                        )

                        if fig_criticas is not None:
                            st.plotly_chart(
                                fig_criticas, use_container_width=True
                            )
                        else:
                            st.info(
                                "Dados insuficientes para gerar o gráfico de paradas críticas."
                            )

                with col2:
                    # Distribuição de paradas críticas por área
                    if (
                        "Área Responsável" in paradas_criticas.columns
                        and len(paradas_criticas) > 0
                    ):
                        fig_areas_criticas = (
                            criar_grafico_pizza_areas_criticas(
                                paradas_criticas
                            )
                        )

                        if fig_areas_criticas is not None:
                            st.plotly_chart(
                                fig_areas_criticas, use_container_width=True
                            )
                        else:
                            st.info(
                                "Dados insuficientes para gerar o gráfico de áreas críticas."
                            )

            st.markdown("</div>", unsafe_allow_html=True)

        # Recomendações
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)

            st.markdown("### 💡 Recomendações")

            # Analisa o impacto
            analise_impacto = analisar_impacto_paradas(
                df_filtrado, tempo_programado
            )

            # Gera recomendações
            recomendacoes = gerar_recomendacoes(df_filtrado, analise_impacto)

            # Exibe recomendações
            exibir_recomendacoes(recomendacoes)

            st.markdown("</div>", unsafe_allow_html=True)

    # Página Dashboard
    if selected == "Dashboard":
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)

            # Upload de arquivo
            uploaded_file = st.file_uploader(
                "Faça upload de um arquivo Excel com dados de paradas:",
                type=["xlsx", "xls"],
            )

            if uploaded_file is not None:
                try:
                    # Lê o arquivo Excel
                    df = pd.read_excel(uploaded_file)

                    # Processa os dados
                    df_processado = processar_dados(df)

                    if df_processado is not None:
                        # Armazena o DataFrame processado no estado da sessão
                        st.session_state.df = df_processado

                        # Exibe mensagem de sucesso
                        st.success(
                            f"✅ Arquivo carregado com sucesso! {len(df_processado)} registros processados."
                        )

                        # Exibe uma prévia dos dados
                        st.markdown("### Prévia dos Dados")
                        st.dataframe(
                            df_processado.head(5), use_container_width=True
                        )
                    else:
                        st.error(
                            "❌ Não foi possível processar o arquivo. Verifique se o formato está correto."
                        )
                except Exception as e:
                    st.error(f"❌ Erro ao carregar o arquivo: {str(e)}")

            st.markdown("</div>", unsafe_allow_html=True)

        # Se houver dados carregados, exibe o dashboard
        if st.session_state.df is not None:
            with st.container():
                st.markdown(
                    '<div class="content-box">', unsafe_allow_html=True
                )

                # Filtros
                col1, col2 = st.columns(2)

                with col1:
                    # Filtro de máquina
                    maquinas = ["Todas"] + sorted(
                        st.session_state.df["Máquina"].unique().tolist()
                    )
                    maquina_selecionada = st.selectbox(
                        "Selecione a máquina:", maquinas
                    )

                with col2:
                    # Filtro de mês
                    meses = ["Todos"] + sorted(
                        st.session_state.df["Ano-Mês"].unique().tolist()
                    )
                    mes_selecionado = st.selectbox("Selecione o mês:", meses)

                # Título do dashboard
                titulo_maquina = (
                    "Todas as Máquinas"
                    if maquina_selecionada == "Todas"
                    else maquina_selecionada
                )
                titulo_mes = (
                    "Todo o Período"
                    if mes_selecionado == "Todos"
                    else obter_nome_mes(mes_selecionado)
                )

                st.markdown(
                    f"## Dashboard de Eficiência - {titulo_maquina} - {titulo_mes}"
                )

                # Analisa os dados
                analisar_dados(
                    st.session_state.df, maquina_selecionada, mes_selecionado
                )

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Mensagem para carregar dados
            st.info(
                "📊 Carregue um arquivo Excel para visualizar o dashboard de eficiência."
            )

    # Página de Dados
    elif selected == "Dados":
        if st.session_state.df is not None:
            st.markdown(
                '<div class="section-title">Visualização dos Dados</div>',
                unsafe_allow_html=True,
            )

            with st.container():
                st.markdown(
                    '<div class="content-box">', unsafe_allow_html=True
                )
                # Opções de filtro para visualização
                col1, col2 = st.columns(2)

                with col1:
                    # Filtro de máquina
                    maquinas_para_filtro = ["Todas"] + sorted(
                        st.session_state.df["Máquina"].unique().tolist()
                    )
                    maquina_filtro = st.selectbox(
                        "Filtrar por Máquina:", maquinas_para_filtro
                    )

                with col2:
                    # Filtro de mês
                    meses_para_filtro = ["Todos"] + sorted(
                        st.session_state.df["Ano-Mês"].unique().tolist()
                    )
                    mes_filtro = st.selectbox(
                        "Filtrar por Mês:", meses_para_filtro
                    )

                # Aplica os filtros
                dados_filtrados = st.session_state.df.copy()

                if maquina_filtro != "Todas":
                    dados_filtrados = dados_filtrados[
                        dados_filtrados["Máquina"] == maquina_filtro
                    ]

                if mes_filtro != "Todos":
                    dados_filtrados = dados_filtrados[
                        dados_filtrados["Ano-Mês"] == mes_filtro
                    ]

                # Exibe os dados filtrados
                st.markdown(f"**Mostrando {len(dados_filtrados)} registros**")
                st.dataframe(
                    dados_filtrados,
                    use_container_width=True,
                    hide_index=True,
                    height=400,
                )

                # Botão para download dos dados
                st.markdown(
                    get_download_link(
                        dados_filtrados,
                        "dados_filtrados.xlsx",
                        "📥 Baixar dados filtrados",
                    ),
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            # Estatísticas básicas
            st.markdown(
                '<div class="section-title">Estatísticas Básicas</div>',
                unsafe_allow_html=True,
            )

            with st.container():
                st.markdown(
                    '<div class="content-box">', unsafe_allow_html=True
                )
                # Resumo por máquina
                resumo_maquina = dados_filtrados.groupby("Máquina").agg(
                    {"Duração": ["count", "sum", "mean"]}
                )
                resumo_maquina.columns = [
                    "Número de Paradas",
                    "Duração Total",
                    "Duração Média",
                ]

                # Converte para horas
                resumo_maquina["Duração Total (horas)"] = resumo_maquina[
                    "Duração Total"
                ].apply(lambda x: x.total_seconds() / 3600)
                resumo_maquina["Duração Média (horas)"] = resumo_maquina[
                    "Duração Média"
                ].apply(lambda x: x.total_seconds() / 3600)

                st.dataframe(
                    resumo_maquina[
                        [
                            "Número de Paradas",
                            "Duração Total (horas)",
                            "Duração Média (horas)",
                        ]
                    ],
                    column_config={
                        "Número de Paradas": st.column_config.NumberColumn(
                            "Número de Paradas", format="%d"
                        ),
                        "Duração Total (horas)": st.column_config.NumberColumn(
                            "Duração Total (horas)", format="%.2f"
                        ),
                        "Duração Média (horas)": st.column_config.NumberColumn(
                            "Duração Média (horas)", format="%.2f"
                        ),
                    },
                    use_container_width=True,
                )

                # Gráfico de resumo por máquina
                if (
                    len(resumo_maquina) > 1
                ):  # Só cria o gráfico se houver mais de uma máquina
                    fig_resumo = px.bar(
                        resumo_maquina.reset_index(),
                        x="Máquina",
                        y="Duração Total (horas)",
                        color="Máquina",
                        title="Duração Total de Paradas por Máquina",
                        labels={
                            "Duração Total (horas)": "Duração Total (horas)",
                            "Máquina": "Máquina",
                        },
                        text="Duração Total (horas)",
                    )

                    fig_resumo.update_traces(
                        texttemplate="%{text:.1f}h", textposition="outside"
                    )

                    fig_resumo.update_layout(
                        xaxis_tickangle=0,
                        autosize=True,
                        margin=dict(l=50, r=50, t=80, b=50),
                        plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                    )

                    st.plotly_chart(fig_resumo, use_container_width=True)

                # Botão para download do resumo
                st.markdown(
                    get_download_link(
                        resumo_maquina.reset_index(),
                        "resumo_maquinas.xlsx",
                        "📥 Baixar resumo por máquina",
                    ),
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            # Distribuição de paradas por dia da semana
            st.markdown(
                '<div class="section-title">Análises Adicionais</div>',
                unsafe_allow_html=True,
            )

            with st.container():
                st.markdown(
                    '<div class="content-box">', unsafe_allow_html=True
                )

                tab1, tab2 = st.tabs(
                    [
                        "📅 Distribuição por Dia da Semana",
                        "🕒 Distribuição por Hora do Dia",
                    ]
                )

                with tab1:
                    # Adiciona coluna de dia da semana
                    dados_filtrados["Dia da Semana"] = dados_filtrados[
                        "Inicio"
                    ].dt.day_name()

                    # Ordem dos dias da semana
                    ordem_dias = [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday",
                    ]
                    nomes_dias_pt = [
                        "Segunda",
                        "Terça",
                        "Quarta",
                        "Quinta",
                        "Sexta",
                        "Sábado",
                        "Domingo",
                    ]

                    # Mapeamento para nomes em português
                    mapeamento_dias = dict(zip(ordem_dias, nomes_dias_pt))
                    dados_filtrados["Dia da Semana PT"] = dados_filtrados[
                        "Dia da Semana"
                    ].map(mapeamento_dias)

                    # Agrupa por dia da semana
                    paradas_por_dia = dados_filtrados.groupby(
                        "Dia da Semana PT"
                    ).agg({"Duração": ["count", "sum"]})
                    paradas_por_dia.columns = [
                        "Número de Paradas",
                        "Duração Total",
                    ]

                    # Converte para horas
                    paradas_por_dia["Duração (horas)"] = paradas_por_dia[
                        "Duração Total"
                    ].apply(lambda x: x.total_seconds() / 3600)

                    # Reordena o índice de acordo com os dias da semana
                    if not paradas_por_dia.empty:
                        paradas_por_dia = paradas_por_dia.reindex(
                            nomes_dias_pt
                        )

                        # Cria o gráfico
                        fig_dias = px.bar(
                            paradas_por_dia.reset_index(),
                            x="Dia da Semana PT",
                            y="Número de Paradas",
                            title="Distribuição de Paradas por Dia da Semana",
                            labels={
                                "Número de Paradas": "Número de Paradas",
                                "Dia da Semana PT": "Dia da Semana",
                            },
                            text="Número de Paradas",
                            color="Dia da Semana PT",
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                        )

                        fig_dias.update_traces(
                            texttemplate="%{text}", textposition="outside"
                        )

                        fig_dias.update_layout(
                            xaxis_tickangle=0,
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=50),
                            plot_bgcolor="rgba(0,0,0,0)",
                            showlegend=False,
                        )

                        st.plotly_chart(fig_dias, use_container_width=True)

                        # Exibe a tabela
                        st.dataframe(
                            paradas_por_dia[
                                ["Número de Paradas", "Duração (horas)"]
                            ],
                            column_config={
                                "Número de Paradas": st.column_config.NumberColumn(
                                    "Número de Paradas", format="%d"
                                ),
                                "Duração (horas)": st.column_config.NumberColumn(
                                    "Duração (horas)", format="%.2f"
                                ),
                            },
                            use_container_width=True,
                        )
                    else:
                        st.info(
                            "Dados insuficientes para análise por dia da semana."
                        )

                with tab2:
                    # Adiciona coluna de hora do dia
                    dados_filtrados["Hora do Dia"] = dados_filtrados[
                        "Inicio"
                    ].dt.hour

                    # Agrupa por hora do dia
                    paradas_por_hora = dados_filtrados.groupby(
                        "Hora do Dia"
                    ).agg({"Duração": ["count", "sum"]})
                    paradas_por_hora.columns = [
                        "Número de Paradas",
                        "Duração Total",
                    ]

                    # Converte para horas
                    paradas_por_hora["Duração (horas)"] = paradas_por_hora[
                        "Duração Total"
                    ].apply(lambda x: x.total_seconds() / 3600)

                    # Cria o gráfico
                    if not paradas_por_hora.empty:
                        fig_horas = px.line(
                            paradas_por_hora.reset_index(),
                            x="Hora do Dia",
                            y="Número de Paradas",
                            title="Distribuição de Paradas por Hora do Dia",
                            labels={
                                "Número de Paradas": "Número de Paradas",
                                "Hora do Dia": "Hora do Dia",
                            },
                            markers=True,
                        )

                        # Adiciona área sob a linha
                        fig_horas.add_trace(
                            go.Scatter(
                                x=paradas_por_hora.reset_index()[
                                    "Hora do Dia"
                                ],
                                y=paradas_por_hora["Número de Paradas"],
                                fill="tozeroy",
                                fillcolor="rgba(52, 152, 219, 0.2)",
                                line=dict(color="rgba(52, 152, 219, 0)"),
                                showlegend=False,
                            )
                        )

                        fig_horas.update_layout(
                            xaxis=dict(
                                tickmode="array",
                                tickvals=list(range(0, 24)),
                                ticktext=[f"{h}:00" for h in range(0, 24)],
                            ),
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=50),
                            plot_bgcolor="rgba(0,0,0,0)",
                            showlegend=False,
                        )

                        st.plotly_chart(fig_horas, use_container_width=True)

                        # Exibe a tabela
                        st.dataframe(
                            paradas_por_hora[
                                ["Número de Paradas", "Duração (horas)"]
                            ],
                            column_config={
                                "Número de Paradas": st.column_config.NumberColumn(
                                    "Número de Paradas", format="%d"
                                ),
                                "Duração (horas)": st.column_config.NumberColumn(
                                    "Duração (horas)", format="%.2f"
                                ),
                            },
                            use_container_width=True,
                        )
                    else:
                        st.info(
                            "Dados insuficientes para análise por hora do dia."
                        )

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning(
                "⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel."
            )

    # Página de Previsões
    elif selected == "Previsões":
        if st.session_state.df is not None:
            pagina_previsao(st.session_state.df)
        else:
            st.warning(
                "⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel."
            )

    # Página de Tendências
    elif selected == "Tendências":
        if st.session_state.df is not None:
            pagina_tendencias(st.session_state.df)
        else:
            st.warning(
                "⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel."
            )

    # Página de Anomalias
    elif selected == "Anomalias":
        if st.session_state.df is not None:
            pagina_anomalias(st.session_state.df)
        else:
            st.warning(
                "⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel."
            )

    # Página de Impacto
    elif selected == "Impacto":
        if st.session_state.df is not None:
            pagina_impacto(st.session_state.df)
        else:
            st.warning(
                "⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel."
            )

    # Página de Relatórios
    elif selected == "Relatórios":
        if st.session_state.df is not None:
            pagina_relatorio(st.session_state.df)
        else:
            st.warning(
                "⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel."
            )

    # Página Sobre
    elif selected == "Sobre":
        st.markdown(
            '<div class="section-title">Sobre a Aplicação</div>',
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(
                    "https://img.icons8.com/fluency/240/factory.png", width=150
                )

            with col2:
                st.markdown(
                    """
                # Análise de Eficiência de Máquinas 3.0
                
                Esta aplicação foi desenvolvida para analisar dados de paradas de máquinas e calcular indicadores de eficiência, 
                fornecendo insights valiosos para melhorar a produtividade e reduzir o tempo de inatividade.
                
                **Versão 3.0** inclui recursos avançados de análise preditiva, detecção de anomalias e geração de relatórios executivos.
                """
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Funcionalidades
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## ✨ Funcionalidades")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    """
                ### 📊 Análise de Dados
                - Visualização de indicadores de disponibilidade e eficiência
                - Identificação das principais causas de paradas
                - Análise da distribuição de paradas por área responsável
                - Acompanhamento da evolução das paradas ao longo do tempo
                """
                )

            with col2:
                st.markdown(
                    """
                ### 🔮 Análise Preditiva
                - Previsão de paradas futuras com machine learning
                - Identificação de tendências e padrões cíclicos
                - Detecção de anomalias e eventos fora do padrão
                - Análise de correlações entre variáveis
                """
                )

            with col3:
                st.markdown(
                    """
                ### 📈 Relatórios e Insights
                - Geração de relatórios executivos
                - Recomendações automáticas baseadas em dados
                - Análise de impacto financeiro das paradas
                - Exportação de dados e visualizações
                """
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Novos recursos
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 🚀 Novos Recursos na Versão 3.0")

            st.markdown(
                """
            ### 🔮 Previsões Avançadas
            Utilize modelos de machine learning para prever o comportamento futuro das paradas com base nos padrões históricos.
            
            ### 📈 Análise de Tendências
            Identifique tendências de aumento, diminuição ou estabilidade nas paradas ao longo do tempo.
            
            ### 🔍 Detecção de Anomalias
            Detecte automaticamente paradas que apresentam comportamento fora do padrão.
            
            ### 💰 Análise de Impacto
            Quantifique o impacto financeiro e operacional das paradas na produção.
            
            ### 📊 Relatórios Executivos
            Gere relatórios completos com os principais indicadores, gráficos e recomendações.
            """
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Como usar
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 📋 Como Usar")

            st.markdown(
                """
            1. **Upload de Dados**: Na página "Dashboard", faça o upload de um arquivo Excel contendo os registros de paradas.
            2. **Explore o Dashboard**: Visualize os indicadores e gráficos principais.
            3. **Análise Detalhada**: Utilize as abas específicas para análises mais aprofundadas:
               - **Dados**: Explore os dados brutos e estatísticas básicas
               - **Previsões**: Veja previsões de paradas futuras
               - **Tendências**: Analise tendências e padrões cíclicos
               - **Anomalias**: Identifique eventos fora do padrão
               - **Impacto**: Quantifique o impacto das paradas
               - **Relatórios**: Gere relatórios executivos
            4. **Exportação**: Use os botões de download para exportar dados e resultados.
            """
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Formato dos dados
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 📋 Formato dos Dados")

            st.markdown(
                """
            O arquivo Excel deve conter as seguintes colunas:
            
            - **Máquina**: Identificador da máquina (será convertido conforme mapeamento)
            - **Inicio**: Data e hora de início da parada
            - **Fim**: Data e hora de fim da parada
            - **Duração**: Tempo de duração da parada (HH:MM:SS)
            - **Parada**: Descrição do tipo de parada
            - **Área Responsável**: Área responsável pela parada
            """
            )

            # Exemplo de dados
            st.markdown("### Exemplo de Dados")

            exemplo_dados = pd.DataFrame(
                {
                    "Máquina": [78, 79, 80, 89, 91],
                    "Inicio": pd.date_range(
                        start="2023-01-01", periods=5, freq="D"
                    ),
                    "Fim": pd.date_range(
                        start="2023-01-01 02:00:00", periods=5, freq="D"
                    ),
                    "Duração": [
                        "02:00:00",
                        "02:00:00",
                        "02:00:00",
                        "02:00:00",
                        "02:00:00",
                    ],
                    "Parada": [
                        "Manutenção",
                        "Erro de Configuração",
                        "Falta de Insumos",
                        "Falha Elétrica",
                        "Troca de Produto",
                    ],
                    "Área Responsável": [
                        "Manutenção",
                        "Operação",
                        "Logística",
                        "Manutenção",
                        "Produção",
                    ],
                }
            )

            st.dataframe(
                exemplo_dados, use_container_width=True, hide_index=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Tecnologias utilizadas
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 🛠️ Tecnologias Utilizadas")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    """
                ### Frontend
                - **Streamlit**: Framework para criação de aplicações web
                - **Plotly**: Biblioteca para criação de gráficos interativos
                - **HTML/CSS**: Estilização e formatação da interface
                """
                )

            with col2:
                st.markdown(
                    """
                ### Análise de Dados
                - **Pandas**: Manipulação e análise de dados
                - **NumPy**: Computação numérica
                - **Scikit-learn**: Modelos de machine learning
                - **Plotly/Matplotlib**: Visualização de dados
                """
                )

            with col3:
                st.markdown(
                    """
                ### Infraestrutura
                - **Streamlit Cloud**: Hospedagem da aplicação
                - **GitHub**: Controle de versão
                - **Python**: Linguagem de programação
                """
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Requisitos do sistema
        with st.expander("📦 Requisitos do Sistema"):
            st.code(
                """
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
            scikit-learn>=1.2.2
            """
            )

    # Rodapé
    st.markdown(
        """
    <div class="footer">
        <p>© 2023-2025 Análise de Eficiência de Máquinas | Desenvolvido com ❤️ usando Streamlit</p>
        <p><small>Versão 3.0.0 | Última atualização: Maio 2025</small></p>
    </div>
    """,
        unsafe_allow_html=True,
    )


# Executa a aplicação
if __name__ == "__main__":
    main()
