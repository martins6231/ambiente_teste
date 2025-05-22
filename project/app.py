"""
Britvic Production Dashboard
---------------------------
A bilingual (PT/EN) dashboard for visualizing and analyzing production data.

Features:
- Production trends and forecasting
- Monthly comparisons and seasonality analysis
- Automated insights generation
- Data export capabilities
- Responsive design with customizable filters

Author: Bolt
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
import calendar
from datetime import datetime
import io
import requests
import tempfile
import zipfile
from typing import Tuple, List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Type aliases
DataFrame = pd.DataFrame
Figure = go.Figure

@dataclass
class DashboardConfig:
    """Dashboard configuration and styling constants"""
    PRIMARY_COLOR: str = "#003057"
    ACCENT_COLOR: str = "#27AE60"
    BG_COLOR: str = "#F4FFF6"
    CHART_TEMPLATE: str = "plotly_white"
    LOGO_URL: str = "https://raw.githubusercontent.com/martins6231/app_atd/main/britvic_logo.png"
    REQUIRED_COLUMNS: List[str] = field(default_factory=lambda: ['categoria', 'data', 'caixas_produzidas'])

class TranslationManager:
    """Handles multilingual support for the dashboard"""
    
    LANGS = {
        "pt": "Português (Brasil)",
        "en": "English"
    }
    
    def __init__(self):
        self.translations = self._load_translations()
        
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations from a centralized dictionary"""
        return {
            "pt": {
                "dashboard_title": "Dashboard de Produção - Britvic",
                "main_title": "Dashboard de Produção",
                "subtitle": "Visualização dos dados de produção Britvic",
                "category": "🏷️ Categoria:",
                "year": "📅 Ano(s):",
                "month": "📆 Mês(es):",
                "date_range": "📅 Intervalo de Datas:",
                "start_date": "Data Inicial:",
                "end_date": "Data Final:",
                "use_date_range": "Usar filtro de intervalo de datas",
                "analysis_for": "Análise para categoria: <b>{cat}</b>",
                "date_range_active": "Período: <b>{start}</b> até <b>{end}</b>",
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
                "reset_filters": "Resetar Filtros",
                # Labels
                "data": "Data",
                "category_lbl": "Categoria",
                "produced_boxes": "Caixas Produzidas",
                "month_lbl": "Mês/Ano",
                "variation": "Variação (%)",
                "prod": "Produção",
                "year_lbl": "Ano",
                "accum_boxes": "Caixas Acumuladas",
                "forecast_boxes": "Previsão Caixas"
            },
            "en": {
                "dashboard_title": "Production Dashboard - Britvic",
                "main_title": "Production Dashboard",
                "subtitle": "Britvic production data visualization",
                "category": "🏷️ Category:",
                "year": "📅 Year(s):",
                "month": "📆 Month(s):",
                "date_range": "📅 Date Range:",
                "start_date": "Start Date:",
                "end_date": "End Date:",
                "use_date_range": "Use date range filter",
                "analysis_for": "Analysis for category: <b>{cat}</b>",
                "date_range_active": "Period: <b>{start}</b> to <b>{end}</b>",
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
                "reset_filters": "Reset Filters",
                # Labels
                "data": "Date",
                "category_lbl": "Category",
                "produced_boxes": "Produced Boxes",
                "month_lbl": "Month/Year",
                "variation": "Variation (%)",
                "prod": "Production",
                "year_lbl": "Year",
                "accum_boxes": "Accum. Boxes",
                "forecast_boxes": "Forecasted Boxes"
            }
        }
    
    def get(self, key: str, lang: str, **kwargs) -> str:
        """Get translation for a key in specified language"""
        translation = self.translations[lang].get(key, key)
        if kwargs:
            translation = translation.format(**kwargs)
        return translation

class DataLoader:
    """Handles data loading and preprocessing"""
    
    def __init__(self, config: DashboardConfig, translator: TranslationManager):
        self.config = config
        self.translator = translator
        
    def load_from_cloud(self, url: str) -> Optional[DataFrame]:
        """Load data from cloud storage"""
        url = self._convert_gsheet_link(url)
        try:
            response = requests.get(url)
            if response.status_code != 200:
                st.error(self.translator.get("error_download_xls", st.session_state.lang, code=response.status_code))
                return None
                
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(response.content)
                tmp.flush()
                
                if not self._is_valid_excel(tmp.name):
                    st.error(self.translator.get("not_valid_excel", st.session_state.lang))
                    return None
                    
                try:
                    df = pd.read_excel(tmp.name, engine="openpyxl")
                    return self._preprocess_data(df)
                except Exception as e:
                    st.error(self.translator.get("excel_open_error", st.session_state.lang, err=str(e)))
                    return None
        except Exception:
            return None
            
    def _convert_gsheet_link(self, url: str) -> str:
        """Convert Google Sheets link to direct download URL"""
        if "docs.google.com/spreadsheets" in url:
            import re
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
            if match:
                sheet_id = match.group(1)
                return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx'
        return url
        
    def _is_valid_excel(self, file_path: str) -> bool:
        """Check if file is a valid Excel file"""
        try:
            with zipfile.ZipFile(file_path):
                return True
        except (zipfile.BadZipFile, Exception):
            return False
            
    def _preprocess_data(self, df: DataFrame) -> DataFrame:
        """Clean and preprocess the data"""
        df = df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"))
        df = df.dropna(subset=self.config.REQUIRED_COLUMNS)
        df['data'] = pd.to_datetime(df['data'])
        df['caixas_produzidas'] = pd.to_numeric(df['caixas_produzidas'], errors='coerce').fillna(0).astype(int)
        df = df[df['caixas_produzidas'] >= 0]
        return df.drop_duplicates(subset=['categoria', 'data'], keep='first')

class Dashboard:
    """Main dashboard class that orchestrates the UI and visualization"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self.translator = TranslationManager()
        self.data_loader = DataLoader(self.config, self.translator)
        self.setup_page()
        self.load_data()
        self.setup_sidebar()
        self.render_dashboard()
        
    def setup_page(self):
        """Configure page settings and style"""
        st.set_page_config(
            page_title=self.translator.get("dashboard_title", "en"),
            layout="wide",
            page_icon="🧃"
        )
        self.apply_custom_css()
        
    def apply_custom_css(self):
        """Apply custom CSS styling"""
        st.markdown(f"""
            <style>
                .stApp {{
                    background-color: {self.config.BG_COLOR};
                }}
                .center {{
                    text-align: center;
                }}
                .britvic-title {{
                    font-size: 2.6rem;
                    font-weight: bold;
                    color: {self.config.PRIMARY_COLOR};
                    text-align: center;
                    margin-bottom: 0.3em;
                }}
                .subtitle {{
                    text-align: center;
                    color: {self.config.PRIMARY_COLOR};
                    font-size: 1.0rem;
                    margin-bottom: 1em;
                }}
                .filter-section {{
                    margin-top: 1.5rem;
                    border-top: 1px solid #e0e0e0;
                    padding-top: 1rem;
                }}
                .date-range-picker {{
                    margin-top: 0.5rem;
                    padding: 0.5rem 0;
                }}
                .date-range-picker label {{
                    font-weight: 500;
                    color: {self.config.PRIMARY_COLOR};
                }}
            </style>
        """, unsafe_allow_html=True)
        
    def load_data(self):
        """Load and prepare the data"""
        if "CLOUD_XLSX_URL" not in st.secrets:
            st.error(self.translator.get("add_secrets", st.session_state.lang))
            st.stop()
            
        self.df = self.data_loader.load_from_cloud(st.secrets["CLOUD_XLSX_URL"])
        if self.df is None:
            st.stop()
            
    def setup_sidebar(self):
        """Configure sidebar filters and controls"""
        st.sidebar.markdown("## 🌐 Idioma | Language")
        self.lang = st.sidebar.radio(
            "Escolha o idioma / Choose language:",
            options=list(self.translator.LANGS.keys()),
            format_func=lambda x: self.translator.LANGS[x],
            key="lang"
        )
        
        # Category filter
        self.category = st.sidebar.selectbox(
            self.translator.get("category", self.lang),
            options=sorted(self.df['categoria'].unique()),
            key="category"
        )
        
        # Year and month filters
        st.sidebar.markdown(f'<div class="filter-section"></div>', unsafe_allow_html=True)
        self.years = st.sidebar.multiselect(
            self.translator.get("year", self.lang),
            options=sorted(self.df['data'].dt.year.unique()),
            default=sorted(self.df['data'].dt.year.unique()),
            key="years"
        )
        
        months = sorted(self.df['data'].dt.month.unique())
        month_names = [
            f"{m:02d} - {calendar.month_name[m][:3] if self.lang == 'en' else calendar.month_abbr[m]}"
            for m in months
        ]
        self.months = st.sidebar.multiselect(
            self.translator.get("month", self.lang),
            options=month_names,
            default=month_names,
            key="months"
        )
        
        # Date range filter
        st.sidebar.markdown(f'<div class="filter-section"></div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'### {self.translator.get("date_range", self.lang)}')
        self.use_date_range = st.sidebar.checkbox(
            self.translator.get("use_date_range", self.lang),
            key="use_date_range"
        )
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            self.start_date = st.date_input(
                self.translator.get("start_date", self.lang),
                value=self.df['data'].min(),
                min_value=self.df['data'].min().date(),
                max_value=self.df['data'].max().date(),
                disabled=not self.use_date_range,
                key="start_date"
            )
        with col2:
            self.end_date = st.date_input(
                self.translator.get("end_date", self.lang),
                value=self.df['data'].max(),
                min_value=self.df['data'].min().date(),
                max_value=self.df['data'].max().date(),
                disabled=not self.use_date_range,
                key="end_date"
            )
            
    def render_dashboard(self):
        """Render the main dashboard content"""
        self.render_header()
        self.render_filters_summary()
        
        # Filter data based on selections
        filtered_df = self.filter_data()
        if filtered_df.empty:
            st.error(self.translator.get("empty_data_for_period", self.lang))
            return
            
        # Render visualizations
        self.render_kpis(filtered_df)
        self.render_trends(filtered_df)
        self.render_monthly_analysis(filtered_df)
        self.render_forecast(filtered_df)
        self.render_insights(filtered_df)
        self.render_export_section(filtered_df)
        
    def render_header(self):
        """Render dashboard header with logo"""
        st.markdown(f"""
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background-color: {self.config.BG_COLOR};
                padding: 10px 0 20px 0;
                margin-bottom: 20px;"
            >
                <img src="{self.config.LOGO_URL}" alt="Britvic Logo" style="width: 150px; margin-bottom: 10px;">
                <h1 style="
                    font-size: 2.2rem;
                    font-weight: bold;
                    color: {self.config.PRIMARY_COLOR};
                    margin: 0;"
                >
                    {self.translator.get("main_title", self.lang)}
                </h1>
            </div>
        """, unsafe_allow_html=True)
        
    def render_filters_summary(self):
        """Display active filters summary"""
        st.markdown(
            f"<h3 style='color:{self.config.ACCENT_COLOR}; text-align:left;'>"
            f"{self.translator.get('analysis_for', self.lang, cat=self.category)}</h3>",
            unsafe_allow_html=True
        )
        
        if self.use_date_range:
            start_fmt = self.start_date.strftime('%d/%m/%Y')
            end_fmt = self.end_date.strftime('%d/%m/%Y')
            st.markdown(
                f"<p style='color:{self.config.PRIMARY_COLOR}; font-size:1.1em;'>"
                f"{self.translator.get('date_range_active', self.lang, start=start_fmt, end=end_fmt)}</p>",
                unsafe_allow_html=True
            )
            
    def filter_data(self) -> DataFrame:
        """Apply filters to the data"""
        if self.use_date_range:
            mask = (
                (self.df['categoria'] == self.category) &
                (self.df['data'].dt.date >= self.start_date) &
                (self.df['data'].dt.date <= self.end_date)
            )
        else:
            selected_months = [int(m.split(' - ')[0]) for m in self.months]
            mask = (
                (self.df['categoria'] == self.category) &
                (self.df['data'].dt.year.isin(self.years)) &
                (self.df['data'].dt.month.isin(selected_months))
            )
        return self.df[mask].copy()
        
    def render_kpis(self, df: DataFrame):
        """Render KPI metrics"""
        df_grouped = df.groupby(df['data'].dt.year).agg({
            'caixas_produzidas': ['sum', 'mean', 'std', 'count']
        }).reset_index()
        
        kpi_html = """
        <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 18px;">
        """
        
        for _, row in df_grouped.iterrows():
            year = int(row['data'])
            kpi_html += f"""
            <div style="
                background: #e8f8ee;
                border-radius: 18px;
                box-shadow: 0 6px 28px 0 rgba(0, 48, 87, 0.13);
                padding: 28px 38px 22px 38px;
                min-width: 220px;
                margin-bottom: 13px;
                text-align: center;
            ">
                <div style="font-weight: 600; color: {self.config.PRIMARY_COLOR}; font-size: 1.12em; margin-bottom:5px;">
                    {self.translator.get("kpi_year", self.lang, ano=year)}
                </div>
                <div style="color: {self.config.ACCENT_COLOR}; font-size:2.1em; font-weight:bold; margin-bottom:7px;">
                    {self.translator.get("kpi_sum", self.lang, qtd=int(row['caixas_produzidas']['sum']))}
                </div>
                <div style="font-size: 1.08em; color: {self.config.PRIMARY_COLOR}; margin-bottom:2px;">
                    {self.translator.get('kpi_daily_avg', self.lang, media=row['caixas_produzidas']['mean'], accent=self.config.ACCENT_COLOR)}
                </div>
                <div style="font-size: 1em; color: #666;">
                    {self.translator.get('kpi_records', self.lang, count=row['caixas_produzidas']['count'])}
                </div>
            </div>
            """
        
        kpi_html += "</div>"
        st.markdown(kpi_html, unsafe_allow_html=True)
        
    def render_trends(self, df: DataFrame):
        """Render trend visualizations"""
        # Daily trend
        daily_data = df.groupby('data')['caixas_produzidas'].sum().reset_index()
        fig = px.bar(
            daily_data,
            x='data',
            y='caixas_produzidas',
            title=self.translator.get("daily_trend", self.lang, cat=self.category),
            labels={
                "data": self.translator.get("data", self.lang),
                "caixas_produzidas": self.translator.get("produced_boxes", self.lang)
            },
            text_auto=True
        )
        fig.update_traces(marker_color=self.config.ACCENT_COLOR)
        fig.update_layout(
            template=self.config.CHART_TEMPLATE,
            hovermode="x",
            title_font_color=self.config.PRIMARY_COLOR,
            plot_bgcolor=self.config.BG_COLOR
        )
        st.plotly_chart(fig, use_container_width=True)
        
    def render_monthly_analysis(self, df: DataFrame):
        """Render monthly analysis charts"""
        monthly_data = df.groupby(df['data'].dt.to_period('M')).agg({
            'caixas_produzidas': 'sum'
        }).reset_index()
        monthly_data['mes'] = monthly_data['data'].dt.strftime('%b/%Y')
        monthly_data['var_%'] = monthly_data['caixas_produzidas'].pct_change() * 100
        
        # Monthly totals
        fig1 = px.bar(
            monthly_data,
            x='mes',
            y='caixas_produzidas',
            title=self.translator.get("monthly_total", self.lang, cat=self.category),
            labels={
                "mes": self.translator.get("month_lbl", self.lang),
                "caixas_produzidas": self.translator.get("produced_boxes", self.lang)
            },
            text_auto=True
        )
        fig1.update_traces(marker_color=self.config.ACCENT_COLOR)
        fig1.update_layout(
            template=self.config.CHART_TEMPLATE,
            title_font_color=self.config.PRIMARY_COLOR,
            plot_bgcolor=self.config.BG_COLOR
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Monthly variation
        fig2 = px.line(
            monthly_data,
            x='mes',
            y='var_%',
            title=self.translator.get("monthly_var", self.lang, cat=self.category),
            labels={
                "mes": self.translator.get("month_lbl", self.lang),
                "var_%": self.translator.get("variation", self.lang)
            },
            markers=True
        )
        fig2.update_traces(
            line_color="#E67E22",
            marker=dict(size=7, color=self.config.ACCENT_COLOR)
        )
        fig2.update_layout(
            template=self.config.CHART_TEMPLATE,
            title_font_color=self.config.PRIMARY_COLOR,
            plot_bgcolor=self.config.BG_COLOR
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    def render_forecast(self, df: DataFrame):
        """Render forecast visualization"""
        if df.shape[0] < 2:
            st.info(self.translator.get("no_forecast", self.lang))
            return
            
        # Prepare data for Prophet
        prophet_data = df.groupby('data')['caixas_produzidas'].sum().reset_index()
        prophet_data = prophet_data.rename(columns={'data': 'ds', 'caixas_produzidas': 'y'})
        
        # Create and fit model
        model = Prophet(yearly_seasonality=True, daily_seasonality=False)
        model.fit(prophet_data)
        
        # Make forecast
        future = model.make_future_dataframe(periods=180)  # 6 months
        forecast = model.predict(future)
        
        # Plot forecast
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=prophet_data['ds'],
            y=prophet_data['y'],
            mode='lines+markers',
            name=self.translator.get("historico", self.lang),
            line=dict(color=self.config.PRIMARY_COLOR, width=2),
            marker=dict(color=self.config.ACCENT_COLOR)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            name=self.translator.get("forecast", self.lang),
            line=dict(color=self.config.ACCENT_COLOR, width=2)
        ))
        
        # Confidence intervals
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            line=dict(dash='dash', color='#AED6F1'),
            name='Upper',
            opacity=0.3
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            line=dict(dash='dash', color='#AED6F1'),
            name='Lower',
            opacity=0.3
        ))
        
        fig.update_layout(
            title=self.translator.get("forecast", self.lang, cat=self.category),
            xaxis_title=self.translator.get("data", self.lang),
            yaxis_title=self.translator.get("produced_boxes", self.lang),
            template=self.config.CHART_TEMPLATE,
            hovermode="x unified",
            title_font_color=self.config.PRIMARY_COLOR,
            plot_bgcolor=self.config.BG_COLOR
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def render_insights(self, df: DataFrame):
        """Generate and display automated insights"""
        insights = []
        
        # Monthly trend analysis
        monthly_data = df.groupby(df['data'].dt.to_period('M'))['caixas_produzidas'].sum()
        if len(monthly_data) > 6:
            recent_months = 3
            recent_avg = monthly_data[-recent_months:].mean()
            previous_avg = monthly_data[:-recent_months].mean()
            
            if recent_avg > previous_avg * 1.1:  # 10% increase
                insights.append(self.translator.get("recent_growth", self.lang))
            elif recent_avg < previous_avg * 0.9:  # 10% decrease
                insights.append(self.translator.get("recent_fall", self.lang))
                
        # Outlier detection
        daily_data = df.groupby('data')['caixas_produzidas'].sum()
        q1 = daily_data.quantile(0.25)
        q3 = daily_data.quantile(0.75)
        iqr = q3 - q1
        outliers = daily_data[(daily_data < (q1 - 1.5 * iqr)) | (daily_data > (q3 + 1.5 * iqr))]
        
        if not outliers.empty:
            insights.append(self.translator.get("outlier_days", self.lang, num=len(outliers)))
            
        # Variability analysis
        if daily_data.std() / daily_data.mean() > 0.5:  # High coefficient of variation
            insights.append(self.translator.get("high_var", self.lang))
            
        with st.expander(self.translator.get("auto_insights", self.lang), expanded=True):
            if insights:
                for insight in insights:
                    st.info(insight)
            else:
                st.success(self.translator.get("no_pattern", self.lang))
                
    def render_export_section(self, df: DataFrame):
        """Render export functionality"""
        with st.expander(self.translator.get("export", self.lang)):
            if st.button(self.translator.get("export_with_fc", self.lang)):
                # Prepare forecast data
                prophet_data = df.groupby('data')['caixas_produzidas'].sum().reset_index()
                prophet_data = prophet_data.rename(columns={'data': 'ds', 'caixas_produzidas': 'y'})
                
                model = Prophet(yearly_seasonality=True, daily_seasonality=False)
                model.fit(prophet_data)
                
                future = model.make_future_dataframe(periods=180)
                forecast = model.predict(future)
                
                # Prepare export data
                export_data = prophet_data.merge(
                    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
                    on='ds',
                    how='right'
                )
                export_data = export_data.rename(columns={
                    'ds': 'data',
                    'y': 'caixas_produzidas',
                    'yhat': 'previsao',
                    'yhat_lower': 'previsao_min',
                    'yhat_upper': 'previsao_max'
                })
                
                # Create Excel file
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    export_data.to_excel(writer, index=False, sheet_name='Dados')
                    
                buffer.seek(0)
                
                # Download button
                st.download_button(
                    label=self.translator.get("download_file", self.lang),
                    data=buffer,
                    file_name=f'previsao_{self.category.lower()}.xlsx',
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    dashboard = Dashboard()
