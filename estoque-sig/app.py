import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Controle de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
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
if 'df_novas' not in st.session_state:
    # Dados da tabela "novas"
    st.session_state.df_novas = pd.DataFrame({
        'codigo': [888443216, 888443206, 860144291, 829341254, 870135114, 888489147, 888487020, 
                   870110216, 888487023, 888489008, 860604041, 861590054, 860144031, 829228753,
                   860123728, 870145770, 870110110, 888316221, 860123552, 860123870, 877744152,
                   850144502, 940212331, 888308765, 888314728, 870180061, 888317803, 888443215,
                   829300605, 888443205, 860123553, 888306715, 860144710, 829228817, 888306713,
                   829341253, 888351027, 888316036, 888316009, 870123411, 860198377],
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
                      'O-RING 24,77X5,33', 'BATERIA S7-400 SPEKTRUM'],
        'qtd': [3, 3, 17, 2, 1, 6, 9, 4, 8, 12, 24, 1, 5, 2, 1, 1, 4, 6, 1, 1, 8, 8, 4, 4, 1, 2,
                4, 1, 1, 1, 3, 3, 14, 5, 4, 2, 2, 1, 1, 1, 2],
        'custo_unitario': [233.09, 287.19, 1243.55, 2400.17, 1045.95, 20.36, 36.73, 26.16, 66.78,
                           42.62, 78.98, 5154.86, 37.83, 14.99, 213.06, 14941.33, 10089.93, 23.39,
                           5.09, 87.74, 1167.65, 993.46, 2980.39, 0.47, 5.52, 154.22, 0.21, 201.63,
                           1431.05, 174.84, 39.89, 0.89, 64.36, 28.37, 0.21, 1744.2, 115.78, 44.82,
                           1.91, 70.25, 191.87],
        'total_r_estoque': [699.27, 861.57, 21140.35, 4800.34, 1045.95, 122.16, 330.57, 104.64,
                            534.24, 511.44, 1895.52, 5154.86, 189.15, 29.98, 213.06, 14941.33,
                            40359.72, 140.34, 5.09, 87.74, 9341.2, 7947.68, 11921.56, 1.88, 5.52,
                            308.44, 0.84, 201.63, 1431.05, 174.84, 119.67, 2.67, 901.04, 141.85,
                            0.84, 3488.4, 231.56, 44.82, 1.91, 70.25, 383.74]
    })

if 'df_usadas' not in st.session_state:
    # Dados da tabela "usadas"
    st.session_state.df_usadas = pd.DataFrame({
        'codigo': [829286002, 829285188, 829284605, 829247981, 829340874, 829213085, 829248898,
                   829247920, 870123419],
        'descricao': ['BORRACHA', 'TAÇA DE ASPIRAÇÃO', 'RODA DENTADA Z=24 D=25X25', 'CILINDRO PNEUMÁTICO',
                      'SILENCIADOR', 'MOLA DE PRESSÃO', 'POLIA DE DESVIO',
                      'TAPETE TRANSPORTADOR B=400MM L=3950MM', 'FOLE DE PASSAGEM'],
        'qtd': [1, 4, 7, 2, 1, 2, 3, 0, 5],  # Convertendo string para int, 0 para vazio
        'custo_unitario': [112.12, 196.04, 283.03, 728.9, 456.67, 112.12, 9513.96, 0, 6814.81],
        'total_r_estoque': [112.12, 784.16, 1981.21, 1457.8, 456.67, 224.24, 28541.88, 0, 34074.05]
    })

if 'historico_movimentacoes' not in st.session_state:
    st.session_state.historico_movimentacoes = []

# Funções auxiliares
def buscar_peca_por_codigo(codigo, tipo='ambas'):
    """Busca uma peça pelo código em uma ou ambas as tabelas"""
    resultado = None
    tabela_origem = None
    
    try:
        codigo = int(codigo)
    except:
        return None, None
    
    if tipo in ['novas', 'ambas']:
        mask = st.session_state.df_novas['codigo'] == codigo
        if mask.any():
            resultado = st.session_state.df_novas[mask].iloc[0]
            tabela_origem = 'novas'
    
    if tipo in ['usadas', 'ambas'] and resultado is None:
        mask = st.session_state.df_usadas['codigo'] == codigo
        if mask.any():
            resultado = st.session_state.df_usadas[mask].iloc[0]
            tabela_origem = 'usadas'
    
    return resultado, tabela_origem

def registrar_movimentacao(tipo, codigo, descricao, quantidade, tabela):
    """Registra uma movimentação no histórico"""
    movimentacao = {
        'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'tipo': tipo,
        'codigo': codigo,
        'descricao': descricao,
        'quantidade': quantidade,
        'tabela': tabela
    }
    st.session_state.historico_movimentacoes.append(movimentacao)

def calcular_metricas():
    """Calcula métricas gerais do estoque"""
    # Combinar dados de ambas as tabelas
    df_total = pd.concat([st.session_state.df_novas, st.session_state.df_usadas], ignore_index=True)
    
    total_pecas = df_total['qtd'].sum()
    valor_total = df_total['total_r_estoque'].sum()
    tipos_diferentes = len(df_total)
    
    # Peças com estoque baixo (menos de 5 unidades)
    pecas_estoque_baixo = len(df_total[df_total['qtd'] < 5])
    
    return total_pecas, valor_total, tipos_diferentes, pecas_estoque_baixo

# Interface principal
st.markdown('<h1 class="main-header">📦 Sistema de Controle de Estoque</h1>', unsafe_allow_html=True)

# Métricas no topo
col1, col2, col3, col4 = st.columns(4)
total_pecas, valor_total, tipos_diferentes, pecas_estoque_baixo = calcular_metricas()

with col1:
    st.metric("Total de Peças", f"{int(total_pecas):,}".replace(',', '.'))
with col2:
    st.metric("Valor Total", f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
with col3:
    st.metric("Tipos Diferentes", tipos_diferentes)
with col4:
    st.metric("Estoque Baixo", pecas_estoque_baixo, delta_color="inverse")

st.divider()

# Tabs principais
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Visualizar Estoque", 
    "🔍 Buscar Peça", 
    "➕ Cadastrar Nova Peça",
    "📤 Registrar Saída", 
    "📊 Análise ABC", 
    "📜 Histórico"
])

# Tab 1: Visualizar Estoque
with tab1:
    st.subheader("📋 Estoque Atual")
    
    tipo_visualizacao = st.radio(
        "Selecione o tipo de peças:",
        ["Peças Novas", "Peças Usadas", "Todas as Peças"],
        horizontal=True
    )
    
    if tipo_visualizacao == "Peças Novas":
        df_exibir = st.session_state.df_novas.copy()
    elif tipo_visualizacao == "Peças Usadas":
        df_exibir = st.session_state.df_usadas.copy()
    else:
        df_novas_temp = st.session_state.df_novas.copy()
        df_usadas_temp = st.session_state.df_usadas.copy()
        df_novas_temp['tipo'] = 'Nova'
        df_usadas_temp['tipo'] = 'Usada'
        df_exibir = pd.concat([df_novas_temp, df_usadas_temp], ignore_index=True)
    
    # Filtros
    col1, col2 = st.columns([3, 1])
    with col1:
        filtro_descricao = st.text_input("Filtrar por descrição:", placeholder="Digite parte da descrição...")
    with col2:
        filtro_estoque_baixo = st.checkbox("Apenas estoque baixo (<5)")
    
    if filtro_descricao:
        df_exibir = df_exibir[df_exibir['descricao'].str.contains(filtro_descricao, case=False, na=False)]
    
    if filtro_estoque_baixo:
        df_exibir = df_exibir[df_exibir['qtd'] < 5]
    
    # Formatação para exibição
    df_display = df_exibir.copy()
    df_display['custo_unitario'] = df_display['custo_unitario'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    df_display['total_r_estoque'] = df_display['total_r_estoque'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "codigo": st.column_config.NumberColumn("Código", format="%d"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "qtd": st.column_config.NumberColumn("Quantidade", format="%d"),
            "custo_unitario": st.column_config.TextColumn("Custo Unitário"),
            "total_r_estoque": st.column_config.TextColumn("Total em Estoque"),
            "tipo": st.column_config.TextColumn("Tipo")
        }
    )
    
    # Gráfico de distribuição
    if len(df_exibir) > 0:
        st.subheader("📊 Distribuição do Valor em Estoque")
        df_top10 = df_exibir.nlargest(10, 'total_r_estoque')
        
        fig = px.bar(
            df_top10,
            x='descricao',
            y='total_r_estoque',
            title="Top 10 Peças por Valor em Estoque",
            labels={'descricao': 'Descrição', 'total_r_estoque': 'Valor Total (R$)'},
            color='total_r_estoque',
            color_continuous_scale='blues'
        )
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Buscar Peça
with tab2:
    st.subheader("🔍 Buscar Peça por Código")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        codigo_busca = st.text_input("Digite o código da peça:", placeholder="Ex: 888443216")
    with col2:
        tipo_busca = st.selectbox("Buscar em:", ["Ambas as tabelas", "Apenas novas", "Apenas usadas"])
    
    if st.button("🔍 Buscar", type="primary"):
        if codigo_busca:
            tipo_param = 'ambas' if tipo_busca == "Ambas as tabelas" else ('novas' if tipo_busca == "Apenas novas" else 'usadas')
            peca, tabela = buscar_peca_por_codigo(codigo_busca, tipo_param)
            
            if peca is not None:
                st.success(f"✅ Peça encontrada na tabela de peças {tabela}!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Código", int(peca['codigo']))
                    st.metric("Descrição", peca['descricao'])
                with col2:
                    st.metric("Quantidade", int(peca['qtd']))
                    st.metric("Tipo", tabela.capitalize())
                with col3:
                    st.metric("Custo Unitário", f"R$ {peca['custo_unitario']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                    st.metric("Total em Estoque", f"R$ {peca['total_r_estoque']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            else:
                st.error("❌ Peça não encontrada!")
        else:
            st.warning("⚠️ Por favor, digite um código para buscar.")

# Tab 3: Cadastrar Nova Peça
with tab3:
    st.subheader("➕ Cadastrar Nova Peça")
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_peca = st.selectbox("Tipo de Peça:", ["Nova", "Usada"])
            codigo = st.number_input("Código:", min_value=1, step=1)
            descricao = st.text_input("Descrição:", placeholder="Digite a descrição da peça")
        
        with col2:
            quantidade = st.number_input("Quantidade:", min_value=0, step=1)
            custo_unitario = st.number_input("Custo Unitário (R$):", min_value=0.0, step=0.01, format="%.2f")
        
        submitted = st.form_submit_button("💾 Cadastrar Peça", type="primary")
        
        if submitted:
            if codigo and descricao:
                # Verificar se o código já existe
                peca_existente, _ = buscar_peca_por_codigo(codigo)
                
                if peca_existente is not None:
                    st.error("❌ Já existe uma peça com este código!")
                else:
                    # Calcular total
                    total = quantidade * custo_unitario
                    
                    # Adicionar à tabela apropriada
                    nova_peca = pd.DataFrame({
                        'codigo': [codigo],
                        'descricao': [descricao],
                        'qtd': [quantidade],
                        'custo_unitario': [custo_unitario],
                        'total_r_estoque': [total]
                    })
                    
                    if tipo_peca == "Nova":
                        st.session_state.df_novas = pd.concat([st.session_state.df_novas, nova_peca], ignore_index=True)
                        tabela = "novas"
                    else:
                        st.session_state.df_usadas = pd.concat([st.session_state.df_usadas, nova_peca], ignore_index=True)
                        tabela = "usadas"
                    
                    registrar_movimentacao("Cadastro", codigo, descricao, quantidade, tabela)
                    st.success(f"✅ Peça cadastrada com sucesso na tabela de peças {tabela}!")
                    st.balloons()
            else:
                st.error("❌ Por favor, preencha todos os campos obrigatórios!")

# Tab 4: Registrar Saída
with tab4:
    st.subheader("📤 Registrar Saída de Estoque")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        codigo_saida = st.text_input("Código da peça:", placeholder="Digite o código da peça")
    with col2:
        if st.button("🔍 Verificar Peça"):
            if codigo_saida:
                peca, tabela = buscar_peca_por_codigo(codigo_saida)
                if peca is not None:
                    st.session_state['peca_saida'] = peca
                    st.session_state['tabela_saida'] = tabela
                else:
                    st.error("❌ Peça não encontrada!")
                    if 'peca_saida' in st.session_state:
                        del st.session_state['peca_saida']
    
    if 'peca_saida' in st.session_state:
        peca = st.session_state['peca_saida']
        tabela = st.session_state['tabela_saida']
        
        st.info(f"📦 **{peca['descricao']}** - Estoque atual: {int(peca['qtd'])} unidades")
        
        with st.form("form_saida"):
            quantidade_saida = st.number_input(
                "Quantidade a retirar:",
                min_value=1,
                max_value=int(peca['qtd']),
                step=1
            )
            
            motivo = st.text_area("Motivo da saída:", placeholder="Descreva o motivo da retirada...")
            
            submitted = st.form_submit_button("📤 Registrar Saída", type="primary")
            
            if submitted:
                # Atualizar o estoque
                if tabela == 'novas':
                    idx = st.session_state.df_novas[st.session_state.df_novas['codigo'] == peca['codigo']].index[0]
                    st.session_state.df_novas.loc[idx, 'qtd'] -= quantidade_saida
                    nova_qtd = st.session_state.df_novas.loc[idx, 'qtd']
                    custo_unit = st.session_state.df_novas.loc[idx, 'custo_unitario']
                    st.session_state.df_novas.loc[idx, 'total_r_estoque'] = nova_qtd * custo_unit
                else:
                    idx = st.session_state.df_usadas[st.session_state.df_usadas['codigo'] == peca['codigo']].index[0]
                    st.session_state.df_usadas.loc[idx, 'qtd'] -= quantidade_saida
                    nova_qtd = st.session_state.df_usadas.loc[idx, 'qtd']
                    custo_unit = st.session_state.df_usadas.loc[idx, 'custo_unitario']
                    st.session_state.df_usadas.loc[idx, 'total_r_estoque'] = nova_qtd * custo_unit
                
                registrar_movimentacao("Saída", peca['codigo'], peca['descricao'], quantidade_saida, tabela)
                st.success(f"✅ Saída registrada com sucesso! Novo estoque: {nova_qtd} unidades")
                del st.session_state['peca_saida']
                del st.session_state['tabela_saida']
                st.rerun()

# Tab 5: Análise ABC
with tab5:
    st.subheader("📊 Análise ABC do Estoque")
    
    # Combinar dados
    df_abc = pd.concat([st.session_state.df_novas, st.session_state.df_usadas], ignore_index=True)
    df_abc = df_abc.sort_values('total_r_estoque', ascending=False)
    
    # Calcular percentuais
    df_abc['percentual'] = (df_abc['total_r_estoque'] / df_abc['total_r_estoque'].sum()) * 100
    df_abc['percentual_acumulado'] = df_abc['percentual'].cumsum()
    
    # Classificar ABC
    df_abc['classificacao'] = pd.cut(
        df_abc['percentual_acumulado'],
        bins=[0, 80, 95, 100],
        labels=['A', 'B', 'C']
    )
    
    # Métricas ABC
    col1, col2, col3 = st.columns(3)
    
    with col1:
        classe_a = df_abc[df_abc['classificacao'] == 'A']
        st.metric(
            "Classe A",
            f"{len(classe_a)} itens",
            f"{classe_a['total_r_estoque'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
    
    with col2:
        classe_b = df_abc[df_abc['classificacao'] == 'B']
        st.metric(
            "Classe B",
            f"{len(classe_b)} itens",
            f"{classe_b['total_r_estoque'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
    
    with col3:
        classe_c = df_abc[df_abc['classificacao'] == 'C']
        st.metric(
            "Classe C",
            f"{len(classe_c)} itens",
            f"{classe_c['total_r_estoque'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
    
    # Gráfico de Pareto
    fig = go.Figure()
    
    # Barras
    fig.add_trace(go.Bar(
        x=list(range(len(df_abc))),
        y=df_abc['total_r_estoque'],
        name='Valor em Estoque',
        marker_color=['red' if c == 'A' else 'yellow' if c == 'B' else 'green' for c in df_abc['classificacao']]
    ))
    
    # Linha de percentual acumulado
    fig.add_trace(go.Scatter(
        x=list(range(len(df_abc))),
        y=df_abc['percentual_acumulado'],
        name='% Acumulado',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='black', width=2)
    ))
    
    fig.update_layout(
        title='Curva ABC - Análise de Pareto',
        xaxis=dict(title='Produtos', showticklabels=False),
        yaxis=dict(title='Valor em Estoque (R$)'),
        yaxis2=dict(title='Percentual Acumulado (%)', overlaying='y', side='right', range=[0, 100]),
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumida
    st.subheader("📋 Detalhamento por Classe")
    
    classe_selecionada = st.selectbox("Selecione a classe:", ["A", "B", "C"])
    df_classe = df_abc[df_abc['classificacao'] == classe_selecionada][['codigo', 'descricao', 'qtd', 'total_r_estoque', 'percentual']]
    
    df_classe_display = df_classe.copy()
    df_classe_display['total_r_estoque'] = df_classe_display['total_r_estoque'].apply(
        lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
    df_classe_display['percentual'] = df_classe_display['percentual'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(df_classe_display, use_container_width=True, hide_index=True)

# Tab 6: Histórico
with tab6:
    st.subheader("📜 Histórico de Movimentações")
    
    if st.session_state.historico_movimentacoes:
        df_historico = pd.DataFrame(st.session_state.historico_movimentacoes)
        
        # Filtros
        col1, col2 = st.columns([1, 1])
        with col1:
            tipo_filtro = st.multiselect(
                "Tipo de movimentação:",
                options=df_historico['tipo'].unique(),
                default=df_historico['tipo'].unique()
            )
        with col2:
            tabela_filtro = st.multiselect(
                "Tabela:",
                options=df_historico['tabela'].unique(),
                default=df_historico['tabela'].unique()
            )
        
        # Aplicar filtros
        df_filtrado = df_historico[
            (df_historico['tipo'].isin(tipo_filtro)) &
            (df_historico['tabela'].isin(tabela_filtro))
        ]
        
        # Exibir histórico
        st.dataframe(
            df_filtrado.sort_values('data', ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "data": st.column_config.TextColumn("Data/Hora"),
                "tipo": st.column_config.TextColumn("Tipo"),
                "codigo": st.column_config.NumberColumn("Código", format="%d"),
                "descricao": st.column_config.TextColumn("Descrição"),
                "quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
                "tabela": st.column_config.TextColumn("Tabela")
            }
        )
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico", type="secondary"):
            st.session_state.historico_movimentacoes = []
            st.rerun()
    else:
        st.info("📭 Nenhuma movimentação registrada ainda.")

# Rodapé
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Sistema de Controle de Estoque v2.0 | Desenvolvido com Streamlit 📦</p>
    </div>
    """,
    unsafe_allow_html=True
)
