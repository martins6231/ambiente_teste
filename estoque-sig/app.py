import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Estoque - SIG CFA 112",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
    .success-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .error-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'historico_movimentacoes' not in st.session_state:
    st.session_state.historico_movimentacoes = pd.DataFrame(
        columns=['data_hora', 'tipo', 'codigo', 'descricao', 'quantidade', 'usuario']
    )

# Função para carregar dados
@st.cache_data
def carregar_dados(file):
    try:
        df = pd.read_excel(file)
        # Garantir que as colunas numéricas estejam no formato correto
        df['qtde_estoque'] = pd.to_numeric(df['qtde_estoque'], errors='coerce').fillna(0)
        df['preco_unitario'] = pd.to_numeric(df['preco_unitario'], errors='coerce').fillna(0)
        df['total_r_estoque'] = df['qtde_estoque'] * df['preco_unitario']
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

# Função para registrar movimentação
def registrar_movimentacao(tipo, codigo, descricao, quantidade, usuario="Sistema"):
    nova_movimentacao = pd.DataFrame({
        'data_hora': [datetime.now()],
        'tipo': [tipo],
        'codigo': [codigo],
        'descricao': [descricao],
        'quantidade': [quantidade],
        'usuario': [usuario]
    })
    st.session_state.historico_movimentacoes = pd.concat(
        [st.session_state.historico_movimentacoes, nova_movimentacao], 
        ignore_index=True
    )

# Header
st.markdown('<h1 class="main-header">📦 Sistema de Gestão de Estoque - SIG CFA 112</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📁 Carregar Dados")
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel",
        type=['xlsx', 'xls'],
        help="Faça upload do arquivo de estoque"
    )
    
    if uploaded_file is not None:
        df = carregar_dados(uploaded_file)
        if df is not None:
            st.session_state.df = df
            st.success(f"✅ Arquivo carregado: {len(df)} itens")
    
    st.divider()
    
    # Filtros
    if st.session_state.df is not None:
        st.header("🔍 Filtros")
        
        # Filtro por categoria
        categorias = ['Todas'] + sorted(st.session_state.df['categoria'].unique().tolist())
        categoria_selecionada = st.selectbox("Categoria", categorias)
        
        # Filtro por faixa de preço
        preco_min = float(st.session_state.df['preco_unitario'].min())
        preco_max = float(st.session_state.df['preco_unitario'].max())
        faixa_preco = st.slider(
            "Faixa de Preço (R$)",
            preco_min,
            preco_max,
            (preco_min, preco_max)
        )
        
        # Filtro por estoque mínimo
        estoque_minimo = st.number_input(
            "Mostrar itens com estoque abaixo de:",
            min_value=0,
            value=10,
            step=1
        )

# Conteúdo principal
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if categoria_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_selecionada]
    
    df_filtrado = df_filtrado[
        (df_filtrado['preco_unitario'] >= faixa_preco[0]) &
        (df_filtrado['preco_unitario'] <= faixa_preco[1])
    ]
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", 
        "📋 Estoque", 
        "➕ Cadastrar Peça",
        "📤 Registrar Saída",
        "📈 Análise ABC",
        "📜 Histórico"
    ])
    
    with tab1:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_itens = len(df_filtrado)
            st.metric("Total de Itens", f"{total_itens:,}")
        
        with col2:
            valor_total = df_filtrado['total_r_estoque'].sum()
            st.metric("Valor Total em Estoque", f"R$ {valor_total:,.2f}")
        
        with col3:
            itens_baixo_estoque = len(df_filtrado[df_filtrado['qtde_estoque'] < estoque_minimo])
            st.metric("Itens com Baixo Estoque", itens_baixo_estoque)
        
        with col4:
            categorias_unicas = df_filtrado['categoria'].nunique()
            st.metric("Categorias", categorias_unicas)
        
        st.divider()
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza por categoria
            df_categoria = df_filtrado.groupby('categoria')['total_r_estoque'].sum().reset_index()
            fig_pizza = px.pie(
                df_categoria,
                values='total_r_estoque',
                names='categoria',
                title='Distribuição do Valor por Categoria'
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        
        with col2:
            # Top 10 produtos por valor
            top_produtos = df_filtrado.nlargest(10, 'total_r_estoque')
            fig_bar = px.bar(
                top_produtos,
                x='total_r_estoque',
                y='descricao',
                orientation='h',
                title='Top 10 Produtos por Valor em Estoque',
                labels={'total_r_estoque': 'Valor Total (R$)', 'descricao': 'Produto'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Produtos com baixo estoque
        st.subheader(f"⚠️ Produtos com Estoque Abaixo de {estoque_minimo} Unidades")
        produtos_baixo_estoque = df_filtrado[df_filtrado['qtde_estoque'] < estoque_minimo]
        if not produtos_baixo_estoque.empty:
            st.dataframe(
                produtos_baixo_estoque[['codigo', 'descricao', 'qtde_estoque', 'categoria']],
                use_container_width=True
            )
        else:
            st.info("Nenhum produto com estoque baixo.")
    
    with tab2:
        st.subheader("📋 Listagem Completa do Estoque")
        
        # Busca
        busca = st.text_input("🔍 Buscar por código ou descrição")
        
        if busca:
            df_busca = df_filtrado[
                df_filtrado['codigo'].astype(str).str.contains(busca, case=False) |
                df_filtrado['descricao'].str.contains(busca, case=False)
            ]
        else:
            df_busca = df_filtrado
        
        # Exibir dataframe
        st.dataframe(
            df_busca.style.format({
                'preco_unitario': 'R$ {:.2f}',
                'total_r_estoque': 'R$ {:.2f}'
            }),
            use_container_width=True
        )
        
        # Download
        csv = df_busca.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f'estoque_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )
    
    with tab3:
        st.subheader("➕ Cadastrar Nova Peça")
        
        with st.form("cadastro_peca"):
            col1, col2 = st.columns(2)
            
            with col1:
                novo_codigo = st.text_input("Código da Peça*")
                nova_descricao = st.text_input("Descrição*")
                nova_categoria = st.selectbox(
                    "Categoria*",
                    sorted(df['categoria'].unique())
                )
            
            with col2:
                nova_quantidade = st.number_input("Quantidade*", min_value=0, step=1)
                novo_preco = st.number_input("Preço Unitário (R$)*", min_value=0.0, step=0.01)
                nova_unidade = st.selectbox(
                    "Unidade de Medida*",
                    sorted(df['unidade_medida'].unique())
                )
            
            submitted = st.form_submit_button("Cadastrar Peça")
            
            if submitted:
                if novo_codigo and nova_descricao:
                    # Verificar se código já existe
                    if novo_codigo in st.session_state.df['codigo'].values:
                        st.error("❌ Código já existe no estoque!")
                    else:
                        # Adicionar nova peça
                        nova_peca = pd.DataFrame({
                            'codigo': [novo_codigo],
                            'descricao': [nova_descricao],
                            'categoria': [nova_categoria],
                            'unidade_medida': [nova_unidade],
                            'qtde_estoque': [nova_quantidade],
                            'preco_unitario': [novo_preco],
                            'total_r_estoque': [nova_quantidade * novo_preco]
                        })
                        
                        st.session_state.df = pd.concat([st.session_state.df, nova_peca], ignore_index=True)
                        registrar_movimentacao("ENTRADA", novo_codigo, nova_descricao, nova_quantidade)
                        st.success("✅ Peça cadastrada com sucesso!")
                        st.rerun()
                else:
                    st.error("❌ Preencha todos os campos obrigatórios!")
    
    with tab4:
        st.subheader("📤 Registrar Saída de Estoque")
        
        with st.form("saida_estoque"):
            # Seleção de produto
            produtos = df['codigo'].astype(str) + ' - ' + df['descricao']
            produto_selecionado = st.selectbox("Selecione o Produto*", produtos)
            
            if produto_selecionado:
                codigo_selecionado = produto_selecionado.split(' - ')[0]
                produto_info = df[df['codigo'] == codigo_selecionado].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Estoque Atual: {produto_info['qtde_estoque']} {produto_info['unidade_medida']}")
                with col2:
                    st.info(f"Valor Unitário: R$ {produto_info['preco_unitario']:.2f}")
                
                quantidade_saida = st.number_input(
                    "Quantidade de Saída*",
                    min_value=1,
                    max_value=int(produto_info['qtde_estoque']),
                    step=1
                )
                
                motivo_saida = st.text_area("Motivo da Saída")
                
                submitted = st.form_submit_button("Registrar Saída")
                
                if submitted:
                    # Atualizar estoque
                    idx = st.session_state.df[st.session_state.df['codigo'] == codigo_selecionado].index[0]
                    st.session_state.df.loc[idx, 'qtde_estoque'] -= quantidade_saida
                    st.session_state.df.loc[idx, 'total_r_estoque'] = (
                        st.session_state.df.loc[idx, 'qtde_estoque'] * 
                        st.session_state.df.loc[idx, 'preco_unitario']
                    )
                    
                    # Registrar movimentação
                    registrar_movimentacao(
                        "SAÍDA",
                        codigo_selecionado,
                        produto_info['descricao'],
                        quantidade_saida
                    )
                    
                    st.success(f"✅ Saída registrada: {quantidade_saida} {produto_info['unidade_medida']}")
                    st.rerun()
    
    with tab5:
        st.subheader("📈 Análise ABC - Curva de Pareto")
        
        # Preparar dados para análise ABC
        df_pareto = df_filtrado.sort_values('total_r_estoque', ascending=False).copy()
        df_pareto['percentual_valor'] = (df_pareto['total_r_estoque'] / df_pareto['total_r_estoque'].sum()) * 100
        df_pareto['percentual_acumulado'] = df_pareto['percentual_valor'].cumsum()
        
        # Corrigir o erro: converter range para numpy array
        df_pareto['percentual_itens'] = (np.arange(1, len(df_pareto) + 1) / len(df_pareto)) * 100
        
        # Classificação ABC
        df_pareto['classificacao'] = pd.cut(
            df_pareto['percentual_acumulado'],
            bins=[0, 80, 95, 100],
            labels=['A', 'B', 'C']
        )
        
        # Gráfico de Pareto
        fig_pareto = go.Figure()
        
        # Barras
        fig_pareto.add_trace(go.Bar(
            x=df_pareto.index,
            y=df_pareto['percentual_valor'],
            name='% do Valor',
            yaxis='y',
            marker_color='lightblue'
        ))
        
        # Linha acumulada
        fig_pareto.add_trace(go.Scatter(
            x=df_pareto.index,
            y=df_pareto['percentual_acumulado'],
            name='% Acumulado',
            yaxis='y2',
            line=dict(color='red', width=2)
        ))
        
        # Layout
        fig_pareto.update_layout(
            title='Curva ABC - Análise de Pareto',
            xaxis=dict(title='Produtos (ordenados por valor)'),
            yaxis=dict(title='% do Valor Total', side='left'),
            yaxis2=dict(title='% Acumulado', overlaying='y', side='right'),
            hovermode='x',
            height=500
        )
        
        st.plotly_chart(fig_pareto, use_container_width=True)
        
        # Resumo ABC
        col1, col2, col3 = st.columns(3)
        
        with col1:
            classe_a = df_pareto[df_pareto['classificacao'] == 'A']
            st.metric(
                "Classe A",
                f"{len(classe_a)} itens",
                f"{classe_a['percentual_valor'].sum():.1f}% do valor"
            )
        
        with col2:
            classe_b = df_pareto[df_pareto['classificacao'] == 'B']
            st.metric(
                "Classe B",
                f"{len(classe_b)} itens",
                f"{classe_b['percentual_valor'].sum():.1f}% do valor"
            )
        
        with col3:
            classe_c = df_pareto[df_pareto['classificacao'] == 'C']
            st.metric(
                "Classe C",
                f"{len(classe_c)} itens",
                f"{classe_c['percentual_valor'].sum():.1f}% do valor"
            )
        
        # Tabela detalhada
        st.subheader("Detalhamento por Classe")
        classe_selecionada = st.selectbox("Selecione a Classe", ['A', 'B', 'C'])
        
        df_classe = df_pareto[df_pareto['classificacao'] == classe_selecionada]
        st.dataframe(
            df_classe[['codigo', 'descricao', 'qtde_estoque', 'total_r_estoque', 'percentual_valor', 'percentual_acumulado']].style.format({
                'total_r_estoque': 'R$ {:.2f}',
                'percentual_valor': '{:.2f}%',
                'percentual_acumulado': '{:.2f}%'
            }),
            use_container_width=True
        )
    
    with tab6:
        st.subheader("📜 Histórico de Movimentações")
        
        if not st.session_state.historico_movimentacoes.empty:
            # Filtros do histórico
            col1, col2 = st.columns(2)
            with col1:
                tipo_mov = st.selectbox(
                    "Tipo de Movimentação",
                    ['Todas', 'ENTRADA', 'SAÍDA']
                )
            with col2:
                dias_historico = st.selectbox(
                    "Período",
                    [1, 7, 30, 90, 365],
                    format_func=lambda x: f"Últimos {x} dias"
                )
            
            # Filtrar histórico
            historico = st.session_state.historico_movimentacoes.copy()
            if tipo_mov != 'Todas':
                historico = historico[historico['tipo'] == tipo_mov]
            
            # Ordenar por data mais recente
            historico = historico.sort_values('data_hora', ascending=False)
            
            # Exibir histórico
            st.dataframe(
                historico.style.apply(
                    lambda x: ['background-color: #d4edda' if x['tipo'] == 'ENTRADA' 
                              else 'background-color: #f8d7da' for _ in x], axis=1
                ),
                use_container_width=True
            )
            
            # Estatísticas do histórico
            st.subheader("📊 Estatísticas de Movimentação")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_entradas = len(historico[historico['tipo'] == 'ENTRADA'])
                st.metric("Total de Entradas", total_entradas)
            
            with col2:
                total_saidas = len(historico[historico['tipo'] == 'SAÍDA'])
                st.metric("Total de Saídas", total_saidas)
            
            with col3:
                total_movimentacoes = len(historico)
                st.metric("Total de Movimentações", total_movimentacoes)
        else:
            st.info("Nenhuma movimentação registrada ainda.")

else:
    # Tela inicial quando não há dados carregados
    st.info("👈 Por favor, carregue um arquivo Excel na barra lateral para começar.")
    
    # Instruções
    with st.expander("📖 Como usar o sistema"):
        st.markdown("""
        1. **Carregar Dados**: Use a barra lateral para fazer upload do arquivo Excel com os dados do estoque
        2. **Dashboard**: Visualize métricas e gráficos importantes sobre seu estoque
        3. **Estoque**: Consulte e pesquise produtos no estoque
        4. **Cadastrar Peça**: Adicione novas peças ao estoque
        5. **Registrar Saída**: Registre saídas de produtos do estoque
        6. **Análise ABC**: Visualize a curva de Pareto e classificação ABC dos produtos
        7. **Histórico**: Acompanhe todas as movimentações realizadas
        """)
    
    # Formato esperado
    with st.expander("📋 Formato esperado do arquivo Excel"):
        st.markdown("""
        O arquivo Excel deve conter as seguintes colunas:
        - **codigo**: Código único do produto
        - **descricao**: Descrição do produto
        - **categoria**: Categoria do produto
        - **unidade_medida**: Unidade de medida (UN, KG, etc.)
        - **qtde_estoque**: Quantidade em estoque
        - **preco_unitario**: Preço unitário do produto
        """)

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Sistema de Gestão de Estoque - SIG CFA 112 | Desenvolvido com Streamlit 🚀</p>
    </div>
    """,
    unsafe_allow_html=True
)
