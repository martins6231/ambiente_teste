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
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import time
import base64
from io import BytesIO

# ----------- Configuração da Página -----------
st.set_page_config(
    page_title="Dashboard de Produção - Britvic",
    layout="wide",
    page_icon="🧃",
    initial_sidebar_state="expanded",
)

# ----------- Suporte Bilíngue (Português e Inglês) -----------
LANGS = {"pt": "Português (Brasil)", "en": "English"}

# ----------- Temas de Cores -----------
THEMES = {
    "light": {
        "primary": "#003057",
        "accent": "#27AE60",
        "bg": "#F4FFF6",
        "text": "#333333",
        "card_bg": "#FFFFFF",
        "shadow": "rgba(0, 48, 87, 0.13)",
    },
    "dark": {
        "primary": "#1E88E5",
        "accent": "#4CAF50",
        "bg": "#121212",
        "text": "#E0E0E0",
        "card_bg": "#1E1E1E",
        "shadow": "rgba(0, 0, 0, 0.3)",
    },
}

# ----------- Inicialização do Estado da Sessão -----------
if "user_preferences" not in st.session_state:
    st.session_state["user_preferences"] = {
        "lang": "pt",
        "theme": "light",
        "show_tips": True,
        "animation_speed": 0.5,
    }

if "filtros" not in st.session_state:
    st.session_state["filtros"] = {}

if "last_update" not in st.session_state:
    st.session_state["last_update"] = datetime.now()

if "prophet_params" not in st.session_state:
    st.session_state["prophet_params"] = {
        "changepoint_prior_scale": 0.05,
        "seasonality_prior_scale": 10.0,
        "seasonality_mode": "multiplicative",
        "interval_width": 0.8,
    }

# ----------- Seleção de Idioma e Tema -----------
with st.sidebar:
    st.sidebar.markdown("## 🌐 Idioma | Language")
    idioma = st.sidebar.radio(
        "Escolha o idioma / Choose language:",
        options=list(LANGS.keys()),
        format_func=lambda x: LANGS[x],
        key="user_lang",
        horizontal=True,
    )
    st.session_state["user_preferences"]["lang"] = idioma

    st.sidebar.markdown("## 🎨 Tema | Theme")
    tema = st.sidebar.radio(
        "Escolha o tema / Choose theme:",
        options=["light", "dark"],
        format_func=lambda x: (
            "Claro"
            if x == "light" and idioma == "pt"
            else (
                "Escuro"
                if x == "dark" and idioma == "pt"
                else "Light" if x == "light" else "Dark"
            )
        ),
        key="user_theme",
        horizontal=True,
    )
    st.session_state["user_preferences"]["theme"] = tema

# ----------- Aplicar Tema Selecionado -----------
current_theme = THEMES[st.session_state["user_preferences"]["theme"]]
BRITVIC_PRIMARY = current_theme["primary"]
BRITVIC_ACCENT = current_theme["accent"]
BRITVIC_BG = current_theme["bg"]
BRITVIC_TEXT = current_theme["text"]
BRITVIC_CARD_BG = current_theme["card_bg"]
BRITVIC_SHADOW = current_theme["shadow"]


# ----------- Sistema de Tradução -----------
def t(msg_key, **kwargs):
    TRANSLATE = {
        "pt": {
            "dashboard_title": "Dashboard de Produção - Britvic",
            "main_title": "Dashboard de Produção",
            "subtitle": "Visualização dos dados de produção Britvic",
            "category": "🏷️ Categoria:",
            "year": "📅 Ano(s):",
            "month": "📆 Mês(es):",
            "analysis_for": "Análise para categoria: <b>{cat}</b>",
            "empty_data_for_period": "Não há dados para esse período e categoria.",
            "mandatory_col_missing": "Coluna obrigatória ausente: {col}",
            "error_date_conversion": "Erro ao converter coluna 'data'.",
            "col_with_missing": "Coluna '{col}' com {num} valores ausentes.",
            "negatives": "{num} registros negativos em 'caixas_produzidas'.",
            "no_critical": "Nenhum problema crítico encontrado.",
            "data_issue_report": "Relatório de problemas encontrados",
            "no_data_selection": "Sem dados para a seleção.",
            "no_trend": "Sem dados para tendência.",
            "daily_trend": "Tendência Diária - {cat}",
            "monthly_total": "Produção Mensal Total - {cat}",
            "monthly_var": "Variação Percentual Mensal (%) - {cat}",
            "monthly_seasonal": "Sazonalidade Mensal - {cat}",
            "monthly_comp": "Produção Mensal {cat} - Comparativo por Ano",
            "monthly_accum": "Produção Acumulada Mês a Mês - {cat}",
            "no_forecast": "Sem previsão disponível.",
            "forecast": "Previsão de Produção - {cat}",
            "auto_insights": "Insights Automáticos",
            "no_pattern": "Nenhum padrão preocupante encontrado para esta categoria.",
            "recent_growth": "Crescimento recente na produção detectado nos últimos meses.",
            "recent_fall": "Queda recente na produção detectada nos últimos meses.",
            "outlier_days": "Foram encontrados {num} dias atípicos de produção (possíveis outliers).",
            "high_var": "Alta variabilidade diária. Sugerido investigar causas das flutuações.",
            "export": "Exportação",
            "export_with_fc": "⬇️ Exportar consolidado com previsão (.xlsx)",
            "download_file": "Download arquivo Excel ⬇️",
            "no_export": "Sem previsão para exportar.",
            "add_secrets": "Adicione CLOUD_XLSX_URL ao seu .streamlit/secrets.toml e compartilhe a planilha para 'qualquer pessoa com o link'.",
            "error_download_xls": "Erro ao baixar planilha. Status code: {code}",
            "not_valid_excel": "Arquivo baixado não é um Excel válido. Confirme se o link é público/correto!",
            "excel_open_error": "Erro ao abrir o Excel: {err}",
            "kpi_year": "📦 Ano {ano}",
            "kpi_sum": "{qtd:,} caixas",
            "historico": "Histórico",
            "kpi_daily_avg": "Média diária:<br><b style='color:{accent};font-size:1.15em'>{media:.0f}</b>",
            "kpi_records": "Registros: <b>{count}</b>",
            # Labels
            "data": "Data",
            "category_lbl": "Categoria",
            "produced_boxes": "Caixas Produzidas",
            "month_lbl": "Mês/Ano",
            "variation": "Variação (%)",
            "prod": "Produção",
            "year_lbl": "Ano",
            "accum_boxes": "Caixas Acumuladas",
            "forecast_boxes": "Previsão Caixas",
            # Novos termos 2.0
            "advanced_settings": "Configurações Avançadas",
            "prophet_settings": "Configurações do Modelo Prophet",
            "changepoint_prior": "Escala de Prior do Ponto de Mudança:",
            "seasonality_prior": "Escala de Prior da Sazonalidade:",
            "seasonality_mode": "Modo de Sazonalidade:",
            "interval_width": "Largura do Intervalo de Confiança:",
            "additive": "Aditivo",
            "multiplicative": "Multiplicativo",
            "apply_settings": "Aplicar Configurações",
            "settings_applied": "Configurações aplicadas com sucesso!",
            "correlation_title": "Matriz de Correlação entre Categorias",
            "no_correlation": "Não há dados suficientes para calcular correlações.",
            "heatmap_title": "Mapa de Calor - Produção Semanal - {cat}",
            "weekday": "Dia da Semana",
            "week_number": "Semana do Ano",
            "anomaly_detection": "Detecção de Anomalias",
            "anomalies_found": "Encontradas {count} anomalias na produção.",
            "no_anomalies": "Nenhuma anomalia significativa detectada.",
            "anomaly_chart": "Detecção de Anomalias - {cat}",
            "normal": "Normal",
            "anomaly": "Anomalia",
            "efficiency_analysis": "Análise de Eficiência",
            "production_efficiency": "Eficiência de Produção",
            "efficiency_metric": "Métrica de Eficiência",
            "tips_and_tricks": "Dicas e Truques",
            "hide_tips": "Ocultar Dicas",
            "show_tips": "Mostrar Dicas",
            "tip_1": "💡 Use a barra de pesquisa para encontrar rapidamente categorias específicas.",
            "tip_2": "💡 Clique duas vezes em um gráfico para resetar o zoom.",
            "tip_3": "💡 Exporte os dados para análise offline ou apresentações.",
            "tip_4": "💡 Ajuste os parâmetros do Prophet para melhorar a precisão da previsão.",
            "tip_5": "💡 Compare diferentes períodos para identificar padrões sazonais.",
            "last_updated": "Última atualização: {time}",
            "refresh_data": "Atualizar Dados",
            "refreshing": "Atualizando...",
            "data_refreshed": "Dados atualizados com sucesso!",
            "share_insights": "Compartilhar Insights",
            "email_insights": "Enviar por Email",
            "share_link": "Copiar Link",
            "link_copied": "Link copiado para a área de transferência!",
            "advanced_filters": "Filtros Avançados",
            "min_production": "Produção Mínima:",
            "max_production": "Produção Máxima:",
            "date_range": "Intervalo de Datas:",
            "apply_filters": "Aplicar Filtros",
            "reset_filters": "Resetar Filtros",
            "filters_applied": "Filtros aplicados com sucesso!",
            "filters_reset": "Filtros resetados com sucesso!",
            "weekday_analysis": "Análise por Dia da Semana",
            "monday": "Segunda",
            "tuesday": "Terça",
            "wednesday": "Quarta",
            "thursday": "Quinta",
            "friday": "Sexta",
            "saturday": "Sábado",
            "sunday": "Domingo",
            "production_by_weekday": "Produção por Dia da Semana - {cat}",
            "comparison_tool": "Ferramenta de Comparação",
            "select_categories": "Selecione categorias para comparar:",
            "compare": "Comparar",
            "category_comparison": "Comparação de Categorias",
            "accessibility_options": "Opções de Acessibilidade",
            "text_size": "Tamanho do Texto:",
            "small": "Pequeno",
            "medium": "Médio",
            "large": "Grande",
            "high_contrast": "Alto Contraste:",
            "animation_speed": "Velocidade de Animação:",
            "slow": "Lenta",
            "normal": "Normal",
            "fast": "Rápida",
            "none": "Nenhuma",
            "apply_accessibility": "Aplicar Configurações",
            "accessibility_applied": "Configurações de acessibilidade aplicadas!",
            "help_center": "Central de Ajuda",
            "faq": "Perguntas Frequentes",
            "tutorial": "Tutorial",
            "contact_support": "Contatar Suporte",
            "loading": "Carregando...",
            "processing": "Processando...",
            "ready": "Pronto!",
            "welcome_message": "Bem-vindo ao Dashboard de Produção Britvic 2.0!",
            "getting_started": "Para começar, selecione uma categoria e período nos filtros à esquerda.",
            "performance_metrics": "Métricas de Desempenho",
            "loading_time": "Tempo de Carregamento: {time}s",
            "data_points": "Pontos de Dados: {count}",
            "memory_usage": "Uso de Memória: {usage}MB",
            "export_options": "Opções de Exportação",
            "export_excel": "Excel (.xlsx)",
            "export_csv": "CSV (.csv)",
            "export_pdf": "PDF (.pdf)",
            "export_image": "Imagem (.png)",
            "annotations": "Anotações",
            "add_annotation": "Adicionar Anotação",
            "edit_annotation": "Editar Anotação",
            "delete_annotation": "Excluir Anotação",
            "annotation_text": "Texto da Anotação:",
            "annotation_date": "Data da Anotação:",
            "save_annotation": "Salvar Anotação",
            "cancel": "Cancelar",
            "no_annotations": "Nenhuma anotação encontrada.",
            "annotations_saved": "Anotação salva com sucesso!",
            "annotations_deleted": "Anotação excluída com sucesso!",
            "scenario_analysis": "Análise de Cenários",
            "optimistic": "Otimista",
            "realistic": "Realista",
            "pessimistic": "Pessimista",
            "scenario_description": "Descrição do Cenário:",
            "create_scenario": "Criar Cenário",
            "scenario_created": "Cenário criado com sucesso!",
            "scenario_comparison": "Comparação de Cenários",
            "goal_tracking": "Acompanhamento de Metas",
            "set_goal": "Definir Meta",
            "goal_value": "Valor da Meta:",
            "goal_date": "Data da Meta:",
            "save_goal": "Salvar Meta",
            "goal_saved": "Meta salva com sucesso!",
            "goal_progress": "Progresso da Meta: {progress}%",
            "goal_achieved": "Meta atingida!",
            "goal_not_achieved": "Meta não atingida.",
            "goal_tracking_chart": "Acompanhamento de Metas - {cat}",
            "actual": "Real",
            "goal": "Meta",
            "variance_analysis": "Análise de Variância",
            "variance_from_goal": "Variância da Meta: {variance}%",
            "positive_variance": "Variância Positiva",
            "negative_variance": "Variância Negativa",
            "variance_chart": "Análise de Variância - {cat}",
            "decomposition_analysis": "Análise de Decomposição",
            "trend_component": "Componente de Tendência",
            "seasonal_component": "Componente Sazonal",
            "residual_component": "Componente Residual",
            "decomposition_chart": "Decomposição da Série Temporal - {cat}",
            "correlation_analysis": "Análise de Correlação",
            "correlation_matrix": "Matriz de Correlação",
            "correlation_heatmap": "Mapa de Calor de Correlação",
            "correlation_value": "Valor de Correlação",
            "strong_positive": "Correlação Positiva Forte",
            "moderate_positive": "Correlação Positiva Moderada",
            "weak_positive": "Correlação Positiva Fraca",
            "no_correlation_value": "Sem Correlação",
            "weak_negative": "Correlação Negativa Fraca",
            "moderate_negative": "Correlação Negativa Moderada",
            "strong_negative": "Correlação Negativa Forte",
            "outlier_analysis": "Análise de Outliers",
            "outlier_detection": "Detecção de Outliers",
            "outlier_chart": "Gráfico de Outliers - {cat}",
            "outlier": "Outlier",
            "not_outlier": "Não Outlier",
            "outlier_threshold": "Limiar de Outlier:",
            "apply_threshold": "Aplicar Limiar",
            "threshold_applied": "Limiar aplicado com sucesso!",
            "production_calendar": "Calendário de Produção",
            "calendar_view": "Visualização de Calendário",
            "daily_view": "Visualização Diária",
            "weekly_view": "Visualização Semanal",
            "monthly_view": "Visualização Mensal",
            "yearly_view": "Visualização Anual",
            "production_intensity": "Intensidade de Produção",
            "low": "Baixa",
            "medium": "Média",
            "high": "Alta",
            "very_high": "Muito Alta",
            "production_calendar_title": "Calendário de Produção - {cat}",
            "benchmark_analysis": "Análise de Benchmark",
            "benchmark_selection": "Seleção de Benchmark",
            "benchmark_comparison": "Comparação de Benchmark",
            "benchmark_chart": "Gráfico de Benchmark - {cat}",
            "benchmark": "Benchmark",
            "actual_value": "Valor Real",
            "benchmark_value": "Valor de Benchmark",
            "benchmark_variance": "Variância de Benchmark: {variance}%",
            "above_benchmark": "Acima do Benchmark",
            "below_benchmark": "Abaixo do Benchmark",
            "at_benchmark": "No Benchmark",
            "efficiency_ratio": "Índice de Eficiência",
            "efficiency_chart": "Gráfico de Eficiência - {cat}",
            "efficiency_score": "Pontuação de Eficiência: {score}/100",
            "efficiency_trend": "Tendência de Eficiência",
            "improving": "Melhorando",
            "stable": "Estável",
            "declining": "Declinando",
            "efficiency_recommendations": "Recomendações de Eficiência",
            "recommendation_1": "Recomendação 1: {rec}",
            "recommendation_2": "Recomendação 2: {rec}",
            "recommendation_3": "Recomendação 3: {rec}",
            "implement_recommendation": "Implementar Recomendação",
            "recommendation_implemented": "Recomendação implementada com sucesso!",
            "what_if_analysis": "Análise 'E se...'",
            "what_if_scenario": "Cenário 'E se...'",
            "what_if_parameter": "Parâmetro 'E se...':",
            "what_if_value": "Valor 'E se...':",
            "simulate": "Simular",
            "simulation_result": "Resultado da Simulação",
            "simulation_chart": "Gráfico de Simulação - {cat}",
            "baseline": "Linha de Base",
            "simulation": "Simulação",
            "simulation_impact": "Impacto da Simulação: {impact}%",
            "positive_impact": "Impacto Positivo",
            "negative_impact": "Impacto Negativo",
            "neutral_impact": "Impacto Neutro",
            "simulation_completed": "Simulação concluída com sucesso!",
            "data_quality_score": "Pontuação de Qualidade dos Dados: {score}/100",
            "data_quality_chart": "Gráfico de Qualidade dos Dados - {cat}",
            "completeness": "Completude",
            "accuracy": "Precisão",
            "consistency": "Consistência",
            "timeliness": "Tempestividade",
            "data_quality_recommendations": "Recomendações de Qualidade dos Dados",
            "improve_completeness": "Melhorar Completude: {rec}",
            "improve_accuracy": "Melhorar Precisão: {rec}",
            "improve_consistency": "Melhorar Consistência: {rec}",
            "improve_timeliness": "Melhorar Tempestividade: {rec}",
            "data_quality_trend": "Tendência de Qualidade dos Dados",
            "data_quality_improving": "Melhorando",
            "data_quality_stable": "Estável",
            "data_quality_declining": "Declinando",
            "data_quality_analysis": "Análise de Qualidade dos Dados",
            "data_profiling": "Perfilamento de Dados",
            "data_profiling_chart": "Gráfico de Perfilamento de Dados - {cat}",
            "data_distribution": "Distribuição dos Dados",
            "data_skewness": "Assimetria dos Dados: {skew}",
            "data_kurtosis": "Curtose dos Dados: {kurt}",
            "data_range": "Intervalo dos Dados: {min} - {max}",
            "data_mean": "Média dos Dados: {mean}",
            "data_median": "Mediana dos Dados: {median}",
            "data_mode": "Moda dos Dados: {mode}",
            "data_std": "Desvio Padrão dos Dados: {std}",
            "data_variance": "Variância dos Dados: {var}",
            "data_profiling_completed": "Perfilamento de dados concluído com sucesso!",
            "production_pattern": "Padrão de Produção",
            "pattern_recognition": "Reconhecimento de Padrão",
            "pattern_chart": "Gráfico de Padrão - {cat}",
            "pattern_detected": "Padrão Detectado: {pattern}",
            "no_pattern_detected": "Nenhum padrão detectado.",
            "pattern_confidence": "Confiança do Padrão: {conf}%",
            "pattern_analysis": "Análise de Padrão",
            "pattern_recommendation": "Recomendação de Padrão: {rec}",
            "pattern_impact": "Impacto do Padrão: {impact}",
            "pattern_recognition_completed": "Reconhecimento de padrão concluído com sucesso!",
        },
        "en": {
            "dashboard_title": "Production Dashboard - Britvic",
            "main_title": "Production Dashboard",
            "subtitle": "Britvic production data visualization",
            "category": "🏷️ Category:",
            "year": "📅 Year(s):",
            "month": "📆 Month(s):",
            "analysis_for": "Analysis for category: <b>{cat}</b>",
            "empty_data_for_period": "No data for this period and category.",
            "mandatory_col_missing": "Mandatory column missing: {col}",
            "error_date_conversion": "Error converting 'data' column.",
            "col_with_missing": "Column '{col}' has {num} missing values.",
            "negatives": "{num} negative records in 'caixas_produzidas'.",
            "no_critical": "No critical issues found.",
            "data_issue_report": "Report of Identified Issues",
            "no_data_selection": "No data for selection.",
            "no_trend": "No data for trend.",
            "daily_trend": "Daily Trend - {cat}",
            "monthly_total": "Total Monthly Production - {cat}",
            "monthly_var": "Monthly Change (%) - {cat}",
            "monthly_seasonal": "Monthly Seasonality - {cat}",
            "monthly_comp": "Monthly Production {cat} - Year Comparison",
            "monthly_accum": "Accumulated Production Month by Month - {cat}",
            "no_forecast": "No available forecast.",
            "forecast": "Production Forecast - {cat}",
            "auto_insights": "Automatic Insights",
            "no_pattern": "No concerning patterns found for this category.",
            "recent_growth": "Recent growth in production detected in the last months.",
            "recent_fall": "Recent drop in production detected in the last months.",
            "outlier_days": "{num} atypical production days found (possible outliers).",
            "high_var": "High daily variability. Suggest to investigate fluctuation causes.",
            "export": "Export",
            "export_with_fc": "⬇️ Export with forecast (.xlsx)",
            "download_file": "Download Excel file ⬇️",
            "no_export": "No forecast to export.",
            "add_secrets": "Add CLOUD_XLSX_URL to your .streamlit/secrets.toml and share the sheet to 'anyone with the link'.",
            "error_download_xls": "Error downloading spreadsheet. Status code: {code}",
            "not_valid_excel": "Downloaded file is not a valid Excel. Confirm the link is public/correct!",
            "excel_open_error": "Error opening Excel: {err}",
            "kpi_year": "📦 Year {ano}",
            "kpi_sum": "{qtd:,} boxes",
            "historico": "History",
            "kpi_daily_avg": "Daily avg.:<br><b style='color:{accent};font-size:1.15em'>{media:.0f}</b>",
            "kpi_records": "Records: <b>{count}</b>",
            # Labels
            "data": "Date",
            "category_lbl": "Category",
            "produced_boxes": "Produced Boxes",
            "month_lbl": "Month/Year",
            "variation": "Variation (%)",
            "prod": "Production",
            "year_lbl": "Year",
            "accum_boxes": "Accum. Boxes",
            "forecast_boxes": "Forecasted Boxes",
            # New terms 2.0
            "advanced_settings": "Advanced Settings",
            "prophet_settings": "Prophet Model Settings",
            "changepoint_prior": "Changepoint Prior Scale:",
            "seasonality_prior": "Seasonality Prior Scale:",
            "seasonality_mode": "Seasonality Mode:",
            "interval_width": "Confidence Interval Width:",
            "additive": "Additive",
            "multiplicative": "Multiplicative",
            "apply_settings": "Apply Settings",
            "settings_applied": "Settings applied successfully!",
            "correlation_title": "Correlation Matrix Between Categories",
            "no_correlation": "Not enough data to calculate correlations.",
            "heatmap_title": "Heat Map - Weekly Production - {cat}",
            "weekday": "Weekday",
            "week_number": "Week of Year",
            "anomaly_detection": "Anomaly Detection",
            "anomalies_found": "Found {count} anomalies in production.",
            "no_anomalies": "No significant anomalies detected.",
            "anomaly_chart": "Anomaly Detection - {cat}",
            "normal": "Normal",
            "anomaly": "Anomaly",
            "efficiency_analysis": "Efficiency Analysis",
            "production_efficiency": "Production Efficiency",
            "efficiency_metric": "Efficiency Metric",
            "tips_and_tricks": "Tips and Tricks",
            "hide_tips": "Hide Tips",
            "show_tips": "Show Tips",
            "tip_1": "💡 Use the search bar to quickly find specific categories.",
            "tip_2": "💡 Double-click on a chart to reset zoom.",
            "tip_3": "💡 Export data for offline analysis or presentations.",
            "tip_4": "💡 Adjust Prophet parameters to improve forecast accuracy.",
            "tip_5": "💡 Compare different periods to identify seasonal patterns.",
            "last_updated": "Last updated: {time}",
            "refresh_data": "Refresh Data",
            "refreshing": "Refreshing...",
            "data_refreshed": "Data refreshed successfully!",
            "share_insights": "Share Insights",
            "email_insights": "Send by Email",
            "share_link": "Copy Link",
            "link_copied": "Link copied to clipboard!",
            "advanced_filters": "Advanced Filters",
            "min_production": "Minimum Production:",
            "max_production": "Maximum Production:",
            "date_range": "Date Range:",
            "apply_filters": "Apply Filters",
            "reset_filters": "Reset Filters",
            "filters_applied": "Filters applied successfully!",
            "filters_reset": "Filters reset successfully!",
            "weekday_analysis": "Weekday Analysis",
            "monday": "Monday",
            "tuesday": "Tuesday",
            "wednesday": "Wednesday",
            "thursday": "Thursday",
            "friday": "Friday",
            "saturday": "Saturday",
            "sunday": "Sunday",
            "production_by_weekday": "Production by Weekday - {cat}",
            "comparison_tool": "Comparison Tool",
            "select_categories": "Select categories to compare:",
            "compare": "Compare",
            "category_comparison": "Category Comparison",
            "accessibility_options": "Accessibility Options",
            "text_size": "Text Size:",
            "small": "Small",
            "medium": "Medium",
            "large": "Large",
            "high_contrast": "High Contrast:",
            "animation_speed": "Animation Speed:",
            "slow": "Slow",
            "normal": "Normal",
            "fast": "Fast",
            "none": "None",
            "apply_accessibility": "Apply Settings",
            "accessibility_applied": "Accessibility settings applied!",
            "help_center": "Help Center",
            "faq": "FAQ",
            "tutorial": "Tutorial",
            "contact_support": "Contact Support",
            "loading": "Loading...",
            "processing": "Processing...",
            "ready": "Ready!",
            "welcome_message": "Welcome to Britvic Production Dashboard 2.0!",
            "getting_started": "To get started, select a category and period in the filters on the left.",
            "performance_metrics": "Performance Metrics",
            "loading_time": "Loading Time: {time}s",
            "data_points": "Data Points: {count}",
            "memory_usage": "Memory Usage: {usage}MB",
            "export_options": "Export Options",
            "export_excel": "Excel (.xlsx)",
            "export_csv": "CSV (.csv)",
            "export_pdf": "PDF (.pdf)",
            "export_image": "Image (.png)",
            "annotations": "Annotations",
            "add_annotation": "Add Annotation",
            "edit_annotation": "Edit Annotation",
            "delete_annotation": "Delete Annotation",
            "annotation_text": "Annotation Text:",
            "annotation_date": "Annotation Date:",
            "save_annotation": "Save Annotation",
            "cancel": "Cancel",
            "no_annotations": "No annotations found.",
            "annotations_saved": "Annotation saved successfully!",
            "annotations_deleted": "Annotation deleted successfully!",
            "scenario_analysis": "Scenario Analysis",
            "optimistic": "Optimistic",
            "realistic": "Realistic",
            "pessimistic": "Pessimistic",
            "scenario_description": "Scenario Description:",
            "create_scenario": "Create Scenario",
            "scenario_created": "Scenario created successfully!",
            "scenario_comparison": "Scenario Comparison",
            "goal_tracking": "Goal Tracking",
            "set_goal": "Set Goal",
            "goal_value": "Goal Value:",
            "goal_date": "Goal Date:",
            "save_goal": "Save Goal",
            "goal_saved": "Goal saved successfully!",
            "goal_progress": "Goal Progress: {progress}%",
            "goal_achieved": "Goal achieved!",
            "goal_not_achieved": "Goal not achieved.",
            "goal_tracking_chart": "Goal Tracking - {cat}",
            "actual": "Actual",
            "goal": "Goal",
            "variance_analysis": "Variance Analysis",
            "variance_from_goal": "Variance from Goal: {variance}%",
            "positive_variance": "Positive Variance",
            "negative_variance": "Negative Variance",
            "variance_chart": "Variance Analysis - {cat}",
            "decomposition_analysis": "Decomposition Analysis",
            "trend_component": "Trend Component",
            "seasonal_component": "Seasonal Component",
            "residual_component": "Residual Component",
            "decomposition_chart": "Time Series Decomposition - {cat}",
            "correlation_analysis": "Correlation Analysis",
            "correlation_matrix": "Correlation Matrix",
            "correlation_heatmap": "Correlation Heatmap",
            "correlation_value": "Correlation Value",
            "strong_positive": "Strong Positive Correlation",
            "moderate_positive": "Moderate Positive Correlation",
            "weak_positive": "Weak Positive Correlation",
            "no_correlation_value": "No Correlation",
            "weak_negative": "Weak Negative Correlation",
            "moderate_negative": "Moderate Negative Correlation",
            "strong_negative": "Strong Negative Correlation",
            "outlier_analysis": "Outlier Analysis",
            "outlier_detection": "Outlier Detection",
            "outlier_chart": "Outlier Chart - {cat}",
            "outlier": "Outlier",
            "not_outlier": "Not Outlier",
            "outlier_threshold": "Outlier Threshold:",
            "apply_threshold": "Apply Threshold",
            "threshold_applied": "Threshold applied successfully!",
            "production_calendar": "Production Calendar",
            "calendar_view": "Calendar View",
            "daily_view": "Daily View",
            "weekly_view": "Weekly View",
            "monthly_view": "Monthly View",
            "yearly_view": "Yearly View",
            "production_intensity": "Production Intensity",
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "very_high": "Very High",
            "production_calendar_title": "Production Calendar - {cat}",
            "benchmark_analysis": "Benchmark Analysis",
            "benchmark_selection": "Benchmark Selection",
            "benchmark_comparison": "Benchmark Comparison",
            "benchmark_chart": "Benchmark Chart - {cat}",
            "benchmark": "Benchmark",
            "actual_value": "Actual Value",
            "benchmark_value": "Benchmark Value",
            "benchmark_variance": "Benchmark Variance: {variance}%",
            "above_benchmark": "Above Benchmark",
            "below_benchmark": "Below Benchmark",
            "at_benchmark": "At Benchmark",
            "efficiency_ratio": "Efficiency Ratio",
            "efficiency_chart": "Efficiency Chart - {cat}",
            "efficiency_score": "Efficiency Score: {score}/100",
            "efficiency_trend": "Efficiency Trend",
            "improving": "Improving",
            "stable": "Stable",
            "declining": "Declining",
            "efficiency_recommendations": "Efficiency Recommendations",
            "recommendation_1": "Recommendation 1: {rec}",
            "recommendation_2": "Recommendation 2: {rec}",
            "recommendation_3": "Recommendation 3: {rec}",
            "implement_recommendation": "Implement Recommendation",
            "recommendation_implemented": "Recommendation implemented successfully!",
            "what_if_analysis": "What-If Analysis",
            "what_if_scenario": "What-If Scenario",
            "what_if_parameter": "What-If Parameter:",
            "what_if_value": "What-If Value:",
            "simulate": "Simulate",
            "simulation_result": "Simulation Result",
            "simulation_chart": "Simulation Chart - {cat}",
            "baseline": "Baseline",
            "simulation": "Simulation",
            "simulation_impact": "Simulation Impact: {impact}%",
            "positive_impact": "Positive Impact",
            "negative_impact": "Negative Impact",
            "neutral_impact": "Neutral Impact",
            "simulation_completed": "Simulation completed successfully!",
            "data_quality_score": "Data Quality Score: {score}/100",
            "data_quality_chart": "Data Quality Chart - {cat}",
            "completeness": "Completeness",
            "accuracy": "Accuracy",
            "consistency": "Consistency",
            "timeliness": "Timeliness",
            "data_quality_recommendations": "Data Quality Recommendations",
            "improve_completeness": "Improve Completeness: {rec}",
            "improve_accuracy": "Improve Accuracy: {rec}",
            "improve_consistency": "Improve Consistency: {rec}",
            "improve_timeliness": "Improve Timeliness: {rec}",
            "data_quality_trend": "Data Quality Trend",
            "data_quality_improving": "Improving",
            "data_quality_stable": "Stable",
            "data_quality_declining": "Declining",
            "data_quality_analysis": "Data Quality Analysis",
            "data_profiling": "Data Profiling",
            "data_profiling_chart": "Data Profiling Chart - {cat}",
            "data_distribution": "Data Distribution",
            "data_skewness": "Data Skewness: {skew}",
            "data_kurtosis": "Data Kurtosis: {kurt}",
            "data_range": "Data Range: {min} - {max}",
            "data_mean": "Data Mean: {mean}",
            "data_median": "Data Median: {median}",
            "data_mode": "Data Mode: {mode}",
            "data_std": "Data Standard Deviation: {std}",
            "data_variance": "Data Variance: {var}",
            "data_profiling_completed": "Data profiling completed successfully!",
            "production_pattern": "Production Pattern",
            "pattern_recognition": "Pattern Recognition",
            "pattern_chart": "Pattern Chart - {cat}",
            "pattern_detected": "Pattern Detected: {pattern}",
            "no_pattern_detected": "No pattern detected.",
            "pattern_confidence": "Pattern Confidence: {conf}%",
            "pattern_analysis": "Pattern Analysis",
            "pattern_recommendation": "Pattern Recommendation: {rec}",
            "pattern_impact": "Pattern Impact: {impact}",
            "pattern_recognition_completed": "Pattern recognition completed successfully!",
        },
    }
    base = TRANSLATE[idioma].get(msg_key, msg_key)
    if kwargs:
        base = base.format(**kwargs)
    return base


# ---------- CSS Customizado ----------
def get_custom_css():
    return f"""
    <style>
        .stApp {{
            background-color: {BRITVIC_BG};
            transition: background-color 0.5s ease;
        }}
        .center {{
            text-align: center;
        }}
        .britvic-title {{
            font-size: 2.6rem;
            font-weight: bold;
            color: {BRITVIC_PRIMARY};
            text-align: center;
            margin-bottom: 0.3em;
            transition: color 0.5s ease;
        }}
        .subtitle {{
            text-align: center;
            color: {BRITVIC_PRIMARY};
            font-size: 1.0rem;
            margin-bottom: 1em;
            transition: color 0.5s ease;
        }}
        .stButton>button {{
            background-color: {BRITVIC_PRIMARY};
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            background-color: {BRITVIC_ACCENT};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .card {{
            background-color: {BRITVIC_CARD_BG};
            border-radius: 18px;
            box-shadow: 0 6px 28px 0 {BRITVIC_SHADOW};
            padding: 28px 38px 22px 38px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 36px 0 {BRITVIC_SHADOW};
        }}
        .metric-container {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: {BRITVIC_CARD_BG};
            border-radius: 18px;
            box-shadow: 0 6px 28px 0 {BRITVIC_SHADOW};
            padding: 28px 38px 22px 38px;
            min-width: 220px;
            margin-bottom: 13px;
            text-align: center;
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 36px 0 {BRITVIC_SHADOW};
        }}
        .metric-title {{
            font-weight: 600;
            color: {BRITVIC_PRIMARY};
            font-size: 1.12em;
            margin-bottom: 5px;
            transition: color 0.5s ease;
        }}
        .metric-value {{
            color: {BRITVIC_ACCENT};
            font-size: 2.1em;
            font-weight: bold;
            margin-bottom: 7px;
            transition: color 0.5s ease;
        }}
        .metric-subtitle {{
            font-size: 1.08em;
            color: {BRITVIC_PRIMARY};
            margin-bottom: 2px;
            transition: color 0.5s ease;
        }}
        .metric-detail {{
            font-size: 1em;
            color: {BRITVIC_TEXT};
            transition: color 0.5s ease;
        }}
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
        }}
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: {BRITVIC_PRIMARY};
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        .tab-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            background-color: {BRITVIC_CARD_BG};
            color: {BRITVIC_PRIMARY};
            border-radius: 8px 8px 0 0;
            margin: 0 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .tab.active {{
            background-color: {BRITVIC_PRIMARY};
            color: white;
        }}
        .tab:hover {{
            background-color: {BRITVIC_ACCENT};
            color: white;
        }}
        .search-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }}
        .search-input {{
            width: 50%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid {BRITVIC_PRIMARY};
            transition: all 0.3s ease;
        }}
        .search-input:focus {{
            outline: none;
            border-color: {BRITVIC_ACCENT};
            box-shadow: 0 0 8px {BRITVIC_ACCENT};
        }}
        .loading-animation {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }}
        .loading-dot {{
            width: 20px;
            height: 20px;
            background-color: {BRITVIC_PRIMARY};
            border-radius: 50%;
            margin: 0 10px;
            animation: loading 1.5s infinite ease-in-out;
        }}
        .loading-dot:nth-child(2) {{
            animation-delay: 0.2s;
        }}
        .loading-dot:nth-child(3) {{
            animation-delay: 0.4s;
        }}
        @keyframes loading {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.5); }}
        }}
        .annotation-marker {{
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: {BRITVIC_ACCENT};
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .annotation-marker:hover {{
            transform: scale(1.2);
        }}
        .tooltip-container {{
            position: relative;
            display: inline-block;
        }}
        .tooltip-text {{
            visibility: hidden;
            width: 200px;
            background-color: {BRITVIC_PRIMARY};
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .tooltip-container:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
        }}
        /* Tamanhos de texto para acessibilidade */
        .text-small {{
            font-size: 0.9rem;
        }}
        .text-medium {{
            font-size: 1rem;
        }}
        .text-large {{
            font-size: 1.2rem;
        }}
        /* Alto contraste */
        .high-contrast {{
            filter: contrast(1.5);
        }}
    </style>
    """


st.markdown(get_custom_css(), unsafe_allow_html=True)


# ----------- Topo/logomarca ------------
def render_header():
    st.markdown(
        f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: {BRITVIC_BG};
            padding: 10px 0 20px 0;
            margin-bottom: 20px;
            transition: background-color 0.5s ease;"
        >
            <img src="https://raw.githubusercontent.com/martins6231/app_atd/main/britvic_logo.png" alt="Britvic Logo" style="width: 150px; margin-bottom: 10px;">
            <h1 style="
                font-size: 2.2rem;
                font-weight: bold;
                color: {BRITVIC_PRIMARY};
                margin: 0;
                transition: color 0.5s ease;"
            >
                {t("main_title")}
            </h1>
            <p style="
                color: {BRITVIC_TEXT};
                margin-top: 5px;
                transition: color 0.5s ease;"
            >
                {t("last_updated", time=st.session_state["last_update"].strftime("%d/%m/%Y %H:%M"))}
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )


render_header()

# ---------- Funções auxiliares ------------


def nome_mes(numero):
    return (
        calendar.month_abbr[int(numero)]
        if idioma == "pt"
        else calendar.month_name[int(numero)][:3]
    )


def nome_dia_semana(numero):
    dias_pt = [
        "Segunda",
        "Terça",
        "Quarta",
        "Quinta",
        "Sexta",
        "Sábado",
        "Domingo",
    ]
    dias_en = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return dias_pt[numero] if idioma == "pt" else dias_en[numero]


def is_excel_file(file_path):
    try:
        with zipfile.ZipFile(file_path):
            return True
    except zipfile.BadZipFile:
        return False
    except Exception:
        return False


def convert_gsheet_link(shared_url):
    if "docs.google.com/spreadsheets" in shared_url:
        import re

        match = re.search(r"/d/([a-zA-Z0-9-_]+)", shared_url)
        if match:
            sheet_id = match.group(1)
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    return shared_url


@st.cache_data(ttl=600)
def carregar_excel_nuvem(link):
    url = convert_gsheet_link(link)
    resp = requests.get(url)
    if resp.status_code != 200:
        st.error(t("error_download_xls", code=resp.status_code))
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(resp.content)
        tmp.flush()
        if not is_excel_file(tmp.name):
            st.error(t("not_valid_excel"))
            return None
        try:
            df = pd.read_excel(tmp.name, engine="openpyxl")
        except Exception as e:
            st.error(t("excel_open_error", err=e))
            return None
    return df


def tratar_dados(df):
    erros = []
    df = df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"))
    obrigatorias = ["categoria", "data", "caixas_produzidas"]
    for col in obrigatorias:
        if col not in df.columns:
            erros.append(t("mandatory_col_missing", col=col))
    try:
        df["data"] = pd.to_datetime(df["data"])
    except Exception:
        erros.append(t("error_date_conversion"))
    na_count = df.isna().sum()
    for col, qtd in na_count.items():
        if qtd > 0:
            erros.append(t("col_with_missing", col=col, num=qtd))
    negativos = (df["caixas_produzidas"] < 0).sum()
    if negativos > 0:
        erros.append(t("negatives", num=negativos))
    df_clean = df.dropna(
        subset=["categoria", "data", "caixas_produzidas"]
    ).copy()
    df_clean["caixas_produzidas"] = (
        pd.to_numeric(df_clean["caixas_produzidas"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    df_clean = df_clean[df_clean["caixas_produzidas"] >= 0]
    df_clean = df_clean.drop_duplicates(
        subset=["categoria", "data"], keep="first"
    )

    # Adicionar campos úteis para análises adicionais
    df_clean["ano"] = df_clean["data"].dt.year
    df_clean["mes"] = df_clean["data"].dt.month
    df_clean["dia_semana"] = df_clean["data"].dt.weekday
    df_clean["semana_ano"] = df_clean["data"].dt.isocalendar().week

    return df_clean, erros


def selecionar_categoria(df):
    return sorted(df["categoria"].dropna().unique())


def dataset_ano_mes(df, categoria=None):
    df_filt = df if categoria is None else df[df["categoria"] == categoria]
    return df_filt


def filtrar_periodo(
    df,
    categoria,
    anos_selecionados,
    meses_selecionados,
    data_inicio=None,
    data_fim=None,
    min_prod=None,
    max_prod=None,
):
    cond = df["categoria"] == categoria
    if anos_selecionados:
        cond &= df["data"].dt.year.isin(anos_selecionados)
    if meses_selecionados:
        cond &= df["data"].dt.month.isin(meses_selecionados)
    if data_inicio is not None and data_fim is not None:
        cond &= (df["data"] >= data_inicio) & (df["data"] <= data_fim)
    if min_prod is not None:
        cond &= df["caixas_produzidas"] >= min_prod
    if max_prod is not None:
        cond &= df["caixas_produzidas"] <= max_prod
    return df[cond].copy()


def gerar_dataset_modelo(df, categoria=None):
    df_cat = df[df["categoria"] == categoria] if categoria else df
    grupo = df_cat.groupby("data")["caixas_produzidas"].sum().reset_index()
    return grupo.sort_values("data")


def detectar_anomalias(df, categoria, eps=0.5, min_samples=5):
    """Detecta anomalias usando DBSCAN"""
    dataset = gerar_dataset_modelo(df, categoria)
    if dataset.shape[0] < min_samples + 1:
        return pd.DataFrame()

    # Preparar dados para clustering
    X = dataset[["caixas_produzidas"]].copy()
    X_scaled = StandardScaler().fit_transform(X)

    # Aplicar DBSCAN
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X_scaled)
    dataset["cluster"] = clustering.labels_

    # -1 é o cluster de outliers/anomalias
    dataset["anomalia"] = dataset["cluster"] == -1

    return dataset


def calcular_correlacao_categorias(df):
    """Calcula a correlação entre diferentes categorias"""
    if df.empty or len(df["categoria"].unique()) < 2:
        return pd.DataFrame()

    # Pivotar os dados para ter categorias como colunas
    pivot = df.pivot_table(
        index="data",
        columns="categoria",
        values="caixas_produzidas",
        aggfunc="sum",
    ).fillna(0)

    # Calcular a matriz de correlação
    corr_matrix = pivot.corr()

    return corr_matrix


def gerar_mapa_calor_semanal(df, categoria):
    """Gera dados para um mapa de calor de produção por dia da semana e semana do ano"""
    df_cat = df[df["categoria"] == categoria].copy()
    if df_cat.empty:
        return pd.DataFrame()

    # Agrupar por semana do ano e dia da semana
    heatmap_data = (
        df_cat.groupby(["semana_ano", "dia_semana"])["caixas_produzidas"]
        .sum()
        .reset_index()
    )

    # Criar matriz para o heatmap
    pivot = heatmap_data.pivot_table(
        index="dia_semana",
        columns="semana_ano",
        values="caixas_produzidas",
        aggfunc="sum",
    ).fillna(0)

    return pivot


def calcular_eficiencia(df, categoria):
    """Calcula métricas de eficiência para a categoria"""
    df_cat = df[df["categoria"] == categoria].copy()
    if df_cat.empty:
        return None

    # Calcular eficiência como razão entre produção real e capacidade teórica
    # Aqui estamos usando um valor teórico simples baseado no máximo histórico
    max_producao = df_cat["caixas_produzidas"].max()
    df_cat["eficiencia"] = (df_cat["caixas_produzidas"] / max_producao) * 100

    # Agrupar por mês para ver tendência de eficiência
    eficiencia_mensal = (
        df_cat.groupby(["ano", "mes"])["eficiencia"].mean().reset_index()
    )
    eficiencia_mensal["data"] = pd.to_datetime(
        eficiencia_mensal["ano"].astype(str)
        + "-"
        + eficiencia_mensal["mes"].astype(str)
        + "-01"
    )

    return eficiencia_mensal


def rodar_previsao_prophet(df, categoria, meses_futuro=6, params=None):
    dataset = gerar_dataset_modelo(df, categoria)
    if dataset.shape[0] < 2:
        return dataset, pd.DataFrame(), None

    dados = dataset.rename(columns={"data": "ds", "caixas_produzidas": "y"})

    # Usar parâmetros personalizados se fornecidos
    if params is None:
        params = {
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 10.0,
            "seasonality_mode": "multiplicative",
            "interval_width": 0.8,
        }

    modelo = Prophet(
        yearly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=params["changepoint_prior_scale"],
        seasonality_prior_scale=params["seasonality_prior_scale"],
        seasonality_mode=params["seasonality_mode"],
        interval_width=params["interval_width"],
    )

    modelo.fit(dados)
    futuro = modelo.make_future_dataframe(periods=meses_futuro * 30)
    previsao = modelo.predict(futuro)

    # Decompor a série para análise de componentes
    decomposicao = None
    if not dados.empty and dados.shape[0] > 2:
        decomposicao = {
            "trend": previsao[["ds", "trend"]],
            "seasonal": previsao[["ds", "yearly", "weekly"]],
            "residual": None,  # Será calculado posteriormente se necessário
        }

    return dados, previsao, modelo, decomposicao


def exportar_para_excel(df, nome_arquivo):
    """Exporta um DataFrame para Excel na memória e retorna o buffer"""
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return buffer


def exportar_para_csv(df, nome_arquivo):
    """Exporta um DataFrame para CSV na memória e retorna o buffer"""
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def gerar_analise_dia_semana(df, categoria):
    """Gera análise de produção por dia da semana"""
    df_cat = df[df["categoria"] == categoria].copy()
    if df_cat.empty:
        return pd.DataFrame()

    # Agrupar por dia da semana
    dias_semana = (
        df_cat.groupby("dia_semana")["caixas_produzidas"]
        .agg(["sum", "mean", "count"])
        .reset_index()
    )
    dias_semana["nome_dia"] = dias_semana["dia_semana"].apply(
        lambda x: nome_dia_semana(x)
    )

    return dias_semana


def calcular_qualidade_dados(df, categoria):
    """Calcula métricas de qualidade dos dados"""
    df_cat = df[df["categoria"] == categoria].copy()
    if df_cat.empty:
        return None

    # Calcular completude (% de dados não nulos)
    completude = 100 - (df_cat.isnull().sum() / len(df_cat) * 100).mean()

    # Calcular consistência (% de dados dentro de limites esperados)
    q1 = df_cat["caixas_produzidas"].quantile(0.25)
    q3 = df_cat["caixas_produzidas"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    consistencia = 100 * (
        1
        - (
            (df_cat["caixas_produzidas"] < lower_bound)
            | (df_cat["caixas_produzidas"] > upper_bound)
        ).mean()
    )

    # Calcular precisão (estimativa baseada na variabilidade)
    cv = (
        df_cat["caixas_produzidas"].std() / df_cat["caixas_produzidas"].mean()
        if df_cat["caixas_produzidas"].mean() > 0
        else 0
    )
    precisao = 100 * (1 - min(cv, 1))

    # Calcular tempestividade (% de dados recentes)
    data_mais_recente = df_cat["data"].max()
    um_mes_atras = data_mais_recente - pd.Timedelta(days=30)
    tempestividade = 100 * (df_cat["data"] >= um_mes_atras).mean()

    # Calcular pontuação geral
    pontuacao = (completude + consistencia + precisao + tempestividade) / 4

    return {
        "pontuacao": pontuacao,
        "completude": completude,
        "consistencia": consistencia,
        "precisao": precisao,
        "tempestividade": tempestividade,
    }


def gerar_recomendacoes_eficiencia(df, categoria):
    """Gera recomendações baseadas na análise de eficiência"""
    df_cat = df[df["categoria"] == categoria].copy()
    if df_cat.empty:
        return []

    recomendacoes = []

    # Verificar variabilidade
    cv = (
        df_cat["caixas_produzidas"].std() / df_cat["caixas_produzidas"].mean()
        if df_cat["caixas_produzidas"].mean() > 0
        else 0
    )
    if cv > 0.3:
        recomendacoes.append(
            "Reduzir a variabilidade da produção para aumentar a previsibilidade e eficiência"
            if idioma == "pt"
            else "Reduce production variability to increase predictability and efficiency"
        )

    # Verificar tendência recente
    if len(df_cat) > 10:
        recentes = df_cat.sort_values("data").tail(5)
        antigas = df_cat.sort_values("data").iloc[:-5]
        if (
            recentes["caixas_produzidas"].mean()
            < antigas["caixas_produzidas"].mean()
        ):
            recomendacoes.append(
                "Investigar causas da queda recente na produção"
                if idioma == "pt"
                else "Investigate causes of recent production decline"
            )

    # Verificar padrões por dia da semana
    dias_semana = df_cat.groupby("dia_semana")["caixas_produzidas"].mean()
    if dias_semana.max() > 2 * dias_semana.min():
        dia_min = dias_semana.idxmin()
        recomendacoes.append(
            f"Melhorar a produção de {nome_dia_semana(dia_min)}, que está significativamente abaixo dos outros dias"
            if idioma == "pt"
            else f"Improve production on {nome_dia_semana(dia_min)}, which is significantly below other days"
        )

    # Se não houver recomendações específicas
    if not recomendacoes:
        recomendacoes.append(
            "Manter o padrão atual de produção, que apresenta boa estabilidade"
            if idioma == "pt"
            else "Maintain current production pattern, which shows good stability"
        )

    return recomendacoes[:3]  # Retornar até 3 recomendações


# Verificar se há segredos configurados
if "CLOUD_XLSX_URL" not in st.secrets:
    st.error(t("add_secrets"))
    st.stop()

# ----------- Carregar Dados -----------
with st.spinner(t("loading")):
    start_time = time.time()
    xlsx_url = st.secrets["CLOUD_XLSX_URL"]
    df_raw = carregar_excel_nuvem(xlsx_url)
    if df_raw is None:
        st.stop()

    df, erros = tratar_dados(df_raw)
    loading_time = time.time() - start_time

# ----------- Sidebar: Filtros e Configurações -----------
with st.sidebar:
    # Seção de filtros
    st.sidebar.markdown(f"## 🔍 {t('advanced_filters')}")

    # Filtro de categoria
    categorias = selecionar_categoria(df)
    default_categoria = categorias[0] if categorias else None

    # Inicializar filtros se necessário
    if "filtros" not in st.session_state or not st.session_state["filtros"]:
        anos_disp = sorted(df["ano"].unique())
        meses_disp = sorted(df["mes"].unique())
        meses_nome = [
            f"{m:02d} - {calendar.month_name[m] if idioma == 'en' else calendar.month_name[m][:3]}"
            for m in meses_disp
        ]
        map_mes = dict(zip(meses_nome, meses_disp))

        st.session_state["filtros"] = {
            "categoria": default_categoria,
            "anos": anos_disp,
            "meses_nome": meses_nome,
            "data_inicio": None,
            "data_fim": None,
            "min_prod": None,
            "max_prod": None,
        }

    # Filtros básicos
    categoria_analise = st.selectbox(
        t("category"),
        categorias,
        index=(
            categorias.index(st.session_state["filtros"]["categoria"])
            if categorias
            and st.session_state["filtros"]["categoria"] in categorias
            else 0
        ),
        key="catbox",
    )

    anos_disp = sorted(df["ano"].unique())
    anos_selecionados = st.multiselect(
        t("year"),
        anos_disp,
        default=st.session_state["filtros"].get("anos", anos_disp),
        key="anobox",
    )

    meses_disp = sorted(df["mes"].unique())
    meses_nome = [
        f"{m:02d} - {calendar.month_name[m] if idioma == 'en' else calendar.month_name[m][:3]}"
        for m in meses_disp
    ]
    map_mes = dict(zip(meses_nome, meses_disp))

    meses_selecionados_nome = st.multiselect(
        t("month"),
        meses_nome,
        default=st.session_state["filtros"].get("meses_nome", meses_nome),
        key="mesbox",
    )

    # Filtros avançados (em um expander)
    with st.expander(t("advanced_filters")):
        col1, col2 = st.columns(2)
        with col1:
            min_prod = st.number_input(
                t("min_production"),
                min_value=0,
                value=st.session_state["filtros"].get("min_prod", 0) or 0,
                key="min_prod_input",
            )
        with col2:
            max_value = (
                int(df["caixas_produzidas"].max()) if not df.empty else 10000
            )
            max_prod = st.number_input(
                t("max_production"),
                min_value=0,
                max_value=max_value,
                value=st.session_state["filtros"].get("max_prod", max_value)
                or max_value,
                key="max_prod_input",
            )

        # Intervalo de datas
        data_min = (
            df["data"].min().date()
            if not df.empty
            else datetime.now().date() - timedelta(days=365)
        )
        data_max = (
            df["data"].max().date() if not df.empty else datetime.now().date()
        )

        data_inicio = st.date_input(
            f"{t('date_range')} - {t('data')} {t('min_production')}",
            value=st.session_state["filtros"].get("data_inicio", data_min)
            or data_min,
            min_value=data_min,
            max_value=data_max,
            key="data_inicio_input",
        )

        data_fim = st.date_input(
            f"{t('date_range')} - {t('data')} {t('max_production')}",
            value=st.session_state["filtros"].get("data_fim", data_max)
            or data_max,
            min_value=data_min,
            max_value=data_max,
            key="data_fim_input",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("apply_filters")):
                st.session_state["filtros"]["min_prod"] = min_prod
                st.session_state["filtros"]["max_prod"] = max_prod
                st.session_state["filtros"]["data_inicio"] = data_inicio
                st.session_state["filtros"]["data_fim"] = data_fim
                st.success(t("filters_applied"))

        with col2:
            if st.button(t("reset_filters")):
                st.session_state["filtros"]["min_prod"] = None
                st.session_state["filtros"]["max_prod"] = None
                st.session_state["filtros"]["data_inicio"] = None
                st.session_state["filtros"]["data_fim"] = None
                st.success(t("filters_reset"))

    # Configurações avançadas do modelo Prophet
    with st.expander(t("prophet_settings")):
        st.slider(
            t("changepoint_prior"),
            min_value=0.001,
            max_value=0.5,
            value=st.session_state["prophet_params"][
                "changepoint_prior_scale"
            ],
            step=0.001,
            format="%.3f",
            key="changepoint_prior_scale",
        )

        st.slider(
            t("seasonality_prior"),
            min_value=0.01,
            max_value=20.0,
            value=st.session_state["prophet_params"][
                "seasonality_prior_scale"
            ],
            step=0.01,
            format="%.2f",
            key="seasonality_prior_scale",
        )

        st.radio(
            t("seasonality_mode"),
            options=["additive", "multiplicative"],
            index=(
                1
                if st.session_state["prophet_params"]["seasonality_mode"]
                == "multiplicative"
                else 0
            ),
            key="seasonality_mode",
            horizontal=True,
        )

        st.slider(
            t("interval_width"),
            min_value=0.5,
            max_value=0.95,
            value=st.session_state["prophet_params"]["interval_width"],
            step=0.05,
            format="%.2f",
            key="interval_width",
        )

        if st.button(t("apply_settings")):
            st.session_state["prophet_params"]["changepoint_prior_scale"] = (
                st.session_state["changepoint_prior_scale"]
            )
            st.session_state["prophet_params"]["seasonality_prior_scale"] = (
                st.session_state["seasonality_prior_scale"]
            )
            st.session_state["prophet_params"]["seasonality_mode"] = (
                st.session_state["seasonality_mode"]
            )
            st.session_state["prophet_params"]["interval_width"] = (
                st.session_state["interval_width"]
            )
            st.success(t("settings_applied"))

    # Opções de acessibilidade
    with st.expander(t("accessibility_options")):
        text_size = st.radio(
            t("text_size"),
            options=["small", "medium", "large"],
            index=1,  # Medium é o padrão
            key="text_size",
            horizontal=True,
        )

        high_contrast = st.checkbox(
            t("high_contrast"), value=False, key="high_contrast"
        )

        animation_speed = st.select_slider(
            t("animation_speed"),
            options=["none", "slow", "normal", "fast"],
            value=st.session_state["user_preferences"].get(
                "animation_speed", "normal"
            ),
            key="animation_speed",
        )

        if st.button(t("apply_accessibility")):
            st.session_state["user_preferences"]["text_size"] = text_size
            st.session_state["user_preferences"][
                "high_contrast"
            ] = high_contrast
            st.session_state["user_preferences"][
                "animation_speed"
            ] = animation_speed
            st.success(t("accessibility_applied"))

    # Botão para atualizar dados
    if st.button(t("refresh_data")):
        with st.spinner(t("refreshing")):
            df_raw = carregar_excel_nuvem(xlsx_url)
            if df_raw is not None:
                df, erros = tratar_dados(df_raw)
                st.session_state["last_update"] = datetime.now()
                st.success(t("data_refreshed"))

# Atualizar os filtros na sessão
st.session_state["filtros"]["categoria"] = st.session_state["catbox"]
st.session_state["filtros"]["anos"] = st.session_state["anobox"]
st.session_state["filtros"]["meses_nome"] = st.session_state["mesbox"]

# Converter os nomes dos meses para números
meses_selecionados = [
    map_mes[n]
    for n in st.session_state["filtros"]["meses_nome"]
    if n in map_mes
]

# Aplicar filtros
data_inicio_dt = (
    pd.to_datetime(st.session_state["filtros"].get("data_inicio"))
    if st.session_state["filtros"].get("data_inicio")
    else None
)
data_fim_dt = (
    pd.to_datetime(st.session_state["filtros"].get("data_fim"))
    if st.session_state["filtros"].get("data_fim")
    else None
)

df_filtrado = filtrar_periodo(
    df,
    st.session_state["filtros"]["categoria"],
    st.session_state["filtros"]["anos"],
    meses_selecionados,
    data_inicio_dt,
    data_fim_dt,
    st.session_state["filtros"].get("min_prod"),
    st.session_state["filtros"].get("max_prod"),
)

# ----------- Relatório de problemas nos dados -----------
with st.expander(t("data_issue_report"), expanded=len(erros) > 0):
    if erros:
        for e in erros:
            st.warning(e)
    else:
        st.success(t("no_critical"))

# --------- Subtítulo ---------
st.markdown(
    f"<h3 style='color:{BRITVIC_ACCENT}; text-align:left;'>{t('analysis_for', cat=st.session_state['filtros']['categoria'])}</h3>",
    unsafe_allow_html=True,
)

if df_filtrado.empty:
    st.error(t("empty_data_for_period"))
    st.stop()

# --------- Dicas e Truques ---------
if st.session_state["user_preferences"].get("show_tips", True):
    with st.expander(t("tips_and_tricks"), expanded=True):
        tips = [t("tip_1"), t("tip_2"), t("tip_3"), t("tip_4"), t("tip_5")]
        for tip in tips:
            st.info(tip)
        if st.button(t("hide_tips")):
            st.session_state["user_preferences"]["show_tips"] = False
            st.experimental_rerun()
else:
    if st.button(t("show_tips")):
        st.session_state["user_preferences"]["show_tips"] = True
        st.experimental_rerun()


# --------- KPIs / Métricas --------
def exibe_kpis(df, categoria):
    df_cat = df[df["categoria"] == categoria]
    if df_cat.empty:
        st.info(t("no_data_selection"))
        return None

    kpis = (
        df_cat.groupby("ano")["caixas_produzidas"]
        .agg(["sum", "mean", "std", "count"])
        .reset_index()
    )

    # Usar o componente de métrica do Streamlit
    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)

    for _, row in kpis.iterrows():
        ano = int(row["ano"])
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>
                    {t("kpi_year", ano=ano)}
                </div>
                <div class='metric-value'>
                    {t("kpi_sum", qtd=int(row['sum']))}
                </div>
                <div class='metric-subtitle'>
                    {t('kpi_daily_avg', media=row["mean"], accent=BRITVIC_ACCENT)}
                </div>
                <div class='metric-detail'>{t('kpi_records', count=row['count'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Adicionar métricas de desempenho
    with st.expander(t("performance_metrics")):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t("loading_time"), f"{loading_time:.2f}s")
        with col2:
            st.metric(t("data_points"), f"{len(df_cat):,}")
        with col3:
            # Estimativa simples de uso de memória
            memory_usage = df_cat.memory_usage(deep=True).sum() / (1024 * 1024)
            st.metric(t("memory_usage"), f"{memory_usage:.2f}MB")

    return kpis


exibe_kpis(df_filtrado, st.session_state["filtros"]["categoria"])

# --------- Abas para organizar visualizações ---------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 " + t("historico"),
        "🔮 " + t("forecast"),
        "🔍 " + t("analysis"),
        "📊 " + t("data_quality_analysis"),
    ]
)

# --------- GRÁFICOS - Aba 1: Histórico ---------
with tab1:

    def plot_tendencia(df, categoria):
        grupo = gerar_dataset_modelo(df, categoria)
        if grupo.empty:
            st.info(t("no_trend"))
            return

        fig = px.bar(
            grupo,
            x="data",
            y="caixas_produzidas",
            title=t("daily_trend", cat=categoria),
            labels={
                "data": t("data"),
                "caixas_produzidas": t("produced_boxes"),
            },
            text_auto=True,
        )

        fig.update_traces(
            marker_color=BRITVIC_ACCENT,
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} " + t("produced_boxes"),
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            xaxis_title=t("data"),
            yaxis_title=t("produced_boxes"),
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    def plot_variacao_mensal(df, categoria):
        agrup = dataset_ano_mes(df, categoria)
        mensal = (
            agrup.groupby([agrup["data"].dt.to_period("M")])[
                "caixas_produzidas"
            ]
            .sum()
            .reset_index()
        )
        mensal["mes"] = mensal["data"].dt.strftime("%b/%Y")
        mensal["var_%"] = mensal["caixas_produzidas"].pct_change() * 100

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(
                mensal,
                x="mes",
                y="caixas_produzidas",
                text_auto=True,
                title=t("monthly_total", cat=categoria),
                labels={
                    "mes": t("month_lbl"),
                    "caixas_produzidas": t("produced_boxes"),
                },
            )

            fig1.update_traces(
                marker_color=BRITVIC_ACCENT,
                hovertemplate="<b>%{x}</b><br>%{y:,.0f} "
                + t("produced_boxes"),
            )

            fig1.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50),
            )

            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(
                mensal,
                x="mes",
                y="var_%",
                markers=True,
                title=t("monthly_var", cat=categoria),
                labels={"mes": t("month_lbl"), "var_%": t("variation")},
            )

            fig2.update_traces(
                line_color=BRITVIC_PRIMARY,
                marker=dict(size=8, color=BRITVIC_ACCENT),
                hovertemplate="<b>%{x}</b><br>%{y:.2f}%",
            )

            fig2.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50),
            )

            st.plotly_chart(fig2, use_container_width=True)

    def plot_sazonalidade(df, categoria):
        agrup = dataset_ano_mes(df, categoria)
        if agrup.empty:
            st.info(t("no_trend"))
            return

        fig = px.box(
            agrup,
            x="mes",
            y="caixas_produzidas",
            color=agrup["ano"].astype(str),
            points="all",
            notched=True,
            title=t("monthly_seasonal", cat=categoria),
            labels={"mes": t("month_lbl"), "caixas_produzidas": t("prod")},
            hover_data=["ano"],
            color_discrete_sequence=px.colors.qualitative.Bold,
        )

        fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=[nome_mes(m) for m in range(1, 13)],
            ),
            template="plotly_white",
            legend_title=t("year_lbl"),
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    def plot_comparativo_ano_mes(df, categoria):
        agrup = dataset_ano_mes(df, categoria)
        tab = (
            agrup.groupby(["ano", "mes"])["caixas_produzidas"]
            .sum()
            .reset_index()
        )
        tab["mes_nome"] = tab["mes"].apply(nome_mes)
        tab = tab.sort_values(["mes"])

        fig = go.Figure()
        anos = sorted(tab["ano"].unique())
        cores = px.colors.qualitative.Bold

        for idx, ano in enumerate(anos):
            dados_ano = tab[tab["ano"] == ano]
            fig.add_trace(
                go.Bar(
                    x=dados_ano["mes_nome"],
                    y=dados_ano["caixas_produzidas"],
                    name=str(ano),
                    text=dados_ano["caixas_produzidas"],
                    textposition="auto",
                    marker_color=cores[idx % len(cores)],
                    hovertemplate="<b>%{x} %{text}</b><br>%{y:,.0f} "
                    + t("produced_boxes"),
                )
            )

        fig.update_layout(
            barmode="group",
            title=t("monthly_comp", cat=categoria),
            xaxis_title=t("month_lbl"),
            yaxis_title=t("produced_boxes"),
            legend_title=t("year_lbl"),
            hovermode="x unified",
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    def plot_comparativo_acumulado(df, categoria):
        agrup = dataset_ano_mes(df, categoria)
        res = (
            agrup.groupby(["ano", "mes"])["caixas_produzidas"]
            .sum()
            .reset_index()
        )
        res["acumulado"] = res.groupby("ano")["caixas_produzidas"].cumsum()

        fig = px.line(
            res,
            x="mes",
            y="acumulado",
            color=res["ano"].astype(str),
            markers=True,
            labels={
                "mes": t("month_lbl"),
                "acumulado": t("accum_boxes"),
                "ano": t("year_lbl"),
            },
            title=t("monthly_accum", cat=categoria),
            color_discrete_sequence=px.colors.qualitative.Bold,
        )

        fig.update_traces(
            mode="lines+markers",
            marker=dict(size=8),
            line=dict(width=3),
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} " + t("accum_boxes"),
        )

        fig.update_layout(
            legend_title=t("year_lbl"),
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=[nome_mes(m) for m in range(1, 13)],
            ),
            hovermode="x unified",
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    def plot_dia_semana(df, categoria):
        dias_semana = gerar_analise_dia_semana(df, categoria)
        if dias_semana.empty:
            st.info(t("no_trend"))
            return

        # Ordenar por dia da semana (0=Segunda, 6=Domingo)
        dias_semana = dias_semana.sort_values("dia_semana")

        fig = px.bar(
            dias_semana,
            x="nome_dia",
            y="mean",
            title=t("production_by_weekday", cat=categoria),
            labels={"nome_dia": t("weekday"), "mean": t("produced_boxes")},
            text_auto=True,
            color="mean",
            color_continuous_scale=px.colors.sequential.Viridis,
        )

        fig.update_traces(
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>"
            + t("produced_boxes")
            + ": %{y:.1f}",
        )

        fig.update_layout(
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    def plot_mapa_calor_semanal(df, categoria):
        pivot = gerar_mapa_calor_semanal(df, categoria)
        if pivot.empty:
            st.info(t("no_trend"))
            return

        # Converter índices numéricos para nomes de dias da semana
        pivot.index = [nome_dia_semana(dia) for dia in pivot.index]

        fig = px.imshow(
            pivot,
            labels=dict(
                x=t("week_number"), y=t("weekday"), color=t("produced_boxes")
            ),
            title=t("heatmap_title", cat=categoria),
            color_continuous_scale=px.colors.sequential.Viridis,
        )

        fig.update_layout(
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    # Executar gráficos da aba Histórico
    plot_tendencia(df_filtrado, st.session_state["filtros"]["categoria"])

    col1, col2 = st.columns(2)
    with col1:
        plot_dia_semana(df_filtrado, st.session_state["filtros"]["categoria"])
    with col2:
        plot_mapa_calor_semanal(
            df_filtrado, st.session_state["filtros"]["categoria"]
        )

    plot_variacao_mensal(df_filtrado, st.session_state["filtros"]["categoria"])
    plot_sazonalidade(df_filtrado, st.session_state["filtros"]["categoria"])

    if len(set(df_filtrado["data"].dt.year)) > 1:
        plot_comparativo_ano_mes(
            df_filtrado, st.session_state["filtros"]["categoria"]
        )
        plot_comparativo_acumulado(
            df_filtrado, st.session_state["filtros"]["categoria"]
        )

# --------- GRÁFICOS - Aba 2: Previsão ---------
with tab2:
    # Configurações do modelo Prophet
    prophet_params = st.session_state["prophet_params"]

    def plot_previsao(dados_hist, previsao, categoria, decomposicao=None):
        if previsao.empty:
            st.info(t("no_forecast"))
            return

        fig = go.Figure()

        # Adicionar dados históricos
        fig.add_trace(
            go.Scatter(
                x=dados_hist["ds"],
                y=dados_hist["y"],
                mode="lines+markers",
                name=t("historico"),
                line=dict(color=BRITVIC_PRIMARY, width=2),
                marker=dict(color=BRITVIC_ACCENT, size=6),
            )
        )

        # Adicionar linha de previsão
        fig.add_trace(
            go.Scatter(
                x=previsao["ds"],
                y=previsao["yhat"],
                mode="lines",
                name=t("forecast"),
                line=dict(color=BRITVIC_ACCENT, width=3),
            )
        )

        # Adicionar intervalo de confiança
        fig.add_trace(
            go.Scatter(
                x=previsao["ds"].tolist() + previsao["ds"].tolist()[::-1],
                y=previsao["yhat_upper"].tolist()
                + previsao["yhat_lower"].tolist()[::-1],
                fill="toself",
                fillcolor=f"rgba({int(BRITVIC_ACCENT[1:3], 16)}, {int(BRITVIC_ACCENT[3:5], 16)}, {int(BRITVIC_ACCENT[5:7], 16)}, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

        # Adicionar linhas de limite superior e inferior
        fig.add_trace(
            go.Scatter(
                x=previsao["ds"],
                y=previsao["yhat_upper"],
                mode="lines",
                line=dict(dash="dash", color="rgba(100,100,100,0.4)"),
                name="Upper Bound",
                hoverinfo="skip",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=previsao["ds"],
                y=previsao["yhat_lower"],
                mode="lines",
                line=dict(dash="dash", color="rgba(100,100,100,0.4)"),
                name="Lower Bound",
                hoverinfo="skip",
            )
        )

        # Marcar onde começa a previsão
        ultima_data = dados_hist["ds"].max()

        fig.add_shape(
            type="line",
            x0=ultima_data,
            y0=0,
            x1=ultima_data,
            y1=previsao["yhat_upper"].max() * 1.1,
            line=dict(color="gray", width=2, dash="dot"),
        )

        fig.add_annotation(
            x=ultima_data,
            y=previsao["yhat_upper"].max() * 1.05,
            text=t("forecast"),
            showarrow=True,
            arrowhead=1,
            ax=40,
            ay=-40,
        )

        fig.update_layout(
            title=t("forecast", cat=categoria),
            xaxis_title=t("data"),
            yaxis_title=t("produced_boxes"),
            template="plotly_white",
            hovermode="x unified",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=600,
            margin=dict(t=50, b=50, l=50, r=50),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Se houver decomposição, mostrar componentes
        if decomposicao:
            with st.expander(t("decomposition_analysis")):
                # Componente de tendência
                fig_trend = px.line(
                    decomposicao["trend"],
                    x="ds",
                    y="trend",
                    title=t("trend_component"),
                    labels={"ds": t("data"), "trend": t("trend_component")},
                )

                fig_trend.update_traces(line_color=BRITVIC_PRIMARY)

                fig_trend.update_layout(
                    template="plotly_white",
                    title_font_color=BRITVIC_PRIMARY,
                    plot_bgcolor=BRITVIC_BG,
                    height=300,
                )

                st.plotly_chart(fig_trend, use_container_width=True)

                # Componente sazonal
                if "yearly" in decomposicao["seasonal"].columns:
                    fig_seasonal = px.line(
                        decomposicao["seasonal"],
                        x="ds",
                        y="yearly",
                        title=t("seasonal_component"),
                        labels={
                            "ds": t("data"),
                            "yearly": t("seasonal_component"),
                        },
                    )

                    fig_seasonal.update_traces(line_color=BRITVIC_ACCENT)

                    fig_seasonal.update_layout(
                        template="plotly_white",
                        title_font_color=BRITVIC_PRIMARY,
                        plot_bgcolor=BRITVIC_BG,
                        height=300,
                    )

                    st.plotly_chart(fig_seasonal, use_container_width=True)

    def plot_cenarios(dados_hist, previsao, categoria):
        if previsao.empty:
            st.info(t("no_forecast"))
            return

        with st.expander(t("scenario_analysis")):
            col1, col2, col3 = st.columns(3)

            with col1:
                otimista = st.slider(
                    t("optimistic"),
                    min_value=1.0,
                    max_value=1.5,
                    value=1.2,
                    step=0.05,
                    format="%.2fx",
                )

            with col2:
                realista = 1.0  # Cenário base
                st.text(f"{t('realistic')}: 1.00x")

            with col3:
                pessimista = st.slider(
                    t("pessimistic"),
                    min_value=0.5,
                    max_value=1.0,
                    value=0.8,
                    step=0.05,
                    format="%.2fx",
                )

            # Criar cenários
            ultima_data = dados_hist["ds"].max()

            # Filtrar apenas dados futuros para cenários
            previsao_futura = previsao[previsao["ds"] > ultima_data].copy()

            # Calcular cenários
            previsao_futura["otimista"] = previsao_futura["yhat"] * otimista
            previsao_futura["realista"] = previsao_futura["yhat"]
            previsao_futura["pessimista"] = (
                previsao_futura["yhat"] * pessimista
            )

            # Plotar cenários
            fig = go.Figure()

            # Dados históricos
            fig.add_trace(
                go.Scatter(
                    x=dados_hist["ds"],
                    y=dados_hist["y"],
                    mode="lines+markers",
                    name=t("historico"),
                    line=dict(color=BRITVIC_PRIMARY, width=2),
                    marker=dict(color=BRITVIC_PRIMARY, size=6),
                )
            )

            # Cenário otimista
            fig.add_trace(
                go.Scatter(
                    x=previsao_futura["ds"],
                    y=previsao_futura["otimista"],
                    mode="lines",
                    name=t("optimistic"),
                    line=dict(color="#2ECC71", width=3),
                )
            )

            # Cenário realista
            fig.add_trace(
                go.Scatter(
                    x=previsao_futura["ds"],
                    y=previsao_futura["realista"],
                    mode="lines",
                    name=t("realistic"),
                    line=dict(color=BRITVIC_ACCENT, width=3),
                )
            )

            # Cenário pessimista
            fig.add_trace(
                go.Scatter(
                    x=previsao_futura["ds"],
                    y=previsao_futura["pessimista"],
                    mode="lines",
                    name=t("pessimistic"),
                    line=dict(color="#E74C3C", width=3),
                )
            )

            # Marcar onde começa a previsão
            fig.add_shape(
                type="line",
                x0=ultima_data,
                y0=0,
                x1=ultima_data,
                y1=previsao_futura["otimista"].max() * 1.1,
                line=dict(color="gray", width=2, dash="dot"),
            )

            fig.update_layout(
                title=t("scenario_comparison"),
                xaxis_title=t("data"),
                yaxis_title=t("produced_boxes"),
                template="plotly_white",
                hovermode="x unified",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=500,
                margin=dict(t=50, b=50, l=50, r=50),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Resumo dos cenários
            st.subheader(t("scenario_comparison"))

            # Calcular totais por cenário
            total_otimista = previsao_futura["otimista"].sum()
            total_realista = previsao_futura["realista"].sum()
            total_pessimista = previsao_futura["pessimista"].sum()

            # Exibir totais em cards
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    t("optimistic"),
                    f"{int(total_otimista):,}",
                    f"+{((total_otimista/total_realista)-1)*100:.1f}%",
                    delta_color="normal",
                )

            with col2:
                st.metric(
                    t("realistic"),
                    f"{int(total_realista):,}",
                    "0.0%",
                    delta_color="off",
                )

            with col3:
                st.metric(
                    t("pessimistic"),
                    f"{int(total_pessimista):,}",
                    f"{((total_pessimista/total_realista)-1)*100:.1f}%",
                    delta_color="inverse",
                )

    def plot_what_if(dados_hist, previsao, categoria):
        if previsao.empty:
            st.info(t("no_forecast"))
            return

        with st.expander(t("what_if_analysis")):
            # Parâmetros para simulação
            col1, col2 = st.columns(2)

            with col1:
                parametro = st.selectbox(
                    t("what_if_parameter"),
                    options=[
                        "seasonality_prior_scale",
                        "changepoint_prior_scale",
                    ],
                    format_func=lambda x: (
                        t("seasonality_prior")
                        if x == "seasonality_prior_scale"
                        else t("changepoint_prior")
                    ),
                )

            with col2:
                if parametro == "seasonality_prior_scale":
                    valor = st.slider(
                        t("what_if_value"),
                        min_value=0.01,
                        max_value=20.0,
                        value=st.session_state["prophet_params"][
                            "seasonality_prior_scale"
                        ]
                        * 2,
                        step=0.01,
                    )
                else:
                    valor = st.slider(
                        t("what_if_value"),
                        min_value=0.001,
                        max_value=0.5,
                        value=st.session_state["prophet_params"][
                            "changepoint_prior_scale"
                        ]
                        * 2,
                        step=0.001,
                    )

            # Botão para simular
            if st.button(t("simulate")):
                with st.spinner(t("processing")):
                    # Criar novos parâmetros
                    new_params = st.session_state["prophet_params"].copy()
                    new_params[parametro] = valor

                    # Executar nova previsão
                    _, nova_previsao, _, _ = rodar_previsao_prophet(
                        df_filtrado,
                        st.session_state["filtros"]["categoria"],
                        meses_futuro=6,
                        params=new_params,
                    )

                    # Plotar comparação
                    fig = go.Figure()

                    # Dados históricos
                    fig.add_trace(
                        go.Scatter(
                            x=dados_hist["ds"],
                            y=dados_hist["y"],
                            mode="lines+markers",
                            name=t("historico"),
                            line=dict(color=BRITVIC_PRIMARY, width=2),
                            marker=dict(color=BRITVIC_PRIMARY, size=6),
                        )
                    )

                    # Previsão original
                    fig.add_trace(
                        go.Scatter(
                            x=previsao["ds"],
                            y=previsao["yhat"],
                            mode="lines",
                            name=t("baseline"),
                            line=dict(color=BRITVIC_ACCENT, width=3),
                        )
                    )

                    # Nova previsão
                    fig.add_trace(
                        go.Scatter(
                            x=nova_previsao["ds"],
                            y=nova_previsao["yhat"],
                            mode="lines",
                            name=t("simulation"),
                            line=dict(color="#E74C3C", width=3),
                        )
                    )

                    # Marcar onde começa a previsão
                    ultima_data = dados_hist["ds"].max()
                    fig.add_shape(
                        type="line",
                        x0=ultima_data,
                        y0=0,
                        x1=ultima_data,
                        y1=max(
                            previsao["yhat"].max(), nova_previsao["yhat"].max()
                        )
                        * 1.1,
                        line=dict(color="gray", width=2, dash="dot"),
                    )

                    fig.update_layout(
                        title=t("simulation_chart", cat=categoria),
                        xaxis_title=t("data"),
                        yaxis_title=t("produced_boxes"),
                        template="plotly_white",
                        hovermode="x unified",
                        title_font_color=BRITVIC_PRIMARY,
                        plot_bgcolor=BRITVIC_BG,
                        height=500,
                        margin=dict(t=50, b=50, l=50, r=50),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                        ),
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Calcular impacto
                    previsao_futura = previsao[previsao["ds"] > ultima_data]
                    nova_previsao_futura = nova_previsao[
                        nova_previsao["ds"] > ultima_data
                    ]

                    total_original = previsao_futura["yhat"].sum()
                    total_simulado = nova_previsao_futura["yhat"].sum()

                    impacto_pct = ((total_simulado / total_original) - 1) * 100

                    # Mostrar impacto
                    st.metric(
                        t("simulation_impact", impact=f"{impacto_pct:.1f}"),
                        f"{int(total_simulado):,}",
                        f"{impacto_pct:.1f}%",
                        delta_color="normal" if impacto_pct > 0 else "inverse",
                    )

                    st.success(t("simulation_completed"))

    # Executar previsão com Prophet
    dados_hist, previsao, modelo_prophet, decomposicao = (
        rodar_previsao_prophet(
            df_filtrado,
            st.session_state["filtros"]["categoria"],
            meses_futuro=6,
            params=prophet_params,
        )
    )

    # Exibir gráficos de previsão
    plot_previsao(
        dados_hist,
        previsao,
        st.session_state["filtros"]["categoria"],
        decomposicao,
    )

    # Análise de cenários
    plot_cenarios(
        dados_hist, previsao, st.session_state["filtros"]["categoria"]
    )

    # Análise "E se..."
    plot_what_if(
        dados_hist, previsao, st.session_state["filtros"]["categoria"]
    )

# --------- GRÁFICOS - Aba 3: Análises ---------
with tab3:

    def plot_anomalias(df, categoria):
        """Plota o gráfico de detecção de anomalias"""
        anomalias = detectar_anomalias(df, categoria)
        if anomalias.empty:
            st.info(t("no_trend"))
            return

        # Contar anomalias
        count_anomalias = anomalias["anomalia"].sum()

        if count_anomalias > 0:
            st.warning(t("anomalies_found", count=count_anomalias))
        else:
            st.success(t("no_anomalies"))

        # Criar gráfico
        fig = px.scatter(
            anomalias,
            x="data",
            y="caixas_produzidas",
            color="anomalia",
            color_discrete_map={True: "#E74C3C", False: BRITVIC_ACCENT},
            title=t("anomaly_chart", cat=categoria),
            labels={
                "data": t("data"),
                "caixas_produzidas": t("produced_boxes"),
                "anomalia": t("anomaly"),
            },
            category_orders={"anomalia": [False, True]},
            size_max=15,
            hover_data=["data", "caixas_produzidas"],
        )

        # Adicionar linha de tendência para pontos normais
        normais = anomalias[~anomalias["anomalia"]]
        if not normais.empty:
            fig.add_trace(
                go.Scatter(
                    x=normais["data"],
                    y=normais["caixas_produzidas"],
                    mode="lines",
                    line=dict(color="rgba(39, 174, 96, 0.3)", width=2),
                    showlegend=False,
                )
            )

        fig.update_traces(marker=dict(size=12), selector=dict(mode="markers"))

        fig.update_layout(
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
            legend=dict(
                title=dict(text=""),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    def plot_correlacao(df):
        """Plota a matriz de correlação entre categorias"""
        corr_matrix = calcular_correlacao_categorias(df)
        if corr_matrix.empty:
            st.info(t("no_correlation"))
            return

        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            title=t("correlation_title"),
            labels=dict(
                x=t("category_lbl"),
                y=t("category_lbl"),
                color=t("correlation_value"),
            ),
            zmin=-1,
            zmax=1,
        )

        fig.update_layout(
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=600,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Adicionar interpretação
        with st.expander(t("correlation_analysis")):
            # Encontrar correlações fortes
            corr_flat = corr_matrix.unstack().reset_index()
            corr_flat.columns = ["categoria1", "categoria2", "correlacao"]
            corr_flat = corr_flat[
                corr_flat["categoria1"] != corr_flat["categoria2"]
            ]
            corr_flat = corr_flat.sort_values("correlacao", ascending=False)

            if not corr_flat.empty:
                # Correlações positivas
                pos_corr = corr_flat[corr_flat["correlacao"] > 0.5].head(3)
                if not pos_corr.empty:
                    st.subheader(t("strong_positive"))
                    for _, row in pos_corr.iterrows():
                        st.write(
                            f"**{row['categoria1']}** & **{row['categoria2']}**: {row['correlacao']:.2f}"
                        )

                # Correlações negativas
                neg_corr = corr_flat[corr_flat["correlacao"] < -0.5].head(3)
                if not neg_corr.empty:
                    st.subheader(t("strong_negative"))
                    for _, row in neg_corr.iterrows():
                        st.write(
                            f"**{row['categoria1']}** & **{row['categoria2']}**: {row['correlacao']:.2f}"
                        )

    def plot_eficiencia(df, categoria):
        """Plota análise de eficiência"""
        eficiencia = calcular_eficiencia(df, categoria)
        if eficiencia is None:
            st.info(t("no_trend"))
            return

        with st.expander(t("efficiency_analysis"), expanded=True):
            # Gráfico de eficiência ao longo do tempo
            fig = px.line(
                eficiencia,
                x="data",
                y="eficiencia",
                title=t("efficiency_chart", cat=categoria),
                labels={
                    "data": t("data"),
                    "eficiencia": t("efficiency_metric"),
                },
                markers=True,
            )

            fig.update_traces(
                line=dict(color=BRITVIC_PRIMARY, width=3),
                marker=dict(color=BRITVIC_ACCENT, size=8),
            )

            # Adicionar linha de referência em 100%
            fig.add_shape(
                type="line",
                x0=eficiencia["data"].min(),
                y0=100,
                x1=eficiencia["data"].max(),
                y1=100,
                line=dict(color="gray", width=2, dash="dash"),
            )

            fig.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Calcular pontuação de eficiência
            eficiencia_media = eficiencia["eficiencia"].mean()
            eficiencia_recente = (
                eficiencia.iloc[-3:]["eficiencia"].mean()
                if len(eficiencia) >= 3
                else eficiencia["eficiencia"].mean()
            )

            # Determinar tendência
            if eficiencia_recente > eficiencia_media * 1.05:
                tendencia = t("improving")
                cor_tendencia = "green"
            elif eficiencia_recente < eficiencia_media * 0.95:
                tendencia = t("declining")
                cor_tendencia = "red"
            else:
                tendencia = t("stable")
                cor_tendencia = "orange"

            # Exibir métricas
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    t("efficiency_score", score=f"{eficiencia_media:.1f}"),
                    f"{eficiencia_media:.1f}%",
                    delta=None,
                )

            with col2:
                st.metric(
                    t("efficiency_trend"),
                    tendencia,
                    delta=f"{eficiencia_recente - eficiencia_media:.1f}%",
                    delta_color=(
                        "normal"
                        if eficiencia_recente >= eficiencia_media
                        else "inverse"
                    ),
                )

            # Recomendações de eficiência
            st.subheader(t("efficiency_recommendations"))
            recomendacoes = gerar_recomendacoes_eficiencia(df, categoria)

            for i, rec in enumerate(recomendacoes, 1):
                st.info(rec)

    def plot_comparacao_categorias(df):
        """Permite comparar diferentes categorias"""
        with st.expander(t("comparison_tool")):
            # Selecionar categorias para comparar
            categorias = selecionar_categoria(df)
            categorias_selecionadas = st.multiselect(
                t("select_categories"),
                options=categorias,
                default=[st.session_state["filtros"]["categoria"]],
                max_selections=5,
            )

            if len(categorias_selecionadas) < 2:
                st.warning(t("select_categories"))
                return

            # Filtrar dados
            df_comp = df[df["categoria"].isin(categorias_selecionadas)].copy()

            # Agrupar por categoria e mês
            comp_mensal = (
                df_comp.groupby(
                    ["categoria", df_comp["data"].dt.to_period("M")]
                )["caixas_produzidas"]
                .sum()
                .reset_index()
            )
            comp_mensal["mes"] = comp_mensal["data"].dt.strftime("%b/%Y")

            # Criar gráfico de comparação
            fig = px.line(
                comp_mensal,
                x="mes",
                y="caixas_produzidas",
                color="categoria",
                title=t("category_comparison"),
                labels={
                    "mes": t("month_lbl"),
                    "caixas_produzidas": t("produced_boxes"),
                    "categoria": t("category_lbl"),
                },
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Bold,
            )

            fig.update_traces(
                mode="lines+markers", marker=dict(size=8), line=dict(width=3)
            )

            fig.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=500,
                margin=dict(t=50, b=50, l=50, r=50),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Comparação de totais
            st.subheader(t("category_comparison"))

            # Calcular totais por categoria
            totais = (
                df_comp.groupby("categoria")["caixas_produzidas"]
                .sum()
                .reset_index()
            )

            # Criar gráfico de barras para totais
            fig_total = px.bar(
                totais,
                x="categoria",
                y="caixas_produzidas",
                color="categoria",
                text_auto=True,
                labels={
                    "categoria": t("category_lbl"),
                    "caixas_produzidas": t("produced_boxes"),
                },
                color_discrete_sequence=px.colors.qualitative.Bold,
            )

            fig_total.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=400,
                margin=dict(t=30, b=50, l=50, r=50),
                showlegend=False,
            )

            st.plotly_chart(fig_total, use_container_width=True)

    # Executar gráficos da aba Análises
    col1, col2 = st.columns(2)

    with col1:
        plot_anomalias(df_filtrado, st.session_state["filtros"]["categoria"])

    with col2:
        plot_eficiencia(df_filtrado, st.session_state["filtros"]["categoria"])

    # Correlação entre categorias (usa todos os dados, não apenas filtrados)
    plot_correlacao(df)

    # Ferramenta de comparação de categorias
    plot_comparacao_categorias(df)

    # Insights automáticos
    def gerar_insights(df, categoria):
        grupo = gerar_dataset_modelo(df, categoria)
        tendencias = []
        mensal = grupo.copy()
        mensal["mes"] = mensal["data"].dt.to_period("M")
        agg = mensal.groupby("mes")["caixas_produzidas"].sum()
        if len(agg) > 6:
            ultimos = min(3, len(agg))
            if agg[-ultimos:].mean() > agg[:-ultimos].mean():
                tendencias.append(t("recent_growth"))
            elif agg[-ultimos:].mean() < agg[:-ultimos].mean():
                tendencias.append(t("recent_fall"))
        q1 = grupo["caixas_produzidas"].quantile(0.25)
        q3 = grupo["caixas_produzidas"].quantile(0.75)
        outliers = grupo[
            (grupo["caixas_produzidas"] < q1 - 1.5 * (q3 - q1))
            | (grupo["caixas_produzidas"] > q3 + 1.5 * (q3 - q1))
        ]
        if not outliers.empty:
            tendencias.append(t("outlier_days", num=outliers.shape[0]))
        std = grupo["caixas_produzidas"].std()
        mean = grupo["caixas_produzidas"].mean()
        if mean > 0 and std / mean > 0.5:
            tendencias.append(t("high_var"))

        # Adicionar insights sobre padrões por dia da semana
        dias_semana = (
            df[df["categoria"] == categoria]
            .groupby("dia_semana")["caixas_produzidas"]
            .mean()
        )
        if not dias_semana.empty and dias_semana.max() > 0:
            dia_max = dias_semana.idxmax()
            dia_min = dias_semana.idxmin()
            if dias_semana.max() > 2 * dias_semana.min():
                tendencias.append(
                    f"{nome_dia_semana(dia_max)} {t('high')} / {nome_dia_semana(dia_min)} {t('low')}"
                )

        with st.expander(t("auto_insights"), expanded=True):
            for text in tendencias:
                st.info(text)
            if not tendencias:
                st.success(t("no_pattern"))

    gerar_insights(df_filtrado, st.session_state["filtros"]["categoria"])

# --------- GRÁFICOS - Aba 4: Qualidade dos Dados ---------
with tab4:

    def plot_qualidade_dados(df, categoria):
        """Plota análise de qualidade dos dados"""
        qualidade = calcular_qualidade_dados(df, categoria)
        if qualidade is None:
            st.info(t("no_trend"))
            return

        # Criar gráfico de radar para qualidade dos dados
        categorias = [
            t("completeness"),
            t("accuracy"),
            t("consistency"),
            t("timeliness"),
        ]
        valores = [
            qualidade["completude"],
            qualidade["precisao"],
            qualidade["consistencia"],
            qualidade["tempestividade"],
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=valores,
                theta=categorias,
                fill="toself",
                line=dict(color=BRITVIC_ACCENT, width=3),
                fillcolor=f"rgba({int(BRITVIC_ACCENT[1:3], 16)}, {int(BRITVIC_ACCENT[3:5], 16)}, {int(BRITVIC_ACCENT[5:7], 16)}, 0.2)",
            )
        )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title=t("data_quality_chart", cat=categoria),
            template="plotly_white",
            title_font_color=BRITVIC_PRIMARY,
            plot_bgcolor=BRITVIC_BG,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Exibir pontuação geral
        st.metric(
            t("data_quality_score", score=f"{qualidade['pontuacao']:.1f}"),
            f"{qualidade['pontuacao']:.1f}/100",
            delta=None,
        )

        # Recomendações de qualidade dos dados
        with st.expander(t("data_quality_recommendations")):
            if qualidade["completude"] < 95:
                st.warning(
                    t(
                        "improve_completeness",
                        rec=(
                            "Verificar processo de coleta de dados para reduzir valores ausentes"
                            if idioma == "pt"
                            else "Check data collection process to reduce missing values"
                        ),
                    )
                )

            if qualidade["precisao"] < 90:
                st.warning(
                    t(
                        "improve_accuracy",
                        rec=(
                            "Revisar métodos de medição para aumentar precisão"
                            if idioma == "pt"
                            else "Review measurement methods to increase accuracy"
                        ),
                    )
                )

            if qualidade["consistencia"] < 90:
                st.warning(
                    t(
                        "improve_consistency",
                        rec=(
                            "Implementar validações para detectar valores atípicos"
                            if idioma == "pt"
                            else "Implement validations to detect outliers"
                        ),
                    )
                )

            if qualidade["tempestividade"] < 80:
                st.warning(
                    t(
                        "improve_timeliness",
                        rec=(
                            "Atualizar dados com maior frequência"
                            if idioma == "pt"
                            else "Update data more frequently"
                        ),
                    )
                )

            if qualidade["pontuacao"] >= 90:
                st.success(
                    "Excelente qualidade de dados! Mantenha o processo atual."
                    if idioma == "pt"
                    else "Excellent data quality! Maintain the current process."
                )

    def plot_distribuicao(df, categoria):
        """Plota a distribuição dos dados"""
        df_cat = df[df["categoria"] == categoria].copy()
        if df_cat.empty:
            st.info(t("no_trend"))
            return

        with st.expander(t("data_distribution")):
            # Calcular estatísticas
            stats = {
                "min": df_cat["caixas_produzidas"].min(),
                "max": df_cat["caixas_produzidas"].max(),
                "mean": df_cat["caixas_produzidas"].mean(),
                "median": df_cat["caixas_produzidas"].median(),
                "std": df_cat["caixas_produzidas"].std(),
                "skew": df_cat["caixas_produzidas"].skew(),
                "kurt": df_cat["caixas_produzidas"].kurtosis(),
            }

            # Exibir estatísticas
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    t(
                        "data_range",
                        min=f"{stats['min']:,.0f}",
                        max=f"{stats['max']:,.0f}",
                    ),
                    f"{stats['max'] - stats['min']:,.0f}",
                )
                st.metric(
                    t("data_mean", mean=f"{stats['mean']:,.1f}"),
                    f"{stats['mean']:,.1f}",
                )
                st.metric(
                    t("data_median", median=f"{stats['median']:,.1f}"),
                    f"{stats['median']:,.1f}",
                )

            with col2:
                st.metric(
                    t("data_std", std=f"{stats['std']:,.1f}"),
                    f"{stats['std']:,.1f}",
                )
                st.metric(
                    t("data_skewness", skew=f"{stats['skew']:.2f}"),
                    f"{stats['skew']:.2f}",
                )
                st.metric(
                    t("data_kurtosis", kurt=f"{stats['kurt']:.2f}"),
                    f"{stats['kurt']:.2f}",
                )

            # Histograma
            fig = px.histogram(
                df_cat,
                x="caixas_produzidas",
                nbins=30,
                title=t("data_distribution"),
                labels={"caixas_produzidas": t("produced_boxes")},
                color_discrete_sequence=[BRITVIC_ACCENT],
            )

            # Adicionar linha para média
            fig.add_vline(
                x=stats["mean"],
                line_dash="dash",
                line_color=BRITVIC_PRIMARY,
                annotation_text=t("data_mean", mean=f"{stats['mean']:,.1f}"),
                annotation_position="top right",
            )

            fig.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Box plot
            fig_box = px.box(
                df_cat,
                y="caixas_produzidas",
                title=t("outlier_analysis"),
                labels={"caixas_produzidas": t("produced_boxes")},
                color_discrete_sequence=[BRITVIC_ACCENT],
            )

            fig_box.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=300,
                margin=dict(t=50, b=50, l=50, r=50),
                showlegend=False,
            )

            st.plotly_chart(fig_box, use_container_width=True)

    def plot_completude_temporal(df, categoria):
        """Plota a completude dos dados ao longo do tempo"""
        df_cat = df[df["categoria"] == categoria].copy()
        if df_cat.empty:
            st.info(t("no_trend"))
            return

        with st.expander(t("data_profiling")):
            # Agrupar por mês e contar registros
            df_cat["mes"] = df_cat["data"].dt.to_period("M")
            completude = (
                df_cat.groupby("mes").size().reset_index(name="registros")
            )
            completude["mes_str"] = completude["mes"].dt.strftime("%b/%Y")

            # Calcular dias no mês
            completude["dias_no_mes"] = completude["mes"].dt.days_in_month

            # Calcular completude (registros / dias no mês)
            completude["completude_pct"] = (
                completude["registros"] / completude["dias_no_mes"]
            ) * 100

            # Criar gráfico
            fig = px.bar(
                completude,
                x="mes_str",
                y="completude_pct",
                title=t("completeness"),
                labels={
                    "mes_str": t("month_lbl"),
                    "completude_pct": t("completeness") + " (%)",
                },
                text_auto=True,
                color="completude_pct",
                color_continuous_scale=px.colors.sequential.Viridis,
            )

            # Adicionar linha para 100%
            fig.add_hline(
                y=100,
                line_dash="dash",
                line_color="gray",
                annotation_text="100%",
                annotation_position="top right",
            )

            fig.update_layout(
                template="plotly_white",
                title_font_color=BRITVIC_PRIMARY,
                plot_bgcolor=BRITVIC_BG,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50),
                coloraxis_showscale=False,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Estatísticas de completude
            media_completude = completude["completude_pct"].mean()
            min_completude = completude["completude_pct"].min()
            max_completude = completude["completude_pct"].max()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(t("data_mean", mean=""), f"{media_completude:.1f}%")

            with col2:
                st.metric(t("min_production"), f"{min_completude:.1f}%")

            with col3:
                st.metric(t("max_production"), f"{max_completude:.1f}%")

    # Executar gráficos da aba Qualidade dos Dados
    plot_qualidade_dados(df_filtrado, st.session_state["filtros"]["categoria"])

    col1, col2 = st.columns(2)

    with col1:
        plot_distribuicao(
            df_filtrado, st.session_state["filtros"]["categoria"]
        )

    with col2:
        plot_completude_temporal(
            df_filtrado, st.session_state["filtros"]["categoria"]
        )

# --------- EXPORTAÇÃO ---------
with st.expander(t("export")):

    def exportar_consolidado(df, previsao, categoria):
        if previsao.empty:
            st.warning(t("no_export"))
            return None, None

        dados = gerar_dataset_modelo(df, categoria)
        previsao_col = previsao[["ds", "yhat"]].rename(
            columns={"ds": "data", "yhat": "previsao_caixas"}
        )
        base_export = dados.merge(
            previsao_col, left_on="data", right_on="data", how="outer"
        ).sort_values("data")
        base_export["categoria"] = categoria

        return base_export, f"consolidado_{categoria.lower()}"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(t("export_excel"), help=t("export_with_fc")):
            base_export, nome_base = exportar_consolidado(
                df_filtrado, previsao, st.session_state["filtros"]["categoria"]
            )
            if base_export is not None:
                buffer = exportar_para_excel(base_export, f"{nome_base}.xlsx")
                st.download_button(
                    label=t("download_file"),
                    data=buffer,
                    file_name=f"{nome_base}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    with col2:
        if st.button(t("export_csv")):
            base_export, nome_base = exportar_consolidado(
                df_filtrado, previsao, st.session_state["filtros"]["categoria"]
            )
            if base_export is not None:
                buffer = exportar_para_csv(base_export, f"{nome_base}.csv")
                st.download_button(
                    label=t("download_file").replace("Excel", "CSV"),
                    data=buffer,
                    file_name=f"{nome_base}.csv",
                    mime="text/csv",
                )

    with col3:
        if st.button(t("export_image")):
            st.info(
                "Para exportar como imagem, use o botão de download disponível no canto superior direito de cada gráfico."
                if idioma == "pt"
                else "To export as image, use the download button available in the top right corner of each chart."
            )

    with col4:
        if st.button(t("share_link")):
            # Criar um link compartilhável (simplificado)
            params = {
                "categoria": st.session_state["filtros"]["categoria"],
                "anos": ",".join(
                    map(str, st.session_state["filtros"]["anos"])
                ),
                "meses": ",".join(map(str, meses_selecionados)),
            }

            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            share_url = f"?{query_string}"

            # Usar clipboard via JavaScript
# Versão corrigida:
link_copied_text = t("link_copied")
st.markdown(
    f"""
    <div style="display: flex; align-items: center;">
        <input type="text" value="{share_url}" id="share-link" 
               style="flex-grow: 1; padding: 8px; border-radius: 4px; border: 1px solid #ccc;">
        <button onclick="copyLink()" style="margin-left: 8px; background-color: {BRITVIC_PRIMARY}; color: white; border: none; border-radius: 4px; padding: 8px 12px; cursor: pointer;">
            Copiar
        </button>
    </div>
    <script>
    function copyLink() {{
        var copyText = document.getElementById("share-link");
        copyText.select();
        copyText.setSelectionRange(0, 99999);
        navigator.clipboard.writeText(copyText.value);
        alert("{link_copied_text}");
    }}
    </script>
    """,
    unsafe_allow_html=True,
)

# Adicionar rodapé com informações de desempenho
st.markdown(
    f"""
    <div style="margin-top: 50px; text-align: center; color: {BRITVIC_TEXT};">
        <p>{t("last_updated", time=st.session_state["last_update"].strftime("%d/%m/%Y %H:%M"))}</p>
        <p>Dashboard Britvic 2.0 | {t("loading_time", time=f"{loading_time:.2f}")} | {t("data_points", count=f"{len(df_filtrado):,}")}</p>
    </div>
""",
    unsafe_allow_html=True,
)
