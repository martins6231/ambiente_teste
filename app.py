import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import requests
import tempfile
import zipfile
from prophet import Prophet
import calendar
import datetime # Adicionado para datetime.date e timedelta

st.set_page_config(
    page_title="Dashboard de Produção - Britvic",
    layout="wide",
    page_icon="🧃"
)

# ----------- Suporte Bilíngue (Português e Inglês) -----------
LANGS = {
    "pt": "Português (Brasil)",
    "en": "English"
}

# Definir idioma padrão se não estiver no session_state
if "user_lang" not in st.session_state:
    st.session_state.user_lang = "pt" # Default para Português

st.sidebar.markdown("## 🌐 Idioma | Language")
# Usar o valor do session_state como index ou default para o radio
idioma_idx = list(LANGS.keys()).index(st.session_state.user_lang) if st.session_state.user_lang in LANGS else 0
idioma_selecionado = st.sidebar.radio(
    "Escolha o idioma / Choose language:",
    options=list(LANGS.keys()),
    format_func=lambda x: LANGS[x],
    key="user_lang_selector", # Nova chave para o widget
    index=idioma_idx
)
# Atualizar o estado do idioma com base na seleção do widget
if st.session_state.user_lang != idioma_selecionado:
    st.session_state.user_lang = idioma_selecionado
    st.rerun() # Reroda o script para aplicar o novo idioma imediatamente


def t(msg_key, **kwargs):
    TRANSLATE = {
        "pt": {
            "dashboard_title": "Dashboard de Produção - Britvic",
            "main_title": "Dashboard de Produção",
            "subtitle": "Visualização dos dados de produção Britvic",
            "category": "🏷️ Categoria:",
            "year": "📅 Ano(s):",
            "month": "📆 Mês(es):",
            "date_range_label": "🗓️ Período de Análise:",
            "analysis_for": "Análise para categoria: <b>{cat}</b>{period_info}",
            "all_data_period": " (Todo o período)",
            "selected_period": " (Período de {start} a {end})",
            "empty_data_for_period": "Não há dados para este período e categoria.",
            "mandatory_col_missing": "Coluna obrigatória ausente: {col}",
            "error_date_conversion": "Erro ao converter coluna 'data'. Algumas datas podem ser inválidas.",
            "error_boxes_conversion": "Erro ao converter 'caixas_produzidas' para numérico. Valores não numéricos foram zerados.",
            "col_with_missing": "Coluna '{col}' com {num} valores ausentes.",
            "negatives": "{num} registros com 'caixas_produzidas' negativas foram removidos.",
            "no_critical": "Nenhum problema crítico encontrado nos dados carregados.",
            "data_issue_report": "Relatório de Qualidade dos Dados",
            "no_data_selection": "Sem dados para a seleção atual.",
            "no_trend": "Sem dados suficientes para exibir a tendência.",
            "daily_trend": "Tendência Diária de Produção - {cat}",
            "monthly_total": "Produção Mensal Total - {cat}",
            "monthly_var": "Variação Percentual Mensal (%) - {cat}",
            "monthly_seasonal": "Sazonalidade Mensal da Produção - {cat}",
            "monthly_comp": "Produção Mensal Comparativa por Ano - {cat}",
            "monthly_accum": "Produção Acumulada Mês a Mês - {cat}",
            "no_forecast": "Previsão não disponível (requer pelo menos 2 pontos de dados históricos).",
            "forecast": "Previsão de Produção (Próximos 6 Meses) - {cat}",
            "auto_insights": "Insights Automáticos sobre a Produção",
            "no_pattern": "Nenhum padrão específico ou preocupante detectado nos dados para esta categoria e período.",
            "recent_growth": "Detectado crescimento na produção nos últimos meses analisados.",
            "recent_fall": "Detectada queda na produção nos últimos meses analisados.",
            "outlier_days": "Foram encontrados {num} dias com produção atípica (possíveis outliers), que podem indicar variações incomuns.",
            "high_var": "Alta variabilidade diária na produção. Sugere-se investigar as causas dessas flutuações para otimizar a estabilidade.",
            "export": "Exportação de Dados",
            "export_with_fc": "⬇️ Exportar dados consolidados com previsão (.xlsx)",
            "download_file": "Download do arquivo Excel ⬇️",
            "no_export": "Sem dados de previsão para incluir na exportação.",
            "add_secrets": "Adicione CLOUD_XLSX_URL ao seu arquivo .streamlit/secrets.toml e certifique-se de que a planilha do Google Sheets está compartilhada como 'qualquer pessoa com o link pode ver'.",
            "error_download_xls": "Erro ao baixar a planilha da nuvem. Código de status: {code}",
            "not_valid_excel": "O arquivo baixado não parece ser um arquivo Excel válido. Verifique se o link no CLOUD_XLSX_URL é público e aponta diretamente para um arquivo .xlsx ou um Google Sheet compartilhável.",
            "excel_open_error": "Erro ao abrir o arquivo Excel: {err}",
            "kpi_year": "Ano {ano}", # Simplificado para o card de KPI
            "kpi_sum": "{qtd:,}", # Apenas o número, "caixas" adicionado no HTML
            "kpi_boxes_label": "caixas", # Label para "caixas"
            "historico": "Histórico de Produção",
            "kpi_daily_avg": "Média diária",
            "kpi_records": "Registros",
            "tab_overview_label": "📈 Visão Geral e Diária",
            "tab_monthly_label": "📅 Análise Mensal",
            "tab_forecast_label": "🔮 Previsão e Insights",
            "tab_export_label": "📥 Exportação",
            "kpi_annual_title": "Resumo Anual da Produção (no período selecionado)",
            "data": "Data",
            "category_lbl": "Categoria",
            "produced_boxes": "Caixas Produzidas",
            "month_lbl": "Mês/Ano",
            "variation": "Variação (%)",
            "prod": "Produção",
            "year_lbl": "Ano",
            "accum_boxes": "Caixas Acumuladas",
            "forecast_boxes": "Previsão de Caixas",
        },
        "en": {
            "dashboard_title": "Production Dashboard - Britvic",
            "main_title": "Production Dashboard",
            "subtitle": "Britvic production data visualization",
            "category": "🏷️ Category:",
            "year": "📅 Year(s):",
            "month": "📆 Month(s):",
            "date_range_label": "🗓️ Analysis Period:",
            "analysis_for": "Analysis for category: <b>{cat}</b>{period_info}",
            "all_data_period": " (All time)",
            "selected_period": " (Period from {start} to {end})",
            "empty_data_for_period": "No data for this period and category.",
            "mandatory_col_missing": "Mandatory column missing: {col}",
            "error_date_conversion": "Error converting 'data' column. Some dates might be invalid.",
            "error_boxes_conversion": "Error converting 'caixas_produzidas' to numeric. Non-numeric values were set to zero.",
            "col_with_missing": "Column '{col}' has {num} missing values.",
            "negatives": "{num} records with negative 'caixas_produzidas' were removed.",
            "no_critical": "No critical issues found in the loaded data.",
            "data_issue_report": "Data Quality Report",
            "no_data_selection": "No data for current selection.",
            "no_trend": "Not enough data to display trend.",
            "daily_trend": "Daily Production Trend - {cat}",
            "monthly_total": "Total Monthly Production - {cat}",
            "monthly_var": "Monthly Percentage Change (%) - {cat}",
            "monthly_seasonal": "Monthly Production Seasonality - {cat}",
            "monthly_comp": "Monthly Production Comparison by Year - {cat}",
            "monthly_accum": "Accumulated Production Month by Month - {cat}",
            "no_forecast": "Forecast not available (requires at least 2 historical data points).",
            "forecast": "Production Forecast (Next 6 Months) - {cat}",
            "auto_insights": "Automatic Production Insights",
            "no_pattern": "No specific or concerning patterns detected in the data for this category and period.",
            "recent_growth": "Production growth detected in the last analyzed months.",
            "recent_fall": "Production drop detected in the last analyzed months.",
            "outlier_days": "{num} days with atypical production found (possible outliers), which may indicate unusual variations.",
            "high_var": "High daily variability in production. It is suggested to investigate the causes of these fluctuations to optimize stability.",
            "export": "Data Export",
            "export_with_fc": "⬇️ Export consolidated data with forecast (.xlsx)",
            "download_file": "Download Excel file ⬇️",
            "no_export": "No forecast data to include in export.",
            "add_secrets": "Add CLOUD_XLSX_URL to your .streamlit/secrets.toml file and ensure the Google Sheet is shared as 'anyone with the link can view'.",
            "error_download_xls": "Error downloading spreadsheet from cloud. Status code: {code}",
            "not_valid_excel": "The downloaded file does not appear to be a valid Excel file. Check if the link in CLOUD_XLSX_URL is public and points directly to an .xlsx file or a shareable Google Sheet.",
            "excel_open_error": "Error opening Excel file: {err}",
            "kpi_year": "Year {ano}",
            "kpi_sum": "{qtd:,}",
            "kpi_boxes_label": "boxes",
            "historico": "Production History",
            "kpi_daily_avg": "Daily avg.",
            "kpi_records": "Records",
            "tab_overview_label": "📈 Overview & Daily",
            "tab_monthly_label": "📅 Monthly Analysis",
            "tab_forecast_label": "🔮 Forecast & Insights",
            "tab_export_label": "📥 Export",
            "kpi_annual_title": "Annual Production Summary (in selected period)",
            "data": "Date",
            "category_lbl": "Category",
            "produced_boxes": "Produced Boxes",
            "month_lbl": "Month/Year",
            "variation": "Variation (%)",
            "prod": "Production",
            "year_lbl": "Year",
            "accum_boxes": "Accum. Boxes",
            "forecast_boxes": "Forecasted Boxes",
        }
    }
    base = TRANSLATE[st.session_state.user_lang].get(msg_key, msg_key)
    if kwargs:
        base = base.format(**kwargs)
    return base

# -------------- Layout e Cor padrão -------------
BRITVIC_PRIMARY = "#003057"
BRITVIC_ACCENT = "#27AE60"
BRITVIC_BG = "#F4FFF6"

# ---------- CSS Customizado ----------
st.markdown(f"""
    <style>
        /* Globals */
        .stApp {{
            background-color: {BRITVIC_BG};
        }}
        .center {{ text-align: center; }}
        hr.styled-hr {{
            border: none;
            height: 1px;
            background-color: {BRITVIC_PRIMARY}33; /* Linha sutil */
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        /* Titles */
        .britvic-title {{
            font-size: 2.6rem;
            font-weight: bold;
            color: {BRITVIC_PRIMARY};
            text-align: center;
            margin-bottom: 0.3em;
        }}
        .subtitle {{ /* Não usado diretamente, mas pode ser útil */
            text-align: center;
            color: {BRITVIC_PRIMARY};
            font-size: 1.0rem;
            margin-bottom: 1em;
        }}
        .analysis-subtitle {{
            color:{BRITVIC_ACCENT};
            text-align:left;
            font-size: 1.6rem;
            font-weight: 600;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }}
        .section-title {{
            color:{BRITVIC_PRIMARY};
            text-align:left;
            font-size: 1.3rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }}

        /* KPI Cards Styling */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 4px 12px 0 rgba(0, 48, 87, 0.08);
            padding: 20px 24px;
            text-align: center;
            border: 1px solid #E0E0E0;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }}
        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px 0 rgba(0, 48, 87, 0.12);
        }}
        .kpi-title {{
            font-weight: 600;
            color: {BRITVIC_PRIMARY};
            font-size: 1.05em; /* Ajustado */
            margin-bottom: 5px;
        }}
        .kpi-value {{
            color: {BRITVIC_ACCENT};
            font-size: 2em;    /* Ajustado */
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .kpi-value-small {{ /* Para o texto "caixas" */
            font-size: 0.6em;
            font-weight: normal;
            color: {BRITVIC_PRIMARY}CC; /* Um pouco mais suave */
            margin-left: 4px;
        }}
        .kpi-detail {{
            font-size: 0.95em;  /* Ajustado */
            color: {BRITVIC_PRIMARY};
            margin-bottom: 3px;
        }}
        .kpi-detail b {{
            color:{BRITVIC_ACCENT}; /* Cor do destaque no detalhe */
            font-size:1.1em !important;
        }}
        .kpi-sub-detail {{
            font-size: 0.9em;   /* Ajustado */
            color: #555555;
        }}

        /* Streamlit Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 16px; /* Espaçamento aumentado */
            border-bottom: 2px solid {BRITVIC_PRIMARY}44; /* Linha mais visível */
            padding-bottom: 0px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 46px; /* Altura aumentada */
            background-color: transparent;
            border-radius: 8px 8px 0px 0px; /* Bordas mais arredondadas */
            padding: 0px 22px; /* Padding aumentado */
            margin-bottom: -2px;
            border: 2px solid transparent;
            border-bottom: none;
            transition: background-color 0.2s, color 0.2s, border-color 0.2s;
        }}
        .stTabs [data-baseweb="tab"] p {{
             color: {BRITVIC_PRIMARY}B3; /* Cor mais suave para abas inativas */
             font-weight: 500;
             font-size: 1.0rem; /* Tamanho da fonte da aba */
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: {BRITVIC_PRIMARY}1A;
            border-top-color: {BRITVIC_ACCENT}88;
            border-left-color: {BRITVIC_PRIMARY}22;
            border-right-color: {BRITVIC_PRIMARY}22;
        }}
        .stTabs [data-baseweb="tab"]:hover p {{
             color: {BRITVIC_PRIMARY};
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {BRITVIC_BG}; /* Fundo da aba ativa */
            border-top: 3px solid {BRITVIC_ACCENT}; /* Linha superior da aba ativa mais grossa */
            border-left: 2px solid {BRITVIC_PRIMARY}44;
            border-right: 2px solid {BRITVIC_PRIMARY}44;
        }}
        .stTabs [aria-selected="true"] p {{
            color: {BRITVIC_PRIMARY};
            font-weight: 600;
        }}
        /* Expander styling */
        .stExpander {{
            border: 1px solid {BRITVIC_PRIMARY}33 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0,48,87,0.06) !important;
        }}
        .stExpander header {{
            background-color: {BRITVIC_PRIMARY}11 !important;
            border-radius: 8px 8px 0 0 !important;
            padding-top: 10px !important;
            padding-bottom: 10px !important;
        }}
        .stExpander header p {{ /* Texto do header do expander */
            font-weight: 600;
            color: {BRITVIC_PRIMARY};
        }}


        /* Footer Styling */
        .footer {{
            text-align: center;
            padding: 25px;
            font-size: 0.9em;
            color: #444444;
            background-color: {BRITVIC_PRIMARY}11; /* Fundo sutil para o rodapé */
            border-top: 1px solid {BRITVIC_PRIMARY}33;
            margin-top: 40px;
        }}
        .footer p {{ margin: 0.3em 0; }}
    </style>
""", unsafe_allow_html=True)

# ----------- Topo/logomarca ------------
st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: transparent;
        padding: 10px 0 20px 0;
        margin-bottom: 20px;"
    >
        <img src="https://raw.githubusercontent.com/martins6231/app_atd/main/britvic_logo.png" alt="Britvic Logo" style="width: 150px; margin-bottom: 10px;">
        <h1 class="britvic-title">{t("main_title")}</h1>
    </div>
""", unsafe_allow_html=True)


# ---------- Funções auxiliares ------------
def nome_mes(numero_mes_int):
    if not isinstance(numero_mes_int, int) or not 1 <= numero_mes_int <= 12:
        return str(numero_mes_int)
    
    if st.session_state.user_lang == "pt":
        return calendar.month_abbr[numero_mes_int].capitalize()
    else: # en
        return calendar.month_name[numero_mes_int][:3]

def is_excel_file(file_path_or_buffer):
    try:
        with zipfile.ZipFile(file_path_or_buffer): # Tenta como .xlsx
            return True
    except zipfile.BadZipFile: # Se não for .xlsx, tenta como .xls
        if hasattr(file_path_or_buffer, 'seek'):
            original_position = file_path_or_buffer.tell()
            file_path_or_buffer.seek(0)
            header = file_path_or_buffer.read(8)
            file_path_or_buffer.seek(original_position)
            return header == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' # Magic number for .xls
        else: # Path
            try:
                with open(file_path_or_buffer, 'rb') as f:
                    header = f.read(8)
                return header == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
            except Exception: return False
    except Exception: return False

def convert_gsheet_link(shared_url):
    if "docs.google.com/spreadsheets" in shared_url:
        import re
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', shared_url)
        if match:
            sheet_id = match.group(1)
            return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx&gid=0'
    return shared_url

@st.cache_data(ttl=600)
def carregar_excel_nuvem(link):
    url = convert_gsheet_link(link)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        content_type = resp.headers.get('Content-Type', '').lower()
        file_buffer = io.BytesIO(resp.content)
        
        # Verifica se é um tipo excel conhecido OU se a função is_excel_file confirma
        is_known_excel_type = 'spreadsheetml.sheet' in content_type or 'ms-excel' in content_type
        if not (is_known_excel_type or is_excel_file(file_buffer)):
            st.error(t("not_valid_excel"))
            return None
        
        try:
            # Tenta com openpyxl primeiro (para .xlsx), depois xlrd (para .xls)
            df = pd.read_excel(file_buffer, engine="openpyxl")
        except Exception:
            try:
                file_buffer.seek(0) # Reset buffer position
                df = pd.read_excel(file_buffer, engine="xlrd")
            except Exception as e_inner:
                st.error(t("excel_open_error", err=str(e_inner)))
                return None
        return df
    except requests.exceptions.RequestException as e:
        st.error(t("error_download_xls", code=str(e)))
        return None
    except Exception as e_outer:
        st.error(f"Erro inesperado ao carregar dados: {str(e_outer)}")
        return None

if "CLOUD_XLSX_URL" not in st.secrets:
    st.error(t("add_secrets"))
    st.stop()

xlsx_url = st.secrets["CLOUD_XLSX_URL"]
df_raw = carregar_excel_nuvem(xlsx_url)

if df_raw is None or df_raw.empty:
    st.warning("Não foi possível carregar os dados da planilha ou a planilha está vazia. Verifique o link e as permissões, ou o conteúdo da planilha.")
    st.stop()

def tratar_dados(df_input):
    erros = []
    df = df_input.copy()
    df = df.rename(columns=lambda x: str(x).strip().lower().replace(" ", "_"))
    
    obrigatorias = ['categoria', 'data', 'caixas_produzidas']
    for col in obrigatorias:
        if col not in df.columns:
            erros.append(t("mandatory_col_missing", col=col))
            df[col] = np.nan # Adiciona coluna com NaN para evitar quebras posteriores

    if 'data' in df.columns:
        original_data_count = len(df)
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        invalid_dates_count = df['data'].isnull().sum()
        if invalid_dates_count > 0:
            erros.append(t("error_date_conversion") + f" {invalid_dates_count} datas inválidas foram removidas.")
            df.dropna(subset=['data'], inplace=True)
    
    if 'caixas_produzidas' in df.columns:
        # Verifica se há não numéricos ANTES da conversão
        non_numeric_before = df['caixas_produzidas'].apply(lambda x: not isinstance(x, (int, float))).sum()
        df['caixas_produzidas'] = pd.to_numeric(df['caixas_produzidas'], errors='coerce')
        
        # Se houve não numéricos e agora são NaN, significa que foram 'coerced'
        coerced_to_nan = df['caixas_produzidas'].isnull().sum()
        if non_numeric_before > 0 and coerced_to_nan > 0 : # Se havia não numéricos que viraram NaN
             erros.append(t("error_boxes_conversion") + f" {coerced_to_nan} valores não numéricos foram zerados.")
        df['caixas_produzidas'] = df['caixas_produzidas'].fillna(0) # Zera os NaNs (originalmente não numéricos)
        
        negativos_count = (df['caixas_produzidas'] < 0).sum()
        if negativos_count > 0:
            erros.append(t("negatives", num=negativos_count))
            df = df[df['caixas_produzidas'] >= 0]
        df['caixas_produzidas'] = df['caixas_produzidas'].astype(int)

    na_count = df.isna().sum()
    for col, qtd in na_count.items():
        if qtd > 0 and col in obrigatorias: # Apenas reporta NAs em colunas obrigatórias após tratamentos
             erros.append(t("col_with_missing", col=col, num=qtd) + " Linhas com valores ausentes nessas colunas foram removidas.")

    df_clean = df.dropna(subset=['categoria', 'data', 'caixas_produzidas']).copy()
    
    # Tratamento de duplicatas: manter a primeira ocorrência para uma combinação de categoria e data
    duplicates_before = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['categoria', 'data'], keep='first')
    duplicates_removed = duplicates_before - len(df_clean)
    if duplicates_removed > 0:
        erros.append(f"{duplicates_removed} linhas duplicadas (mesma categoria e data) foram removidas, mantendo a primeira ocorrência.")
        
    return df_clean, erros

df, erros_tratamento = tratar_dados(df_raw)

with st.expander(t("data_issue_report"), expanded=len(erros_tratamento) > 0):
    if erros_tratamento:
        for e in erros_tratamento:
            st.warning(f"⚠️ {e}")
    else:
        st.success(f"✅ {t('no_critical')}")

if df.empty:
    st.error("Após o tratamento, não restaram dados válidos para análise. Verifique a planilha de origem.")
    st.stop()

def selecionar_categoria(df_clean):
    return sorted(df_clean['categoria'].dropna().unique())

# ----------- Parâmetros / Filtros na Sidebar -----------
categorias_disponiveis = selecionar_categoria(df)
if not categorias_disponiveis:
    st.error("Nenhuma categoria encontrada nos dados tratados.")
    st.stop()

# Define valores padrão para os filtros se não existirem no session_state
if "filtros" not in st.session_state:
    st.session_state["filtros"] = {
        "categoria": categorias_disponiveis[0],
        "data_inicio": df['data'].min().date() if not df.empty else datetime.date.today() - datetime.timedelta(days=365),
        "data_fim": df['data'].max().date() if not df.empty else datetime.date.today()
    }

with st.sidebar:
    st.markdown("## 📊 Filtros de Análise")
    
    # Filtro de Categoria
    categoria_selecionada = st.selectbox(
        t("category"), 
        categorias_disponiveis, 
        index=categorias_disponiveis.index(st.session_state["filtros"]["categoria"]) if st.session_state["filtros"]["categoria"] in categorias_disponiveis else 0,
        key="cat_selector"
    )
    st.session_state["filtros"]["categoria"] = categoria_selecionada

    # Filtro de Período (Date Range Picker)
    min_data_disponivel = df['data'].min().date()
    max_data_disponivel = df['data'].max().date()

    # Garantir que as datas no session_state são válidas e dentro do range
    if not (min_data_disponivel <= st.session_state["filtros"]["data_inicio"] <= max_data_disponivel):
        st.session_state["filtros"]["data_inicio"] = min_data_disponivel
    if not (min_data_disponivel <= st.session_state["filtros"]["data_fim"] <= max_data_disponivel):
        st.session_state["filtros"]["data_fim"] = max_data_disponivel
    # Garantir que data_inicio não é posterior a data_fim
    if st.session_state["filtros"]["data_inicio"] > st.session_state["filtros"]["data_fim"]:
        st.session_state["filtros"]["data_fim"] = st.session_state["filtros"]["data_inicio"]


    datas_selecionadas = st.date_input(
        t("date_range_label"),
        value=(st.session_state["filtros"]["data_inicio"], st.session_state["filtros"]["data_fim"]),
        min_value=min_data_disponivel,
        max_value=max_data_disponivel,
        key="date_range_selector"
    )

    if len(datas_selecionadas) == 2:
        st.session_state["filtros"]["data_inicio"], st.session_state["filtros"]["data_fim"] = datas_selecionadas
    else: # Caso o date_input retorne apenas uma data (pode acontecer em certas interações)
        st.session_state["filtros"]["data_inicio"] = datas_selecionadas[0]
        st.session_state["filtros"]["data_fim"] = datas_selecionadas[0]

# Filtrar DataFrame com base nas seleções
df_filtrado = df[
    (df['categoria'] == st.session_state["filtros"]["categoria"]) &
    (df['data'].dt.date >= st.session_state["filtros"]["data_inicio"]) &
    (df['data'].dt.date <= st.session_state["filtros"]["data_fim"])
].copy() # .copy() para evitar SettingWithCopyWarning

# --------- Subtítulo Dinâmico ---------
periodo_info_str = t("selected_period", start=st.session_state['filtros']['data_inicio'].strftime('%d/%m/%Y'), end=st.session_state['filtros']['data_fim'].strftime('%d/%m/%Y'))
st.markdown(
    f"<h2 class='analysis-subtitle'>{t('analysis_for', cat=st.session_state['filtros']['categoria'], period_info=periodo_info_str)}</h2>",
    unsafe_allow_html=True
)

if df_filtrado.empty:
    st.warning(t("empty_data_for_period"))
    st.stop()

# --------- Funções de Geração de Dados para Gráficos --------
def dataset_ano_mes(df_periodo, categoria_foco):
    df_f = df_periodo[df_periodo['categoria'] == categoria_foco].copy() # .copy()
    if df_f.empty: return pd.DataFrame(columns=['ano', 'mes', 'caixas_produzidas']) # Retorna DF vazio se não há dados
    df_f['ano'] = df_f['data'].dt.year
    df_f['mes'] = df_f['data'].dt.month
    return df_f

def gerar_dataset_modelo(df_periodo, categoria_foco):
    df_cat = df_periodo[df_periodo['categoria'] == categoria_foco].copy() # .copy()
    if df_cat.empty: return pd.DataFrame(columns=['data', 'caixas_produzidas'])
    grupo = df_cat.groupby(df_cat['data'].dt.date)['caixas_produzidas'].sum().reset_index()
    grupo['data'] = pd.to_datetime(grupo['data']) # Certifica que 'data' é datetime
    return grupo.sort_values('data')


# --------- KPIs Anuais ---------
def exibe_kpis_anuais(df_kpi, categoria_kpi):
    df_cat_kpi = df_kpi[df_kpi['categoria'] == categoria_kpi].copy() # .copy()
    if df_cat_kpi.empty:
        st.info(t("no_data_selection"))
        return None
    
    df_cat_kpi['ano'] = df_cat_kpi['data'].dt.year
    kpis_df = df_cat_kpi.groupby('ano')['caixas_produzidas'].agg(['sum', 'mean', 'count']).reset_index()
    
    if kpis_df.empty:
        st.info(t("no_data_selection"))
        return None

    st.markdown(f"<h3 class='section-title'>{t('kpi_annual_title')}</h3>", unsafe_allow_html=True)
    
    kpi_html_items = []
    for _, row in kpis_df.iterrows():
        ano = int(row['ano'])
        kpi_item_html = f"""
        <div class="kpi-card">
            <div class="kpi-title">{t("kpi_year", ano=ano)}</div>
            <div class="kpi-value">{t("kpi_sum", qtd=int(row['sum']))} <span class="kpi-value-small">{t("kpi_boxes_label")}</span></div>
            <div class="kpi-detail">{t('kpi_daily_avg')}: <b>{row["mean"]:.0f}</b></div>
            <div class="kpi-sub-detail">{t('kpi_records')}: <b>{row['count']}</b></div>
        </div>
        """
        kpi_html_items.append(kpi_item_html)
    
    st.markdown(f"<div class='kpi-grid'>{''.join(kpi_html_items)}</div>", unsafe_allow_html=True)
    return kpis_df


# --------- Abas para Organização ---------
tab_overview, tab_monthly, tab_forecast, tab_export_tab = st.tabs([
    t("tab_overview_label"), 
    t("tab_monthly_label"), 
    t("tab_forecast_label"),
    t("tab_export_label")
])

# ------- ABA: Visão Geral e Diária -------
with tab_overview:
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)
    exibe_kpis_anuais(df_filtrado, st.session_state["filtros"]["categoria"])
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)

    def plot_tendencia_diaria(df_plot, categoria_plot):
        grupo_plot = gerar_dataset_modelo(df_plot, categoria_plot)
        if grupo_plot.empty or len(grupo_plot) < 2 : # Precisa de pelo menos 2 pontos para uma linha/barra significativa
            st.info(t("no_trend"))
            return
        
        fig = px.bar(
            grupo_plot, x='data', y='caixas_produzidas',
            title=t("daily_trend", cat=categoria_plot),
            labels={"data": t("data"), "caixas_produzidas": t("produced_boxes")},
            # text_auto='.2s' # Formato para texto dentro das barras
        )
        fig.update_traces(marker_color=BRITVIC_ACCENT, hovertemplate="<b>%{x|%d %b %Y}</b><br>" + t("produced_boxes") + ": %{y:,}<extra></extra>")
        fig.update_layout(
            template="plotly_white", 
            hovermode="x unified",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor='rgba(0,0,0,0)', # Fundo transparente
            paper_bgcolor='rgba(0,0,0,0)', # Fundo do papel transparente
            xaxis_title=t("data"),
            yaxis_title=t("produced_boxes"),
            height=450 # Altura do gráfico
        )
        st.plotly_chart(fig, use_container_width=True)

    plot_tendencia_diaria(df_filtrado, st.session_state["filtros"]["categoria"])

# ------- ABA: Análise Mensal -------
with tab_monthly:
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)
    categoria_atual = st.session_state["filtros"]["categoria"]

    def plot_variacao_mensal(df_plot, categoria_plot):
        agrup_plot = dataset_ano_mes(df_plot, categoria_plot)
        if agrup_plot.empty:
            st.info(t("no_trend"))
            return

        mensal = agrup_plot.groupby(agrup_plot['data'].dt.to_period('M'))['caixas_produzidas'].sum().reset_index()
        mensal['data'] = mensal['data'].dt.to_timestamp() # Convertendo Period para Timestamp para Plotly
        mensal = mensal.sort_values('data')
        mensal['mes_ano_str'] = mensal['data'].dt.strftime('%b/%Y')
        mensal['var_%'] = mensal['caixas_produzidas'].pct_change() * 100
        mensal['var_%'] = mensal['var_%'].round(2) # Arredonda para 2 casas decimais

        if mensal.empty or len(mensal) < 2:
            st.info(t("no_trend") + " (mensal)")
            return

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(
                mensal, x='mes_ano_str', y='caixas_produzidas', 
                # text_auto='.2s',
                title=t("monthly_total", cat=categoria_plot),
                labels={"mes_ano_str":t("month_lbl"), "caixas_produzidas":t("produced_boxes")}
            )
            fig1.update_traces(marker_color=BRITVIC_ACCENT, hovertemplate="<b>%{x}</b><br>" + t("produced_boxes") + ": %{y:,}<extra></extra>")
            fig1.update_layout(template="plotly_white", title_font_color=BRITVIC_PRIMARY, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.line(
                mensal.dropna(subset=['var_%']), x='mes_ano_str', y='var_%', markers=True,
                title=t("monthly_var", cat=categoria_plot),
                labels={"mes_ano_str": t("month_lbl"), "var_%":t("variation")}
            )
            fig2.update_traces(line_color="#E67E22", marker=dict(size=8, color=BRITVIC_ACCENT, symbol='circle'), hovertemplate="<b>%{x}</b><br>" + t("variation") + ": %{y:.2f}%<extra></extra>")
            fig2.update_layout(template="plotly_white", title_font_color=BRITVIC_PRIMARY, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig2, use_container_width=True)
    
    plot_variacao_mensal(df_filtrado, categoria_atual)
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)

    def plot_sazonalidade_mensal(df_plot, categoria_plot):
        agrup_plot = dataset_ano_mes(df_plot, categoria_plot)
        if agrup_plot.empty or agrup_plot['mes'].nunique() < 1:
            st.info(t("no_trend") + " (sazonalidade)")
            return
        
        fig = px.box(
            agrup_plot, x='mes', y='caixas_produzidas', color='ano',
            # points='all', # Pode poluir se houver muitos dados
            notched=True,
            title=t("monthly_seasonal", cat=categoria_plot),
            labels={'mes': t("month_lbl"), "caixas_produzidas":t("prod"), "ano": t("year_lbl")},
            category_orders={"mes": list(range(1,13))}, # Garante a ordem dos meses
            color_discrete_sequence=px.colors.qualitative.Pastel # Esquema de cores mais suave
        )
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1,13)),
                ticktext=[nome_mes(m) for m in range(1,13)]
            ),
            template="plotly_white",
            legend_title_text=t('year_lbl'),
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    plot_sazonalidade_mensal(df_filtrado, categoria_atual)
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)

    def plot_comparativo_ano_mes(df_plot, categoria_plot):
        agrup_plot = dataset_ano_mes(df_plot, categoria_plot)
        if agrup_plot.empty or agrup_plot['ano'].nunique() < 1: # Precisa de pelo menos 1 ano para comparar (ou mostrar)
            st.info(t("no_trend") + " (comparativo ano/mês)")
            return

        tab = agrup_plot.groupby(['ano','mes'])['caixas_produzidas'].sum().reset_index()
        tab['mes_nome'] = tab['mes'].apply(nome_mes)
        
        # Ordenar meses corretamente
        month_order = [nome_mes(i) for i in range(1,13)]
        tab['mes_nome'] = pd.Categorical(tab['mes_nome'], categories=month_order, ordered=True)
        tab = tab.sort_values(['ano', 'mes_nome'])

        fig = go.Figure()
        anos_unicos = sorted(tab['ano'].unique())
        cores = px.colors.qualitative.Plotly # Usar paleta padrão do Plotly

        for idx, ano_val in enumerate(anos_unicos):
            dados_ano = tab[tab['ano'] == ano_val]
            fig.add_trace(go.Bar(
                x=dados_ano['mes_nome'],
                y=dados_ano['caixas_produzidas'],
                name=str(ano_val),
                # text=dados_ano['caixas_produzidas'].apply(lambda x: f'{x:,.0f}'), # Formata texto
                # textposition='auto',
                marker_color=cores[idx % len(cores)],
                hovertemplate="<b>" + str(ano_val) + " - %{x}</b><br>" + t("produced_boxes") + ": %{y:,}<extra></extra>"
            ))
        fig.update_layout(
            barmode='group',
            title=t("monthly_comp", cat=categoria_plot),
            xaxis_title=t("month_lbl"),
            yaxis_title=t("produced_boxes"),
            legend_title_text=t("year_lbl"),
            hovermode="x unified",
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    if df_filtrado['data'].dt.year.nunique() > 0: # Só mostra se houver mais de um ano no período filtrado
        plot_comparativo_ano_mes(df_filtrado, categoria_atual)
        st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)

    def plot_comparativo_acumulado(df_plot, categoria_plot):
        agrup_plot = dataset_ano_mes(df_plot, categoria_plot)
        if agrup_plot.empty or agrup_plot['ano'].nunique() < 1:
            st.info(t("no_trend") + " (acumulado)")
            return

        res = agrup_plot.groupby(['ano','mes'])['caixas_produzidas'].sum().reset_index()
        res['acumulado'] = res.groupby('ano')['caixas_produzidas'].cumsum()
        res['mes_nome'] = res['mes'].apply(nome_mes)
        
        month_order = [nome_mes(i) for i in range(1,13)]
        res['mes_nome'] = pd.Categorical(res['mes_nome'], categories=month_order, ordered=True)
        res = res.sort_values(['ano', 'mes_nome'])

        fig = px.line(
            res, x='mes_nome', y='acumulado', color='ano', markers=True,
            labels={'mes_nome': t("month_lbl"), 'acumulado':t("accum_boxes"), 'ano':t("year_lbl")},
            title=t("monthly_accum", cat=categoria_plot),
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_traces(mode="lines+markers", hovertemplate="<b>%{fullData.name} - %{x}</b><br>" + t("accum_boxes") + ": %{y:,}<extra></extra>")
        fig.update_layout(
            legend_title_text=t("year_lbl"),
            hovermode="x unified",
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if df_filtrado['data'].dt.year.nunique() > 0:
        plot_comparativo_acumulado(df_filtrado, categoria_atual)

# ------- ABA: Previsão e Insights -------
with tab_forecast:
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)
    categoria_atual = st.session_state["filtros"]["categoria"]

    @st.cache_data(ttl=3600) # Cache da previsão
    def rodar_previsao_prophet(_df_modelo, meses_futuro=6):
        if _df_modelo.shape[0] < 2: # Prophet precisa de pelo menos 2 pontos
            return _df_modelo, pd.DataFrame(), None 
        
        dados_prophet = _df_modelo.rename(columns={'data':'ds', 'caixas_produzidas':'y'})
        
        try:
            # Configurações do Prophet: seasonality_mode='multiplicative' pode ser bom para % de crescimento
            # yearly_seasonality e weekly_seasonality podem ser ajustados ou auto.
            # daily_seasonality é False pois os dados são diários agregados, a sazonalidade diária não se aplica da mesma forma.
            modelo = Prophet(
                yearly_seasonality=True, 
                weekly_seasonality=False, # Geralmente não relevante para produção diária agregada
                daily_seasonality=False,
                # seasonality_mode='multiplicative', # Pode ser testado
                # growth='logistic', # Se houver um teto de produção conhecido (cap)
            )
            # Se houver poucos dados anuais, pode ser melhor desabilitar yearly_seasonality
            if dados_prophet['ds'].dt.year.nunique() < 2:
                 modelo.yearly_seasonality = False

            modelo.fit(dados_prophet)
            futuro = modelo.make_future_dataframe(periods=meses_futuro*30, freq='D') # Frequência diária
            previsao = modelo.predict(futuro)
            return dados_prophet, previsao, modelo
        except Exception as e:
            st.error(f"Erro ao rodar o modelo Prophet: {e}")
            return dados_prophet, pd.DataFrame(), None


    df_para_modelo = gerar_dataset_modelo(df_filtrado, categoria_atual)
    dados_hist_prophet, previsao_prophet, _ = rodar_previsao_prophet(df_para_modelo.copy(), meses_futuro=6) # Passa cópia

    def plot_previsao(dados_hist_plot, previsao_plot, categoria_plot):
        if previsao_plot.empty or dados_hist_plot.empty:
            st.info(t("no_forecast"))
            return
        
        fig = go.Figure()
        # Histórico
        fig.add_trace(go.Scatter(
            x=dados_hist_plot['ds'], y=dados_hist_plot['y'],
            mode='lines+markers', name=t("historico"),
            line=dict(color=BRITVIC_PRIMARY, width=2.5),
            marker=dict(color=BRITVIC_ACCENT, size=5),
            hovertemplate="<b>" + t("historico") + " (%{x|%d %b %Y})</b><br>" + t("produced_boxes") + ": %{y:,.0f}<extra></extra>"
        ))
        # Previsão (yhat)
        fig.add_trace(go.Scatter(
            x=previsao_plot['ds'], y=previsao_plot['yhat'],
            mode='lines', name=t("forecast_boxes"), 
            line=dict(color=BRITVIC_ACCENT, width=2.5, dash='dash'),
            hovertemplate="<b>" + t("forecast_boxes") + " (%{x|%d %b %Y})</b><br>" + t("produced_boxes") + ": %{y:,.0f}<extra></extra>"
        ))
        # Intervalo de confiança
        fig.add_trace(go.Scatter(
            x=previsao_plot['ds'], y=previsao_plot['yhat_upper'],
            mode='lines', line=dict(width=0), showlegend=False, name='Upper Bound',
            hoverinfo='skip' # Não mostrar no hover individual
        ))
        fig.add_trace(go.Scatter(
            x=previsao_plot['ds'], y=previsao_plot['yhat_lower'],
            mode='lines', line=dict(width=0), fillcolor='rgba(39, 174, 96, 0.2)', fill='tonexty', # Preenche até o yhat_upper
            showlegend=False, name='Lower Bound',
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title=t("forecast", cat=categoria_plot),
            xaxis_title=t("data"), yaxis_title=t("produced_boxes"),
            template="plotly_white", hovermode="x unified",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    plot_previsao(dados_hist_prophet, previsao_prophet, categoria_atual)
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)
    
    def gerar_insights_automaticos(df_plot, categoria_plot):
        st.markdown(f"<h3 class='section-title'>{t('auto_insights')}</h3>", unsafe_allow_html=True)
        insights = []
        grupo_insights = gerar_dataset_modelo(df_plot, categoria_plot)

        if grupo_insights.empty or len(grupo_insights) < 7: # Poucos dados para insights robustos
            st.info(t("no_pattern"))
            return

        # 1. Crescimento/Queda Recente (baseado em média móvel simples de produção mensal)
        mensal_sum = grupo_insights.set_index('data')['caixas_produzidas'].resample('M').sum()
        if len(mensal_sum) >= 6: # Precisa de pelo menos 6 meses
            media_ultimos_3m = mensal_sum.rolling(window=3).mean().iloc[-1]
            media_3m_anteriores = mensal_sum.rolling(window=3).mean().iloc[-2] if len(mensal_sum) >= 4 else None # Média do período anterior de 3 meses
            
            if media_3m_anteriores is not None and not pd.isna(media_ultimos_3m) and not pd.isna(media_3m_anteriores):
                if media_ultimos_3m > media_3m_anteriores * 1.05: # Crescimento de >5%
                    insights.append(f"💡 {t('recent_growth')}")
                elif media_ultimos_3m < media_3m_anteriores * 0.95: # Queda de >5%
                    insights.append(f"📉 {t('recent_fall')}")

        # 2. Outliers Diários (usando IQR)
        q1 = grupo_insights['caixas_produzidas'].quantile(0.25)
        q3 = grupo_insights['caixas_produzidas'].quantile(0.75)
        iqr = q3 - q1
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr
        outliers = grupo_insights[(grupo_insights['caixas_produzidas'] < limite_inferior) | (grupo_insights['caixas_produzidas'] > limite_superior)]
        if not outliers.empty:
            insights.append(f"⚠️ {t('outlier_days', num=outliers.shape[0])}")

        # 3. Alta Variabilidade (Coeficiente de Variação)
        mean_prod = grupo_insights['caixas_produzidas'].mean()
        std_prod = grupo_insights['caixas_produzidas'].std()
        if mean_prod > 0 and (std_prod / mean_prod) > 0.6: # CV > 60% pode ser considerado alto
            insights.append(f"📊 {t('high_var')}")
        
        if insights:
            for insight_text in insights:
                st.info(insight_text)
        else:
            st.success(f"✅ {t('no_pattern')}")

    gerar_insights_automaticos(df_filtrado, categoria_atual)


# ------- ABA: Exportação -------
with tab_export_tab:
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)
    st.markdown(f"<h3 class='section-title'>{t('export')}</h3>", unsafe_allow_html=True)

    def exportar_consolidado_excel(df_hist_export, previsao_export, categoria_export):
        if df_hist_export.empty:
            st.warning(t("no_data_selection") + " para exportação.")
            return None, None

        # Prepara dados históricos
        base_export = df_hist_export[df_hist_export['categoria'] == categoria_export][['data', 'caixas_produzidas']].copy()
        base_export = base_export.rename(columns={'caixas_produzidas': t('produced_boxes')})
        
        # Prepara dados de previsão se existirem
        if not previsao_export.empty:
            previsao_col = previsao_export[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            previsao_col.rename(columns={
                'ds':'data', 
                'yhat': t('forecast_boxes'),
                'yhat_lower': f"{t('forecast_boxes')} (Lower)",
                'yhat_upper': f"{t('forecast_boxes')} (Upper)"
            }, inplace=True)
            previsao_col[t('forecast_boxes')] = previsao_col[t('forecast_boxes')].round(0).astype(int)
            previsao_col[f"{t('forecast_boxes')} (Lower)"] = previsao_col[f"{t('forecast_boxes')} (Lower)"].round(0).astype(int)
            previsao_col[f"{t('forecast_boxes')} (Upper)"] = previsao_col[f"{t('forecast_boxes')} (Upper)"].round(0).astype(int)

            # Merge: outer join para manter todas as datas, tanto históricas quanto futuras
            base_export = pd.merge(base_export, previsao_col, on='data', how='outer')
        else:
            st.info(t("no_export")) # Informa que a previsão não está incluída

        base_export['data'] = pd.to_datetime(base_export['data'])
        base_export = base_export.sort_values("data")
        base_export['data'] = base_export['data'].dt.strftime('%Y-%m-%d') # Formata data para Excel
        
        # Adicionar coluna de categoria
        base_export[t('category_lbl')] = categoria_export
        
        # Reordenar colunas para melhor visualização no Excel
        cols_order = [t('category_lbl'), 'data', t('produced_boxes')]
        if not previsao_export.empty:
            cols_order.extend([t('forecast_boxes'), f"{t('forecast_boxes')} (Lower)", f"{t('forecast_boxes')} (Upper)""])
        
        # Filtra colunas existentes para evitar erro se alguma não foi gerada
        cols_order = [col for col in cols_order if col in base_export.columns]
        base_export = base_export[cols_order]

        nome_arq = f"producao_britvic_{categoria_export.lower().replace(' ', '_')}_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            base_export.to_excel(writer, index=False, sheet_name=f"Dados_{categoria_export[:25]}") # Limita nome da aba
        buffer.seek(0)
        return buffer, nome_arq

    # Usa df_filtrado para dados históricos, e previsao_prophet (que já é filtrada)
    buffer_export, nome_arquivo_export = exportar_consolidado_excel(df_filtrado, previsao_prophet, categoria_atual)

    if buffer_export and nome_arquivo_export:
        st.download_button(
            label=t("export_with_fc"),
            data=buffer_export,
            file_name=nome_arquivo_export,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel_button"
        )
    elif df_filtrado.empty:
        st.info("Não há dados filtrados para exportar.")


# Rodapé
st.markdown("""
<div class="footer">
    <p>© 2024-2025 Dashboard de Produção Britvic | Desenvolvido por Matheus Martins Lopes usando Streamlit</p>
    <p><small>Versão 2.1.0 | Última atualização: Maio 2025</small></p>
</div>
""", unsafe_allow_html=True)
