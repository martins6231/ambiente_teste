import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Define days in Portuguese
dias_semana_pt = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}

# Define month names in Portuguese
meses_pt = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}

def create_pareto_chart(df):
    """
    Create a Pareto chart of downtime causes.
    
    Args:
        df: Processed pandas DataFrame
    
    Returns:
        Plotly figure object
    """
    if 'Parada' not in df.columns or len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para gerar o gráfico",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Pareto de Causas de Paradas (Top 10 por Duração)",
            height=400,
        )
        return fig
    
    # Group by downtime cause and sum durations
    pareto = df.groupby('Parada')['Duração'].sum().reset_index()
    
    # Convert timedelta to hours for better visualization
    pareto['Duração (horas)'] = pareto['Duração'].apply(lambda x: x.total_seconds() / 3600)
    
    # Sort and take top 10
    pareto = pareto.sort_values('Duração (horas)', ascending=False).head(10)
    
    # Calculate cumulative percentage
    pareto['Porcentagem'] = 100 * pareto['Duração (horas)'] / pareto['Duração (horas)'].sum()
    pareto['Porcentagem Acumulada'] = pareto['Porcentagem'].cumsum()
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=pareto['Parada'],
        y=pareto['Duração (horas)'],
        name='Duração (horas)',
        marker_color='#3498db',
        text=pareto['Duração (horas)'].round(1).astype(str) + 'h',
        textposition='auto',
    ))
    
    # Add cumulative line
    fig.add_trace(go.Scatter(
        x=pareto['Parada'],
        y=pareto['Porcentagem Acumulada'],
        name='% Acumulada',
        marker=dict(color='#e74c3c'),
        yaxis='y2',
        line=dict(width=3),
        mode='lines+markers',
    ))
    
    # Update layout
    fig.update_layout(
        title="Pareto de Causas de Paradas (Top 10 por Duração)",
        xaxis=dict(
            title="Causa da Parada",
            tickangle=45,
        ),
        yaxis=dict(
            title="Duração (horas)",
            titlefont=dict(color='#3498db'),
            tickfont=dict(color='#3498db'),
        ),
        yaxis2=dict(
            title="Porcentagem Acumulada",
            titlefont=dict(color='#e74c3c'),
            tickfont=dict(color='#e74c3c'),
            anchor="x",
            overlaying="y",
            side="right",
            range=[0, 100],
            ticksuffix="%",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400,
    )
    
    return fig

def create_area_pie_chart(df):
    """
    Create a pie chart of downtime by responsible area.
    
    Args:
        df: Processed pandas DataFrame
    
    Returns:
        Plotly figure object
    """
    if 'Área Responsável' not in df.columns or len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para gerar o gráfico",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Índice de Paradas por Área Responsável",
            height=400,
        )
        return fig
    
    # Group by area and sum durations
    area_counts = df.groupby('Área Responsável')['Duração'].sum().reset_index()
    
    # Convert timedelta to hours
    area_counts['Duração (horas)'] = area_counts['Duração'].apply(lambda x: x.total_seconds() / 3600)
    
    # Calculate percentages
    total_hours = area_counts['Duração (horas)'].sum()
    area_counts['Percentual'] = (area_counts['Duração (horas)'] / total_hours * 100).round(1)
    
    # Create figure
    fig = px.pie(
        area_counts,
        names='Área Responsável',
        values='Duração (horas)',
        title="Índice de Paradas por Área Responsável",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_data=['Percentual'],
        labels={'Duração (horas)': 'Duração (horas)', 'Percentual': 'Percentual'}
    )
    
    # Update layout
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if i == area_counts['Duração (horas)'].idxmax() else 0 for i in range(len(area_counts))]
    )
    
    fig.update_layout(
        height=400,
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_occurrences_chart(df):
    """
    Create a line chart of occurrences by month.
    
    Args:
        df: Processed pandas DataFrame
    
    Returns:
        Plotly figure object
    """
    if 'Ano-Mês' not in df.columns or len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para gerar o gráfico",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Taxa de Ocorrência de Paradas por Mês",
            height=400,
        )
        return fig
    
    # Group by month and count occurrences
    occurrences = df.groupby('Ano-Mês').size().reset_index()
    occurrences.columns = ['Mês', 'Número de Paradas']
    
    # If there's only one month, create a bar chart instead
    if len(occurrences) == 1:
        fig = px.bar(
            occurrences,
            x='Mês',
            y='Número de Paradas',
            title="Número de Paradas no Período",
            color_discrete_sequence=['#2ecc71'],
            text='Número de Paradas'
        )
    else:
        # Sort by month
        occurrences['sort_key'] = pd.to_datetime(occurrences['Mês'])
        occurrences = occurrences.sort_values('sort_key')
        
        # Create a line chart
        fig = px.line(
            occurrences,
            x='Mês',
            y='Número de Paradas',
            title="Taxa de Ocorrência de Paradas por Mês",
            markers=True,
            color_discrete_sequence=['#2ecc71'],
        )
        
        # Add data points
        fig.add_trace(go.Scatter(
            x=occurrences['Mês'],
            y=occurrences['Número de Paradas'],
            mode='markers+text',
            text=occurrences['Número de Paradas'],
            textposition='top center',
            showlegend=False,
            marker=dict(color='#2ecc71', size=10)
        ))
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title="Mês", tickangle=45),
        yaxis=dict(title="Número de Paradas"),
        height=400,
    )
    
    return fig

def create_area_bar_chart(df):
    """
    Create a horizontal bar chart of total downtime by responsible area.
    
    Args:
        df: Processed pandas DataFrame
    
    Returns:
        Plotly figure object
    """
    if 'Área Responsável' not in df.columns or len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para gerar o gráfico",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Tempo Total de Paradas por Área",
            height=400,
        )
        return fig
    
    # Group by area and sum durations
    area_time = df.groupby('Área Responsável')['Duração'].sum().reset_index()
    
    # Convert timedelta to hours
    area_time['Duração (horas)'] = area_time['Duração'].apply(lambda x: x.total_seconds() / 3600)
    
    # Sort by duration
    area_time = area_time.sort_values('Duração (horas)')
    
    # Create figure
    fig = px.bar(
        area_time,
        y='Área Responsável',
        x='Duração (horas)',
        title="Tempo Total de Paradas por Área",
        orientation='h',
        color='Duração (horas)',
        color_continuous_scale=px.colors.sequential.Reds,
        text=area_time['Duração (horas)'].round(1).astype(str) + 'h'
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title="Duração (horas)"),
        yaxis=dict(title="Área Responsável"),
        height=400,
        coloraxis_showscale=False,
    )
    
    return fig

def create_downtime_by_day(df):
    """
    Create a bar chart showing downtime distribution by days of the week.
    
    Args:
        df: Processed pandas DataFrame
    
    Returns:
        Plotly figure object
    """
    if 'Dia_Semana' not in df.columns or len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para gerar o gráfico",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Distribuição de Paradas por Dia da Semana",
            height=400,
        )
        return fig
    
    # Group by day of week and sum durations
    day_data = df.groupby('Dia_Semana')['Duração'].sum().reset_index()
    
    # Convert timedelta to hours
    day_data['Duração (horas)'] = day_data['Duração'].apply(lambda x: x.total_seconds() / 3600)
    
    # Map numeric days to day names in Portuguese
    day_data['Dia da Semana'] = day_data['Dia_Semana'].map(dias_semana_pt)
    
    # Sort by day of week (0=Monday to 6=Sunday)
    day_data = day_data.sort_values('Dia_Semana')
    
    # Create figure
    fig = px.bar(
        day_data,
        x='Dia da Semana',
        y='Duração (horas)',
        title="Distribuição de Paradas por Dia da Semana",
        color='Duração (horas)',
        color_continuous_scale=px.colors.sequential.Blues,
        text=day_data['Duração (horas)'].round(1).astype(str) + 'h'
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title="Dia da Semana", categoryorder='array', 
                  categoryarray=[dias_semana_pt[i] for i in range(7)]),
        yaxis=dict(title="Duração Total (horas)"),
        height=400,
        coloraxis_showscale=False,
    )
    
    return fig

def create_downtime_by_hour(df):
    """
    Create a line chart showing accumulation of downtime hours by hour in the day.
    
    Args:
        df: Processed pandas DataFrame
    
    Returns:
        Plotly figure object
    """
    if 'Hora_Dia' not in df.columns or len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para gerar o gráfico",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Acumulação de Horas de Parada por Hora do Dia",
            height=400,
        )
        return fig
    
    # Group by hour of day and sum durations
    hour_data = df.groupby('Hora_Dia')['Duração'].sum().reset_index()
    
    # Convert timedelta to hours
    hour_data['Duração (horas)'] = hour_data['Duração'].apply(lambda x: x.total_seconds() / 3600)
    
    # Make sure all 24 hours are represented
    all_hours = pd.DataFrame({'Hora_Dia': range(24)})
    hour_data = pd.merge(all_hours, hour_data, on='Hora_Dia', how='left').fillna(0)
    
    # Sort by hour
    hour_data = hour_data.sort_values('Hora_Dia')
    
    # Format hour labels (0-23)
    hour_data['Hora'] = hour_data['Hora_Dia'].apply(lambda x: f"{int(x)}:00")
    
    # Create figure
    fig = go.Figure()
    
    # Add line and area
    fig.add_trace(go.Scatter(
        x=hour_data['Hora'],
        y=hour_data['Duração (horas)'],
        mode='lines+markers',
        name='Duração (horas)',
        line=dict(color='#9b59b6', width=3),
        marker=dict(color='#9b59b6', size=8),
        fill='tozeroy',
        fillcolor='rgba(155, 89, 182, 0.2)'
    ))
    
    # Add data point labels
    fig.add_trace(go.Scatter(
        x=hour_data['Hora'],
        y=hour_data['Duração (horas)'],
        mode='text',
        text=hour_data['Duração (horas)'].round(1).astype(str),
        textposition='top center',
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title="Acumulação de Horas de Parada por Hora do Dia",
        xaxis=dict(
            title="Hora do Dia",
            tickmode='array',
            tickvals=hour_data['Hora'],
            ticktext=hour_data['Hora'],
            tickangle=45
        ),
        yaxis=dict(title="Duração Total (horas)"),
        height=400,
        showlegend=False,
    )
    
    return fig