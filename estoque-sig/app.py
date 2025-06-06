import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Estoque - SIG", 
    page_icon="📦",
    layout="wide"
)

# Função para salvar dados
def salvar_dados(df, df_historico):
    """Salva os dataframes em arquivos locais"""
    try:
        # Salvar estoque
        df.to_csv('estoque_atual.csv', index=False)
        
        # Salvar histórico
        df_historico.to_csv('historico_movimentacoes.csv', index=False)
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {str(e)}")
        return False

# Função para carregar dados
def carregar_dados():
    """Carrega os dados salvos ou cria novos"""
    try:
        # Tentar carregar estoque
        if os.path.exists('estoque_atual.csv'):
            df = pd.read_csv('estoque_atual.csv')
        else:
            # Se não existir, criar DataFrame vazio com as colunas corretas
            df = pd.DataFrame(columns=[
                'CÓDIGO BM', 'DISCRIMINAÇÃO DOS MATERIAIS', 
                'UNIDADE', 'QUANTIDADE', 'PREÇO UNITÁRIO'
            ])
        
        # Tentar carregar histórico
        if os.path.exists('historico_movimentacoes.csv'):
            df_historico = pd.read_csv('historico_movimentacoes.csv')
        else:
            df_historico = pd.DataFrame(columns=[
                'Data', 'Hora', 'Tipo', 'CÓDIGO BM', 'DISCRIMINAÇÃO DOS MATERIAIS',
                'Quantidade', 'Valor Total', 'Responsável', 'Observações'
            ])
        
        return df, df_historico
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        # Retornar DataFrames vazios em caso de erro
        df = pd.DataFrame(columns=[
            'CÓDIGO BM', 'DISCRIMINAÇÃO DOS MATERIAIS', 
            'UNIDADE', 'QUANTIDADE', 'PREÇO UNITÁRIO'
        ])
        df_historico = pd.DataFrame(columns=[
            'Data', 'Hora', 'Tipo', 'CÓDIGO BM', 'DISCRIMINAÇÃO DOS MATERIAIS',
            'Quantidade', 'Valor Total', 'Responsável', 'Observações'
        ])
        return df, df_historico

# Inicializar session state
if 'df' not in st.session_state:
    df, df_historico = carregar_dados()
    st.session_state.df = df
    st.session_state.historico_movimentacoes = df_historico

# Garantir que as colunas existam e tenham tipos corretos
if not st.session_state.df.empty:
    # Garantir tipos numéricos
    st.session_state.df['QUANTIDADE'] = pd.to_numeric(st.session_state.df['QUANTIDADE'], errors='coerce').fillna(0)
    st.session_state.df['PREÇO UNITÁRIO'] = pd.to_numeric(st.session_state.df['PREÇO UNITÁRIO'], errors='coerce').fillna(0)
    
    # Criar coluna de valor total se não existir
    st.session_state.df['VALOR TOTAL'] = st.session_state.df['QUANTIDADE'] * st.session_state.df['PREÇO UNITÁRIO']

# Função para formatar moeda
def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para buscar peça por código
def buscar_peca_por_codigo(codigo):
    """Busca uma peça pelo código BM"""
    df = st.session_state.df
    # Converter para string para comparação
    df['CÓDIGO BM'] = df['CÓDIGO BM'].astype(str)
    codigo = str(codigo).strip()
    
    resultado = df[df['CÓDIGO BM'] == codigo]
    
    if not resultado.empty:
        return resultado.iloc[0]
    return None

# Função para registrar movimentação
def registrar_movimentacao(tipo, codigo, discriminacao, quantidade, valor_total, responsavel, observacoes=""):
    """Registra uma movimentação no histórico"""
    nova_movimentacao = pd.DataFrame({
        'Data': [datetime.now().strftime('%d/%m/%Y')],
        'Hora': [datetime.now().strftime('%H:%M:%S')],
        'Tipo': [tipo],
        'CÓDIGO BM': [codigo],
        'DISCRIMINAÇÃO DOS MATERIAIS': [discriminacao],
        'Quantidade': [quantidade],
        'Valor Total': [valor_total],
        'Responsável': [responsavel],
        'Observações': [observacoes]
    })
    
    st.session_state.historico_movimentacoes = pd.concat(
        [st.session_state.historico_movimentacoes, nova_movimentacao], 
        ignore_index=True
    )

# Título principal
st.title("📦 Sistema de Gestão de Estoque - SIG")
st.markdown("---")

# Abas principais
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", "🔍 Buscar Peça", "➕ Cadastrar Peça", 
    "📤 Registrar Saída", "📈 Análise ABC", "📜 Histórico"
])

# Tab 1: Dashboard
with tab1:
    st.subheader("📊 Visão Geral do Estoque")
    
    # Verificar se há dados
    df = st.session_state.df
    
    if df.empty:
        st.warning("⚠️ Nenhum item cadastrado no estoque. Faça o upload de uma planilha ou cadastre novos itens.")
    else:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_itens = len(df)
            st.metric("Total de Itens", f"{total_itens:,}".replace(",", "."))
        
        with col2:
            # Calcular valor total baseado nas colunas existentes
            if 'VALOR TOTAL' in df.columns:
                valor_total = df['VALOR TOTAL'].sum()
            else:
                valor_total = (df['QUANTIDADE'] * df['PREÇO UNITÁRIO']).sum()
            st.metric("Valor Total", formatar_moeda(valor_total))
        
        with col3:
            # Itens com estoque baixo (menos de 10 unidades)
            itens_baixo = len(df[df['QUANTIDADE'] < 10])
            st.metric("Itens com Estoque Baixo", itens_baixo, delta=f"-{itens_baixo}")
        
        with col4:
            # Valor médio por item
            valor_medio = valor_total / total_itens if total_itens > 0 else 0
            st.metric("Valor Médio/Item", formatar_moeda(valor_medio))
        
        # Gráficos
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 itens por valor
            df_top_valor = df.nlargest(10, 'VALOR TOTAL' if 'VALOR TOTAL' in df.columns else 'PREÇO UNITÁRIO')
            fig_valor = px.bar(
                df_top_valor, 
                x='DISCRIMINAÇÃO DOS MATERIAIS', 
                y='VALOR TOTAL' if 'VALOR TOTAL' in df.columns else 'PREÇO UNITÁRIO',
                title="Top 10 Itens por Valor Total",
                labels={'y': 'Valor (R$)', 'x': 'Item'}
            )
            fig_valor.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_valor, use_container_width=True)
        
        with col2:
            # Distribuição por unidade
            dist_unidade = df.groupby('UNIDADE').size().reset_index(name='Quantidade')
            fig_unidade = px.pie(
                dist_unidade, 
                values='Quantidade', 
                names='UNIDADE',
                title="Distribuição por Unidade"
            )
            fig_unidade.update_layout(height=400)
            st.plotly_chart(fig_unidade, use_container_width=True)
        
        # Tabela com itens de estoque baixo
        st.markdown("---")
        st.subheader("⚠️ Itens com Estoque Baixo (< 10 unidades)")
        
        df_baixo = df[df['QUANTIDADE'] < 10].sort_values('QUANTIDADE')
        if not df_baixo.empty:
            st.dataframe(
                df_baixo[['CÓDIGO BM', 'DISCRIMINAÇÃO DOS MATERIAIS', 'QUANTIDADE', 'UNIDADE']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("✅ Todos os itens estão com estoque adequado!")

# Tab 2: Buscar Peça
with tab2:
    st.subheader("🔍 Buscar Peça por Código")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        codigo_busca = st.text_input("Digite o Código BM:", placeholder="Ex: 123456")
        buscar_btn = st.button("🔍 Buscar", type="primary", use_container_width=True)
    
    if buscar_btn and codigo_busca:
        peca = buscar_peca_por_codigo(codigo_busca)
        
        if peca is not None:
            st.success(f"✅ Peça encontrada!")
            
            # Exibir informações da peça
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Código BM", peca['CÓDIGO BM'])
                st.metric("Unidade", peca['UNIDADE'])
            
            with col2:
                st.metric("Quantidade", f"{int(peca['QUANTIDADE']):,}".replace(",", "."))
                st.metric("Preço Unitário", formatar_moeda(peca['PREÇO UNITÁRIO']))
            
            with col3:
                valor_total = peca['QUANTIDADE'] * peca['PREÇO UNITÁRIO']
                st.metric("Valor Total", formatar_moeda(valor_total))
                
                # Indicador de estoque
                if peca['QUANTIDADE'] < 10:
                    st.error("⚠️ Estoque Baixo!")
                elif peca['QUANTIDADE'] < 50:
                    st.warning("📊 Estoque Médio")
                else:
                    st.success("✅ Estoque Adequado")
            
            # Descrição
            st.markdown("---")
            st.markdown("**Descrição do Material:**")
            st.info(peca['DISCRIMINAÇÃO DOS MATERIAIS'])
            
        else:
            st.error(f"❌ Peça com código '{codigo_busca}' não encontrada!")

# Tab 3: Cadastrar Peça
with tab3:
    st.subheader("➕ Cadastrar Nova Peça")
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código BM*", placeholder="Ex: 123456")
            discriminacao = st.text_area("Descrição do Material*", placeholder="Descreva o material...")
            unidade = st.selectbox("Unidade*", ["UN", "PC", "CX", "KG", "M", "L", "PAR", "JG", "ROLO"])
        
        with col2:
            quantidade = st.number_input("Quantidade*", min_value=0, value=0, step=1)
            preco = st.number_input("Preço Unitário (R$)*", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            responsavel = st.text_input("Responsável pelo Cadastro*", placeholder="Nome do responsável")
        
        observacoes = st.text_area("Observações", placeholder="Observações adicionais (opcional)")
        
        submitted = st.form_submit_button("💾 Cadastrar Peça", type="primary", use_container_width=True)
        
        if submitted:
            # Validações
            if not all([codigo, discriminacao, responsavel]):
                st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            elif buscar_peca_por_codigo(codigo) is not None:
                st.error(f"❌ Já existe uma peça com o código {codigo}!")
            else:
                # Adicionar nova peça
                nova_peca = pd.DataFrame({
                    'CÓDIGO BM': [codigo],
                    'DISCRIMINAÇÃO DOS MATERIAIS': [discriminacao],
                    'UNIDADE': [unidade],
                    'QUANTIDADE': [quantidade],
                    'PREÇO UNITÁRIO': [preco],
                    'VALOR TOTAL': [quantidade * preco]
                })
                
                st.session_state.df = pd.concat([st.session_state.df, nova_peca], ignore_index=True)
                
                # Registrar no histórico
                registrar_movimentacao(
                    "Entrada - Cadastro",
                    codigo,
                    discriminacao,
                    quantidade,
                    quantidade * preco,
                    responsavel,
                    observacoes
                )
                
                # Salvar dados
                salvar_dados(st.session_state.df, st.session_state.historico_movimentacoes)
                
                st.success(f"✅ Peça {codigo} cadastrada com sucesso!")
                st.balloons()

# Tab 4: Registrar Saída
with tab4:
    st.subheader("📤 Registrar Saída de Material")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        codigo_saida = st.text_input("Código BM da Peça:", placeholder="Ex: 123456", key="cod_saida")
        verificar_btn = st.button("🔍 Verificar Disponibilidade", use_container_width=True)
    
    if verificar_btn and codigo_saida:
        peca = buscar_peca_por_codigo(codigo_saida)
        
        if peca is not None:
            st.success("✅ Peça encontrada!")
            
            # Mostrar informações da peça
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Material:** {peca['DISCRIMINAÇÃO DOS MATERIAIS']}")
            with col2:
                st.info(f"**Quantidade Disponível:** {int(peca['QUANTIDADE'])}")
            with col3:
                st.info(f"**Unidade:** {peca['UNIDADE']}")
            
            # Formulário de saída
            with st.form("form_saida"):
                col1, col2 = st.columns(2)
                
                with col1:
                    quantidade_saida = st.number_input(
                        "Quantidade a Retirar*", 
                        min_value=1, 
                        max_value=int(peca['QUANTIDADE']),
                        value=1
                    )
                    responsavel_saida = st.text_input("Responsável pela Retirada*", placeholder="Nome do responsável")
                
                with col2:
                    destino = st.text_input("Destino/Setor*", placeholder="Ex: Produção, Manutenção...")
                    documento = st.text_input("Nº Documento/OS", placeholder="Opcional")
                
                obs_saida = st.text_area("Observações", placeholder="Motivo da retirada, observações...")
                
                confirmar_saida = st.form_submit_button("📤 Confirmar Saída", type="primary", use_container_width=True)
                
                if confirmar_saida:
                    if not all([responsavel_saida, destino]):
                        st.error("❌ Preencha todos os campos obrigatórios!")
                    else:
                        # Atualizar quantidade no estoque
                        idx = st.session_state.df[st.session_state.df['CÓDIGO BM'].astype(str) == str(codigo_saida)].index[0]
                        st.session_state.df.loc[idx, 'QUANTIDADE'] -= quantidade_saida
                        
                        # Recalcular valor total
                        st.session_state.df.loc[idx, 'VALOR TOTAL'] = (
                            st.session_state.df.loc[idx, 'QUANTIDADE'] * 
                            st.session_state.df.loc[idx, 'PREÇO UNITÁRIO']
                        )
                        
                        # Registrar movimentação
                        valor_saida = quantidade_saida * peca['PREÇO UNITÁRIO']
                        obs_completa = f"Destino: {destino}. Doc: {documento}. {obs_saida}" if documento else f"Destino: {destino}. {obs_saida}"
                        
                        registrar_movimentacao(
                            "Saída",
                            codigo_saida,
                            peca['DISCRIMINAÇÃO DOS MATERIAIS'],
                            quantidade_saida,
                            valor_saida,
                            responsavel_saida,
                            obs_completa
                        )
                        
                        # Salvar dados
                        salvar_dados(st.session_state.df, st.session_state.historico_movimentacoes)
                        
                        st.success(f"✅ Saída registrada com sucesso! Quantidade retirada: {quantidade_saida}")
                        st.info(f"📊 Nova quantidade em estoque: {int(st.session_state.df.loc[idx, 'QUANTIDADE'])}")
        else:
            st.error(f"❌ Peça com código '{codigo_saida}' não encontrada!")

# Tab 5: Análise ABC
with tab5:
    st.subheader("📈 Análise ABC do Estoque")
    
    df = st.session_state.df
    
    if df.empty:
        st.warning("⚠️ Nenhum item no estoque para análise.")
    else:
        # Calcular valor total se não existir
        if 'VALOR TOTAL' not in df.columns:
            df['VALOR TOTAL'] = df['QUANTIDADE'] * df['PREÇO UNITÁRIO']
        
        # Ordenar por valor total
        df_abc = df.sort_values('VALOR TOTAL', ascending=False).copy()
        
        # Calcular percentuais acumulados
        valor_total = df_abc['VALOR TOTAL'].sum()
        df_abc['% Valor'] = (df_abc['VALOR TOTAL'] / valor_total * 100).round(2)
        df_abc['% Acumulado'] = df_abc['% Valor'].cumsum()
        
        # Classificar ABC
        def classificar_abc(percentual):
            if percentual <= 80:
                return 'A'
            elif percentual <= 95:
                return 'B'
            else:
                return 'C'
        
        df_abc['Classe ABC'] = df_abc['% Acumulado'].apply(classificar_abc)
        
        # Métricas por classe
        col1, col2, col3 = st.columns(3)
        
        for col, classe in zip([col1, col2, col3], ['A', 'B', 'C']):
            with col:
                qtd = len(df_abc[df_abc['Classe ABC'] == classe])
                valor = df_abc[df_abc['Classe ABC'] == classe]['VALOR TOTAL'].sum()
                perc = (valor / valor_total * 100) if valor_total > 0 else 0
                
                st.metric(
                    f"Classe {classe}",
                    f"{qtd} itens",
                    f"{perc:.1f}% do valor"
                )
        
        # Gráfico de Pareto
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=["Análise ABC - Curva de Pareto"]
        )
        
        # Barras de valor
        fig.add_trace(
            go.Bar(
                x=df_abc.index[:20],  # Top 20 itens
                y=df_abc['VALOR TOTAL'][:20],
                name="Valor Total",
                marker_color=['#FF6B6B' if c == 'A' else '#4ECDC4' if c == 'B' else '#95E1D3' 
                              for c in df_abc['Classe ABC'][:20]]
            ),
            secondary_y=False
        )
        
        # Linha de percentual acumulado
        fig.add_trace(
            go.Scatter(
                x=df_abc.index[:20],
                y=df_abc['% Acumulado'][:20],
                name="% Acumulado",
                line=dict(color='#2E86AB', width=3),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        fig.update_xaxes(title_text="Itens (Top 20)")
        fig.update_yaxes(title_text="Valor Total (R$)", secondary_y=False)
        fig.update_yaxes(title_text="% Acumulado", secondary_y=True)
        fig.update_layout(height=500, hovermode='x unified')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela com classificação
        st.markdown("---")
        st.subheader("📋 Classificação Detalhada")
        
        # Filtro por classe
        classe_filtro = st.multiselect(
            "Filtrar por Classe:",
            ['A', 'B', 'C'],
            default=['A', 'B', 'C']
        )
        
        df_filtrado = df_abc[df_abc['Classe ABC'].isin(classe_filtro)]
        
        # Exibir tabela
        st.dataframe(
            df_filtrado[['CÓDIGO BM', 'DISCRIMINAÇÃO DOS MATERIAIS', 'QUANTIDADE', 
                         'PREÇO UNITÁRIO', 'VALOR TOTAL', '% Valor', '% Acumulado', 'Classe ABC']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'PREÇO UNITÁRIO': st.column_config.NumberColumn(format="R$ %.2f"),
                'VALOR TOTAL': st.column_config.NumberColumn(format="R$ %.2f"),
                '% Valor': st.column_config.NumberColumn(format="%.2f%%"),
                '% Acumulado': st.column_config.NumberColumn(format="%.2f%%")
            }
        )

# Tab 6: Histórico
with tab6:
    st.subheader("📜 Histórico de Movimentações")
    
    if st.session_state.historico_movimentacoes.empty:
        st.info("📭 Nenhuma movimentação registrada ainda.")
    else:
        df_historico = st.session_state.historico_movimentacoes
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_filtro = st.multiselect(
                "Tipo de Movimentação:",
                df_historico['Tipo'].unique(),
                default=df_historico['Tipo'].unique()
            )
        
        with col2:
            if 'Data' in df_historico.columns:
                datas = pd.to_datetime(df_historico['Data'], format='%d/%m/%Y', errors='coerce')
                data_min = datas.min()
                data_max = datas.max()
                
                if pd.notna(data_min) and pd.notna(data_max):
                    data_inicio = st.date_input("Data Inicial:", value=data_min)
                    data_fim = st.date_input("Data Final:", value=data_max)
        
        with col3:
            codigo_filtro = st.text_input("Filtrar por Código BM:", placeholder="Deixe vazio para todos")
        
        # Aplicar filtros
        df_filtrado = df_historico[df_historico['Tipo'].isin(tipo_filtro)]
        
        if codigo_filtro:
            df_filtrado = df_filtrado[df_filtrado['CÓDIGO BM'].astype(str).str.contains(str(codigo_filtro), case=False)]
        
        # Exibir histórico
        st.dataframe(
            df_filtrado.sort_values(['Data', 'Hora'], ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                'Valor Total': st.column_config.NumberColumn(format="R$ %.2f")
            }
        )
        
        # Estatísticas
        st.markdown("---")
        st.subheader("📊 Resumo de Movimentações")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_mov = len(df_filtrado)
            st.metric("Total de Movimentações", total_mov)
        
        with col2:
            entradas = len(df_filtrado[df_filtrado['Tipo'].str.contains('Entrada')])
            st.metric("Entradas", entradas)
        
        with col3:
            saidas = len(df_filtrado[df_filtrado['Tipo'] == 'Saída'])
            st.metric("Saídas", saidas)
        
        with col4:
            valor_mov = df_filtrado['Valor Total'].sum()
            st.metric("Valor Total Movimentado", formatar_moeda(valor_mov))

# Rodapé
st.markdown("---")
st.markdown("🏢 **Sistema de Gestão de Estoque - SIG** | Desenvolvido com Streamlit")
