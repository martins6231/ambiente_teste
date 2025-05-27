# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from prophet import Prophet

# ---------- Configurações da Página ----------
st.set_page_config(
    page_title="Dashboard de Produção - Britvic",
    layout="wide",
    page_icon="🧃"
)

# ---------- Dicionários de Tradução ----------
LANGS = {
    "pt": "Português (Brasil)",
    "en": "English"
}

TRANSLATIONS = {
    "dashboard_title": {
        "pt": "Dashboard de Produção - Britvic",
        "en": "Production Dashboard - Britvic"
    },
    "overview": {"pt": "Visão Geral", "en": "Overview"},
    "forecast": {"pt": "Previsão", "en": "Forecast"},
    "data": {"pt": "Dados", "en": "Data"},
    "select_file": {
        "pt": "Faça upload do arquivo de produção",
        "en": "Upload your production file"
    },
    "date_range": {"pt": "Intervalo de Datas", "en": "Date Range"},
    "download_file": {
        "pt": "Baixar Arquivo Filtrado",
        "en": "Download Filtered File"
    },
    "download_forecast": {
        "pt": "Baixar Previsão",
        "en": "Download Forecast"
    },
    "language": {"pt": "🌐 Idioma", "en": "🌐 Language"},
    "total_production": {"pt": "Produção Total", "en": "Total Production"},
    "average_daily": {"pt": "Média Diária", "en": "Daily Average"},
    "max_production": {"pt": "Máxima Produção", "en": "Max Production"},
    "min_production": {"pt": "Mínima Produção", "en": "Min Production"},
    "production_over_time": {
        "pt": "Produção ao Longo do Tempo",
        "en": "Production Over Time"
    },
    "forecast_over_time": {
        "pt": "Previsão ao Longo do Tempo",
        "en": "Forecast Over Time"
    },
    "training_model": {
        "pt": "Treinando o modelo...",
        "en": "Training model..."
    }
}

def t(key):
    return TRANSLATIONS.get(key, {}).get(idioma, key)

# ---------- Sidebar ----------
st.sidebar.markdown("## " + t("language"))
idioma = st.sidebar.selectbox("", options=list(LANGS.keys()),
                              format_func=lambda x: LANGS[x])

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader(
    t("select_file"),
    type=["csv", "xlsx", "xls"]
)

# ---------- Main ----------
st.title(t("dashboard_title"))

if uploaded_file is not None:
    # Leitura do arquivo
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file, parse_dates=True)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    # Conversão da coluna de data
    if "date" not in df.columns:
        st.error("O arquivo deve conter a coluna 'date'.")
        st.stop()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Filtro de intervalo de datas
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input(
        t("date_range"),
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        st.error("Selecione duas datas válidas.")
        st.stop()

    df_filtered = df[(df["date"].dt.date >= start_date) &
                     (df["date"].dt.date <= end_date)]

    # Criação de Tabs
    tab1, tab2, tab3 = st.tabs([t("overview"),
                                t("forecast"), t("data")])

    # ----- Visão Geral -----
    with tab1:
        # Métricas
        total = df_filtered["production"].sum()
        avg_daily = df_filtered["production"].mean()
        max_prod = df_filtered["production"].max()
        min_prod = df_filtered["production"].min()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t("total_production"), f"{total:,.0f}")
        col2.metric(t("average_daily"), f"{avg_daily:,.2f}")
        col3.metric(t("max_production"), f"{max_prod:,.0f}")
        col4.metric(t("min_production"), f"{min_prod:,.0f}")

        # Gráfico de Produção ao Longo do Tempo
        fig = px.line(
            df_filtered,
            x="date",
            y="production",
            title=t("production_over_time"),
            labels={"date": "", "production": ""}
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    # ----- Previsão -----
    with tab2:
        df_prophet = df_filtered.rename(
            columns={"date": "ds", "production": "y"}
        )[['ds', 'y']]
        with st.spinner(t("training_model")):
            m = Prophet()
            m.fit(df_prophet)
            future = m.make_future_dataframe(periods=30)
            forecast = m.predict(future)

        fig_f = px.line(
            forecast,
            x="ds",
            y="yhat",
            title=t("forecast_over_time"),
            labels={"ds": "", "yhat": ""}
        )
        fig_f.update_traces(line=dict(dash="dash"))
        st.plotly_chart(fig_f, use_container_width=True)

        # Botão de download da previsão
        buf_f = io.BytesIO()
        forecast[['ds', 'yhat']].to_excel(buf_f,
                                          index=False,
                                          engine="openpyxl")
        buf_f.seek(0)
        st.download_button(
            label=t("download_forecast"),
            data=buf_f,
            file_name="forecast.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ----- Dados -----
    with tab3:
        st.dataframe(df_filtered, use_container_width=True)
        buf = io.BytesIO()
        df_filtered.to_excel(buf,
                             index=False,
                             engine="openpyxl")
        buf.seek(0)
        st.download_button(
            label=t("download_file"),
            data=buf,
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ----- CSS e Rodapé -----
    st.markdown(
        """
        <style>
        .footer {
            text-align: center;
            color: gray;
            padding: 10px;
        }
        </style>
        <div class="footer">
            <p>© 2025 Dashboard de Produção | Desenvolvido por Matheus Martins Lopes usando Streamlit</p>
            <p><small>Versão 2.0.0 | Última atualização: Maio 2025</small></p>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.info(t("select_file"))
