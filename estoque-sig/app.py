import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64
from typing import Tuple, List, Optional, Dict, Any

# Configuração da página
st.set_page_config(
    page_title="SIG CFA 112 - Sistema de Gestão de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS customizados
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-message {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .warning-message {
        padding: 10px;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Classe para gerenciar o banco de dados
class DatabaseManager:
    def __init__(self, db_name: str = "estoque.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o banco de dados."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self) -> None:
        """Inicializa o banco de dados e cria as tabelas necessárias."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Criar tabela de peças (corrigido o bug da vírgula)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pecas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descricao TEXT NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 0,
                    estoque_minimo INTEGER NOT NULL DEFAULT 0,
                    estoque_maximo INTEGER NOT NULL DEFAULT 0,
                    localizacao TEXT,
                    categoria TEXT,
                    unidade_medida TEXT DEFAULT 'UN',
                    valor_unitario REAL DEFAULT 0.0,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Criar tabela de movimentações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    peca_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                    quantidade INTEGER NOT NULL,
                    motivo TEXT,
                    responsavel TEXT,
                    data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (peca_id) REFERENCES pecas (id)
                )
            ''')
            
            # Criar índices para melhor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pecas_codigo ON pecas(codigo)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_movimentacoes_peca ON movimentacoes(peca_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes(data_movimentacao)')
            
            conn.commit()

# Classe para gerenciar as operações de estoque
class EstoqueManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def adicionar_peca(self, codigo: str, descricao: str, quantidade: int, 
                      estoque_minimo: int, estoque_maximo: int, 
                      localizacao: str = None, categoria: str = None,
                      unidade_medida: str = 'UN', valor_unitario: float = 0.0) -> Tuple[bool, str]:
        """Adiciona uma nova peça ao estoque."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO pecas (codigo, descricao, quantidade, estoque_minimo, 
                                     estoque_maximo, localizacao, categoria, 
                                     unidade_medida, valor_unitario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (codigo, descricao, quantidade, estoque_minimo, estoque_maximo,
                     localizacao, categoria, unidade_medida, valor_unitario))
                conn.commit()
                return True, "Peça adicionada com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Erro: Já existe uma peça com este código!"
        except Exception as e:
            return False, f"Erro ao adicionar peça: {str(e)}"
    
    def atualizar_peca(self, peca_id: int, **kwargs) -> Tuple[bool, str]:
        """Atualiza os dados de uma peça (corrigido o bug dos parâmetros)."""
        try:
            campos_permitidos = ['descricao', 'estoque_minimo', 'estoque_maximo', 
                               'localizacao', 'categoria', 'unidade_medida', 'valor_unitario']
            
            campos_update = []
            valores = []
            
            for campo, valor in kwargs.items():
                if campo in campos_permitidos and valor is not None:
                    campos_update.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos_update:
                return False, "Nenhum campo válido para atualizar"
            
            valores.append(datetime.now())
            valores.append(peca_id)
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                query = f'''
                    UPDATE pecas 
                    SET {', '.join(campos_update)}, data_atualizacao = ?
                    WHERE id = ?
                '''
                cursor.execute(query, valores)
                
                if cursor.rowcount == 0:
                    return False, "Peça não encontrada"
                
                conn.commit()
                return True, "Peça atualizada com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar peça: {str(e)}"
    
    def registrar_movimentacao(self, peca_id: int, tipo: str, quantidade: int,
                             motivo: str = None, responsavel: str = None) -> Tuple[bool, str]:
        """Registra uma movimentação de entrada ou saída."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar estoque atual
                cursor.execute('SELECT quantidade FROM pecas WHERE id = ?', (peca_id,))
                result = cursor.fetchone()
                
                if not result:
                    return False, "Peça não encontrada"
                
                estoque_atual = result['quantidade']
                
                if tipo == 'saida' and estoque_atual < quantidade:
                    return False, f"Estoque insuficiente! Disponível: {estoque_atual}"
                
                # Atualizar quantidade
                nova_quantidade = estoque_atual + quantidade if tipo == 'entrada' else estoque_atual - quantidade
                cursor.execute('''
                    UPDATE pecas 
                    SET quantidade = ?, data_atualizacao = ? 
                    WHERE id = ?
                ''', (nova_quantidade, datetime.now(), peca_id))
                
                # Registrar movimentação
                cursor.execute('''
                    INSERT INTO movimentacoes (peca_id, tipo, quantidade, motivo, responsavel)
                    VALUES (?, ?, ?, ?, ?)
                ''', (peca_id, tipo, quantidade, motivo, responsavel))
                
                conn.commit()
                return True, f"Movimentação registrada! Novo estoque: {nova_quantidade}"
        except Exception as e:
            return False, f"Erro ao registrar movimentação: {str(e)}"
    
    def buscar_pecas(self, filtro: str = None) -> pd.DataFrame:
        """Busca peças no estoque com filtro opcional."""
        with self.db.get_connection() as conn:
            if filtro:
                query = '''
                    SELECT * FROM pecas 
                    WHERE codigo LIKE ? OR descricao LIKE ? OR categoria LIKE ? OR localizacao LIKE ?
                    ORDER BY codigo
                '''
                df = pd.read_sql_query(query, conn, params=(f'%{filtro}%', f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
            else:
                df = pd.read_sql_query('SELECT * FROM pecas ORDER BY codigo', conn)
            
            return df
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas gerais do estoque."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de peças
            cursor.execute('SELECT COUNT(*) as total FROM pecas')
            total_pecas = cursor.fetchone()['total']
            
            # Valor total do estoque
            cursor.execute('SELECT SUM(quantidade * valor_unitario) as valor_total FROM pecas')
            valor_total = cursor.fetchone()['valor_total'] or 0
            
            # Peças abaixo do mínimo
            cursor.execute('SELECT COUNT(*) as total FROM pecas WHERE quantidade < estoque_minimo')
            pecas_abaixo_minimo = cursor.fetchone()['total']
            
            # Peças acima do máximo
            cursor.execute('SELECT COUNT(*) as total FROM pecas WHERE quantidade > estoque_maximo')
            pecas_acima_maximo = cursor.fetchone()['total']
            
            # Peças sem estoque
            cursor.execute('SELECT COUNT(*) as total FROM pecas WHERE quantidade = 0')
            pecas_sem_estoque = cursor.fetchone()['total']
            
            return {
                'total_pecas': total_pecas,
                'valor_total': valor_total,
                'pecas_abaixo_minimo': pecas_abaixo_minimo,
                'pecas_acima_maximo': pecas_acima_maximo,
                'pecas_sem_estoque': pecas_sem_estoque
            }
    
    def exportar_dados(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Exporta dados de peças e movimentações."""
        with self.db.get_connection() as conn:
            pecas_df = pd.read_sql_query('SELECT * FROM pecas', conn)
            movimentacoes_df = pd.read_sql_query('''
                SELECT m.*, p.codigo, p.descricao 
                FROM movimentacoes m
                JOIN pecas p ON m.peca_id = p.id
                ORDER BY m.data_movimentacao DESC
            ''', conn)
            
            return pecas_df, movimentacoes_df
    
    def importar_pecas(self, df: pd.DataFrame) -> Tuple[int, int, List[str]]:
        """Importa peças de um DataFrame."""
        sucessos = 0
        falhas = 0
        erros = []
        
        colunas_obrigatorias = ['codigo', 'descricao', 'quantidade', 'estoque_minimo', 'estoque_maximo']
        
        # Verificar colunas obrigatórias
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        if colunas_faltantes:
            return 0, len(df), [f"Colunas obrigatórias faltando: {', '.join(colunas_faltantes)}"]
        
        for _, row in df.iterrows():
            try:
                sucesso, msg = self.adicionar_peca(
                    codigo=str(row['codigo']),
                    descricao=str(row['descricao']),
                    quantidade=int(row['quantidade']),
                    estoque_minimo=int(row['estoque_minimo']),
                    estoque_maximo=int(row['estoque_maximo']),
                    localizacao=str(row.get('localizacao', '')) if pd.notna(row.get('localizacao')) else None,
                    categoria=str(row.get('categoria', '')) if pd.notna(row.get('categoria')) else None,
                    unidade_medida=str(row.get('unidade_medida', 'UN')),
                    valor_unitario=float(row.get('valor_unitario', 0))
                )
                
                if sucesso:
                    sucessos += 1
                else:
                    falhas += 1
                    erros.append(f"Código {row['codigo']}: {msg}")
            except Exception as e:
                falhas += 1
                erros.append(f"Código {row.get('codigo', 'DESCONHECIDO')}: {str(e)}")
        
        return sucessos, falhas, erros

# Funções auxiliares para a interface
def mostrar_mensagem(tipo: str, mensagem: str):
    """Mostra mensagem formatada na interface."""
    if tipo == "success":
        st.markdown(f'<div class="success-message">✅ {mensagem}</div>', unsafe_allow_html=True)
    elif tipo == "error":
        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', unsafe_allow_html=True)
    elif tipo == "warning":
        st.markdown(f'<div class="warning-message">⚠️ {mensagem}</div>', unsafe_allow_html=True)

def download_link(df: pd.DataFrame, filename: str, text: str):
    """Cria um link para download de DataFrame como CSV."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Inicializar managers
db_manager = DatabaseManager()
estoque_manager = EstoqueManager(db_manager)

# Interface principal
st.title("📦 SIG CFA 112 - Sistema de Gestão de Estoque")
st.markdown("---")

# Sidebar com navegação
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=SIG+CFA+112", use_column_width=True)
    st.markdown("---")
    
    pagina = st.selectbox(
        "Navegação",
        ["🏠 Dashboard", "➕ Cadastrar Peça", "📥 Entrada de Estoque", 
         "📤 Saída de Estoque", "🔍 Consultar Estoque", "📊 Relatórios", 
         "🔧 Manutenção", "📁 Importar/Exportar"]
    )
    
    st.markdown("---")
    st.markdown("### 📌 Informações")
    st.info("Sistema desenvolvido para gerenciamento completo de estoque com controle de entradas, saídas e níveis críticos.")

# Dashboard
if pagina == "🏠 Dashboard":
    st.header("Dashboard - Visão Geral")
    
    # Estatísticas
    stats = estoque_manager.obter_estatisticas()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total de Peças", stats['total_pecas'])
    
    with col2:
        st.metric("Valor do Estoque", f"R$ {stats['valor_total']:,.2f}")
    
    with col3:
        st.metric("Abaixo do Mínimo", stats['pecas_abaixo_minimo'], 
                 delta=None if stats['pecas_abaixo_minimo'] == 0 else "⚠️")
    
    with col4:
        st.metric("Acima do Máximo", stats['pecas_acima_maximo'])
    
    with col5:
        st.metric("Sem Estoque", stats['pecas_sem_estoque'],
                 delta=None if stats['pecas_sem_estoque'] == 0 else "❗")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição por Categoria")
        df_pecas = estoque_manager.buscar_pecas()
        
        if not df_pecas.empty and 'categoria' in df_pecas.columns:
            categoria_counts = df_pecas['categoria'].value_counts()
            fig_pizza = px.pie(
                values=categoria_counts.values, 
                names=categoria_counts.index,
                title="Peças por Categoria"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info("Sem dados de categorias para exibir")
    
    with col2:
        st.subheader("📈 Top 10 - Maiores Estoques")
        if not df_pecas.empty:
            top_10 = df_pecas.nlargest(10, 'quantidade')[['codigo', 'descricao', 'quantidade']]
            fig_bar = px.bar(
                top_10, 
                x='quantidade', 
                y='descricao',
                orientation='h',
                title="Top 10 Peças com Maior Estoque",
                labels={'quantidade': 'Quantidade', 'descricao': 'Descrição'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Sem dados para exibir")
    
    # Alertas
    st.markdown("---")
    st.subheader("🚨 Alertas de Estoque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚠️ Peças Abaixo do Mínimo")
        df_abaixo = df_pecas[df_pecas['quantidade'] < df_pecas['estoque_minimo']]
        if not df_abaixo.empty:
            st.dataframe(
                df_abaixo[['codigo', 'descricao', 'quantidade', 'estoque_minimo']],
                hide_index=True
            )
        else:
            st.success("Nenhuma peça abaixo do estoque mínimo!")
    
    with col2:
        st.markdown("#### 📈 Peças Acima do Máximo")
        df_acima = df_pecas[df_pecas['quantidade'] > df_pecas['estoque_maximo']]
        if not df_acima.empty:
            st.dataframe(
                df_acima[['codigo', 'descricao', 'quantidade', 'estoque_maximo']],
                hide_index=True
            )
        else:
            st.success("Nenhuma peça acima do estoque máximo!")

# Cadastrar Peça
elif pagina == "➕ Cadastrar Peça":
    st.header("Cadastrar Nova Peça")
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código da Peça*", help="Código único da peça")
            descricao = st.text_input("Descrição*", help="Descrição detalhada da peça")
            categoria = st.selectbox("Categoria", ["", "Eletrônico", "Mecânico", "Hidráulico", "Elétrico", "Outros"])
            unidade_medida = st.selectbox("Unidade de Medida", ["UN", "PC", "CX", "KG", "MT", "LT"])
        
        with col2:
            quantidade = st.number_input("Quantidade Inicial*", min_value=0, value=0)
            estoque_minimo = st.number_input("Estoque Mínimo*", min_value=0, value=0)
            estoque_maximo = st.number_input("Estoque Máximo*", min_value=0, value=100)
            valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.0, value=0.0, format="%.2f")
        
        localizacao = st.text_input("Localização", placeholder="Ex: Prateleira A-01")
        
        submitted = st.form_submit_button("Cadastrar Peça", type="primary")
        
        if submitted:
            if not codigo or not descricao:
                mostrar_mensagem("error", "Código e descrição são obrigatórios!")
            elif estoque_minimo > estoque_maximo:
                mostrar_mensagem("error", "Estoque mínimo não pode ser maior que o máximo!")
            else:
                sucesso, mensagem = estoque_manager.adicionar_peca(
                    codigo=codigo,
                    descricao=descricao,
                    quantidade=quantidade,
                    estoque_minimo=estoque_minimo,
                    estoque_maximo=estoque_maximo,
                    localizacao=localizacao if localizacao else None,
                    categoria=categoria if categoria else None,
                    unidade_medida=unidade_medida,
                    valor_unitario=valor_unitario
                )
                
                if sucesso:
                    mostrar_mensagem("success", mensagem)
                    st.balloons()
                else:
                    mostrar_mensagem("error", mensagem)

# Entrada de Estoque
elif pagina == "📥 Entrada de Estoque":
    st.header("Registrar Entrada de Estoque")
    
    # Buscar peças
    df_pecas = estoque_manager.buscar_pecas()
    
    if df_pecas.empty:
        st.warning("Nenhuma peça cadastrada. Cadastre peças primeiro!")
    else:
        with st.form("form_entrada"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                pecas_opcoes = df_pecas.apply(lambda x: f"{x['codigo']} - {x['descricao']}", axis=1).tolist()
                peca_selecionada = st.selectbox("Selecione a Peça", pecas_opcoes)
                
                if peca_selecionada:
                    peca_index = pecas_opcoes.index(peca_selecionada)
                    peca_info = df_pecas.iloc[peca_index]
                    
                    st.info(f"""
                    **Estoque Atual:** {peca_info['quantidade']} {peca_info['unidade_medida']}  
                    **Localização:** {peca_info['localizacao'] or 'Não definida'}  
                    **Categoria:** {peca_info['categoria'] or 'Não definida'}
                    """)
            
            with col2:
                quantidade = st.number_input("Quantidade", min_value=1, value=1)
            
            motivo = st.text_input("Motivo da Entrada", placeholder="Ex: Compra, Devolução, etc.")
            responsavel = st.text_input("Responsável", placeholder="Nome do responsável")
            
            submitted = st.form_submit_button("Registrar Entrada", type="primary")
            
            if submitted and peca_selecionada:
                peca_id = df_pecas.iloc[peca_index]['id']
                
                sucesso, mensagem = estoque_manager.registrar_movimentacao(
                    peca_id=peca_id,
                    tipo='entrada',
                    quantidade=quantidade,
                    motivo=motivo if motivo else None,
                    responsavel=responsavel if responsavel else None
                )
                
                if sucesso:
                    mostrar_mensagem("success", mensagem)
                    st.balloons()
                else:
                    mostrar_mensagem("error", mensagem)

# Saída de Estoque
elif pagina == "📤 Saída de Estoque":
    st.header("Registrar Saída de Estoque")
    
    # Buscar peças
    df_pecas = estoque_manager.buscar_pecas()
    
    if df_pecas.empty:
        st.warning("Nenhuma peça cadastrada. Cadastre peças primeiro!")
    else:
        # Filtrar apenas peças com estoque
        df_com_estoque = df_pecas[df_pecas['quantidade'] > 0]
        
        if df_com_estoque.empty:
            st.warning("Nenhuma peça disponível em estoque!")
        else:
            with st.form("form_saida"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    pecas_opcoes = df_com_estoque.apply(lambda x: f"{x['codigo']} - {x['descricao']}", axis=1).tolist()
                    peca_selecionada = st.selectbox("Selecione a Peça", pecas_opcoes)
                    
                    if peca_selecionada:
                        peca_index = pecas_opcoes.index(peca_selecionada)
                        peca_info = df_com_estoque.iloc[peca_index]
                        
                        st.info(f"""
                        **Estoque Atual:** {peca_info['quantidade']} {peca_info['unidade_medida']}  
                        **Localização:** {peca_info['localizacao'] or 'Não definida'}  
                        **Categoria:** {peca_info['categoria'] or 'Não definida'}
                        """)
                
                with col2:
                    max_quantidade = int(peca_info['quantidade']) if peca_selecionada else 1
                    quantidade = st.number_input("Quantidade", min_value=1, max_value=max_quantidade, value=1)
                
                motivo = st.text_input("Motivo da Saída", placeholder="Ex: Manutenção, Projeto, etc.")
                responsavel = st.text_input("Responsável", placeholder="Nome do responsável")
                
                submitted = st.form_submit_button("Registrar Saída", type="primary")
                
                if submitted and peca_selecionada:
                    peca_id = df_com_estoque.iloc[peca_index]['id']
                    
                    sucesso, mensagem = estoque_manager.registrar_movimentacao(
                        peca_id=peca_id,
                        tipo='saida',
                        quantidade=quantidade,
                        motivo=motivo if motivo else None,
                        responsavel=responsavel if responsavel else None
                    )
                    
                    if sucesso:
                        mostrar_mensagem("success", mensagem)
                        st.balloons()
                    else:
                        mostrar_mensagem("error", mensagem)

# Consultar Estoque
elif pagina == "🔍 Consultar Estoque":
    st.header("Consultar Estoque")
    
    # Filtros
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        filtro = st.text_input("🔍 Buscar (código, descrição, categoria ou localização)", 
                              placeholder="Digite para filtrar...")
    
    with col2:
        mostrar_criticos = st.checkbox("Apenas críticos", help="Mostrar apenas itens abaixo do mínimo")
    
    with col3:
        mostrar_sem_estoque = st.checkbox("Incluir sem estoque", help="Incluir itens com estoque zerado")
    
    # Buscar peças
    df_pecas = estoque_manager.buscar_pecas(filtro)
    
    if not df_pecas.empty:
        # Aplicar filtros adicionais
        if mostrar_criticos:
            df_pecas = df_pecas[df_pecas['quantidade'] < df_pecas['estoque_minimo']]
        
        if not mostrar_sem_estoque:
            df_pecas = df_pecas[df_pecas['quantidade'] > 0]
        
        # Adicionar coluna de status
        def definir_status(row):
            if row['quantidade'] == 0:
                return "❌ Sem Estoque"
            elif row['quantidade'] < row['estoque_minimo']:
                return "⚠️ Abaixo do Mínimo"
            elif row['quantidade'] > row['estoque_maximo']:
                return "📈 Acima do Máximo"
            else:
                return "✅ Normal"
        
        df_pecas['Status'] = df_pecas.apply(definir_status, axis=1)
        
        # Estatísticas da busca
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Itens", len(df_pecas))
        with col2:
            st.metric("Valor Total", f"R$ {(df_pecas['quantidade'] * df_pecas['valor_unitario']).sum():,.2f}")
        with col3:
            st.metric("Itens Críticos", len(df_pecas[df_pecas['quantidade'] < df_pecas['estoque_minimo']]))
        with col4:
            st.metric("Sem Estoque", len(df_pecas[df_pecas['quantidade'] == 0]))
        
        st.markdown("---")
        
        # Tabela de resultados
        colunas_exibir = ['codigo', 'descricao', 'quantidade', 'unidade_medida', 
                         'estoque_minimo', 'estoque_maximo', 'valor_unitario', 
                         'localizacao', 'categoria', 'Status']
        
        st.dataframe(
            df_pecas[colunas_exibir],
            hide_index=True,
            column_config={
                "codigo": "Código",
                "descricao": "Descrição",
                "quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
                "unidade_medida": "Un.",
                "estoque_minimo": st.column_config.NumberColumn("Mínimo", format="%d"),
                "estoque_maximo": st.column_config.NumberColumn("Máximo", format="%d"),
                "valor_unitario": st.column_config.NumberColumn("Valor Unit.", format="R$ %.2f"),
                "localizacao": "Localização",
                "categoria": "Categoria",
                "Status": "Status"
            }
        )
    else:
        st.info("Nenhuma peça encontrada com os filtros aplicados.")

# Relatórios
elif pagina == "📊 Relatórios":
    st.header("Relatórios e Análises")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Análise Geral", "📈 Movimentações", "💰 Financeiro", "📋 Inventário"])
    
    with tab1:
        st.subheader("Análise Geral do Estoque")
        
        df_pecas = estoque_manager.buscar_pecas()
        
        if not df_pecas.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de categorias
                if 'categoria' in df_pecas.columns:
                    fig_cat = px.pie(
                        df_pecas.groupby('categoria').size().reset_index(name='count'),
                        values='count',
                        names='categoria',
                        title='Distribuição por Categoria'
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)
            
            with col2:
                # Gráfico de status
                df_status = pd.DataFrame({
                    'Status': ['Normal', 'Abaixo do Mínimo', 'Acima do Máximo', 'Sem Estoque'],
                    'Quantidade': [
                        len(df_pecas[(df_pecas['quantidade'] >= df_pecas['estoque_minimo']) & 
                                   (df_pecas['quantidade'] <= df_pecas['estoque_maximo']) & 
                                   (df_pecas['quantidade'] > 0)]),
                        len(df_pecas[df_pecas['quantidade'] < df_pecas['estoque_minimo']]),
                        len(df_pecas[df_pecas['quantidade'] > df_pecas['estoque_maximo']]),
                        len(df_pecas[df_pecas['quantidade'] == 0])
                    ]
                })
                
                fig_status = px.bar(
                    df_status,
                    x='Status',
                    y='Quantidade',
                    title='Análise de Status do Estoque',
                    color='Status',
                    color_discrete_map={
                        'Normal': 'green',
                        'Abaixo do Mínimo': 'orange',
                        'Acima do Máximo': 'blue',
                        'Sem Estoque': 'red'
                    }
                )
                st.plotly_chart(fig_status, use_container_width=True)
    
    with tab2:
        st.subheader("Histórico de Movimentações")
        
        # Período
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Inicial", value=pd.Timestamp.now() - pd.Timedelta(days=30))
        with col2:
            data_fim = st.date_input("Data Final", value=pd.Timestamp.now())
        
        # Buscar movimentações
        with db_manager.get_connection() as conn:
            query = '''
                SELECT m.*, p.codigo, p.descricao 
                FROM movimentacoes m
                JOIN pecas p ON m.peca_id = p.id
                WHERE DATE(m.data_movimentacao) BETWEEN ? AND ?
                ORDER BY m.data_movimentacao DESC
            '''
            df_mov = pd.read_sql_query(query, conn, params=(data_inicio, data_fim))
        
        if not df_mov.empty:
            # Estatísticas do período
            col1, col2, col3 = st.columns(3)
            with col1:
                total_entradas = len(df_mov[df_mov['tipo'] == 'entrada'])
                st.metric("Total de Entradas", total_entradas)
            with col2:
                total_saidas = len(df_mov[df_mov['tipo'] == 'saida'])
                st.metric("Total de Saídas", total_saidas)
            with col3:
                st.metric("Total de Movimentações", len(df_mov))
            
            # Gráfico de movimentações por dia
            df_mov['data'] = pd.to_datetime(df_mov['data_movimentacao']).dt.date
            mov_por_dia = df_mov.groupby(['data', 'tipo']).size().reset_index(name='quantidade')
            
            fig_mov = px.line(
                mov_por_dia,
                x='data',
                y='quantidade',
                color='tipo',
                title='Movimentações por Dia',
                markers=True
            )
            st.plotly_chart(fig_mov, use_container_width=True)
            
            # Tabela de movimentações
            st.subheader("Detalhamento das Movimentações")
            st.dataframe(
                df_mov[['data_movimentacao', 'codigo', 'descricao', 'tipo', 'quantidade', 'motivo', 'responsavel']],
                hide_index=True,
                column_config={
                    'data_movimentacao': st.column_config.DatetimeColumn('Data/Hora', format='DD/MM/YYYY HH:mm'),
                    'codigo': 'Código',
                    'descricao': 'Descrição',
                    'tipo': 'Tipo',
                    'quantidade': st.column_config.NumberColumn('Quantidade', format='%d'),
                    'motivo': 'Motivo',
                    'responsavel': 'Responsável'
                }
            )
        else:
            st.info("Nenhuma movimentação encontrada no período selecionado.")
    
    with tab3:
        st.subheader("Análise Financeira")
        
        df_pecas = estoque_manager.buscar_pecas()
        
        if not df_pecas.empty:
            # Calcular valores
            df_pecas['valor_total'] = df_pecas['quantidade'] * df_pecas['valor_unitario']
            
            # Métricas financeiras
            col1, col2, col3 = st.columns(3)
            with col1:
                valor_total_estoque = df_pecas['valor_total'].sum()
                st.metric("Valor Total do Estoque", f"R$ {valor_total_estoque:,.2f}")
            with col2:
                valor_medio = df_pecas[df_pecas['valor_unitario'] > 0]['valor_unitario'].mean()
                st.metric("Valor Médio Unitário", f"R$ {valor_medio:,.2f}")
            with col3:
                itens_com_valor = len(df_pecas[df_pecas['valor_unitario'] > 0])
                st.metric("Itens com Valor Cadastrado", itens_com_valor)
            
            # Top 10 mais valiosos
            st.subheader("Top 10 - Itens Mais Valiosos em Estoque")
            top_valor = df_pecas.nlargest(10, 'valor_total')[['codigo', 'descricao', 'quantidade', 'valor_unitario', 'valor_total']]
            
            fig_valor = px.bar(
                top_valor,
                x='valor_total',
                y='descricao',
                orientation='h',
                title='Top 10 Itens por Valor Total',
                labels={'valor_total': 'Valor Total (R$)', 'descricao': 'Descrição'}
            )
            st.plotly_chart(fig_valor, use_container_width=True)
            
            # Valor por categoria
            if 'categoria' in df_pecas.columns:
                valor_categoria = df_pecas.groupby('categoria')['valor_total'].sum().reset_index()
                
                fig_cat_valor = px.pie(
                    valor_categoria,
                    values='valor_total',
                    names='categoria',
                    title='Distribuição de Valor por Categoria'
                )
                st.plotly_chart(fig_cat_valor, use_container_width=True)
    
    with tab4:
        st.subheader("Relatório de Inventário")
        
        df_pecas = estoque_manager.buscar_pecas()
        
        if not df_pecas.empty:
            # Opções de filtro para o relatório
            col1, col2 = st.columns(2)
            with col1:
                categorias = ['Todas'] + df_pecas['categoria'].dropna().unique().tolist()
                categoria_filtro = st.selectbox("Filtrar por Categoria", categorias)
            with col2:
                ordenar_por = st.selectbox("Ordenar por", ['Código', 'Descrição', 'Quantidade', 'Valor Total'])
            
            # Aplicar filtros
            df_relatorio = df_pecas.copy()
            if categoria_filtro != 'Todas':
                df_relatorio = df_relatorio[df_relatorio['categoria'] == categoria_filtro]
            
            # Adicionar valor total
            df_relatorio['valor_total'] = df_relatorio['quantidade'] * df_relatorio['valor_unitario']
            
            # Ordenar
            ordem_map = {
                'Código': 'codigo',
                'Descrição': 'descricao',
                'Quantidade': 'quantidade',
                'Valor Total': 'valor_total'
            }
            df_relatorio = df_relatorio.sort_values(ordem_map[ordenar_por])
            
            # Resumo
            st.markdown("### 📊 Resumo do Inventário")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Itens", len(df_relatorio))
            with col2:
                st.metric("Quantidade Total", f"{df_relatorio['quantidade'].sum():,}")
            with col3:
                st.metric("Valor Total", f"R$ {df_relatorio['valor_total'].sum():,.2f}")
            with col4:
                itens_criticos = len(df_relatorio[df_relatorio['quantidade'] < df_relatorio['estoque_minimo']])
                st.metric("Itens Críticos", itens_criticos)
            
            # Tabela do inventário
            st.markdown("### 📋 Detalhamento do Inventário")
            
            # Preparar dados para exibição
            df_exibir = df_relatorio[[
                'codigo', 'descricao', 'categoria', 'quantidade', 
                'unidade_medida', 'estoque_minimo', 'estoque_maximo',
                'valor_unitario', 'valor_total', 'localizacao'
            ]].copy()
            
            # Download do relatório
            csv = df_exibir.to_csv(index=False)
            st.download_button(
                label="📥 Baixar Relatório em CSV",
                data=csv,
                file_name=f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Exibir tabela
            st.dataframe(
                df_exibir,
                hide_index=True,
                column_config={
                    'codigo': 'Código',
                    'descricao': 'Descrição',
                    'categoria': 'Categoria',
                    'quantidade': st.column_config.NumberColumn('Qtd', format='%d'),
                    'unidade_medida': 'Un.',
                    'estoque_minimo': st.column_config.NumberColumn('Mín', format='%d'),
                    'estoque_maximo': st.column_config.NumberColumn('Máx', format='%d'),
                    'valor_unitario': st.column_config.NumberColumn('Valor Unit.', format='R$ %.2f'),
                    'valor_total': st.column_config.NumberColumn('Valor Total', format='R$ %.2f'),
                    'localizacao': 'Local'
                }
            )

# Manutenção
elif pagina == "🔧 Manutenção":
    st.header("Manutenção de Peças")
    
    df_pecas = estoque_manager.buscar_pecas()
    
    if df_pecas.empty:
        st.warning("Nenhuma peça cadastrada para manutenção.")
    else:
        # Seleção da peça
        pecas_opcoes = df_pecas.apply(lambda x: f"{x['codigo']} - {x['descricao']}", axis=1).tolist()
        peca_selecionada = st.selectbox("Selecione a peça para editar", pecas_opcoes)
        
        if peca_selecionada:
            peca_index = pecas_opcoes.index(peca_selecionada)
            peca_info = df_pecas.iloc[peca_index]
            
            st.markdown("---")
            st.subheader(f"Editando: {peca_info['codigo']} - {peca_info['descricao']}")
            
            # Formulário de edição
            with st.form("form_edicao"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nova_descricao = st.text_input("Descrição", value=peca_info['descricao'])
                    nova_categoria = st.selectbox(
                        "Categoria", 
                        ["", "Eletrônico", "Mecânico", "Hidráulico", "Elétrico", "Outros"],
                        index=["", "Eletrônico", "Mecânico", "Hidráulico", "Elétrico", "Outros"].index(peca_info['categoria'] or "")
                    )
                    nova_unidade = st.selectbox(
                        "Unidade de Medida",
                        ["UN", "PC", "CX", "KG", "MT", "LT"],
                        index=["UN", "PC", "CX", "KG", "MT", "LT"].index(peca_info['unidade_medida'])
                    )
                
                with col2:
                    novo_minimo = st.number_input("Estoque Mínimo", min_value=0, value=int(peca_info['estoque_minimo']))
                    novo_maximo = st.number_input("Estoque Máximo", min_value=0, value=int(peca_info['estoque_maximo']))
                    novo_valor = st.number_input("Valor Unitário (R$)", min_value=0.0, value=float(peca_info['valor_unitario']), format="%.2f")
                
                nova_localizacao = st.text_input("Localização", value=peca_info['localizacao'] or "")
                
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    submitted = st.form_submit_button("💾 Salvar Alterações", type="primary")
                with col2:
                    deletar = st.form_submit_button("🗑️ Excluir Peça", type="secondary")
                
                if submitted:
                    if novo_minimo > novo_maximo:
                        mostrar_mensagem("error", "Estoque mínimo não pode ser maior que o máximo!")
                    else:
                        sucesso, mensagem = estoque_manager.atualizar_peca(
                            peca_id=peca_info['id'],
                            descricao=nova_descricao,
                            estoque_minimo=novo_minimo,
                            estoque_maximo=novo_maximo,
                            localizacao=nova_localizacao if nova_localizacao else None,
                            categoria=nova_categoria if nova_categoria else None,
                            unidade_medida=nova_unidade,
                            valor_unitario=novo_valor
                        )
                        
                        if sucesso:
                            mostrar_mensagem("success", mensagem)
                            st.balloons()
                            st.rerun()
                        else:
                            mostrar_mensagem("error", mensagem)
                
                if deletar:
                    # Confirmar exclusão
                    if st.session_state.get('confirmar_exclusao', False):
                        try:
                            with db_manager.get_connection() as conn:
                                cursor = conn.cursor()
                                # Verificar se há movimentações
                                cursor.execute('SELECT COUNT(*) as total FROM movimentacoes WHERE peca_id = ?', (peca_info['id'],))
                                movimentacoes = cursor.fetchone()['total']
                                
                                if movimentacoes > 0:
                                    mostrar_mensagem("error", f"Não é possível excluir! Existem {movimentacoes} movimentações registradas para esta peça.")
                                else:
                                    cursor.execute('DELETE FROM pecas WHERE id = ?', (peca_info['id'],))
                                    conn.commit()
                                    mostrar_mensagem("success", "Peça excluída com sucesso!")
                                    st.session_state['confirmar_exclusao'] = False
                                    st.rerun()
                        except Exception as e:
                            mostrar_mensagem("error", f"Erro ao excluir peça: {str(e)}")
                    else:
                        st.session_state['confirmar_exclusao'] = True
                        st.warning("⚠️ Clique novamente em 'Excluir Peça' para confirmar a exclusão!")

# Importar/Exportar
elif pagina == "📁 Importar/Exportar":
    st.header("Importar/Exportar Dados")
    
    tab1, tab2 = st.tabs(["📥 Importar", "📤 Exportar"])
    
    with tab1:
        st.subheader("Importar Peças")
        
        st.info("""
        ### 📋 Formato do arquivo CSV:
        O arquivo deve conter as seguintes colunas obrigatórias:
        - **codigo**: Código único da peça
        - **descricao**: Descrição da peça
        - **quantidade**: Quantidade em estoque
        - **estoque_minimo**: Estoque mínimo
        - **estoque_maximo**: Estoque máximo
        
        Colunas opcionais:
        - **localizacao**: Localização da peça
        - **categoria**: Categoria da peça
        - **unidade_medida**: Unidade de medida (padrão: UN)
        - **valor_unitario**: Valor unitário (padrão: 0.00)
        """)
        
        # Download do modelo
        modelo_df = pd.DataFrame({
            'codigo': ['PEC001', 'PEC002'],
            'descricao': ['Peça Exemplo 1', 'Peça Exemplo 2'],
            'quantidade': [10, 20],
            'estoque_minimo': [5, 10],
            'estoque_maximo': [50, 100],
            'localizacao': ['A-01', 'B-02'],
            'categoria': ['Eletrônico', 'Mecânico'],
            'unidade_medida': ['UN', 'PC'],
            'valor_unitario': [15.50, 25.00]
        })
        
        csv_modelo = modelo_df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Modelo CSV",
            data=csv_modelo,
            file_name="modelo_importacao_pecas.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # Upload do arquivo
        uploaded_file = st.file_uploader("Escolha o arquivo CSV", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df_import = pd.read_csv(uploaded_file)
                
                st.subheader("📋 Prévia dos dados")
                st.dataframe(df_import.head(10))
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🚀 Importar Dados", type="primary"):
                        with st.spinner("Importando dados..."):
                            sucessos, falhas, erros = estoque_manager.importar_pecas(df_import)
                        
                        if sucessos > 0:
                            mostrar_mensagem("success", f"✅ {sucessos} peças importadas com sucesso!")
                        
                        if falhas > 0:
                            mostrar_mensagem("warning", f"⚠️ {falhas} peças não foram importadas")
                            
                            if erros:
                                with st.expander("Ver detalhes dos erros"):
                                    for erro in erros[:10]:  # Mostrar até 10 erros
                                        st.text(erro)
                                    if len(erros) > 10:
                                        st.text(f"... e mais {len(erros) - 10} erros")
                        
                        if sucessos > 0:
                            st.balloons()
                
            except Exception as e:
                mostrar_mensagem("error", f"Erro ao ler arquivo: {str(e)}")
    
    with tab2:
        st.subheader("Exportar Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📦 Exportar Peças")
            st.write("Baixe todos os dados de peças cadastradas no sistema.")
            
            pecas_df, _ = estoque_manager.exportar_dados()
            
            if not pecas_df.empty:
                csv_pecas = pecas_df.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar Peças (CSV)",
                    data=csv_pecas,
                    file_name=f"pecas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.info(f"Total de {len(pecas_df)} peças disponíveis para exportação")
            else:
                st.warning("Nenhuma peça cadastrada para exportar")
        
        with col2:
            st.markdown("### 📊 Exportar Movimentações")
            st.write("Baixe o histórico completo de movimentações.")
            
            _, mov_df = estoque_manager.exportar_dados()
            
            if not mov_df.empty:
                csv_mov = mov_df.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar Movimentações (CSV)",
                    data=csv_mov,
                    file_name=f"movimentacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.info(f"Total de {len(mov_df)} movimentações disponíveis para exportação")
            else:
                st.warning("Nenhuma movimentação registrada para exportar")
        
        st.markdown("---")
        
        # Backup completo
        st.subheader("💾 Backup Completo")
        st.write("Faça o download de um backup completo do sistema (peças + movimentações)")
        
        if st.button("🔄 Gerar Backup Completo", type="primary"):
            pecas_df, mov_df = estoque_manager.exportar_dados()
            
            # Criar um arquivo Excel com múltiplas abas
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pecas_df.to_excel(writer, sheet_name='Peças', index=False)
                mov_df.to_excel(writer, sheet_name='Movimentações', index=False)
                
                # Adicionar formatação
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BD',
                    'border': 1
                })
                
                # Formatar cabeçalhos
                for sheet_name in ['Peças', 'Movimentações']:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_row(0, 20, header_format)
            
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Baixar Backup Completo (Excel)",
                data=excel_data,
                file_name=f"backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            mostrar_mensagem("success", "Backup gerado com sucesso!")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>SIG CFA 112 - Sistema de Gestão de Estoque v2.0</p>
        <p>Desenvolvido por Matheus Martins Lopes usando Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)