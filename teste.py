# Web app com Streamlit baseado no notebook original

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Dashboard de Paradas", layout="wide")
sns.set_theme(style="whitegrid")

def formatar_duracao(d):
    if pd.isnull(d): return "00:00:00"
    total_segundos = int(d.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# --- Upload e tratamento ---
st.title("Análise de Eficiência de Máquinas")
st.info("Faça o upload de um arquivo Excel com as colunas: Máquina, Parada, Área Responsável, Inicio, Fim, Duração, Mês, Ano")

uploaded_file = st.file_uploader("Upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    df['Inicio'] = pd.to_datetime(df['Inicio'], errors='coerce')
    df['Fim'] = pd.to_datetime(df['Fim'], errors='coerce')
    df['Duração'] = pd.to_timedelta(df['Duração'])
    df.dropna(subset=['Máquina', 'Inicio', 'Fim', 'Duração'], inplace=True)
    df['Ano-Mês'] = df['Inicio'].dt.to_period("M").astype(str)
    df['Dia da Semana'] = df['Inicio'].dt.day_name()
    df['Hora'] = df['Inicio'].dt.hour

    maquinas = sorted(df['Máquina'].unique())
    periodos = ['Todos'] + sorted(df['Ano-Mês'].unique())

    col1, col2 = st.columns(2)
    maquina = col1.selectbox("Máquina", options=['Todas'] + maquinas)
    mes = col2.selectbox("Período (Ano-Mês)", options=periodos)

    df_filtrado = df.copy()
    if maquina != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Máquina'] == maquina]
    if mes != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Ano-Mês'] == mes]

    st.markdown(f"**Registros filtrados:** {len(df_filtrado)}")

    if not df_filtrado.empty:
        tempo_programado = pd.Timedelta(hours=24 * df_filtrado['Inicio'].dt.date.nunique())
        disponibilidade = max(0, min(100, (tempo_programado - df_filtrado['Duração'].sum()) / tempo_programado * 100))
        eficiencia = disponibilidade
        tmp = df_filtrado['Duração'].mean()
        paradas_criticas = df_filtrado[df_filtrado['Duração'] > pd.Timedelta(hours=1)]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Disponibilidade", f"{disponibilidade:.2f}%")
        col2.metric("Eficiência Operacional", f"{eficiencia:.2f}%")
        col3.metric("TMP", formatar_duracao(tmp))
        col4.metric("Paradas Críticas", f"{len(paradas_criticas)} ({len(paradas_criticas)/len(df_filtrado)*100:.1f}%)")

        st.subheader("Gráficos de Análise")
        fig1, ax1 = plt.subplots()
        pareto = df_filtrado.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
        pareto_h = pareto.apply(lambda x: x.total_seconds() / 3600)
        pareto_h.plot(kind='barh', ax=ax1, color='#3498db')
        ax1.set_title("Top 10 Causas de Parada (h)")
        ax1.invert_yaxis()
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        indice_area = df_filtrado['Área Responsável'].value_counts()
        ax2.pie(indice_area, labels=indice_area.index, autopct='%1.1f%%')
        ax2.set_title("Paradas por Área Responsável")
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots()
        por_hora = df_filtrado.groupby('Hora')['Duração'].sum().apply(lambda x: x.total_seconds() / 3600)
        por_hora.plot(ax=ax3, kind='line', marker='o', color='purple')
        ax3.set_title("Horas Paradas por Hora do Dia")
        st.pyplot(fig3)

        fig4, ax4 = plt.subplots()
        por_dia = df_filtrado['Dia da Semana'].value_counts().reindex([
            'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
        por_dia.plot(kind='bar', ax=ax4, color='green')
        ax4.set_title("Distribuição de Paradas por Dia da Semana")
        st.pyplot(fig4)

        st.subheader("Top 10 Paradas Mais Frequentes")
        frequencia = df_filtrado['Parada'].value_counts().head(10)
        st.dataframe(frequencia.rename("Ocorrências"))

        st.subheader("Top 10 Paradas por Duração")
        st.dataframe(pareto_h.rename("Duração (h)").round(2))
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
