# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import io
from prophet import Prophet

# ---------- Configurações da Página ----------
st.set_page_config(
    page_title="Dashboard de Produção - Britvic",
    layout="wide",
    page_icon="🧃",
    initial_sidebar_state="expanded"
)

# ---------- Dicionários de Tradução ----------
LANGS = {
    "pt": "Português (Brasil)",
    "en": "English"
}

TRANSLATIONS = {
    "dashboard_title": {"pt": "Dashboard de Produção - Britvic", "en": "Production Dashboard - Britvic"},
    "overview": {"pt": "Visão Geral", "en": "Overview"},
    "forecast": {"pt": "Previsão", "en": "Forecast"},
    "data": {"pt": "Dados", "en": "Data"},
    "select_file": {"pt": "Faça upload do arquivo de produção", "en": "Upload your production file"},
    "date_range": {"pt": "Intervalo de Datas", "en": "Date Range"},
    "download_file": {"pt": "Baixar Arquivo Filtrado", "en": "Download Filtered File"},
    "download_forecast": {"pt": "Baixar Previsão", "en": "Download Forecast"},
    "language": {"pt": "Idioma", "en": "Language"},
    "total_production": {"pt": "Produção Total", "en": "Total Production"},
    "average_daily": {"pt": "Média Diária", "en": "Daily Average"},
    "max_production": {"pt": "Máxima Produção", "en": "Max Production"},
    "min_production": {"pt": "Mínima Produção", "en": "Min Production"},
    "production_over_time": {"pt": "Produção ao Longo do Tempo", "en": "Production Over Time"},
    "forecast_over_time": {"pt": "Previsão ao Longo do Tempo", "en": "Forecast Over Time"},
    "training_model": {"pt": "Treinando o modelo...", "en": "Training model..."},
    "filters": {"pt": "Filtros", "en": "Filters"}
}

def t(key):
    return TRANSLATIONS.get(key, {}).get(idioma, key)

# ---------- Sidebar (Filtros) ----------
with st.sidebar.expander("", expanded=True):
    st.markdown("## 🌐 " + " / ".join([LANGS["pt"], LANGS["en"]]))
    idioma = st.selectbox("", options=list(LANGS.keys()), format_func=lambda x: LANGS[x])
    st.markdown("---")
    uploaded_file = st.file_uploader(
        t("select_file"),
        type=["csv", "xlsx", "xls"]
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                _df = pd.read_csv(uploaded_file, parse_dates=["date"])
            else:
                _df = pd.read_excel(uploaded_file, engine="openpyxl", parse_dates=["date"])
            min_date = _df["date"].min().date()
            max_date = _df["date"].max().date()
        except Exception:
            st.error("O arquivo deve conter coluna 'date' em formato reconhecível.")
            st.stop()
        date_range = st.date_input(
            t("date_range"),
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = None

st.sidebar.markdown("---")

# ---------- Main ----------
st.title(t("dashboard_title"))

if uploaded_file:
    # Releitura completa do arquivo
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file, parse_dates=["date"])
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl", parse_dates=["date"])
    df = df.sort_values("date")

    if "production" not in df.columns:
        st.error("O arquivo deve conter a coluna 'production'.")
        st.stop()

    if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
    else:
        st.error("Selecione um intervalo de datas válido.")
        st.stop()

    tab1, tab2, tab3 = st.tabs([t("overview"), t("forecast"), t("data")])

    # Visão Geral
    with tab1:
        total = df["production"].sum()
        avg = df["production"].mean()
        mx = df["production"].max()
        mn = df["production"].min()

        c1, c2, c3, c4 = st.columns(4, gap="large")
        c1.metric(t("total_production"), f"{total:,.0f}")
        c2.metric(t("average_daily"), f"{avg:,.2f}")
        c3.metric(t("max_production"), f"{mx:,.0f}")
        c4.metric(t("min_production"), f"{mn:,.0f}")

        fig = px.line(
            df, x="date", y="production",
            title=t("production_over_time"),
            labels={"date": "", "production": ""}
        )
        fig.update_layout(hovermode="x unified", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    # Previsão
    with tab2:
        df_p = df.rename(columns={"date": "ds", "production": "y"})[["ds", "y"]]
        with st.spinner(t("training_model")):
            m = Prophet()
            m.fit(df_p)
            future = m.make_future_dataframe(periods=30)
            forecast = m.predict(future)

        fig_f = px.line(
            forecast, x="ds", y="yhat",
            title=t("forecast_over_time"),
            labels={"ds": "", "yhat": ""}
        )
        fig_f.update_traces(line=dict(dash="dash"))
        fig_f.update_layout(template="plotly_white")
        st.plotly_chart(fig_f, use_container_width=True)

        buf = io.BytesIO()
        forecast[["ds", "yhat"]].to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button(
            label=t("download_forecast"),
            data=buf,
            file_name="forecast.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Dados
    with tab3:
        st.dataframe(df, use_container_width=True)
        buf2 = io.BytesIO()
        df.to_excel(buf2, index=False, engine="openpyxl")
        buf2.seek(0)
        st.download_button(
            label=t("download_file"),
            data=buf2,
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # CSS Customizado e Rodapé
    st.markdown("""
    <style>
      .stMetric { background-color: #f9f9f9 !important; border-radius: 8px !important; padding: 16px !important; }
      .css-1v3fvcr { font-size: 2rem !important; font-weight: bold !important; }
    </style>
    <div style="text-align:center; color:gray; margin-top:40px;">
      © 2025 Dashboard de Produção | Desenvolvido por Matheus Martins Lopes<br>
      <small>Versão 2.0.0 | Última atualização: Maio 2025</small>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info(t("select_file"))
