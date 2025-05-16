import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

from data_processing import preprocess_data, calculate_metrics
from visualizations import create_pareto_chart, create_area_pie_chart, create_occurrences_chart
from visualizations import create_area_bar_chart, create_downtime_by_day, create_downtime_by_hour
from utils import format_duration, get_month_name_pt

# Configure the Streamlit page
st.set_page_config(
    page_title="Dashboard de Análise de Paradas",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='main-title'>Dashboard de Análise de Eficiência de Máquinas</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='info-box'>
    Este dashboard permite analisar indicadores de eficiência de máquinas com base nos dados de paradas.
    Faça o upload do arquivo Excel contendo os registros para iniciar a análise.
</div>
""", unsafe_allow_html=True)

# Sidebar for file upload and filters
with st.sidebar:
    st.markdown("<h2 class='sidebar-title'>Configurações</h2>", unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader("Faça upload do arquivo Excel (XLSX)", type=["xlsx"])
    
    # Initialize session state for data
    if 'data' not in st.session_state:
        st.session_state.data = None
        
    if uploaded_file is not None:
        try:
            # Read and process the data
            df = pd.read_excel(uploaded_file)
            df = preprocess_data(df)
            st.session_state.data = df
            st.success(f"Arquivo carregado com sucesso! {len(df)} registros encontrados.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            st.session_state.data = None

# Main content
if st.session_state.data is not None:
    df = st.session_state.data
    
    # Filters section
    st.markdown("<h2 class='section-title'>Filtros de Análise</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Machine filter
        machine_options = ["Todas as Máquinas"] + sorted(df['Máquina'].unique().tolist())
        selected_machine = st.selectbox("Máquina", machine_options)
    
    with col2:
        # Time period filter
        period_options = ["Todos os Períodos", "Último Mês", "Últimos 3 Meses", "Último Ano", "Período Personalizado"]
        selected_period = st.selectbox("Período", period_options)
    
    with col3:
        # Month-Year filter
        month_year_options = ["Todos"] + sorted(df['Ano-Mês'].unique().tolist())
        selected_month_year = st.selectbox("Mês/Ano", month_year_options)
    
    # Custom date range if selected
    if selected_period == "Período Personalizado":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data Inicial", min(df['Inicio'].dt.date))
        with col2:
            end_date = st.date_input("Data Final", max(df['Inicio'].dt.date))
    
    # Filter the data based on selections
    filtered_df = df.copy()
    
    # Apply machine filter
    if selected_machine != "Todas as Máquinas":
        filtered_df = filtered_df[filtered_df['Máquina'] == selected_machine]
    
    # Apply time period filter
    if selected_period == "Último Mês":
        last_date = max(df['Inicio'])
        one_month_ago = last_date - pd.DateOffset(months=1)
        filtered_df = filtered_df[filtered_df['Inicio'] >= one_month_ago]
    elif selected_period == "Últimos 3 Meses":
        last_date = max(df['Inicio'])
        three_months_ago = last_date - pd.DateOffset(months=3)
        filtered_df = filtered_df[filtered_df['Inicio'] >= three_months_ago]
    elif selected_period == "Último Ano":
        last_date = max(df['Inicio'])
        one_year_ago = last_date - pd.DateOffset(years=1)
        filtered_df = filtered_df[filtered_df['Inicio'] >= one_year_ago]
    elif selected_period == "Período Personalizado":
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        filtered_df = filtered_df[(filtered_df['Inicio'] >= start_datetime) & (filtered_df['Inicio'] <= end_datetime)]
    
    # Apply month-year filter
    if selected_month_year != "Todos":
        filtered_df = filtered_df[filtered_df['Ano-Mês'] == selected_month_year]
    
    # Check if filtered data is not empty
    if len(filtered_df) > 0:
        # Calculate metrics
        dias_unicos = filtered_df['Inicio'].dt.date.nunique()
        tempo_programado = pd.Timedelta(hours=24 * dias_unicos)
        metrics = calculate_metrics(filtered_df, tempo_programado)
        
        # Display top metrics
        st.markdown("<h2 class='section-title'>Indicadores Principais</h2>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Disponibilidade</h3>
                <p class="metric-value">{metrics['disponibilidade']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Eficiência Operacional</h3>
                <p class="metric-value">{metrics['eficiencia']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Tempo Médio de Paradas</h3>
                <p class="metric-value">{format_duration(metrics['tmp'])}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Paradas Críticas (>1h)</h3>
                <p class="metric-value">{metrics['percentual_criticas']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualizations
        st.markdown("<h2 class='section-title'>Análise Gráfica</h2>", unsafe_allow_html=True)
        
        # First row of charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Pareto chart of downtime causes
            fig_pareto = create_pareto_chart(filtered_df)
            st.plotly_chart(fig_pareto, use_container_width=True)
            
        with col2:
            # Pie chart of responsible areas
            fig_pie = create_area_pie_chart(filtered_df)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Second row of charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Line chart of occurrences by month
            fig_occurrences = create_occurrences_chart(filtered_df)
            st.plotly_chart(fig_occurrences, use_container_width=True)
            
        with col2:
            # Bar chart of total downtime by area
            fig_area_bar = create_area_bar_chart(filtered_df)
            st.plotly_chart(fig_area_bar, use_container_width=True)
        
        # New visualizations (as requested)
        st.markdown("<h2 class='section-title'>Análises Adicionais</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution of downtime by days of the week
            fig_day_distribution = create_downtime_by_day(filtered_df)
            st.plotly_chart(fig_day_distribution, use_container_width=True)
            
        with col2:
            # Accumulation of downtime hours by hour in the day
            fig_hour_distribution = create_downtime_by_hour(filtered_df)
            st.plotly_chart(fig_hour_distribution, use_container_width=True)
        
        # Tables section
        st.markdown("<h2 class='section-title'>Tabelas de Resumo</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top most frequent downtimes
            st.markdown("<h3>Top 10 Paradas Mais Frequentes</h3>", unsafe_allow_html=True)
            
            if 'Parada' in filtered_df.columns:
                freq_df = filtered_df['Parada'].value_counts().reset_index()
                freq_df.columns = ['Tipo de Parada', 'Frequência']
                freq_df = freq_df.head(10)
                st.dataframe(freq_df, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar a tabela.")
        
        with col2:
            # Top longest downtimes
            st.markdown("<h3>Top 10 Paradas Mais Longas</h3>", unsafe_allow_html=True)
            
            if 'Parada' in filtered_df.columns:
                duration_df = filtered_df.groupby('Parada')['Duração'].sum().reset_index()
                duration_df['Duração (horas)'] = duration_df['Duração'].apply(lambda x: round(x.total_seconds() / 3600, 2))
                duration_df['Duração (HH:MM:SS)'] = duration_df['Duração'].apply(format_duration)
                duration_df = duration_df[['Parada', 'Duração (HH:MM:SS)', 'Duração (horas)']]
                duration_df.columns = ['Tipo de Parada', 'Duração (HH:MM:SS)', 'Duração (horas)']
                duration_df = duration_df.sort_values('Duração (horas)', ascending=False).head(10)
                st.dataframe(duration_df, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar a tabela.")
        
        # Temporal analysis
        if selected_month_year == "Todos" and len(filtered_df['Ano-Mês'].unique()) > 1:
            st.markdown("<h2 class='section-title'>Análise Temporal</h2>", unsafe_allow_html=True)
            
            monthly_data = filtered_df.groupby('Ano-Mês').agg({
                'Parada': 'count',
                'Duração': 'sum'
            }).reset_index()
            monthly_data.columns = ['Mês', 'Número de Paradas', 'Duração Total']
            monthly_data['Duração (horas)'] = monthly_data['Duração Total'].apply(lambda x: round(x.total_seconds() / 3600, 2))
            monthly_data['Duração Média (horas)'] = monthly_data['Duração (horas)'] / monthly_data['Número de Paradas']
            monthly_data['Mês Nome'] = monthly_data['Mês'].apply(lambda x: get_month_name_pt(x))
            
            # Plot temporal charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(
                    monthly_data, 
                    x='Mês Nome', 
                    y='Número de Paradas',
                    markers=True,
                    title='Evolução do Número de Paradas por Mês'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(
                    monthly_data, 
                    x='Mês Nome', 
                    y='Duração (horas)',
                    markers=True,
                    title='Evolução da Duração Total de Paradas por Mês'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Monthly summary table
            st.markdown("<h3>Resumo Mensal de Paradas</h3>", unsafe_allow_html=True)
            monthly_display = monthly_data[['Mês Nome', 'Número de Paradas', 'Duração (horas)', 'Duração Média (horas)']]
            st.dataframe(monthly_display, use_container_width=True)
        
        # Conclusions and recommendations
        st.markdown("<h2 class='section-title'>Conclusões e Recomendações</h2>", unsafe_allow_html=True)
        
        # Generate insights based on the data
        if 'Área Responsável' in filtered_df.columns and len(filtered_df) > 0:
            area_counts = filtered_df.groupby('Área Responsável')['Duração'].sum()
            
            if not area_counts.empty:
                area_mais_problematica = area_counts.idxmax()
                tempo_area_problematica = format_duration(area_counts.max())
                percentual_area = (area_counts.max() / area_counts.sum()) * 100
                
                if 'Parada' in filtered_df.columns:
                    causa_counts = filtered_df['Parada'].value_counts()
                    causa_mais_frequente = causa_counts.idxmax()
                    frequencia_causa = causa_counts.max()
                    percentual_frequencia = (frequencia_causa / causa_counts.sum()) * 100
                    
                    causa_duracao = filtered_df.groupby('Parada')['Duração'].sum()
                    causa_maior_impacto = causa_duracao.idxmax()
                    tempo_causa_impacto = format_duration(causa_duracao.max())
                    percentual_impacto = (causa_duracao.max() / causa_duracao.sum()) * 100
                    
                    # Format machine and period text
                    texto_maquina = f" para a máquina <b>{selected_machine}</b>" if selected_machine != "Todas as Máquinas" else ""
                    
                    texto_periodo = ""
                    if selected_month_year != "Todos":
                        texto_periodo = f" no período de <b>{get_month_name_pt(selected_month_year)}</b>"
                    elif selected_period != "Todos os Períodos":
                        texto_periodo = f" no <b>{selected_period.lower()}</b>"
                    
                    # Create HTML conclusions
                    st.markdown(f"""
                    <div class="conclusions-box">
                        <h3>Principais Conclusões:</h3>
                        <ul>
                            <li>A área <b>{area_mais_problematica}</b> é responsável pelo maior tempo de paradas{texto_maquina}{texto_periodo} ({tempo_area_problematica}, representando {percentual_area:.1f}% do tempo total).</li>
                            <li>A causa mais frequente de paradas é <b>"{causa_mais_frequente}"</b> com {frequencia_causa} ocorrências ({percentual_frequencia:.1f}% do total).</li>
                            <li>A causa com maior impacto em tempo é <b>"{causa_maior_impacto}"</b> com duração total de {tempo_causa_impacto} ({percentual_impacto:.1f}% do tempo total de paradas).</li>
                            <li>A disponibilidade geral{texto_maquina}{texto_periodo} está em <b>{metrics['disponibilidade']:.2f}%</b>, com eficiência operacional de <b>{metrics['eficiencia']:.2f}%</b>.</li>
                        </ul>
                        
                        <h3>Recomendações:</h3>
                        <ol>
                            <li>Implementar um plano de ação focado na área <b>{area_mais_problematica}</b> para reduzir o tempo de paradas.</li>
                            <li>Investigar a causa raiz das paradas do tipo <b>"{causa_maior_impacto}"</b> para mitigar seu impacto.</li>
                            <li>Desenvolver treinamentos específicos para reduzir a frequência de paradas do tipo <b>"{causa_mais_frequente}"</b>.</li>
                            <li>Estabelecer metas de disponibilidade e eficiência, com acompanhamento periódico dos indicadores.</li>
                            <li>Implementar um programa de manutenção preventiva focado nos componentes críticos identificados na análise.</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Dados insuficientes para gerar conclusões completas.")
            else:
                st.info("Dados insuficientes para gerar conclusões.")
        else:
            st.info("Dados insuficientes para gerar conclusões.")
        
        # Download filtered data as Excel
        st.markdown("<h2 class='section-title'>Exportar Dados</h2>", unsafe_allow_html=True)
        
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados')
                workbook = writer.book
                worksheet = writer.sheets['Dados']
                format1 = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm:ss'})
                worksheet.set_column('C:D', 18, format1)
                worksheet.set_column('A:Z', 15)
            processed_data = output.getvalue()
            return processed_data
        
        excel_file = to_excel(filtered_df)
        
        st.download_button(
            label="📥 Baixar Dados Filtrados como Excel",
            data=excel_file,
            file_name=f"analise_paradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados. Por favor, ajuste os filtros.")
else:
    # Display sample data if no file is uploaded
    st.markdown("<h2 class='section-title'>Exemplo de Visualização</h2>", unsafe_allow_html=True)
    st.info("Faça o upload de um arquivo Excel contendo dados de paradas de máquinas para visualizar a análise completa.")
    
    # Sample image or placeholder
    st.image("https://images.pexels.com/photos/257904/pexels-photo-257904.jpeg", 
             caption="Imagem ilustrativa: Painel de controle industrial")
    
    # Example table structure
    st.markdown("<h3>Estrutura esperada do arquivo:</h3>", unsafe_allow_html=True)
    
    example_data = {
        'Máquina': [78, 79, 80],
        'Parada': ['Manutenção Preventiva', 'Troca de Ferramenta', 'Quebra'],
        'Área Responsável': ['Manutenção', 'Produção', 'Manutenção'],
        'Inicio': ['2023-01-01 08:00:00', '2023-01-02 10:30:00', '2023-01-03 14:15:00'],
        'Fim': ['2023-01-01 10:00:00', '2023-01-02 11:00:00', '2023-01-03 18:45:00'],
        'Duração': ['02:00:00', '00:30:00', '04:30:00']
    }
    
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df)