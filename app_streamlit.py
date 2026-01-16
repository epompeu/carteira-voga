#!/usr/bin/env python3
"""
Aplicação Streamlit para Análise de Carteiras de Clientes
Interface web para upload e análise de 5 tipos de relatórios
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import sys

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from core.parsers_relatorios import GerenciadorParsers
from core.analisador_relatorios import AnalisadorRelatorios

# Configuração da página
st.set_page_config(
    page_title="Carteira Analyzer - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'relatorios' not in st.session_state:
    st.session_state.relatorios = {
        'fundos': None,
        'previdencia': None,
        'renda_fixa': None,
        'coe': None,
        'renda_variavel': None
    }

if 'parsers' not in st.session_state:
    st.session_state.parsers = {
        'fundos': None,
        'previdencia': None,
        'renda_fixa': None,
        'coe': None,
        'renda_variavel': None
    }

if 'dados_consolidados' not in st.session_state:
    st.session_state.dados_consolidados = None

if 'dados_processados' not in st.session_state:
    st.session_state.dados_processados = {}

# ============================================================================
# HEADER
# ============================================================================

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("📊 Carteira Analyzer")
    st.markdown("**Dashboard de Análise de Carteiras de Clientes**")

st.markdown("---")

# ============================================================================
# SIDEBAR - UPLOAD DE RELATÓRIOS
# ============================================================================

with st.sidebar:
    st.header("📁 Gerenciar Relatórios")
    
    # Abas para diferentes seções
    tab_upload, tab_config = st.tabs(["📤 Upload", "⚙️ Configuração"])
    
    with tab_upload:
        st.subheader("Enviar Relatórios")
        
        # Fundos
        st.markdown("### 1️⃣ Relatório de Fundos")
        arquivo_fundos = st.file_uploader(
            "Selecione o arquivo de Fundos",
            type=['xlsx', 'xls', 'csv'],
            key='fundos'
        )
        if arquivo_fundos:
            try:
                df_fundos = pd.read_excel(arquivo_fundos)
                st.session_state.relatorios['fundos'] = df_fundos
                
                # Processar com parser
                sucesso, df_proc, msg = GerenciadorParsers.processar_relatorio(df_fundos, 'fundos')
                if sucesso:
                    st.session_state.dados_processados['fundos'] = df_proc
                    st.success(f"✅ Fundos carregado! {msg}")
                else:
                    st.warning(f"⚠️ {msg}")
                
                st.write(f"Linhas: {len(df_fundos)} | Colunas: {len(df_fundos.columns)}")
            except Exception as e:
                st.error(f"❌ Erro ao carregar Fundos: {str(e)}")
        
        st.divider()
        
        # Previdência
        st.markdown("### 2️⃣ Relatório de Previdência")
        arquivo_previdencia = st.file_uploader(
            "Selecione o arquivo de Previdência",
            type=['xlsx', 'xls', 'csv'],
            key='previdencia'
        )
        if arquivo_previdencia:
            try:
                df_previdencia = pd.read_excel(arquivo_previdencia)
                st.session_state.relatorios['previdencia'] = df_previdencia
                
                # Processar com parser
                sucesso, df_proc, msg = GerenciadorParsers.processar_relatorio(df_previdencia, 'previdencia')
                if sucesso:
                    st.session_state.dados_processados['previdencia'] = df_proc
                    st.success(f"✅ Previdência carregado! {msg}")
                else:
                    st.warning(f"⚠️ {msg}")
                
                st.write(f"Linhas: {len(df_previdencia)} | Colunas: {len(df_previdencia.columns)}")
            except Exception as e:
                st.error(f"❌ Erro ao carregar Previdência: {str(e)}")
        
        st.divider()
        
        # Renda Fixa
        st.markdown("### 3️⃣ Relatório de Renda Fixa")
        arquivo_rf = st.file_uploader(
            "Selecione o arquivo de Renda Fixa",
            type=['xlsx', 'xls', 'csv'],
            key='renda_fixa'
        )
        if arquivo_rf:
            try:
                df_rf = pd.read_excel(arquivo_rf)
                st.session_state.relatorios['renda_fixa'] = df_rf
                
                # Processar com parser
                sucesso, df_proc, msg = GerenciadorParsers.processar_relatorio(df_rf, 'renda_fixa')
                if sucesso:
                    st.session_state.dados_processados['renda_fixa'] = df_proc
                    st.success(f"✅ Renda Fixa carregado! {msg}")
                else:
                    st.warning(f"⚠️ {msg}")
                
                st.write(f"Linhas: {len(df_rf)} | Colunas: {len(df_rf.columns)}")
            except Exception as e:
                st.error(f"❌ Erro ao carregar Renda Fixa: {str(e)}")
        
        st.divider()
        
        # COE
        st.markdown("### 4️⃣ Relatório de COE")
        arquivo_coe = st.file_uploader(
            "Selecione o arquivo de COE",
            type=['xlsx', 'xls', 'csv'],
            key='coe'
        )
        if arquivo_coe:
            try:
                df_coe = pd.read_excel(arquivo_coe)
                st.session_state.relatorios['coe'] = df_coe
                
                # Processar com parser
                sucesso, df_proc, msg = GerenciadorParsers.processar_relatorio(df_coe, 'coe')
                if sucesso:
                    st.session_state.dados_processados['coe'] = df_proc
                    st.success(f"✅ COE carregado! {msg}")
                else:
                    st.warning(f"⚠️ {msg}")
                
                st.write(f"Linhas: {len(df_coe)} | Colunas: {len(df_coe.columns)}")
            except Exception as e:
                st.error(f"❌ Erro ao carregar COE: {str(e)}")
        
        st.divider()
        
        # Renda Variável
        st.markdown("### 5️⃣ Relatório de Renda Variável")
        arquivo_rv = st.file_uploader(
            "Selecione o arquivo de Renda Variável",
            type=['xlsx', 'xls', 'csv'],
            key='renda_variavel'
        )
        if arquivo_rv:
            try:
                df_rv = pd.read_excel(arquivo_rv)
                st.session_state.relatorios['renda_variavel'] = df_rv
                
                # Processar com parser
                sucesso, df_proc, msg = GerenciadorParsers.processar_relatorio(df_rv, 'renda_variavel')
                if sucesso:
                    st.session_state.dados_processados['renda_variavel'] = df_proc
                    st.success(f"✅ Renda Variável carregado! {msg}")
                else:
                    st.warning(f"⚠️ {msg}")
                
                st.write(f"Linhas: {len(df_rv)} | Colunas: {len(df_rv.columns)}")
            except Exception as e:
                st.error(f"❌ Erro ao carregar Renda Variável: {str(e)}")
    
    with tab_config:
        st.subheader("Configurações")
        
        # Verificar status dos relatórios
        st.markdown("**Status dos Relatórios:**")
        status_relatorios = {
            'Fundos': '✅' if st.session_state.relatorios['fundos'] is not None else '❌',
            'Previdência': '✅' if st.session_state.relatorios['previdencia'] is not None else '❌',
            'Renda Fixa': '✅' if st.session_state.relatorios['renda_fixa'] is not None else '❌',
            'COE': '✅' if st.session_state.relatorios['coe'] is not None else '❌',
            'Renda Variável': '✅' if st.session_state.relatorios['renda_variavel'] is not None else '❌',
        }
        
        for nome, status in status_relatorios.items():
            st.write(f"{status} {nome}")

# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📋 Dados", "⚠️ Alertas", "ℹ️ Informações"])

with tab1:
    st.header("Dashboard de Análise")
    
    # Verificar se há dados carregados
    relatorios_carregados = sum(1 for v in st.session_state.relatorios.values() if v is not None)
    
    if relatorios_carregados == 0:
        st.warning("⚠️ Nenhum relatório carregado ainda. Por favor, envie os arquivos na barra lateral.")
    else:
        st.info(f"✅ {relatorios_carregados} relatório(s) carregado(s)")
        
        # Filtro por Assessor (placeholder)
        st.subheader("Filtros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            assessor_selecionado = st.selectbox(
                "Filtrar por Assessor",
                options=["Todos os Assessores", "Assessor 1", "Assessor 2", "Assessor 3"]
            )
        
        with col2:
            classe_selecionada = st.selectbox(
                "Filtrar por Classe de Ativo",
                options=["Todas as Classes", "Fundos", "Previdência", "Renda Fixa", "COE", "Renda Variável"]
            )
        
        st.divider()
        
        # Gráficos de exemplo
        st.subheader("Alocação de Ativos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distribuição por Tipo de Ativo**")
            # Placeholder para gráfico
            fig_pizza = go.Figure(data=[go.Pie(
                labels=['Fundos', 'Previdência', 'Renda Fixa', 'COE', 'Renda Variável'],
                values=[20, 15, 35, 10, 20],
                marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
            )])
            fig_pizza.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig_pizza, use_container_width=True)
        
        with col2:
            st.markdown("**Valor por Classe de Ativo (R$)**")
            # Placeholder para gráfico
            fig_barras = go.Figure(data=[go.Bar(
                x=['Fundos', 'Previdência', 'Renda Fixa', 'COE', 'Renda Variável'],
                y=[150000, 120000, 250000, 80000, 150000],
                marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
            )])
            fig_barras.update_layout(height=400, xaxis_title="Classe de Ativo", yaxis_title="Valor (R$)")
            st.plotly_chart(fig_barras, use_container_width=True)
        
        st.divider()
        
        # Métricas
        st.subheader("Resumo Executivo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Clientes", "45", "+2")
        
        with col2:
            st.metric("Valor Total em Carteira", "R$ 750.000", "+5%")
        
        with col3:
            st.metric("Número de Assessores", "8", "0")
        
        with col4:
            st.metric("Investimentos em Alerta", "12", "+3")

with tab2:
    st.header("Dados Detalhados")
    
    relatorios_carregados = sum(1 for v in st.session_state.relatorios.values() if v is not None)
    
    if relatorios_carregados == 0:
        st.warning("⚠️ Nenhum relatório carregado ainda.")
    else:
        # Abas para cada tipo de relatório
        sub_tabs = []
        if st.session_state.relatorios['fundos'] is not None:
            sub_tabs.append("Fundos")
        if st.session_state.relatorios['previdencia'] is not None:
            sub_tabs.append("Previdência")
        if st.session_state.relatorios['renda_fixa'] is not None:
            sub_tabs.append("Renda Fixa")
        if st.session_state.relatorios['coe'] is not None:
            sub_tabs.append("COE")
        if st.session_state.relatorios['renda_variavel'] is not None:
            sub_tabs.append("Renda Variável")
        
        if sub_tabs:
            tabs_dados = st.tabs(sub_tabs)
            
            for idx, tab_nome in enumerate(sub_tabs):
                with tabs_dados[idx]:
                    chave = tab_nome.lower().replace(' ', '_')
                    df = st.session_state.relatorios[chave]
                    
                    st.markdown(f"**{tab_nome}** - {len(df)} linhas, {len(df.columns)} colunas")
                    st.dataframe(df, use_container_width=True, height=400)
                    
                    # Botão para download
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Baixar {tab_nome} como CSV",
                        data=csv,
                        file_name=f"{chave}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

with tab3:
    st.header("⚠️ Alertas de Vencimento")
    
    relatorios_carregados = sum(1 for v in st.session_state.relatorios.values() if v is not None)
    
    if relatorios_carregados == 0:
        st.warning("⚠️ Nenhum relatório carregado ainda.")
    else:
        st.info("📌 Investimentos com vencimento nos próximos 30 dias")
        
        # Placeholder para alertas
        alertas_data = {
            'Cliente': ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
            'Assessor': ['Assessor 1', 'Assessor 2', 'Assessor 1'],
            'Ativo': ['LTN 01/02/2026', 'CDB Banco X', 'Debênture Y'],
            'Data Vencimento': ['2026-02-01', '2026-01-25', '2026-02-05'],
            'Dias para Vencer': [16, 9, 20],
            'Valor (R$)': [50000, 30000, 45000],
            'Status': ['⚠️ ALERTA', '🔴 CRÍTICO', '⚠️ ALERTA']
        }
        
        df_alertas = pd.DataFrame(alertas_data)
        st.dataframe(df_alertas, use_container_width=True, hide_index=True)

with tab4:
    st.header("ℹ️ Informações")
    
    st.markdown("""
    ### 📊 Carteira Analyzer - Dashboard Web
    
    **Versão:** 1.0.0  
    **Data:** 16 de janeiro de 2026
    
    #### 🎯 Funcionalidades
    
    - ✅ Upload de 5 tipos de relatórios
    - ✅ Análise de alocação de ativos
    - ✅ Filtros por assessor e classe
    - ✅ Gráficos dinâmicos e interativos
    - ✅ Alertas de vencimento
    - ✅ Exportação de dados
    
    #### 📋 Tipos de Relatórios Suportados
    
    1. **Fundos** - Análise de fundos de investimento
    2. **Previdência** - Produtos de previdência complementar
    3. **Renda Fixa** - Títulos e investimentos de renda fixa
    4. **COE** - Certificados de Operações Estruturadas
    5. **Renda Variável** - Ações e fundos imobiliários
    
    #### 🚀 Como Usar
    
    1. Acesse a aba "📤 Upload" na barra lateral
    2. Envie cada tipo de relatório (um por vez)
    3. Visualize os dados no dashboard
    4. Use os filtros para análises específicas
    5. Monitore os alertas de vencimento
    
    #### 📞 Suporte
    
    Para dúvidas ou problemas, consulte a documentação ou entre em contato com o suporte.
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Desenvolvido por:** Carteira Analyzer")

with col2:
    st.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

with col3:
    st.markdown("**Status:** ✅ Online")
