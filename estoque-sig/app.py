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

# Configuração da página - DEVE SER O PRIMEIRO COMANDO STREAMLIT
st.set_page_config(
    page_title="Sistema de Gestão de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Tema principal */
    .stApp {
        background-color: #f5f5f5;
    }
    
    /* Cards de métricas */
    [data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Tabelas */
    .dataframe {
        font-size: 14px;
    }
    
    /* Botões personalizados */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #145a8d;
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Alertas customizados */
    .alert-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .alert-critical {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-left: 5px solid #ff9800;
    }
    
    .alert-info {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    
    /* Sidebar customizada */
    .css-1d391kg {
        background-color: #fafafa;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #333;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# [RESTO DO CÓDIGO CONTINUA IGUAL, MAS REMOVA A CONFIGURAÇÃO DUPLICADA NA FUNÇÃO main()]

class EstoqueManager:
    def __init__(self):
        self.estoque = {}
        self.historico = []
        self.usuarios = {
            "admin": {"senha": self.hash_senha("admin123"), "tipo": "Administrador"},
            "user": {"senha": self.hash_senha("user123"), "tipo": "Operador"}
        }
        self.inicializar_estoque()
    
    def hash_senha(self, senha: str) -> str:
        """Hash de senha para segurança"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def inicializar_estoque(self):
        """Inicializa estoque com dados de exemplo baseados na planilha"""
        dados_exemplo = [
            {"codigo": "001", "descricao": "ABRAÇADEIRA TIPO D 1/2", "unidade": "PÇ", 
             "quantidade": 50, "minimo": 10, "maximo": 100, "localizacao": "A-01", 
             "fornecedor": "Fornecedor A", "valor_unitario": 2.50},
            
            {"codigo": "002", "descricao": "ABRAÇADEIRA TIPO D 3/4", "unidade": "PÇ", 
             "quantidade": 30, "minimo": 15, "maximo": 80, "localizacao": "A-02", 
             "fornecedor": "Fornecedor A", "valor_unitario": 3.00},
            
            {"codigo": "003", "descricao": "ABRAÇADEIRA TIPO D 1", "unidade": "PÇ", 
             "quantidade": 5, "minimo": 20, "maximo": 60, "localizacao": "A-03", 
             "fornecedor": "Fornecedor A", "valor_unitario": 3.50},
            
            {"codigo": "004", "descricao": "ABRAÇADEIRA TIPO D 2", "unidade": "PÇ", 
             "quantidade": 25, "minimo": 10, "maximo": 50, "localizacao": "A-04", 
             "fornecedor": "Fornecedor B", "valor_unitario": 4.50},
            
            {"codigo": "005", "descricao": "ABRAÇADEIRA TIPO U 1/2", "unidade": "PÇ", 
             "quantidade": 100, "minimo": 30, "maximo": 200, "localizacao": "B-01", 
             "fornecedor": "Fornecedor B", "valor_unitario": 1.80},
            
            {"codigo": "006", "descricao": "ABRAÇADEIRA TIPO U 3/4", "unidade": "PÇ", 
             "quantidade": 75, "minimo": 25, "maximo": 150, "localizacao": "B-02", 
             "fornecedor": "Fornecedor C", "valor_unitario": 2.20},
            
            {"codigo": "007", "descricao": "PARAFUSO SEXTAVADO 1/2 x 2", "unidade": "PÇ", 
             "quantidade": 200, "minimo": 50, "maximo": 300, "localizacao": "C-01", 
             "fornecedor": "Fornecedor C", "valor_unitario": 0.50},
            
            {"codigo": "008", "descricao": "PORCA SEXTAVADA 1/2", "unidade": "PÇ", 
             "quantidade": 150, "minimo": 50, "maximo": 250, "localizacao": "C-02", 
             "fornecedor": "Fornecedor D", "valor_unitario": 0.30},
            
            {"codigo": "009", "descricao": "ARRUELA LISA 1/2", "unidade": "PÇ", 
             "quantidade": 180, "minimo": 100, "maximo": 300, "localizacao": "C-03", 
             "fornecedor": "Fornecedor D", "valor_unitario": 0.15},
            
            {"codigo": "010", "descricao": "BUCHA DE REDUÇÃO 1 x 3/4", "unidade": "PÇ", 
             "quantidade": 8, "minimo": 20, "maximo": 60, "localizacao": "D-01", 
             "fornecedor": "Fornecedor E", "valor_unitario": 5.00}
        ]
        
        for item in dados_exemplo:
            self.estoque[item["codigo"]] = {
                "descricao": item["descricao"],
                "unidade": item["unidade"],
                "quantidade": item["quantidade"],
                "minimo": item["minimo"],
                "maximo": item["maximo"],
                "localizacao": item["localizacao"],
                "fornecedor": item["fornecedor"],
                "valor_unitario": item["valor_unitario"],
                "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def autenticar_usuario(self, usuario: str, senha: str) -> bool:
        """Autentica usuário"""
        if usuario in self.usuarios:
            return self.usuarios[usuario]["senha"] == self.hash_senha(senha)
        return False
    
    def adicionar_item(self, codigo: str, descricao: str, unidade: str, 
                      quantidade: int, minimo: int, maximo: int, 
                      localizacao: str, fornecedor: str, valor_unitario: float) -> bool:
        """Adiciona novo item ao estoque"""
        if codigo in self.estoque:
            return False
        
        self.estoque[codigo] = {
            "descricao": descricao,
            "unidade": unidade,
            "quantidade": quantidade,
            "minimo": minimo,
            "maximo": maximo,
            "localizacao": localizacao,
            "fornecedor": fornecedor,
            "valor_unitario": valor_unitario,
            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.registrar_historico("CADASTRO", codigo, descricao, quantidade, 
                               st.session_state.usuario_atual)
        return True
    
    def atualizar_item(self, codigo: str, campo: str, valor) -> bool:
        """Atualiza campo específico de um item"""
        if codigo not in self.estoque:
            return False
        
        valor_anterior = self.estoque[codigo].get(campo)
        self.estoque[codigo][campo] = valor
        self.estoque[codigo]["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.registrar_historico("ATUALIZAÇÃO", codigo, 
                               f"{campo}: {valor_anterior} → {valor}", 
                               self.estoque[codigo]["quantidade"], 
                               st.session_state.usuario_atual)
        return True
    
    def entrada_estoque(self, codigo: str, quantidade: int, observacao: str = "") -> bool:
        """Registra entrada no estoque"""
        if codigo not in self.estoque or quantidade <= 0:
            return False
        
        qtd_anterior = self.estoque[codigo]["quantidade"]
        self.estoque[codigo]["quantidade"] += quantidade
        self.estoque[codigo]["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.registrar_historico("ENTRADA", codigo, 
                               f"Qtd: +{quantidade}. {observacao}", 
                               self.estoque[codigo]["quantidade"], 
                               st.session_state.usuario_atual)
        return True
    
    def saida_estoque(self, codigo: str, quantidade: int, observacao: str = "") -> bool:
        """Registra saída do estoque"""
        if codigo not in self.estoque or quantidade <= 0:
            return False
        
        if self.estoque[codigo]["quantidade"] < quantidade:
            return False
        
        self.estoque[codigo]["quantidade"] -= quantidade
        self.estoque[codigo]["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.registrar_historico("SAÍDA", codigo, 
                               f"Qtd: -{quantidade}. {observacao}", 
                               self.estoque[codigo]["quantidade"], 
                               st.session_state.usuario_atual)
        return True
    
    def registrar_historico(self, tipo: str, codigo: str, descricao: str, 
                          quantidade: int, usuario: str):
        """Registra operação no histórico"""
        registro = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "codigo": codigo,
            "descricao": descricao,
            "quantidade": quantidade,
            "usuario": usuario
        }
        self.historico.append(registro)
    
    def obter_alertas(self) -> Dict[str, List]:
        """Retorna alertas de estoque"""
        alertas = {
            "critico": [],
            "baixo": [],
            "reposicao": [],
            "excesso": []
        }
        
        for codigo, item in self.estoque.items():
            qtd = item["quantidade"]
            minimo = item["minimo"]
            maximo = item["maximo"]
            
            if qtd == 0:
                alertas["critico"].append({
                    "codigo": codigo,
                    "descricao": item["descricao"],
                    "quantidade": qtd,
                    "minimo": minimo
                })
            elif qtd < minimo:
                alertas["baixo"].append({
                    "codigo": codigo,
                    "descricao": item["descricao"],
                    "quantidade": qtd,
                    "minimo": minimo
                })
            elif qtd < minimo * 1.2:
                alertas["reposicao"].append({
                    "codigo": codigo,
                    "descricao": item["descricao"],
                    "quantidade": qtd,
                    "minimo": minimo
                })
            elif qtd > maximo:
                alertas["excesso"].append({
                    "codigo": codigo,
                    "descricao": item["descricao"],
                    "quantidade": qtd,
                    "maximo": maximo
                })
        
        return alertas
    
    def gerar_relatorio(self) -> pd.DataFrame:
        """Gera relatório completo do estoque"""
        dados = []
        for codigo, item in self.estoque.items():
            dados.append({
                "Código": codigo,
                "Descrição": item["descricao"],
                "Unidade": item["unidade"],
                "Quantidade": item["quantidade"],
                "Mínimo": item["minimo"],
                "Máximo": item["maximo"],
                "Localização": item["localizacao"],
                "Fornecedor": item["fornecedor"],
                "Valor Unit.": f"R$ {item['valor_unitario']:.2f}",
                "Valor Total": f"R$ {item['quantidade'] * item['valor_unitario']:.2f}",
                "Status": self.get_status(item["quantidade"], item["minimo"], item["maximo"]),
                "Última Atualização": item["ultima_atualizacao"]
            })
        
        return pd.DataFrame(dados)
    
    def get_status(self, qtd: int, minimo: int, maximo: int) -> str:
        """Retorna status do item baseado na quantidade"""
        if qtd == 0:
            return "🔴 Sem Estoque"
        elif qtd < minimo:
            return "🟡 Abaixo do Mínimo"
        elif qtd > maximo:
            return "🟠 Acima do Máximo"
        else:
            return "🟢 Normal"
    
    def buscar_item(self, termo: str) -> Dict:
        """Busca item por código ou descrição"""
        resultados = {}
        termo_lower = termo.lower()
        
        for codigo, item in self.estoque.items():
            if (termo_lower in codigo.lower() or 
                termo_lower in item["descricao"].lower()):
                resultados[codigo] = item
        
        return resultados
    
    def calcular_valor_total(self) -> float:
        """Calcula valor total do estoque"""
        total = 0
        for item in self.estoque.values():
            total += item["quantidade"] * item["valor_unitario"]
        return total
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do estoque"""
        qtd_total = sum(item["quantidade"] for item in self.estoque.values())
        itens_criticos = len([1 for item in self.estoque.values() 
                            if item["quantidade"] < item["minimo"]])
        itens_excesso = len([1 for item in self.estoque.values() 
                           if item["quantidade"] > item["maximo"]])
        
        return {
            "total_itens": len(self.estoque),
            "quantidade_total": qtd_total,
            "valor_total": self.calcular_valor_total(),
            "itens_criticos": itens_criticos,
            "itens_excesso": itens_excesso,
            "taxa_ocupacao": (qtd_total / sum(item["maximo"] 
                            for item in self.estoque.values())) * 100
        }

# [CONTINUA O RESTO DO CÓDIGO...]

# Função principal
def main():
    # NÃO COLOQUE st.set_page_config() AQUI - JÁ FOI CHAMADO NO INÍCIO
    
    # Inicialização do session state
    if "estoque_manager" not in st.session_state:
        st.session_state.estoque_manager = EstoqueManager()
    
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    
    if "usuario_atual" not in st.session_state:
        st.session_state.usuario_atual = None
    
    if "tipo_usuario" not in st.session_state:
        st.session_state.tipo_usuario = None
    
    # Sistema de autenticação
    if not st.session_state.autenticado:
        st.title("🔐 Sistema de Gestão de Estoque - Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("### Faça login para continuar")
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("Entrar", use_container_width=True):
                        if st.session_state.estoque_manager.autenticar_usuario(usuario, senha):
                            st.session_state.autenticado = True
                            st.session_state.usuario_atual = usuario
                            st.session_state.tipo_usuario = st.session_state.estoque_manager.usuarios[usuario]["tipo"]
                            st.rerun()
                        else:
                            st.error("Usuário ou senha incorretos!")
                
                with col_btn2:
                    if st.form_submit_button("Limpar", use_container_width=True):
                        st.rerun()
            
            # Informações de teste
            with st.expander("ℹ️ Credenciais de Teste"):
                st.info("""
                **Administrador:**
                - Usuário: admin
                - Senha: admin123
                
                **Operador:**
                - Usuário: user
                - Senha: user123
                """)
        
        return
    
    # Interface principal (após autenticação)
    # Sidebar
    with st.sidebar:
        st.title("📦 Gestão de Estoque")
        st.markdown(f"**Usuário:** {st.session_state.usuario_atual}")
        st.markdown(f"**Tipo:** {st.session_state.tipo_usuario}")
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario_atual = None
            st.session_state.tipo_usuario = None
            st.rerun()
        
        st.markdown("---")
        
        # Filtros globais
        st.subheader("🔍 Filtros")
        
        # Busca
        busca = st.text_input("Buscar (código ou descrição)")
        
        # Filtro por fornecedor
        fornecedores = ["Todos"] + list(set(item["fornecedor"] 
                                          for item in st.session_state.estoque_manager.estoque.values()))
        fornecedor_filtro = st.selectbox("Fornecedor", fornecedores)
        
        # Filtro por status
        status_filtro = st.selectbox("Status", 
                                    ["Todos", "Normal", "Abaixo do Mínimo", 
                                     "Sem Estoque", "Acima do Máximo"])
        
        # Filtro por localização
        localizacoes = ["Todas"] + list(set(item["localizacao"] 
                                          for item in st.session_state.estoque_manager.estoque.values()))
        localizacao_filtro = st.selectbox("Localização", localizacoes)
    
    # Título principal
    st.title("📊 Sistema de Gestão de Estoque")
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Dashboard", "📦 Estoque", "➕ Cadastro", 
        "🔄 Movimentações", "📊 Relatórios", "📜 Histórico", "⚙️ Configurações"
    ])
    
    # Tab Dashboard
    with tab1:
        # Estatísticas
        stats = st.session_state.estoque_manager.obter_estatisticas()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Itens", stats["total_itens"])
        with col2:
            st.metric("Quantidade Total", f"{stats['quantidade_total']:,}")
        with col3:
            st.metric("Valor Total", f"R$ {stats['valor_total']:,.2f}")
        with col4:
            st.metric("Taxa de Ocupação", f"{stats['taxa_ocupacao']:.1f}%")
        
        # Alertas
        st.subheader("🚨 Alertas de Estoque")
        alertas = st.session_state.estoque_manager.obter_alertas()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if alertas["critico"]:
                st.markdown('<div class="alert-box alert-critical">', unsafe_allow_html=True)
                st.markdown("### 🔴 Itens Sem Estoque")
                for item in alertas["critico"]:
                    st.write(f"- **{item['codigo']}** - {item['descricao']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if alertas["baixo"]:
                st.markdown('<div class="alert-box alert-warning">', unsafe_allow_html=True)
                st.markdown("### 🟡 Itens Abaixo do Mínimo")
                for item in alertas["baixo"]:
                    st.write(f"- **{item['codigo']}** - {item['descricao']} "
                           f"(Qtd: {item['quantidade']}, Mín: {item['minimo']})")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if alertas["reposicao"]:
                st.markdown('<div class="alert-box alert-info">', unsafe_allow_html=True)
                st.markdown("### 🔵 Itens para Reposição")
                for item in alertas["reposicao"]:
                    st.write(f"- **{item['codigo']}** - {item['descricao']} "
                           f"(Qtd: {item['quantidade']})")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if alertas["excesso"]:
                st.markdown('<div class="alert-box alert-warning">', unsafe_allow_html=True)
                st.markdown("### 🟠 Itens em Excesso")
                for item in alertas["excesso"]:
                    st.write(f"- **{item['codigo']}** - {item['descricao']} "
                           f"(Qtd: {item['quantidade']}, Máx: {item['maximo']})")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráficos
        st.subheader("📊 Análise Visual")
        
        # Preparar dados para gráficos
        df_estoque = st.session_state.estoque_manager.gerar_relatorio()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de status
            status_counts = df_estoque['Status'].value_counts()
            fig_data = []
            colors = []
            
            for status, count in status_counts.items():
                if "Normal" in status:
                    colors.append("#4CAF50")
                elif "Sem Estoque" in status:
                    colors.append("#F44336")
                elif "Abaixo" in status:
                    colors.append("#FF9800")
                else:
                    colors.append("#FFC107")
                
                fig_data.append({
                    "name": status,
                    "data": count
                })
            
            if fig_data:
                chart_config = {
                    "type": "pie",
                    "title": {
                        "text": "Distribuição por Status"
                    },
                    "series": fig_data
                }
                st.write(json.dumps(chart_config))
        
        with col2:
            # Top 10 itens por valor
            df_top = df_estoque.copy()
            df_top['Valor_Numerico'] = df_top['Valor Total'].str.replace('R$ ', '').str.replace(',', '').astype(float)
            df_top = df_top.nlargest(10, 'Valor_Numerico')
            
            chart_config = {
                "type": "bar",
                "title": {
                    "text": "Top 10 Itens por Valor Total"
                },
                "series": [{
                    "name": "Valor Total",
                    "data": df_top['Valor_Numerico'].tolist()
                }],
                "categories": df_top['Descrição'].tolist()
            }
            st.write(json.dumps(chart_config))
    
    # Tab Estoque
    with tab2:
        st.subheader("📦 Consulta de Estoque")
        
        # Aplicar filtros
        df_filtrado = st.session_state.estoque_manager.gerar_relatorio()
        
        # Filtro de busca
        if busca:
            df_filtrado = df_filtrado[
                df_filtrado['Código'].str.contains(busca, case=False) |
                df_filtrado['Descrição'].str.contains(busca, case=False)
            ]
        
        # Filtro de fornecedor
        if fornecedor_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == fornecedor_filtro]
        
        # Filtro de status
        if status_filtro != "Todos":
            status_map = {
                "Normal": "🟢 Normal",
                "Abaixo do Mínimo": "🟡 Abaixo do Mínimo",
                "Sem Estoque": "🔴 Sem Estoque",
                "Acima do Máximo": "🟠 Acima do Máximo"
            }
            if status_filtro in status_map:
                df_filtrado = df_filtrado[df_filtrado['Status'] == status_map[status_filtro]]
        
        # Filtro de localização
        if localizacao_filtro != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Localização'] == localizacao_filtro]
        
        # Exibir tabela
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="medium"),
                "Valor Unit.": st.column_config.TextColumn("Valor Unit.", width="small"),
                "Valor Total": st.column_config.TextColumn("Valor Total", width="small"),
            }
        )
        
        # Resumo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Total de itens filtrados:** {len(df_filtrado)}")
        with col2:
            total_valor = df_filtrado['Valor Total'].str.replace('R$ ', '').str.replace(',', '').astype(float).sum()
            st.info(f"**Valor total filtrado:** R$ {total_valor:,.2f}")
        with col3:
            if st.button("📥 Exportar para CSV"):
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Tab Cadastro
    with tab3:
        st.subheader("➕ Cadastro de Novo Item")
        
        if st.session_state.tipo_usuario == "Administrador":
            with st.form("cadastro_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    codigo = st.text_input("Código*", max_chars=10)
                    descricao = st.text_input("Descrição*", max_chars=100)
                    unidade = st.selectbox("Unidade*", ["PÇ", "UN", "CX", "KG", "M", "L"])
                    fornecedor = st.text_input("Fornecedor*", max_chars=50)
                    localizacao = st.text_input("Localização*", max_chars=20)
                
                with col2:
                    quantidade = st.number_input("Quantidade Inicial*", min_value=0, value=0)
                    minimo = st.number_input("Estoque Mínimo*", min_value=0, value=10)
                    maximo = st.number_input("Estoque Máximo*", min_value=0, value=100)
                    valor_unitario = st.number_input("Valor Unitário (R$)*", 
                                                   min_value=0.0, value=0.0, 
                                                   format="%.2f")
                
                st.markdown("**Campos obrigatórios*")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    submitted = st.form_submit_button("Cadastrar Item", use_container_width=True)
                
                if submitted:
                    # Validações
                    if not all([codigo, descricao, unidade, fornecedor, localizacao]):
                        st.error("Preencha todos os campos obrigatórios!")
                    elif minimo >= maximo:
                        st.error("Estoque mínimo deve ser menor que o máximo!")
                    elif quantidade > maximo:
                        st.error("Quantidade inicial não pode ser maior que o estoque máximo!")
                    else:
                        if st.session_state.estoque_manager.adicionar_item(
                            codigo, descricao, unidade, quantidade, minimo, maximo,
                            localizacao, fornecedor, valor_unitario
                        ):
                            st.success(f"Item {codigo} cadastrado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Código {codigo} já existe no sistema!")
        else:
            st.warning("Apenas administradores podem cadastrar novos itens.")
    
    # Tab Movimentações
    with tab4:
        st.subheader("🔄 Movimentações de Estoque")
        
        # Seleção de item
        codigos = list(st.session_state.estoque_manager.estoque.keys())
        codigo_selecionado = st.selectbox(
            "Selecione o item",
            codigos,
            format_func=lambda x: f"{x} - {st.session_state.estoque_manager.estoque[x]['descricao']}"
        )
        
        if codigo_selecionado:
            item = st.session_state.estoque_manager.estoque[codigo_selecionado]
            
            # Informações do item
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Quantidade Atual", item["quantidade"])
            with col2:
                st.metric("Estoque Mínimo", item["minimo"])
            with col3:
                st.metric("Estoque Máximo", item["maximo"])
            with col4:
                st.metric("Localização", item["localizacao"])
            
            st.markdown("---")
            
            # Formulários de movimentação
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📥 Entrada de Estoque")
                with st.form("entrada_form"):
                    qtd_entrada = st.number_input("Quantidade", min_value=1, value=1)
                    obs_entrada = st.text_area("Observações", max_chars=200)
                    
                    if st.form_submit_button("Registrar Entrada", use_container_width=True):
                        if st.session_state.estoque_manager.entrada_estoque(
                            codigo_selecionado, qtd_entrada, obs_entrada
                        ):
                            st.success(f"Entrada de {qtd_entrada} unidades registrada!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro ao registrar entrada!")
            
            with col2:
                st.markdown("### 📤 Saída de Estoque")
                with st.form("saida_form"):
                    qtd_saida = st.number_input("Quantidade", 
                                              min_value=1, 
                                              max_value=item["quantidade"],
                                              value=1)
                    obs_saida = st.text_area("Observações", max_chars=200)
                    
                    if st.form_submit_button("Registrar Saída", use_container_width=True):
                        if st.session_state.estoque_manager.saida_estoque(
                            codigo_selecionado, qtd_saida, obs_saida
                        ):
                            st.success(f"Saída de {qtd_saida} unidades registrada!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro ao registrar saída!")
            
            # Atualização de dados
            if st.session_state.tipo_usuario == "Administrador":
                st.markdown("---")
                st.markdown("### ✏️ Atualizar Informações do Item")
                
                with st.form("atualizar_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        campo = st.selectbox("Campo a atualizar", 
                                           ["descricao", "unidade", "minimo", "maximo", 
                                            "localizacao", "fornecedor", "valor_unitario"])
                    
                    with col2:
                        if campo in ["minimo", "maximo"]:
                            novo_valor = st.number_input("Novo valor", min_value=0)
                        elif campo == "valor_unitario":
                            novo_valor = st.number_input("Novo valor", min_value=0.0, format="%.2f")
                        elif campo == "unidade":
                            novo_valor = st.selectbox("Novo valor", ["PÇ", "UN", "CX", "KG", "M", "L"])
                        else:
                            novo_valor = st.text_input("Novo valor")
                    
                    if st.form_submit_button("Atualizar", use_container_width=True):
                        if st.session_state.estoque_manager.atualizar_item(
                            codigo_selecionado, campo, novo_valor
                        ):
                            st.success(f"Campo {campo} atualizado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar item!")
    
    # Tab Relatórios
    with tab5:
        st.subheader("📊 Relatórios e Análises")
        
        # Seleção de relatório
        tipo_relatorio = st.selectbox(
            "Tipo de Relatório",
            ["Resumo Geral", "Análise por Fornecedor", "Análise por Localização", 
             "Itens Críticos", "Análise de Valor", "Previsão de Reposição"]
        )
        
        if tipo_relatorio == "Resumo Geral":
            st.markdown("### 📋 Resumo Geral do Estoque")
            
            stats = st.session_state.estoque_manager.obter_estatisticas()
            df_estoque = st.session_state.estoque_manager.gerar_relatorio()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Estatísticas Gerais**")
                st.write(f"- Total de SKUs: {stats['total_itens']}")
                st.write(f"- Quantidade total em estoque: {stats['quantidade_total']:,}")
                st.write(f"- Valor total do estoque: R$ {stats['valor_total']:,.2f}")
                st.write(f"- Taxa de ocupação: {stats['taxa_ocupacao']:.1f}%")
                st.write(f"- Itens críticos: {stats['itens_criticos']}")
                st.write(f"- Itens em excesso: {stats['itens_excesso']}")
            
            with col2:
                # Gráfico de distribuição de valor
                df_valor = df_estoque.copy()
                df_valor['Valor_Num'] = df_valor['Valor Total'].str.replace('R$ ', '').str.replace(',', '').astype(float)
                df_top5 = df_valor.nlargest(5, 'Valor_Num')
                
                chart_config = {
                    "type": "pie",
                    "title": {
                        "text": "Top 5 Itens por Valor"
                    },
                    "series": [
                        {"name": row['Descrição'][:30], "data": row['Valor_Num']} 
                        for _, row in df_top5.iterrows()
                    ]
                }
                st.write(json.dumps(chart_config))
        
        elif tipo_relatorio == "Análise por Fornecedor":
            st.markdown("### 🏢 Análise por Fornecedor")
            
            df_fornecedor = st.session_state.estoque_manager.gerar_relatorio()
            df_fornecedor['Valor_Num'] = df_fornecedor['Valor Total'].str.replace('R$ ', '').str.replace(',', '').astype(float)
            
            resumo_fornecedor = df_fornecedor.groupby('Fornecedor').agg({
                'Código': 'count',
                'Quantidade': 'sum',
                'Valor_Num': 'sum'
            }).round(2)
            
            resumo_fornecedor.columns = ['Qtd. Itens', 'Qtd. Total', 'Valor Total (R$)']
            st.dataframe(resumo_fornecedor, use_container_width=True)
            
            # Gráfico
            chart_config = {
                "type": "bar",
                "title": {
                    "text": "Valor por Fornecedor"
                },
                "series": [{
                    "name": "Valor Total",
                    "data": resumo_fornecedor['Valor Total (R$)'].tolist()
                }],
                "categories": resumo_fornecedor.index.tolist()
            }
            st.write(json.dumps(chart_config))
        
        elif tipo_relatorio == "Análise por Localização":
            st.markdown("### 📍 Análise por Localização")
            
            df_local = st.session_state.estoque_manager.gerar_relatorio()
            
            resumo_local = df_local.groupby('Localização').agg({
                'Código': 'count',
                'Quantidade': 'sum'
            })
            
            resumo_local.columns = ['Qtd. Itens', 'Qtd. Total']
            st.dataframe(resumo_local, use_container_width=True)
            
            # Mapa de calor simulado
            locais = resumo_local.index.tolist()
            valores = resumo_local['Qtd. Total'].tolist()
            
            chart_config = {
                "type": "heatmap",
                "title": {
                    "text": "Mapa de Ocupação por Localização"
                },
                "series": [{
                    "data": [valores]
                }],
                "categories": locais,
                "labels": ["Quantidade"]
            }
            st.write(json.dumps(chart_config))
        
        elif tipo_relatorio == "Itens Críticos":
            st.markdown("### 🚨 Relatório de Itens Críticos")
            
            alertas = st.session_state.estoque_manager.obter_alertas()
            
            # Criar DataFrame com todos os itens críticos
            itens_criticos = []
            
            for item in alertas["critico"]:
                itens_criticos.append({
                    "Código": item["codigo"],
                    "Descrição": item["descricao"],
                    "Quantidade": item["quantidade"],
                    "Mínimo": item["minimo"],
                    "Status": "Sem Estoque",
                    "Urgência": "🔴 Crítica"
                })
            
            for item in alertas["baixo"]:
                itens_criticos.append({
                    "Código": item["codigo"],
                    "Descrição": item["descricao"],
                    "Quantidade": item["quantidade"],
                    "Mínimo": item["minimo"],
                    "Status": "Abaixo do Mínimo",
                    "Urgência": "🟡 Alta"
                })
            
            for item in alertas["reposicao"]:
                itens_criticos.append({
                    "Código": item["codigo"],
                    "Descrição": item["descricao"],
                    "Quantidade": item["quantidade"],
                    "Mínimo": item["minimo"],
                    "Status": "Próximo ao Mínimo",
                    "Urgência": "🔵 Média"
                })
            
            if itens_criticos:
                df_criticos = pd.DataFrame(itens_criticos)
                st.dataframe(df_criticos, use_container_width=True, hide_index=True)
                
                # Resumo
                st.markdown("**Resumo:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.error(f"Itens sem estoque: {len(alertas['critico'])}")
                with col2:
                    st.warning(f"Itens abaixo do mínimo: {len(alertas['baixo'])}")
                with col3:
                    st.info(f"Itens para reposição: {len(alertas['reposicao'])}")
            else:
                st.success("Nenhum item crítico encontrado!")
        
        elif tipo_relatorio == "Análise de Valor":
            st.markdown("### 💰 Análise de Valor do Estoque")
            
            df_valor = st.session_state.estoque_manager.gerar_relatorio()
            df_valor['Valor_Num'] = df_valor['Valor Total'].str.replace('R$ ', '').str.replace(',', '').astype(float)
            df_valor['Valor_Unit_Num'] = df_valor['Valor Unit.'].str.replace('R$ ', '').str.replace(',', '').astype(float)
            
            # Curva ABC
            df_valor = df_valor.sort_values('Valor_Num', ascending=False)
            df_valor['Valor_Acumulado'] = df_valor['Valor_Num'].cumsum()
            df_valor['Percentual_Acumulado'] = (df_valor['Valor_Acumulado'] / df_valor['Valor_Num'].sum()) * 100
            
            df_valor['Classe_ABC'] = pd.cut(
                df_valor['Percentual_Acumulado'],
                bins=[0, 80, 95, 100],
                labels=['A', 'B', 'C']
            )
            
            # Resumo ABC
            resumo_abc = df_valor.groupby('Classe_ABC').agg({
                'Código': 'count',
                'Valor_Num': 'sum'
            })
            
            st.markdown("**Classificação ABC**")
            col1, col2, col3 = st.columns(3)
            
            for idx, (classe, dados) in enumerate(resumo_abc.iterrows()):
                with [col1, col2, col3][idx]:
                    st.metric(
                        f"Classe {classe}",
                        f"{dados['Código']} itens",
                        f"R$ {dados['Valor_Num']:,.2f}"
                    )
            
            # Tabela detalhada
            st.markdown("**Detalhamento por Item**")
            df_display = df_valor[['Código', 'Descrição', 'Quantidade', 'Valor Unit.', 
                                  'Valor Total', 'Percentual_Acumulado', 'Classe_ABC']]
            df_display['Percentual_Acumulado'] = df_display['Percentual_Acumulado'].round(2).astype(str) + '%'
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        elif tipo_relatorio == "Previsão de Reposição":
            st.markdown("### 🔮 Previsão de Reposição")
            
            # Simular consumo médio baseado em dados históricos fictícios
            df_reposicao = []
            
            for codigo, item in st.session_state.estoque_manager.estoque.items():
                # Simular consumo diário (entre 5% e 15% do estoque mínimo)
                consumo_diario = random.uniform(0.05, 0.15) * item["minimo"]
                dias_para_minimo = max(0, (item["quantidade"] - item["minimo"]) / consumo_diario) if consumo_diario > 0 else 999
                
                if dias_para_minimo < 30:  # Mostrar apenas itens que precisam reposição em 30 dias
                    df_reposicao.append({
                        "Código": codigo,
                        "Descrição": item["descricao"],
                        "Quantidade Atual": item["quantidade"],
                        "Estoque Mínimo": item["minimo"],
                        "Consumo Diário Médio": round(consumo_diario, 1),
                        "Dias até Mínimo": round(dias_para_minimo, 0),
                        "Data Prevista": (datetime.now() + timedelta(days=dias_para_minimo)).strftime("%d/%m/%Y"),
                        "Qtd. Sugerida para Compra": item["maximo"] - item["quantidade"]
                    })
            
            if df_reposicao:
                df_reposicao = pd.DataFrame(df_reposicao)
                df_reposicao = df_reposicao.sort_values('Dias até Mínimo')
                
                st.dataframe(df_reposicao, use_container_width=True, hide_index=True)
                
                # Gráfico de timeline
                chart_config = {
                    "type": "bar",
                    "title": {
                        "text": "Dias até Atingir Estoque Mínimo"
                    },
                    "series": [{
                        "name": "Dias",
                        "data": df_reposicao['Dias até Mínimo'].tolist()
                    }],
                    "categories": df_reposicao['Código'].tolist()
                }
                st.write(json.dumps(chart_config))
            else:
                st.info("Todos os itens estão com estoque adequado para os próximos 30 dias.")
    
    # Tab Histórico
    with tab6:
        st.subheader("📜 Histórico de Movimentações")
        
        if st.session_state.estoque_manager.historico:
            # Filtros de histórico
            col1, col2, col3 = st.columns(3)
            
            with col1:
                tipos_mov = ["Todos"] + list(set(h["tipo"] for h in st.session_state.estoque_manager.historico))
                tipo_filtro = st.selectbox("Tipo de Movimentação", tipos_mov)
            
            with col2:
                usuarios = ["Todos"] + list(set(h["usuario"] for h in st.session_state.estoque_manager.historico))
                usuario_filtro = st.selectbox("Usuário", usuarios)
            
            with col3:
                periodo_filtro = st.selectbox("Período", 
                                            ["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Todos"])
            
            # Converter histórico para DataFrame
            df_historico = pd.DataFrame(st.session_state.estoque_manager.historico)
            df_historico['data'] = pd.to_datetime(df_historico['data'])
            
            # Aplicar filtros
            if tipo_filtro != "Todos":
                df_historico = df_historico[df_historico['tipo'] == tipo_filtro]
            
            if usuario_filtro != "Todos":
                df_historico = df_historico[df_historico['usuario'] == usuario_filtro]
            
            # Filtro de período
            hoje = datetime.now()
            if periodo_filtro == "Hoje":
                df_historico = df_historico[df_historico['data'].dt.date == hoje.date()]
            elif periodo_filtro == "Últimos 7 dias":
                df_historico = df_historico[df_historico['data'] >= hoje - timedelta(days=7)]
            elif periodo_filtro == "Últimos 30 dias":
                df_historico = df_historico[df_historico['data'] >= hoje - timedelta(days=30)]
            
            # Ordenar por data decrescente
            df_historico = df_historico.sort_values('data', ascending=False)
            
            # Formatar data para exibição
            df_historico['Data/Hora'] = df_historico['data'].dt.strftime('%d/%m/%Y %H:%M:%S')
            
            # Exibir histórico
            df_display = df_historico[['Data/Hora', 'tipo', 'codigo', 'descricao', 'quantidade', 'usuario']]
            df_display.columns = ['Data/Hora', 'Tipo', 'Código', 'Descrição', 'Quantidade', 'Usuário']
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Estatísticas do histórico
            st.markdown("### 📊 Estatísticas do Período")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Movimentações", len(df_historico))
            
            with col2:
                entradas = len(df_historico[df_historico['tipo'] == 'ENTRADA'])
                st.metric("Entradas", entradas)
            
            with col3:
                saidas = len(df_historico[df_historico['tipo'] == 'SAÍDA'])
                st.metric("Saídas", saidas)
            
            with col4:
                usuarios_ativos = df_historico['usuario'].nunique()
                st.metric("Usuários Ativos", usuarios_ativos)
        else:
            st.info("Nenhuma movimentação registrada até o momento.")
    
    # Tab Configurações
    with tab7:
        st.subheader("⚙️ Configurações do Sistema")
        
        tab1, tab2 = st.tabs(["👥 Usuários", "🔧 Sistema"])
        
        with tab1:
            st.subheader("Gerenciamento de Usuários")
            
            if st.session_state.tipo_usuario == "Administrador":
                # Adicionar novo usuário
                with st.expander("➕ Adicionar Novo Usuário"):
                    with st.form("novo_usuario_form"):
                        novo_usuario = st.text_input("Nome de Usuário")
                        nova_senha = st.text_input("Senha", type="password")
                        confirmar_senha = st.text_input("Confirmar Senha", type="password")
                        tipo = st.selectbox("Tipo de Usuário", ["Operador", "Administrador"])
                        
                        if st.form_submit_button("Criar Usuário"):
                            if nova_senha != confirmar_senha:
                                st.error("As senhas não coincidem!")
                            elif novo_usuario in st.session_state.estoque_manager.usuarios:
                                st.error("Usuário já existe!")
                            elif len(nova_senha) < 6:
                                st.error("A senha deve ter pelo menos 6 caracteres!")
                            else:
                                st.session_state.estoque_manager.usuarios[novo_usuario] = {
                                    "senha": st.session_state.estoque_manager.hash_senha(nova_senha),
                                    "tipo": tipo
                                }
                                st.success(f"Usuário {novo_usuario} criado com sucesso!")
                
                # Lista de usuários
                st.markdown("### 📋 Usuários Cadastrados")
                for user, info in st.session_state.estoque_manager.usuarios.items():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"👤 **{user}**")
                    with col2:
                        st.write(f"Tipo: {info['tipo']}")
                    with col3:
                        if user not in ["admin", "user"]:  # Proteger usuários padrão
                            if st.button(f"🗑️", key=f"del_{user}"):
                                del st.session_state.estoque_manager.usuarios[user]
                                st.rerun()
            else:
                st.warning("Apenas administradores podem gerenciar usuários.")
        
        with tab2:
            st.subheader("Configurações do Sistema")
            
            # Configurações de alertas
            st.markdown("### 🔔 Configurações de Alertas")
            col1, col2 = st.columns(2)
            
            with col1:
                alerta_critico = st.checkbox("Alertas de estoque crítico", value=True)
                alerta_baixo = st.checkbox("Alertas de estoque baixo", value=True)
            
            with col2:
                alerta_reposicao = st.checkbox("Alertas de reposição", value=True)
                alerta_excesso = st.checkbox("Alertas de excesso", value=True)
            
            # Parâmetros do sistema
            st.markdown("### 📊 Parâmetros do Sistema")
            col1, col2 = st.columns(2)
            
            with col1:
                dias_historico = st.number_input("Dias de histórico para análise", 
                                               min_value=7, max_value=365, value=30)
                taxa_reposicao = st.slider("Taxa de reposição (%)", 
                                         min_value=10, max_value=50, value=20)
            
            with col2:
                formato_data = st.selectbox("Formato de data", 
                                          ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
                tema = st.selectbox("Tema da interface", 
                                  ["Claro", "Escuro", "Automático"])
            
            # Backup e restauração
            st.markdown("### 💾 Backup e Restauração")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Fazer Backup", use_container_width=True):
                    # Criar backup dos dados
                    backup_data = {
                        "estoque": st.session_state.estoque_manager.estoque,
                        "historico": st.session_state.estoque_manager.historico,
                        "usuarios": st.session_state.estoque_manager.usuarios,
                        "data_backup": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="Download Backup JSON",
                        data=backup_json,
                        file_name=f"backup_estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                uploaded_file = st.file_uploader("Restaurar Backup", type=['json'])
                if uploaded_file is not None:
                    try:
                        backup_data = json.load(uploaded_file)
                        
                        if st.button("🔄 Restaurar", use_container_width=True):
                            st.session_state.estoque_manager.estoque = backup_data["estoque"]
                            st.session_state.estoque_manager.historico = backup_data["historico"]
                            st.session_state.estoque_manager.usuarios = backup_data["usuarios"]
                            st.success("Backup restaurado com sucesso!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao restaurar backup: {str(e)}")
            
            # Informações do sistema
            st.markdown("### ℹ️ Informações do Sistema")
            st.info(f"""
            **Versão:** 1.0.0  
            **Última atualização:** {datetime.now().strftime('%d/%m/%Y')}  
            **Total de registros:** {len(st.session_state.estoque_manager.estoque)}  
            **Total de movimentações:** {len(st.session_state.estoque_manager.historico)}  
            **Usuários cadastrados:** {len(st.session_state.estoque_manager.usuarios)}
            """)

# Executar aplicação
if __name__ == "__main__":
    main()
