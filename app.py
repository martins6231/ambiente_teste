import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import locale
from streamlit_option_menu import option_menu

# Set page configuration
st.set_page_config(
    page_title="Juice Industry Analytics",
    page_icon="🧃",
    layout="wide"
)

# Language settings
LANGUAGES = {
    "pt-BR": {
        "title": "Análise de Eficiência - Indústria de Sucos",
        "period": "Período",
        "efficiency": "Eficiência",
        "maintenance": "Manutenção",
        "compare": "Comparar Períodos",
        "settings": "Configurações",
        "language": "Idioma",
        "dark_mode": "Modo Escuro",
    },
    "en": {
        "title": "Efficiency Analysis - Juice Industry",
        "period": "Period",
        "efficiency": "Efficiency",
        "maintenance": "Maintenance",
        "compare": "Compare Periods",
        "settings": "Settings",
        "language": "Language",
        "dark_mode": "Dark Mode",
    }
}

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'pt-BR'
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def get_text(key):
    return LANGUAGES[st.session_state.language][key]

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=[
            get_text("efficiency"),
            get_text("maintenance"),
            get_text("compare"),
            get_text("settings")
        ],
        icons=['graph-up', 'tools', 'bar-chart', 'gear'],
        default_index=0,
    )

# Main content
st.title(get_text("title"))

if selected == get_text("settings"):
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            get_text("language"),
            options=['pt-BR', 'en'],
            index=0 if st.session_state.language == 'pt-BR' else 1
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.experimental_rerun()
    
    with col2:
        dark_mode = st.toggle(get_text("dark_mode"), st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.experimental_rerun()

elif selected == get_text("efficiency"):
    # Sample efficiency data (replace with actual data)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    efficiency_data = pd.DataFrame({
        'date': dates,
        'efficiency': np.random.uniform(75, 95, len(dates)),
        'maintenance_hours': np.random.uniform(0, 8, len(dates))
    })

    # Date filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=efficiency_data['date'].min(),
            min_value=efficiency_data['date'].min(),
            max_value=efficiency_data['date'].max()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=efficiency_data['date'].max(),
            min_value=efficiency_data['date'].min(),
            max_value=efficiency_data['date'].max()
        )

    # Filter data based on date range
    mask = (efficiency_data['date'].dt.date >= start_date) & (efficiency_data['date'].dt.date <= end_date)
    filtered_data = efficiency_data.loc[mask]

    # Efficiency trend chart
    fig = px.line(
        filtered_data,
        x='date',
        y='efficiency',
        title='Machine Efficiency Over Time'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Efficiency statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Efficiency", f"{filtered_data['efficiency'].mean():.2f}%")
    with col2:
        st.metric("Min Efficiency", f"{filtered_data['efficiency'].min():.2f}%")
    with col3:
        st.metric("Max Efficiency", f"{filtered_data['efficiency'].max():.2f}%")

elif selected == get_text("maintenance"):
    st.info("Maintenance analysis section under development")

elif selected == get_text("compare"):
    st.info("Period comparison section under development")