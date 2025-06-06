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
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    h1 {
        color: #1f77b4;
        font-family: 'Arial', sans-serif;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #145a8b;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'historico_movimentacoes' not in st.session_state:
    st.session_state.historico_movimentacoes = []

# Funções auxiliares
def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def salvar_dados():
    """Salva os dados em um arquivo local"""
    if st.session_state.df is not None:
        # Salva o DataFrame
        st.session_state.df.to_csv('estoque_backup.csv', index=False)
        
        # Salva o histórico
        with open('historico_backup.json', 'w') as f:
            json.dump(st.session_state.historico_movimentacoes, f)

def carregar_dados_salvos():
    """Carrega dados salvos se existirem"""
    if os.path.exists('estoque_backup.csv'):
        st.session_state.df = pd.read_csv('estoque_backup.csv')
        
    if os.path.exists('historico_backup.json'):
        with open('historico_backup.json', 'r') as f:
            st.session_state.historico_movimentacoes = json.load(f)

def registrar_movimentacao(tipo, codigo_bm, descricao, quantidade, motivo=""):
    """Registra uma movimentação no histórico"""
    movimentacao = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "codigo_bm": codigo_bm,
        "descricao": descricao,
        "quantidade": quantidade,
        "motivo": motivo
    }
    st.session_state.historico_movimentacoes.append(movimentacao)
    salvar_dados()

# Título principal
st.title("📦 Sistema de Controle de Estoque")

# Sidebar para upload de arquivo
with st.sidebar:
    st.header("📤 Upload de Dados")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel",
        type=['xlsx', 'xls'],
        help="Faça upload do arquivo de estoque"
    )
    
    if uploaded_file is not None:
        try:
            st.session_state.df = pd.read_excel(uploaded_file)
            st.success("✅ Arquivo carregado com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
    
    # Tentar carregar dados salvos
    elif st.session_state.df is None:
        carregar_dados_salvos()
        if st.session_state.df is not None:
            st.info("📁 Dados anteriores carregados")

# Verifica se há dados carregados
if st.session_state.df is None:
    st.warning("⚠️ Por favor, faça upload do arquivo Excel na barra lateral.")
    st.stop()

# Preparar dados
df = st.session_state.df.copy()

# Criar abas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", 
    "📋 Estoque Atual", 
    "🔍 Buscar Peça",
    "➕ Cadastrar Peça",
    "➖ Registrar Saída",
    "📜 Histórico"
])

# Tab 1 - Dashboard
with tab1:
    st.subheader("📊 Visão Geral do Estoque")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_itens = len(df)
        st.metric("Total de Itens", f"{total_itens:,}".replace(",", "."))
    
    with col2:
        valor_total = df['TOTAL R$ ESTOQUE'].sum()
        st.metric("Valor Total", formatar_moeda(valor_total))
    
    with col3:
        qtd_total = df['QUANTIDADE'].sum()
        st.metric("Quantidade Total", f"{int(qtd_total):,}".replace(",", "."))
    
    with col4:
        valor_medio = valor_total / total_itens if total_itens > 0 else 0
        st.metric("Valor Médio/Item", formatar_moeda(valor_medio))
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 peças por valor
        top_pecas = df.nlargest(10, 'TOTAL R$ ESTOQUE')
        fig_top = px.bar(
            top_pecas, 
            x='TOTAL R$ ESTOQUE', 
            y='DESCRICAO DO MATERIAL',
            orientation='h',
            title='Top 10 Peças por Valor em Estoque',
            labels={'TOTAL R$ ESTOQUE': 'Valor Total (R$)', 'DESCRICAO DO MATERIAL': 'Descrição'}
        )
        fig_top.update_layout(height=400)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        # Análise ABC
        df_abc = df.sort_values('TOTAL R$ ESTOQUE', ascending=False).copy()
        df_abc['percentual_valor'] = (df_abc['TOTAL R$ ESTOQUE'] / df_abc['TOTAL R$ ESTOQUE'].sum() * 100)
        df_abc['percentual_acumulado'] = df_abc['percentual_valor'].cumsum()
        df_abc['percentual_itens'] = (np.arange(1, len(df_abc) + 1) / len(df_abc) * 100)
        
        # Classificação ABC
        df_abc['classificacao'] = pd.cut(
            df_abc['percentual_acumulado'],
            bins=[0, 80, 95, 100],
            labels=['A', 'B', 'C']
        )
        
        # Contagem por classe
        abc_count = df_abc['classificacao'].value_counts().sort_index()
        
        fig_abc = px.pie(
            values=abc_count.values,
            names=abc_count.index,
            title='Classificação ABC do Estoque',
            color_discrete_map={'A': '#ff4444', 'B': '#ffaa00', 'C': '#00aa00'}
        )
        fig_abc.update_layout(height=400)
        st.plotly_chart(fig_abc, use_container_width=True)
    
    # Curva ABC
    st.subheader("📈 Curva ABC - Análise de Pareto")
    
    fig_pareto = go.Figure()
    
    # Linha de valor acumulado
    fig_pareto.add_trace(go.Scatter(
        x=df_abc['percentual_itens'],
        y=df_abc['percentual_acumulado'],
        mode='lines',
        name='Valor Acumulado (%)',
        line=dict(color='blue', width=3)
    ))
    
    # Linhas de referência
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Classe A (80%)")
    fig_pareto.add_hline(y=95, line_dash="dash", line_color="orange", annotation_text="Classe B (95%)")
    
    fig_pareto.update_layout(
        title='Curva ABC - Percentual de Itens vs Valor Acumulado',
        xaxis_title='Percentual de Itens (%)',
        yaxis_title='Percentual do Valor Acumulado (%)',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig_pareto, use_container_width=True)

# Tab 2 - Estoque Atual
with tab2:
    st.subheader("📋 Listagem Completa do Estoque")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_descricao = st.text_input("🔍 Filtrar por Descrição", "")
    
    with col2:
        filtro_codigo = st.text_input("🔍 Filtrar por Código BM", "")
    
    with col3:
        min_valor = st.number_input("Valor Mínimo (R$)", min_value=0.0, value=0.0)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if filtro_descricao:
        df_filtrado = df_filtrado[df_filtrado['DESCRICAO DO MATERIAL'].str.contains(filtro_descricao, case=False, na=False)]
    
    if filtro_codigo:
        df_filtrado = df_filtrado[df_filtrado['CODIGO BM'].astype(str).str.contains(filtro_codigo, na=False)]
    
    if min_valor > 0:
        df_filtrado = df_filtrado[df_filtrado['TOTAL R$ ESTOQUE'] >= min_valor]
    
    # Exibir dados
    st.write(f"**Total de itens encontrados:** {len(df_filtrado)}")
    
    # Formatar colunas monetárias
    df_display = df_filtrado.copy()
    df_display['CUSTO UNIT'] = df_display['CUSTO UNIT'].apply(formatar_moeda)
    df_display['TOTAL R$ ESTOQUE'] = df_display['TOTAL R$ ESTOQUE'].apply(formatar_moeda)
    
    st.dataframe(df_display, use_container_width=True, height=600)
    
    # Download
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data=csv,
        file_name=f'estoque_filtrado_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

# Tab 3 - Buscar Peça
with tab3:
    st.subheader("🔍 Buscar Peça por Código")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        codigo_busca = st.text_input("Digite o Código BM da peça:", key="busca_codigo")
    
    with col2:
        st.write("")  # Espaçamento
        st.write("")  # Espaçamento
        buscar = st.button("🔍 Buscar", type="primary")
    
    if buscar and codigo_busca:
        # Buscar a peça
        peca = df[df['CODIGO BM'].astype(str) == str(codigo_busca)]
        
        if not peca.empty:
            st.success("✅ Peça encontrada!")
            
            # Exibir informações da peça
            peca_info = peca.iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📦 Informações da Peça")
                st.write(f"**Código BM:** {peca_info['CODIGO BM']}")
                st.write(f"**Descrição:** {peca_info['DESCRICAO DO MATERIAL']}")
                st.write(f"**Quantidade em Estoque:** {int(peca_info['QUANTIDADE'])}")
            
            with col2:
                st.markdown("### 💰 Valores")
                st.write(f"**Custo Unitário:** {formatar_moeda(peca_info['CUSTO UNIT'])}")
                st.write(f"**Valor Total:** {formatar_moeda(peca_info['TOTAL R$ ESTOQUE'])}")
            
            # Opções de ação
            st.markdown("---")
            st.markdown("### ⚡ Ações Rápidas")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➖ Registrar Saída", key=f"saida_{codigo_busca}"):
                    st.session_state['tab_selecionada'] = 4
                    st.session_state['codigo_preenchido'] = str(codigo_busca)
                    st.rerun()
            
            with col2:
                if st.button("📊 Ver Histórico", key=f"hist_{codigo_busca}"):
                    st.session_state['tab_selecionada'] = 5
                    st.session_state['filtro_historico'] = str(codigo_busca)
                    st.rerun()
        else:
            st.error(f"❌ Nenhuma peça encontrada com o código: {codigo_busca}")

# Tab 4 - Cadastrar Peça
with tab4:
    st.subheader("➕ Cadastrar Nova Peça")
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        
        with col1:
            novo_codigo = st.text_input("Código BM*", key="novo_codigo")
            nova_descricao = st.text_area("Descrição do Material*", key="nova_descricao", height=100)
            nova_quantidade = st.number_input("Quantidade*", min_value=0, value=0, key="nova_quantidade")
        
        with col2:
            novo_custo = st.number_input("Custo Unitário (R$)*", min_value=0.0, value=0.0, format="%.2f", key="novo_custo")
            st.write("")  # Espaçamento
            valor_total = nova_quantidade * novo_custo
            st.metric("Valor Total", formatar_moeda(valor_total))
        
        submitted = st.form_submit_button("✅ Cadastrar Peça", type="primary")
        
        if submitted:
            # Validações
            if not novo_codigo or not nova_descricao:
                st.error("❌ Preencha todos os campos obrigatórios!")
            elif novo_codigo in df['CODIGO BM'].astype(str).values:
                st.error(f"❌ Já existe uma peça com o código {novo_codigo}!")
            else:
                # Adicionar nova peça
                nova_peca = pd.DataFrame({
                    'CODIGO BM': [novo_codigo],
                    'DESCRICAO DO MATERIAL': [nova_descricao],
                    'QUANTIDADE': [nova_quantidade],
                    'CUSTO UNIT': [novo_custo],
                    'TOTAL R$ ESTOQUE': [valor_total]
                })
                
                st.session_state.df = pd.concat([st.session_state.df, nova_peca], ignore_index=True)
                
                # Registrar no histórico
                registrar_movimentacao(
                    tipo="ENTRADA",
                    codigo_bm=novo_codigo,
                    descricao=nova_descricao,
                    quantidade=nova_quantidade,
                    motivo="Cadastro inicial"
                )
                
                salvar_dados()
                st.success(f"✅ Peça {novo_codigo} cadastrada com sucesso!")
                st.rerun()

# Tab 5 - Registrar Saída
with tab5:
    st.subheader("➖ Registrar Saída de Estoque")
    
    # Verificar se há código preenchido
    codigo_preenchido = st.session_state.get('codigo_preenchido', '')
    
    with st.form("form_saida"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo_saida = st.text_input("Código BM da Peça*", value=codigo_preenchido, key="codigo_saida")
            
            # Buscar informações da peça
            if codigo_saida:
                peca = df[df['CODIGO BM'].astype(str) == str(codigo_saida)]
                if not peca.empty:
                    peca_info = peca.iloc[0]
                    st.info(f"📦 {peca_info['DESCRICAO DO MATERIAL']}")
                    st.write(f"**Estoque Atual:** {int(peca_info['QUANTIDADE'])} unidades")
                    max_qtd = int(peca_info['QUANTIDADE'])
                else:
                    st.warning("⚠️ Peça não encontrada")
                    max_qtd = 0
            else:
                max_qtd = 0
        
        with col2:
            qtd_saida = st.number_input("Quantidade a Retirar*", min_value=0, max_value=max_qtd, value=0, key="qtd_saida")
            motivo_saida = st.text_area("Motivo/Observações", key="motivo_saida", height=100)
        
        submitted = st.form_submit_button("📤 Registrar Saída", type="primary")
        
        if submitted:
            if not codigo_saida or qtd_saida == 0:
                st.error("❌ Preencha todos os campos obrigatórios!")
            elif codigo_saida not in df['CODIGO BM'].astype(str).values:
                st.error("❌ Código BM não encontrado!")
            else:
                # Atualizar quantidade
                idx = df[df['CODIGO BM'].astype(str) == str(codigo_saida)].index[0]
                df.loc[idx, 'QUANTIDADE'] -= qtd_saida
                df.loc[idx, 'TOTAL R$ ESTOQUE'] = df.loc[idx, 'QUANTIDADE'] * df.loc[idx, 'CUSTO UNIT']
                
                st.session_state.df = df
                
                # Registrar no histórico
                registrar_movimentacao(
                    tipo="SAÍDA",
                    codigo_bm=codigo_saida,
                    descricao=peca_info['DESCRICAO DO MATERIAL'],
                    quantidade=qtd_saida,
                    motivo=motivo_saida
                )
                
                salvar_dados()
                st.success(f"✅ Saída de {qtd_saida} unidades registrada com sucesso!")
                
                # Limpar código preenchido
                if 'codigo_preenchido' in st.session_state:
                    del st.session_state['codigo_preenchido']
                
                st.rerun()

# Tab 6 - Histórico
with tab6:
    st.subheader("📜 Histórico de Movimentações")
    
    if len(st.session_state.historico_movimentacoes) > 0:
        df_historico = pd.DataFrame(st.session_state.historico_movimentacoes)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_tipo = st.selectbox("Tipo de Movimentação", ["Todos", "ENTRADA", "SAÍDA"])
        
        with col2:
            filtro_codigo_hist = st.text_input("Filtrar por Código BM", value=st.session_state.get('filtro_historico', ''))
        
        with col3:
            ordem = st.selectbox("Ordenar por", ["Mais recente", "Mais antigo"])
        
        # Aplicar filtros
        df_hist_filtrado = df_historico.copy()
        
        if filtro_tipo != "Todos":
            df_hist_filtrado = df_hist_filtrado[df_hist_filtrado['tipo'] == filtro_tipo]
        
        if filtro_codigo_hist:
            df_hist_filtrado = df_hist_filtrado[df_hist_filtrado['codigo_bm'].astype(str).str.contains(filtro_codigo_hist, na=False)]
        
        # Ordenar
        df_hist_filtrado = df_hist_filtrado.sort_values('data', ascending=(ordem == "Mais antigo"))
        
        # Exibir
        st.write(f"**Total de movimentações:** {len(df_hist_filtrado)}")
        
        for idx, mov in df_hist_filtrado.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 2])
                
                with col1:
                    if mov['tipo'] == 'ENTRADA':
                        st.success(f"➕ {mov['tipo']}")
                    else:
                        st.error(f"➖ {mov['tipo']}")
                
                with col2:
                    st.write(f"**{mov['codigo_bm']}** - {mov['descricao']}")
                    st.write(f"Quantidade: {mov['quantidade']} | {mov.get('motivo', '')}")
                
                with col3:
                    st.write(f"📅 {mov['data']}")
                
                st.markdown("---")
        
        # Limpar filtro do histórico
        if 'filtro_historico' in st.session_state:
            del st.session_state['filtro_historico']
    else:
        st.info("📭 Nenhuma movimentação registrada ainda.")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Sistema de Controle de Estoque v2.0 | Desenvolvido com Streamlit</p>
    </div>
    """, 
    unsafe_allow_html=True
)
