import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do session state
if 'df_estoque' not in st.session_state:
    # Dados da planilha
    data = {
        'codigo': [888443216, 888443206, 860144291, 829341254, 870135114, 888489147, 888487020, 
                   870110216, 888487023, 888489008, 860604041, 861590054, 860144031, 829228753, 
                   860123728, 870145770, 870110110, 888316221, 860123552, 860123870, 877744152, 
                   850144502, 940212331, 888308765, 888314728, 870180061, 888317803, 888443215, 
                   829300605, 888443205, 860123553, 888306715, 860144710, 829228817, 888306713, 
                   829341253, 888351027, 888316036, 888316009, 870123411, 860198377, 829286002, 
                   829285188, 829284605, 829247981, 829340874, 829213085, 829248898, 829247920, 
                   870123419],
        'descricao': ['CABEÇA ARTICULADA 16XM16LH', 'CABEÇA ARTICULADA 16XM16', 'VÁLVULA PILOTO 500MM', 
                      'CORREIA DENTADA', 'POLIA DE DESVIO', 'TUBO DE PLÁSTICO 8X1 -PA 11 W-GN', 
                      'UNIÃO ANGULAR C8X1/8', 'ANILHA DE BORRACHA', 'UNIÃO ANGULAR', 
                      'TUBO DE PLÁSTICO 6X1', 'EXAUSTOR CB6 FA. ACLA', 'JGO. PEÇAS DESGASTE FUER 861590053', 
                      'SILENCIADOR G 1-8', 'ANEL DE RETENÇÃO', 'ENCAIXE DO FILTRO 55X4; 90-110', 
                      'BIGORNA CFA112 RS COMPLETE', 'CILINDRO', 'ANEL DE RETENÇÃO', 'O-RING 6X1,5 - NBR', 
                      'O-RING ASSÉPTICO 152 X 5', 'VÁLV. DISTRIB. 5/2 V581-ISO1', 
                      'CORPO DA VÁLVULA 5-2MONOSTABLE VDMA01', 'CORPO DA VÁLVULA 5-3 GESCHL. VDMA01', 
                      'ARRUELA DE PRESSÃO B10', 'PINO CILÍNDRICO 4X16', 'ROLO CASTER ROLL.501RL2CG', 
                      'DISCO A 5,3-X12', 'CABEÇA ARTICULADA 10XM10LH', 'FACA', 'CABEÇA ARTICULADA 10XM10', 
                      'O-RING 16X3 - EPDM', 'PORCA SEXTAVADA M10-A2', 'SILENCIADOR G 3-8', 
                      'ANEL DE RETENÇÃO', 'PORCA SEXTAVADA M6-A2', 'ROLAMENTO DE ESFERA', 
                      'ROLAMENTO DE ESFERAS ESTRIADA 6302-2RS1', 'ANEL DE RETENÇÃO', 'ANEL DE RETENÇÃO', 
                      'O-RING 24,77X5,33', 'BATERIA S7-400 SPEKTRUM', 'BORRACHA', 'TAÇA DE ASPIRAÇÃO', 
                      'RODA DENTADA Z=24 D=25X25', 'CILINDRO PNEUMÁTICO', 'SILENCIADOR', 'MOLA DE PRESSÃO', 
                      'POLIA DE DESVIO', 'TAPETE TRANSPORTADOR B=400MM L=3950MM', 'FOLE DE PASSAGEM'],
        'qtd': [3, 3, 17, 2, 1, 6, 9, 4, 8, 12, 24, 1, 5, 2, 1, 1, 4, 6, 1, 1, 8, 8, 4, 4, 1, 
                2, 4, 1, 1, 1, 3, 3, 14, 5, 4, 2, 2, 1, 1, 1, 2, 1, 4, 7, 2, 1, 2, 3, 0, 5],
        'custo_unitario': [233.09, 287.19, 1243.55, 2400.17, 1045.95, 20.36, 36.73, 26.16, 66.78, 
                           42.62, 78.98, 5154.86, 37.83, 14.99, 213.06, 14941.33, 10089.93, 23.39, 
                           5.09, 87.74, 1167.65, 993.46, 2980.39, 0.47, 5.52, 154.22, 0.21, 201.63, 
                           1431.05, 174.84, 39.89, 0.89, 64.36, 28.37, 0.21, 1744.2, 115.78, 44.82, 
                           1.91, 70.25, 191.87, 112.12, 196.04, 283.03, 728.9, 456.67, 112.12, 
                           9513.96, 0, 6814.81],
        'total_r_estoque': [699.27, 861.57, 21140.35, 4800.34, 1045.95, 122.16, 330.57, 104.64, 
                            534.24, 511.44, 1895.52, 5154.86, 189.15, 29.98, 213.06, 14941.33, 
                            40359.72, 140.34, 5.09, 87.74, 9341.2, 7947.68, 11921.56, 1.88, 5.52, 
                            308.44, 0.84, 201.63, 1431.05, 174.84, 119.67, 2.67, 901.04, 141.85, 
                            0.84, 3488.4, 231.56, 44.82, 1.91, 70.25, 383.74, 112.12, 784.16, 
                            1981.21, 1457.8, 456.67, 224.24, 28541.88, 0, 34074.05]
    }
    
    st.session_state.df_estoque = pd.DataFrame(data)

# Título principal
st.markdown('<h1 class="main-header">📦 Sistema de Gestão de Estoque</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Filtros
    st.subheader("🔍 Filtros")
    
    # Filtro por descrição
    descricoes = ['Todos'] + sorted(st.session_state.df_estoque['descricao'].unique().tolist())
    descricao_selecionada = st.selectbox("Descrição do Produto", descricoes)
    
    # Filtro por faixa de quantidade
    qtd_min, qtd_max = st.slider(
        "Faixa de Quantidade",
        min_value=0,
        max_value=int(st.session_state.df_estoque['qtd'].max()),
        value=(0, int(st.session_state.df_estoque['qtd'].max()))
    )
    
    # Filtro por faixa de valor
    valor_min, valor_max = st.slider(
        "Faixa de Valor Total (R$)",
        min_value=0.0,
        max_value=float(st.session_state.df_estoque['total_r_estoque'].max()),
        value=(0.0, float(st.session_state.df_estoque['total_r_estoque'].max())),
        format="R$ %.2f"
    )

# Aplicar filtros
df_filtrado = st.session_state.df_estoque.copy()

if descricao_selecionada != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['descricao'] == descricao_selecionada]

df_filtrado = df_filtrado[
    (df_filtrado['qtd'] >= qtd_min) & 
    (df_filtrado['qtd'] <= qtd_max) &
    (df_filtrado['total_r_estoque'] >= valor_min) & 
    (df_filtrado['total_r_estoque'] <= valor_max)
]

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total de Produtos",
        f"{len(df_filtrado):,}",
        delta=f"{len(df_filtrado) - len(st.session_state.df_estoque)} filtrados"
    )

with col2:
    st.metric(
        "Valor Total em Estoque",
        f"R$ {df_filtrado['total_r_estoque'].sum():,.2f}"
    )

with col3:
    st.metric(
        "Quantidade Total",
        f"{df_filtrado['qtd'].sum():,}"
    )

with col4:
    st.metric(
        "Ticket Médio",
        f"R$ {df_filtrado['custo_unitario'].mean():,.2f}"
    )

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📋 Gestão de Produtos", "📈 Análises", "⚠️ Alertas"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 produtos por valor
        top_produtos = df_filtrado.nlargest(10, 'total_r_estoque')
        fig_top = px.bar(
            top_produtos,
            x='total_r_estoque',
            y='descricao',
            orientation='h',
            title='Top 10 Produtos por Valor em Estoque',
            labels={'total_r_estoque': 'Valor Total (R$)', 'descricao': 'Produto'},
            color='total_r_estoque',
            color_continuous_scale='Blues'
        )
        fig_top.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        # Distribuição de valores
        fig_dist = px.pie(
            df_filtrado.nlargest(10, 'total_r_estoque'),
            values='total_r_estoque',
            names='descricao',
            title='Distribuição do Valor em Estoque (Top 10)'
        )
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Análise de Pareto
    st.subheader("📊 Análise de Pareto (Curva ABC)")
    
    # Preparar dados para Pareto
    df_pareto = df_filtrado.sort_values('total_r_estoque', ascending=False).copy()
    df_pareto['percentual_valor'] = (df_pareto['total_r_estoque'] / df_pareto['total_r_estoque'].sum()) * 100
    df_pareto['percentual_acumulado'] = df_pareto['percentual_valor'].cumsum()
    df_pareto['percentual_itens'] = (range(1, len(df_pareto) + 1) / len(df_pareto)) * 100
    
    # Classificação ABC
    df_pareto['classificacao'] = pd.cut(
        df_pareto['percentual_acumulado'],
        bins=[0, 80, 95, 100],
        labels=['A', 'B', 'C']
    )
    
    # Gráfico de Pareto
    fig_pareto = go.Figure()
    
    fig_pareto.add_trace(go.Bar(
        x=df_pareto.index,
        y=df_pareto['percentual_valor'],
        name='% do Valor',
        yaxis='y',
        marker_color='lightblue'
    ))
    
    fig_pareto.add_trace(go.Scatter(
        x=df_pareto.index,
        y=df_pareto['percentual_acumulado'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color='red', width=2)
    ))
    
    fig_pareto.update_layout(
        title='Curva ABC - Análise de Pareto',
        xaxis=dict(title='Produtos'),
        yaxis=dict(title='% do Valor Total', side='left'),
        yaxis2=dict(title='% Acumulado', overlaying='y', side='right'),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    # Resumo ABC
    col1, col2, col3 = st.columns(3)
    
    for col, classe in zip([col1, col2, col3], ['A', 'B', 'C']):
        with col:
            classe_df = df_pareto[df_pareto['classificacao'] == classe]
            st.metric(
                f"Classe {classe}",
                f"{len(classe_df)} produtos",
                f"R$ {classe_df['total_r_estoque'].sum():,.2f}"
            )

with tab2:
    st.subheader("📋 Tabela de Produtos")
    
    # Opções de visualização
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        ordenar_por = st.selectbox(
            "Ordenar por",
            ['codigo', 'descricao', 'qtd', 'custo_unitario', 'total_r_estoque']
        )
    
    with col2:
        ordem = st.radio("Ordem", ['Crescente', 'Decrescente'], horizontal=True)
    
    with col3:
        mostrar_zeros = st.checkbox("Mostrar produtos zerados", value=True)
    
    # Aplicar ordenação
    df_tabela = df_filtrado.copy()
    if not mostrar_zeros:
        df_tabela = df_tabela[df_tabela['qtd'] > 0]
    
    df_tabela = df_tabela.sort_values(ordenar_por, ascending=(ordem == 'Crescente'))
    
    # Formatar valores para exibição
    df_display = df_tabela.copy()
    df_display['custo_unitario'] = df_display['custo_unitario'].apply(lambda x: f"R$ {x:,.2f}")
    df_display['total_r_estoque'] = df_display['total_r_estoque'].apply(lambda x: f"R$ {x:,.2f}")
    
    # Exibir tabela
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        column_config={
            "codigo": st.column_config.NumberColumn("Código", format="%d"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "qtd": st.column_config.NumberColumn("Quantidade", format="%d"),
            "custo_unitario": "Custo Unitário",
            "total_r_estoque": "Total em Estoque"
        }
    )
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Atualizar Estoque", use_container_width=True):
            st.info("Funcionalidade de atualização em desenvolvimento")
    
    with col2:
        if st.button("➕ Adicionar Produto", use_container_width=True):
            st.info("Funcionalidade de adição em desenvolvimento")
    
    with col3:
        # Exportar para Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_tabela.to_excel(writer, sheet_name='Estoque', index=False)
        
        st.download_button(
            label="📥 Exportar Excel",
            data=buffer.getvalue(),
            file_name=f"estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with tab3:
    st.subheader("📈 Análises Avançadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Análise de correlação
        st.subheader("🔗 Correlação entre Variáveis")
        
        df_corr = df_filtrado[['qtd', 'custo_unitario', 'total_r_estoque']].corr()
        
        fig_corr = px.imshow(
            df_corr,
            labels=dict(x="Variável", y="Variável", color="Correlação"),
            x=['Quantidade', 'Custo Unitário', 'Total Estoque'],
            y=['Quantidade', 'Custo Unitário', 'Total Estoque'],
            color_continuous_scale='RdBu',
            aspect="auto"
        )
        fig_corr.update_layout(height=400)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with col2:
        # Distribuição de quantidades
        st.subheader("📊 Distribuição de Quantidades")
        
        fig_hist = px.histogram(
            df_filtrado[df_filtrado['qtd'] > 0],
            x='qtd',
            nbins=20,
            title='Histograma de Quantidades em Estoque',
            labels={'qtd': 'Quantidade', 'count': 'Frequência'}
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Análise de outliers
    st.subheader("🎯 Análise de Outliers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_box1 = px.box(
            df_filtrado,
            y='custo_unitario',
            title='Box Plot - Custo Unitário',
            labels={'custo_unitario': 'Custo Unitário (R$)'}
        )
        fig_box1.update_layout(height=300)
        st.plotly_chart(fig_box1, use_container_width=True)
    
    with col2:
        fig_box2 = px.box(
            df_filtrado,
            y='total_r_estoque',
            title='Box Plot - Valor Total',
            labels={'total_r_estoque': 'Valor Total (R$)'}
        )
        fig_box2.update_layout(height=300)
        st.plotly_chart(fig_box2, use_container_width=True)

with tab4:
    st.subheader("⚠️ Alertas e Notificações")
    
    # Produtos com estoque zero
    produtos_zerados = df_filtrado[df_filtrado['qtd'] == 0]
    if not produtos_zerados.empty:
        st.error(f"🚨 {len(produtos_zerados)} produto(s) com estoque zerado!")
        with st.expander("Ver produtos zerados"):
            st.dataframe(
                produtos_zerados[['codigo', 'descricao', 'custo_unitario']],
                use_container_width=True
            )
    
    # Produtos de alto valor com baixo estoque
    st.warning("📌 Produtos de alto valor com estoque baixo")
    
    # Definir produtos de alto valor (top 20% por custo unitário)
    percentil_80 = df_filtrado['custo_unitario'].quantile(0.8)
    produtos_alto_valor = df_filtrado[
        (df_filtrado['custo_unitario'] >= percentil_80) & 
        (df_filtrado['qtd'] <= 5) &
        (df_filtrado['qtd'] > 0)
    ]
    
    if not produtos_alto_valor.empty:
        st.dataframe(
            produtos_alto_valor[['codigo', 'descricao', 'qtd', 'custo_unitario', 'total_r_estoque']],
            use_container_width=True
        )
    else:
        st.success("✅ Nenhum produto de alto valor com estoque crítico")
    
    # Resumo de alertas
    st.subheader("📊 Resumo de Alertas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        produtos_criticos = len(df_filtrado[df_filtrado['qtd'] <= 2])
        st.metric(
            "Estoque Crítico (≤ 2)",
            produtos_criticos,
            delta=f"{(produtos_criticos/len(df_filtrado)*100):.1f}% do total"
        )
    
    with col2:
        produtos_baixos = len(df_filtrado[(df_filtrado['qtd'] > 2) & (df_filtrado['qtd'] <= 5)])
        st.metric(
            "Estoque Baixo (3-5)",
            produtos_baixos,
            delta=f"{(produtos_baixos/len(df_filtrado)*100):.1f}% do total"
        )
    
    with col3:
        produtos_adequados = len(df_filtrado[df_filtrado['qtd'] > 5])
        st.metric(
            "Estoque Adequado (> 5)",
            produtos_adequados,
            delta=f"{(produtos_adequados/len(df_filtrado)*100):.1f}% do total"
        )

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray;'>Sistema de Gestão de Estoque v2.0 | "
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>",
    unsafe_allow_html=True
)
