import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import hashlib
import time
from typing import Dict, List, Tuple, Optional
import random

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS customizados
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
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .alert-info {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# Classe para gerenciamento de dados
class EstoqueManager:
    def __init__(self):
        self.data_file = "estoque_data.json"
        self.load_data()
        
    def load_data(self):
        """Carrega dados do arquivo ou cria dados iniciais"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.produtos = pd.DataFrame(data['produtos'])
                self.movimentacoes = pd.DataFrame(data['movimentacoes'])
                self.usuarios = data['usuarios']
        else:
            # Dados iniciais baseados na planilha
            self.produtos = pd.DataFrame({
                'codigo': [888443216, 888443206, 860144291, 829341254, 870135114, 
                          888489147, 888487020, 870110216, 888487023, 888489008,
                          860604041, 861590054, 860144031, 829228753, 860123728,
                          870145770, 870110110, 888316221, 860123552, 860123870,
                          877744152, 850144502, 940212331, 888308765, 888314728,
                          870180061, 888317803, 888443215, 829300605, 888443205,
                          860123553, 888306715, 860144710, 829228817, 888306713,
                          829341253, 888351027, 888316036, 888316009, 870123411,
                          860198377, 829286002, 829285188, 829284605, 829247981,
                          829340874, 829213085, 829248898, 829247920, 870123419],
                'descricao': ['CABEÇA ARTICULADA 16XM16LH', 'CABEÇA ARTICULADA 16XM16', 
                             'VÁLVULA PILOTO 500MM', 'CORREIA DENTADA', 'POLIA DE DESVIO',
                             'TUBO DE PLÁSTICO 8X1 -PA 11 W-GN', 'UNIÃO ANGULAR C8X1/8',
                             'ANILHA DE BORRACHA', 'UNIÃO ANGULAR', 'TUBO DE PLÁSTICO 6X1',
                             'EXAUSTOR CB6 FA. ACLA', 'JGO. PEÇAS DESGASTE FUER 861590053',
                             'SILENCIADOR G 1-8', 'ANEL DE RETENÇÃO', 'ENCAIXE DO FILTRO 55X4; 90-110',
                             'BIGORNA CFA112 RS COMPLETE', 'CILINDRO', 'ANEL DE RETENÇÃO',
                             'O-RING 6X1,5 - NBR', 'O-RING ASSÉPTICO 152 X 5',
                             'VÁLV. DISTRIB. 5/2 V581-ISO1', 'CORPO DA VÁLVULA 5-2MONOSTABLE VDMA01',
                             'CORPO DA VÁLVULA 5-3 GESCHL. VDMA01', 'ARRUELA DE PRESSÃO B10',
                             'PINO CILÍNDRICO 4X16', 'ROLO CASTER ROLL.501RL2CG',
                             'DISCO A 5,3-X12', 'CABEÇA ARTICULADA 10XM10LH', 'FACA',
                             'CABEÇA ARTICULADA 10XM10', 'O-RING 16X3 - EPDM',
                             'PORCA SEXTAVADA M10-A2', 'SILENCIADOR G 3-8', 'ANEL DE RETENÇÃO',
                             'PORCA SEXTAVADA M6-A2', 'ROLAMENTO DE ESFERA',
                             'ROLAMENTO DE ESFERAS ESTRIADA 6302-2RS1', 'ANEL DE RETENÇÃO',
                             'ANEL DE RETENÇÃO', 'O-RING 24,77X5,33', 'BATERIA S7-400 SPEKTRUM',
                             'BORRACHA', 'TAÇA DE ASPIRAÇÃO', 'RODA DENTADA Z=24 D=25X25',
                             'CILINDRO PNEUMÁTICO', 'SILENCIADOR', 'MOLA DE PRESSÃO',
                             'POLIA DE DESVIO', 'TAPETE TRANSPORTADOR B=400MM L=3950MM',
                             'FOLE DE PASSAGEM'],
                'quantidade': [3, 3, 17, 2, 1, 6, 9, 4, 8, 12, 24, 1, 5, 2, 1, 1, 4, 6, 1, 1,
                              8, 8, 4, 4, 1, 2, 4, 1, 1, 1, 3, 3, 14, 5, 4, 2, 2, 1, 1, 1, 2,
                              1, 4, 7, 2, 1, 2, 3, 0, 5],
                'valor_unitario': [233.09, 287.19, 1243.55, 2400.17, 1045.95, 20.36, 36.73,
                                  26.16, 66.78, 42.62, 78.98, 5154.86, 37.83, 14.99, 213.06,
                                  14941.33, 10089.93, 23.39, 5.09, 87.74, 1167.65, 993.46,
                                  2980.39, 0.47, 5.52, 154.22, 0.21, 201.63, 1431.05, 174.84,
                                  39.89, 0.89, 64.36, 28.37, 0.21, 1744.20, 115.78, 44.82,
                                  1.91, 70.25, 191.87, 112.12, 196.04, 283.03, 728.90, 456.67,
                                  112.12, 9513.96, 0, 6814.81],
                'estoque_minimo': [2, 2, 10, 1, 1, 4, 6, 3, 5, 8, 15, 1, 3, 2, 1, 1, 2, 4,
                                  1, 1, 5, 5, 2, 3, 1, 1, 3, 1, 1, 1, 2, 2, 10, 3, 3, 1,
                                  1, 1, 1, 1, 1, 1, 3, 5, 1, 1, 1, 2, 1, 3],
                'estoque_maximo': [10, 10, 50, 5, 3, 15, 20, 10, 20, 30, 50, 3, 15, 5, 3,
                                  2, 10, 15, 3, 3, 20, 20, 10, 10, 3, 5, 10, 3, 3, 3, 10,
                                  10, 30, 15, 10, 5, 5, 3, 3, 3, 5, 3, 10, 20, 5, 3, 5,
                                  10, 2, 15],
                'categoria': ['Mecânica', 'Mecânica', 'Pneumática', 'Mecânica', 'Mecânica',
                             'Pneumática', 'Pneumática', 'Vedação', 'Pneumática', 'Pneumática',
                             'Elétrica', 'Manutenção', 'Pneumática', 'Mecânica', 'Filtração',
                             'Equipamento', 'Pneumática', 'Mecânica', 'Vedação', 'Vedação',
                             'Pneumática', 'Pneumática', 'Pneumática', 'Mecânica', 'Mecânica',
                             'Mecânica', 'Mecânica', 'Mecânica', 'Ferramenta', 'Mecânica',
                             'Vedação', 'Mecânica', 'Pneumática', 'Mecânica', 'Mecânica',
                             'Mecânica', 'Mecânica', 'Mecânica', 'Mecânica', 'Vedação',
                             'Elétrica', 'Vedação', 'Mecânica', 'Mecânica', 'Pneumática',
                             'Pneumática', 'Mecânica', 'Mecânica', 'Transporte', 'Mecânica'],
                'localizacao': [f"A{i%10+1}-{(i//10)+1}" for i in range(50)],
                'fornecedor': ['Fornecedor ' + str((i % 5) + 1) for i in range(50)],
                'tempo_reposicao': [random.randint(5, 30) for _ in range(50)]
            })
            
            # Calcula valor total
            self.produtos['valor_total'] = self.produtos['quantidade'] * self.produtos['valor_unitario']
            
            # Movimentações iniciais vazias
            self.movimentacoes = pd.DataFrame(columns=['data', 'codigo', 'tipo', 'quantidade', 
                                                      'usuario', 'observacao'])
            
            # Usuários padrão
            self.usuarios = {
                'admin': self._hash_password('admin123'),
                'operador': self._hash_password('oper123')
            }
            
            self.save_data()
    
    def save_data(self):
        """Salva dados no arquivo"""
        data = {
            'produtos': self.produtos.to_dict('records'),
            'movimentacoes': self.movimentacoes.to_dict('records'),
            'usuarios': self.usuarios
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash de senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Autentica usuário"""
        if username in self.usuarios:
            return self.usuarios[username] == self._hash_password(password)
        return False
    
    def add_user(self, username: str, password: str) -> bool:
        """Adiciona novo usuário"""
        if username not in self.usuarios:
            self.usuarios[username] = self._hash_password(password)
            self.save_data()
            return True
        return False
    
    def get_produto(self, codigo: int) -> Optional[pd.Series]:
        """Busca produto por código"""
        produto = self.produtos[self.produtos['codigo'] == codigo]
        return produto.iloc[0] if not produto.empty else None
    
    def update_estoque(self, codigo: int, quantidade: int, tipo: str, usuario: str, observacao: str = ""):
        """Atualiza estoque e registra movimentação"""
        idx = self.produtos[self.produtos['codigo'] == codigo].index
        if len(idx) > 0:
            idx = idx[0]
            if tipo == 'entrada':
                self.produtos.loc[idx, 'quantidade'] += quantidade
            else:  # saída
                if self.produtos.loc[idx, 'quantidade'] >= quantidade:
                    self.produtos.loc[idx, 'quantidade'] -= quantidade
                else:
                    return False
            
            # Atualiza valor total
            self.produtos.loc[idx, 'valor_total'] = (
                self.produtos.loc[idx, 'quantidade'] * self.produtos.loc[idx, 'valor_unitario']
            )
            
            # Registra movimentação
            nova_mov = pd.DataFrame([{
                'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'codigo': codigo,
                'tipo': tipo,
                'quantidade': quantidade,
                'usuario': usuario,
                'observacao': observacao
            }])
            self.movimentacoes = pd.concat([self.movimentacoes, nova_mov], ignore_index=True)
            
            self.save_data()
            return True
        return False
    
    def get_alertas(self) -> Dict[str, List[pd.Series]]:
        """Retorna produtos com alertas de estoque"""
        alertas = {
            'critico': [],
            'baixo': [],
            'excesso': []
        }
        
        for idx, produto in self.produtos.iterrows():
            if produto['quantidade'] == 0:
                alertas['critico'].append(produto)
            elif produto['quantidade'] < produto['estoque_minimo']:
                alertas['baixo'].append(produto)
            elif produto['quantidade'] > produto['estoque_maximo']:
                alertas['excesso'].append(produto)
        
        return alertas
    
    def get_estatisticas(self) -> Dict:
        """Calcula estatísticas do estoque"""
        total_produtos = len(self.produtos)
        valor_total = self.produtos['valor_total'].sum()
        produtos_zerados = len(self.produtos[self.produtos['quantidade'] == 0])
        produtos_baixo = len(self.produtos[self.produtos['quantidade'] < self.produtos['estoque_minimo']])
        
        # Movimentações do mês
        if not self.movimentacoes.empty:
            self.movimentacoes['data'] = pd.to_datetime(self.movimentacoes['data'])
            mes_atual = datetime.now().replace(day=1)
            mov_mes = self.movimentacoes[self.movimentacoes['data'] >= mes_atual]
            entradas_mes = len(mov_mes[mov_mes['tipo'] == 'entrada'])
            saidas_mes = len(mov_mes[mov_mes['tipo'] == 'saida'])
        else:
            entradas_mes = 0
            saidas_mes = 0
        
        return {
            'total_produtos': total_produtos,
            'valor_total': valor_total,
            'produtos_zerados': produtos_zerados,
            'produtos_baixo': produtos_baixo,
            'entradas_mes': entradas_mes,
            'saidas_mes': saidas_mes
        }
    
    def get_produtos_reposicao(self) -> pd.DataFrame:
        """Retorna produtos que precisam reposição"""
        produtos_repo = self.produtos[
            self.produtos['quantidade'] <= self.produtos['estoque_minimo']
        ].copy()
        
        produtos_repo['quantidade_repor'] = (
            produtos_repo['estoque_maximo'] - produtos_repo['quantidade']
        )
        produtos_repo['valor_reposicao'] = (
            produtos_repo['quantidade_repor'] * produtos_repo['valor_unitario']
        )
        
        return produtos_repo.sort_values('quantidade')
    
    def buscar_produtos(self, termo: str) -> pd.DataFrame:
        """Busca produtos por código ou descrição"""
        if termo.isdigit():
            return self.produtos[self.produtos['codigo'] == int(termo)]
        else:
            return self.produtos[
                self.produtos['descricao'].str.contains(termo, case=False, na=False)
            ]
    
    def get_movimentacoes_produto(self, codigo: int, dias: int = 30) -> pd.DataFrame:
        """Retorna movimentações de um produto"""
        if self.movimentacoes.empty:
            return pd.DataFrame()
        
        mov_produto = self.movimentacoes[self.movimentacoes['codigo'] == codigo].copy()
        if not mov_produto.empty:
            mov_produto['data'] = pd.to_datetime(mov_produto['data'])
            data_limite = datetime.now() - timedelta(days=dias)
            return mov_produto[mov_produto['data'] >= data_limite].sort_values('data', ascending=False)
        return pd.DataFrame()

# Funções auxiliares
def init_session_state():
    """Inicializa variáveis de sessão"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'estoque_manager' not in st.session_state:
        st.session_state.estoque_manager = EstoqueManager()

def login_page():
    """Página de login"""
    st.markdown('<h1 class="main-header">🔐 Login - Sistema de Gestão de Estoque</h1>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                if st.session_state.estoque_manager.authenticate(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")
        
        st.info("Usuários padrão: admin/admin123 ou operador/oper123")

def dashboard_page():
    """Página principal - Dashboard"""
    st.markdown('<h1 class="main-header">📊 Dashboard - Sistema de Gestão de Estoque</h1>', 
                unsafe_allow_html=True)
    
    # Estatísticas
    stats = st.session_state.estoque_manager.get_estatisticas()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Produtos", stats['total_produtos'])
    with col2:
        st.metric("Valor Total", f"R$ {stats['valor_total']:,.2f}")
    with col3:
        st.metric("Produtos Zerados", stats['produtos_zerados'], 
                 delta=f"-{stats['produtos_zerados']}" if stats['produtos_zerados'] > 0 else "0")
    with col4:
        st.metric("Abaixo do Mínimo", stats['produtos_baixo'],
                 delta=f"-{stats['produtos_baixo']}" if stats['produtos_baixo'] > 0 else "0")
    
    st.markdown("---")
    
    # Alertas
    st.subheader("🚨 Alertas de Estoque")
    alertas = st.session_state.estoque_manager.get_alertas()
    
    if alertas['critico']:
        st.markdown('<div class="alert-box alert-critical">', unsafe_allow_html=True)
        st.markdown("**⚠️ CRÍTICO - Produtos sem estoque:**")
        for produto in alertas['critico']:
            st.write(f"- {produto['codigo']} - {produto['descricao']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if alertas['baixo']:
        st.markdown('<div class="alert-box alert-warning">', unsafe_allow_html=True)
        st.markdown("**⚡ ATENÇÃO - Estoque baixo:**")
        for produto in alertas['baixo']:
            st.write(f"- {produto['codigo']} - {produto['descricao']} (Qtd: {produto['quantidade']})")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if alertas['excesso']:
        st.markdown('<div class="alert-box alert-info">', unsafe_allow_html=True)
        st.markdown("**📦 Estoque em excesso:**")
        for produto in alertas['excesso']:
            st.write(f"- {produto['codigo']} - {produto['descricao']} (Qtd: {produto['quantidade']})")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráficos
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Produtos por Categoria")
        cat_counts = st.session_state.estoque_manager.produtos['categoria'].value_counts()
        st.bar_chart(cat_counts)
    
    with col2:
        st.subheader("💰 Valor por Categoria")
        cat_values = st.session_state.estoque_manager.produtos.groupby('categoria')['valor_total'].sum()
        st.bar_chart(cat_values)

def consulta_estoque_page():
    """Página de consulta de estoque"""
    st.markdown('<h1 class="main-header">🔍 Consulta de Estoque</h1>', unsafe_allow_html=True)
    
    # Busca
    col1, col2 = st.columns([3, 1])
    with col1:
        termo_busca = st.text_input("Buscar por código ou descrição:", 
                                   placeholder="Digite o código ou parte da descrição...")
    with col2:
        st.write("")
        st.write("")
        buscar = st.button("🔍 Buscar", use_container_width=True)
    
    # Filtros
    with st.expander("Filtros Avançados"):
        col1, col2, col3 = st.columns(3)
        with col1:
            categorias = ['Todas'] + list(st.session_state.estoque_manager.produtos['categoria'].unique())
            categoria_filtro = st.selectbox("Categoria", categorias)
        with col2:
            fornecedores = ['Todos'] + list(st.session_state.estoque_manager.produtos['fornecedor'].unique())
            fornecedor_filtro = st.selectbox("Fornecedor", fornecedores)
        with col3:
            status_filtro = st.selectbox("Status", 
                                        ['Todos', 'Normal', 'Estoque Baixo', 'Sem Estoque', 'Excesso'])
    
    # Resultados
    df_filtrado = st.session_state.estoque_manager.produtos.copy()
    
    if termo_busca and buscar:
        df_filtrado = st.session_state.estoque_manager.buscar_produtos(termo_busca)
    
    if categoria_filtro != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]
    
    if fornecedor_filtro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['fornecedor'] == fornecedor_filtro]
    
    if status_filtro != 'Todos':
        if status_filtro == 'Normal':
            df_filtrado = df_filtrado[
                (df_filtrado['quantidade'] > df_filtrado['estoque_minimo']) &
                (df_filtrado['quantidade'] <= df_filtrado['estoque_maximo'])
            ]
        elif status_filtro == 'Estoque Baixo':
            df_filtrado = df_filtrado[
                (df_filtrado['quantidade'] > 0) &
                (df_filtrado['quantidade'] <= df_filtrado['estoque_minimo'])
            ]
        elif status_filtro == 'Sem Estoque':
            df_filtrado = df_filtrado[df_filtrado['quantidade'] == 0]
        elif status_filtro == 'Excesso':
            df_filtrado = df_filtrado[df_filtrado['quantidade'] > df_filtrado['estoque_maximo']]
    
    # Exibição dos resultados
    st.subheader(f"Resultados ({len(df_filtrado)} produtos)")
    
    if not df_filtrado.empty:
        # Formatar valores
        df_display = df_filtrado[['codigo', 'descricao', 'quantidade', 'estoque_minimo', 
                                 'estoque_maximo', 'valor_unitario', 'valor_total', 
                                 'categoria', 'localizacao']].copy()
        
        df_display['valor_unitario'] = df_display['valor_unitario'].apply(lambda x: f"R$ {x:,.2f}")
        df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Download
        csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f"estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum produto encontrado com os critérios selecionados.")

def movimentacao_page():
    """Página de movimentação de estoque"""
    st.markdown('<h1 class="main-header">📦 Movimentação de Estoque</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Nova Movimentação", "Histórico"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção de produto
            produtos_list = st.session_state.estoque_manager.produtos[['codigo', 'descricao']].values
            produto_options = [f"{p[0]} - {p[1]}" for p in produtos_list]
            produto_selecionado = st.selectbox("Produto", produto_options)
            
            if produto_selecionado:
                codigo = int(produto_selecionado.split(' - ')[0])
                produto = st.session_state.estoque_manager.get_produto(codigo)
                
                if produto is not None:
                    st.info(f"Estoque atual: {produto['quantidade']} unidades")
                    st.info(f"Localização: {produto['localizacao']}")
        
        with col2:
            tipo_mov = st.radio("Tipo de Movimentação", ["entrada", "saida"])
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
            observacao = st.text_area("Observação")
        
        if st.button("✅ Confirmar Movimentação", use_container_width=True):
            if produto_selecionado:
                codigo = int(produto_selecionado.split(' - ')[0])
                
                if st.session_state.estoque_manager.update_estoque(
                    codigo, quantidade, tipo_mov, st.session_state.username, observacao
                ):
                    st.success(f"Movimentação de {tipo_mov} realizada com sucesso!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Erro: Quantidade insuficiente em estoque!")
    
    with tab2:
        st.subheader("Histórico de Movimentações")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            dias_historico = st.selectbox("Período", [7, 15, 30, 60, 90], index=2)
        with col2:
            tipo_filtro = st.selectbox("Tipo", ["Todos", "entrada", "saida"])
        with col3:
            produto_filtro = st.selectbox("Produto", ["Todos"] + produto_options)
        
        # Exibir histórico
        if not st.session_state.estoque_manager.movimentacoes.empty:
            df_mov = st.session_state.estoque_manager.movimentacoes.copy()
            df_mov['data'] = pd.to_datetime(df_mov['data'])
            
            # Aplicar filtros
            data_limite = datetime.now() - timedelta(days=dias_historico)
            df_mov = df_mov[df_mov['data'] >= data_limite]
            
            if tipo_filtro != "Todos":
                df_mov = df_mov[df_mov['tipo'] == tipo_filtro]
            
            if produto_filtro != "Todos":
                codigo_filtro = int(produto_filtro.split(' - ')[0])
                df_mov = df_mov[df_mov['codigo'] == codigo_filtro]
            
            if not df_mov.empty:
                # Adicionar descrição do produto
                df_mov = df_mov.merge(
                    st.session_state.estoque_manager.produtos[['codigo', 'descricao']], 
                    on='codigo', 
                    how='left'
                )
                
                # Formatar data
                df_mov['data'] = df_mov['data'].dt.strftime('%d/%m/%Y %H:%M')
                
                # Reordenar colunas
                df_mov = df_mov[['data', 'codigo', 'descricao', 'tipo', 'quantidade', 
                               'usuario', 'observacao']]
                
                st.dataframe(df_mov.sort_values('data', ascending=False), 
                           use_container_width=True, height=400)
            else:
                st.info("Nenhuma movimentação encontrada no período selecionado.")
        else:
            st.info("Ainda não há movimentações registradas.")

def relatorios_page():
    """Página de relatórios"""
    st.markdown('<h1 class="main-header">📊 Relatórios</h1>', unsafe_allow_html=True)
    
    tipo_relatorio = st.selectbox(
        "Selecione o tipo de relatório:",
        ["Produtos para Reposição", "Análise ABC", "Movimentações por Período", 
         "Inventário Completo", "Análise de Fornecedores"]
    )
    
    if tipo_relatorio == "Produtos para Reposição":
        st.subheader("📋 Produtos que Necessitam Reposição")
        
        df_repo = st.session_state.estoque_manager.get_produtos_reposicao()
        
        if not df_repo.empty:
            # Resumo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Produtos", len(df_repo))
            with col2:
                st.metric("Valor Total de Reposição", 
                         f"R$ {df_repo['valor_reposicao'].sum():,.2f}")
            with col3:
                st.metric("Urgentes (Zerados)", 
                         len(df_repo[df_repo['quantidade'] == 0]))
            
            # Tabela
            df_display = df_repo[['codigo', 'descricao', 'quantidade', 'estoque_minimo', 
                                 'quantidade_repor', 'valor_unitario', 'valor_reposicao', 
                                 'fornecedor', 'tempo_reposicao']].copy()
            
            df_display['valor_unitario'] = df_display['valor_unitario'].apply(lambda x: f"R$ {x:,.2f}")
            df_display['valor_reposicao'] = df_display['valor_reposicao'].apply(lambda x: f"R$ {x:,.2f}")
            
            st.dataframe(df_display, use_container_width=True)
            
            # Gerar pedido
            if st.button("📄 Gerar Pedido de Compra"):
                pedido_text = f"""
PEDIDO DE COMPRA - {datetime.now().strftime('%d/%m/%Y')}
{'='*50}

RESUMO:
- Total de itens: {len(df_repo)}
- Valor total estimado: R$ {df_repo['valor_reposicao'].sum():,.2f}

ITENS:
"""
                for _, item in df_repo.iterrows():
                    pedido_text += f"\nCódigo: {item['codigo']}\n"
                    pedido_text += f"Descrição: {item['descricao']}\n"
                    pedido_text += f"Quantidade: {item['quantidade_repor']} unidades\n"
                    pedido_text += f"Fornecedor: {item['fornecedor']}\n"
                    pedido_text += f"Prazo estimado: {item['tempo_reposicao']} dias\n"
                    pedido_text += "-" * 30
                
                st.download_button(
                    label="💾 Baixar Pedido",
                    data=pedido_text,
                    file_name=f"pedido_compra_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
        else:
            st.success("✅ Todos os produtos estão com estoque adequado!")
    
    elif tipo_relatorio == "Análise ABC":
        st.subheader("📊 Análise ABC - Curva de Pareto")
        
        df_abc = st.session_state.estoque_manager.produtos.copy()
        df_abc = df_abc.sort_values('valor_total', ascending=False)
        df_abc['percentual'] = (df_abc['valor_total'] / df_abc['valor_total'].sum()) * 100
        df_abc['percentual_acumulado'] = df_abc['percentual'].cumsum()
        
        # Classificação ABC
        df_abc['classe'] = 'C'
        df_abc.loc[df_abc['percentual_acumulado'] <= 80, 'classe'] = 'A'
        df_abc.loc[(df_abc['percentual_acumulado'] > 80) & 
                   (df_abc['percentual_acumulado'] <= 95), 'classe'] = 'B'
        
        # Resumo
        col1, col2, col3 = st.columns(3)
        with col1:
            classe_a = df_abc[df_abc['classe'] == 'A']
            st.metric("Classe A", f"{len(classe_a)} produtos",
                     f"{classe_a['percentual'].sum():.1f}% do valor")
        with col2:
            classe_b = df_abc[df_abc['classe'] == 'B']
            st.metric("Classe B", f"{len(classe_b)} produtos",
                     f"{classe_b['percentual'].sum():.1f}% do valor")
        with col3:
            classe_c = df_abc[df_abc['classe'] == 'C']
            st.metric("Classe C", f"{len(classe_c)} produtos",
                     f"{classe_c['percentual'].sum():.1f}% do valor")
        
        # Gráfico
        st.line_chart(df_abc['percentual_acumulado'].values)
        
        # Tabela
        df_display = df_abc[['codigo', 'descricao', 'valor_total', 'percentual', 
                            'percentual_acumulado', 'classe']].head(20)
        df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        df_display['percentual'] = df_display['percentual'].apply(lambda x: f"{x:.2f}%")
        df_display['percentual_acumulado'] = df_display['percentual_acumulado'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(df_display, use_container_width=True)
    
    elif tipo_relatorio == "Movimentações por Período":
        st.subheader("📅 Análise de Movimentações")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Inicial", 
                                       value=datetime.now() - timedelta(days=30))
        with col2:
            data_fim = st.date_input("Data Final", value=datetime.now())
        
        if not st.session_state.estoque_manager.movimentacoes.empty:
            df_mov = st.session_state.estoque_manager.movimentacoes.copy()
            df_mov['data'] = pd.to_datetime(df_mov['data'])
            
            # Filtrar período
            df_mov = df_mov[(df_mov['data'].dt.date >= data_inicio) & 
                           (df_mov['data'].dt.date <= data_fim)]
            
            if not df_mov.empty:
                # Resumo
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Movimentações", len(df_mov))
                with col2:
                    st.metric("Entradas", len(df_mov[df_mov['tipo'] == 'entrada']))
                with col3:
                    st.metric("Saídas", len(df_mov[df_mov['tipo'] == 'saida']))
                
                # Produtos mais movimentados
                st.subheader("Top 10 Produtos Mais Movimentados")
                top_produtos = df_mov.groupby('codigo')['quantidade'].sum().sort_values(ascending=False).head(10)
                
                # Adicionar descrições
                top_df = pd.DataFrame(top_produtos).reset_index()
                top_df = top_df.merge(
                    st.session_state.estoque_manager.produtos[['codigo', 'descricao']], 
                    on='codigo'
                )
                st.bar_chart(top_df.set_index('descricao')['quantidade'])
            else:
                st.info("Nenhuma movimentação encontrada no período selecionado.")
        else:
            st.info("Ainda não há movimentações registradas.")
    
    elif tipo_relatorio == "Inventário Completo":
        st.subheader("📦 Inventário Completo")
        
        df_inv = st.session_state.estoque_manager.produtos.copy()
        
        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de SKUs", len(df_inv))
        with col2:
            st.metric("Valor Total", f"R$ {df_inv['valor_total'].sum():,.2f}")
        with col3:
            st.metric("Itens em Estoque", df_inv['quantidade'].sum())
        with col4:
            st.metric("Valor Médio/Item", f"R$ {df_inv['valor_total'].sum() / len(df_inv):,.2f}")
        
        # Gerar relatório PDF simulado
        if st.button("📄 Gerar Relatório Completo"):
            relatorio_text = f"""
RELATÓRIO DE INVENTÁRIO - {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*80}

RESUMO EXECUTIVO:
- Total de produtos cadastrados: {len(df_inv)}
- Valor total do estoque: R$ {df_inv['valor_total'].sum():,.2f}
- Total de itens: {df_inv['quantidade'].sum()}
- Produtos sem estoque: {len(df_inv[df_inv['quantidade'] == 0])}
- Produtos abaixo do mínimo: {len(df_inv[df_inv['quantidade'] < df_inv['estoque_minimo']])}

DETALHAMENTO POR CATEGORIA:
"""
            for cat in df_inv['categoria'].unique():
                cat_data = df_inv[df_inv['categoria'] == cat]
                relatorio_text += f"\n{cat}:\n"
                relatorio_text += f"  - Produtos: {len(cat_data)}\n"
                relatorio_text += f"  - Valor: R$ {cat_data['valor_total'].sum():,.2f}\n"
                relatorio_text += f"  - Quantidade: {cat_data['quantidade'].sum()}\n"
            
            st.download_button(
                label="💾 Baixar Relatório",
                data=relatorio_text,
                file_name=f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    elif tipo_relatorio == "Análise de Fornecedores":
        st.subheader("🏢 Análise de Fornecedores")
        
        df_forn = st.session_state.estoque_manager.produtos.groupby('fornecedor').agg({
            'codigo': 'count',
            'valor_total': 'sum',
            'quantidade': 'sum'
        }).reset_index()
        
        df_forn.columns = ['Fornecedor', 'Produtos', 'Valor Total', 'Quantidade']
        df_forn = df_forn.sort_values('Valor Total', ascending=False)
        
        # Gráfico
        st.bar_chart(df_forn.set_index('Fornecedor')['Valor Total'])
        
        # Tabela
        df_forn['Valor Total'] = df_forn['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(df_forn, use_container_width=True)

def configuracoes_page():
    """Página de configurações"""
    st.markdown('<h1 class="main-header">⚙️ Configurações</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Usuários", "Sistema", "Backup"])
    
    with tab1:
        st.subheader("Gerenciamento de Usuários")
        
        if st.session_state.username == 'admin':
            # Adicionar usuário
            with st.form("add_user"):
                st.write("**Adicionar Novo Usuário**")
                new_username = st.text_input("Nome de usuário")
                new_password = st.text_input("Senha", type="password")
                confirm_password = st.text_input("Confirmar senha", type="password")
                
                if st.form_submit_button("Adicionar Usuário"):
                    if new_password == confirm_password:
                        if st.session_state.estoque_manager.add_user(new_username, new_password):
                            st.success(f"Usuário {new_username} adicionado com sucesso!")
                        else:
                            st.error("Usuário já existe!")
                    else:
                        st.error("As senhas não coincidem!")
            
            # Listar usuários
            st.write("**Usuários Cadastrados:**")
            for user in st.session_state.estoque_manager.usuarios.keys():
                st.write(f"- {user}")
        else:
            st.warning("Apenas administradores podem gerenciar usuários.")
    
    with tab2:
        st.subheader("Configurações do Sistema")
        
        # Alertas
        st.write("**Configurações de Alertas**")
        col1, col2 = st.columns(2)
        with col1:
            alerta_critico = st.checkbox("Alertas de estoque crítico", value=True)
            alerta_baixo = st.checkbox("Alertas de estoque baixo", value=True)
        with col2:
            alerta_reposicao = st.checkbox("Alertas de reposição", value=True)
            alerta_excesso = st.checkbox("Alertas de excesso", value=True)
        
        # Parâmetros do sistema
        st.write("**Parâmetros do Sistema**")
        col1, col2 = st.columns(2)
        with col1:
            dias_historico = st.number_input("Dias de histórico para análise", 
                                           min_value=7, max_value=365, value=30)
            taxa_crescimento = st.slider("Taxa de crescimento esperada (%)", 
                                       min_value=-50, max_value=50, value=5)
        with col2:
            lead_time_padrao = st.number_input("Lead time padrão (dias)", 
                                             min_value=1, max_value=90, value=7)
            margem_seguranca = st.slider("Margem de segurança (%)", 
                                        min_value=0, max_value=100, value=20)
        
        # Exportar configurações
        if st.button("Salvar Configurações"):
            st.success("Configurações salvas com sucesso!")
            st.balloons()

# Função principal
def main():
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
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Título principal
    st.title("🏭 Sistema de Gestão de Estoque")
    st.markdown("---")
    
    # Inicializar dados
    if 'df' not in st.session_state:
        st.session_state.df = criar_dataframe_inicial()
    
    if 'historico' not in st.session_state:
        st.session_state.historico = gerar_historico_movimentacoes(st.session_state.df)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Menu Principal")
        
        # Seleção de página
        pagina = st.radio(
            "Navegação",
            ["Dashboard", "Gestão de Estoque", "Análises e Relatórios", 
             "Previsões", "Alertas", "Configurações"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Filtros globais
        st.subheader("🔍 Filtros Globais")
        
        # Filtro por categoria
        categorias = ["Todas"] + list(st.session_state.df['categoria'].unique())
        categoria_selecionada = st.selectbox("Categoria", categorias)
        
        # Filtro por faixa de valor
        valor_min, valor_max = st.slider(
            "Faixa de Valor Total (R$)",
            min_value=0,
            max_value=int(st.session_state.df['valor_total'].max()),
            value=(0, int(st.session_state.df['valor_total'].max())),
            format="R$ %d"
        )
        
        # Aplicar filtros
        df_filtrado = st.session_state.df.copy()
        if categoria_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_selecionada]
        df_filtrado = df_filtrado[
            (df_filtrado['valor_total'] >= valor_min) & 
            (df_filtrado['valor_total'] <= valor_max)
        ]
        
        # Informações do filtro
        st.info(f"📋 {len(df_filtrado)} itens selecionados")
        
        st.markdown("---")
        
        # Ações rápidas
        st.subheader("⚡ Ações Rápidas")
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.rerun()
        
        if st.button("📥 Exportar Relatório", use_container_width=True):
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        if st.button("🖨️ Imprimir", use_container_width=True):
            st.info("Preparando impressão...")
    
    # Renderizar página selecionada
    if pagina == "Dashboard":
        dashboard_principal(df_filtrado)
    elif pagina == "Gestão de Estoque":
        gestao_estoque(df_filtrado)
    elif pagina == "Análises e Relatórios":
        analises_relatorios(df_filtrado)
    elif pagina == "Previsões":
        previsoes_demanda(df_filtrado)
    elif pagina == "Alertas":
        sistema_alertas(df_filtrado)
    elif pagina == "Configurações":
        configuracoes()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("Sistema de Gestão de Estoque v1.0")
    with col2:
        st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    with col3:
        st.caption("© 2024 - Todos os direitos reservados")

# Executar aplicação
if __name__ == "__main__":
    main()
