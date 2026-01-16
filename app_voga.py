"""
Carteira VOGA - Aplicação Web para Análise de Carteiras de Investimentos
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Adicionar diretório ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from parsers_relatorios import (
    ParserRendaFixa, ParserFundos, ParserPrevidencia,
    ParserCOE, ParserRendaVariavel
)
from analisador_relatorios import AnalisadorRelatorios
from gerador_excel import gerar_excel_para_download

# Configuração da página
st.set_page_config(
    page_title="Carteira VOGA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #30363d;
    }
    .alert-critical {
        background-color: #3d1f1f;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ff0000;
        color: #ff6b6b;
    }
    .alert-warning {
        background-color: #3d3a1f;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        color: #ffd700;
    }
    </style>
""", unsafe_allow_html=True)

# Header com logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("assets/logo.png", width=200)
    except Exception as e:
        st.write("📊 Carteira VOGA")
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Carteira VOGA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #c9d1d9;'>Análise Profissional de Carteiras de Investimentos</p>", unsafe_allow_html=True)

st.markdown("---")

# Inicializar session state
if 'dados_processados' not in st.session_state:
    st.session_state.dados_processados = {}

# Sidebar - Upload de relatórios
st.sidebar.title("📁 Upload de Relatórios")
st.sidebar.markdown("Envie os arquivos Excel dos relatórios para análise")

tipos_relatorios = {
    'Renda Fixa': ParserRendaFixa,
    'Fundos': ParserFundos,
    'Previdência': ParserPrevidencia,
    'COE': ParserCOE,
    'Renda Variável': ParserRendaVariavel
}

for tipo, parser_class in tipos_relatorios.items():
    uploaded_file = st.sidebar.file_uploader(
        f"📄 {tipo}",
        type=['xlsx', 'xls'],
        key=f"upload_{tipo}"
    )
    
    if uploaded_file is not None:
        try:
            # Ler arquivo
            df = pd.read_excel(uploaded_file)
            
            # Validar estrutura
            valido, mensagem = parser_class.validar_estrutura(df)
            
            if valido:
                # Processar dados
                df_processado = parser_class.processar(df)
                st.session_state.dados_processados[tipo] = df_processado
                st.sidebar.success(f"✅ {tipo} carregado com sucesso!")
            else:
                st.sidebar.error(f"❌ {tipo}: {mensagem}")
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao processar {tipo}: {str(e)}")

# Botão de download
st.sidebar.markdown("---")
if st.session_state.dados_processados:
    if st.sidebar.button("📥 Download Planilha Consolidada", use_container_width=True):
        buffer, nome_arquivo = gerar_excel_para_download(st.session_state.dados_processados)
        
        if buffer:
            st.sidebar.download_button(
                label="📊 Baixar Excel",
                data=buffer,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# Conteúdo principal
if not st.session_state.dados_processados:
    st.info("👈 Por favor, envie os relatórios no painel lateral para começar a análise")
else:
    # Consolidar dados
    df_consolidado = pd.concat(
        list(st.session_state.dados_processados.values()),
        ignore_index=True
    )
    
    # Criar abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "📋 Dados Detalhados",
        "⚠️ Alertas de Vencimento",
        "📈 Análises",
        "ℹ️ Informações"
    ])
    
    # TAB 1: Dashboard
    with tab1:
        st.subheader("Dashboard de Carteira")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            assessores = ['Todos'] + sorted(df_consolidado['assessor'].unique().tolist())
            assessor_selecionado = st.selectbox("🧑‍💼 Filtrar por Assessor", assessores)
        
        with col2:
            classes_unicas = df_consolidado['classe_ativo'].unique().tolist()
            # Converter para string e remover NaN
            classes_unicas = [str(c) for c in classes_unicas if pd.notna(c)]
            classes = ['Todos'] + sorted(set(classes_unicas))
            classe_selecionada = st.selectbox("📂 Filtrar por Classe", classes)
        
        # Aplicar filtros
        df_filtrado = df_consolidado.copy()
        
        if assessor_selecionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['assessor'] == assessor_selecionado]
        
        if classe_selecionada != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['classe_ativo'] == classe_selecionada]
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Valor Total", f"R$ {df_filtrado['valor_bruto'].sum():,.2f}")
        
        with col2:
            st.metric("📊 Total de Ativos", len(df_filtrado))
        
        with col3:
            st.metric("👥 Clientes", df_filtrado['cliente_nome'].nunique())
        
        with col4:
            st.metric("🎯 Assessores", df_filtrado['assessor'].nunique())
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de Pizza - Alocação por Tipo de Relatório
            df_tipo = df_filtrado.groupby('tipo_relatorio')['valor_bruto'].sum().reset_index()
            fig_tipo = px.pie(
                df_tipo,
                values='valor_bruto',
                names='tipo_relatorio',
                title="Alocação por Tipo de Relatório",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_tipo, use_container_width=True)
        
        with col2:
            # Gráfico de Pizza - Alocação por Classe
            df_classe = df_filtrado.groupby('classe_ativo')['valor_bruto'].sum().reset_index()
            fig_classe = px.pie(
                df_classe,
                values='valor_bruto',
                names='classe_ativo',
                title="Alocação por Classe de Ativo",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_classe, use_container_width=True)
        
        # Gráfico de Barras - Top 10 Ativos
        df_top = df_filtrado.nlargest(10, 'valor_bruto')[['tipo_ativo', 'valor_bruto', 'tipo_relatorio']]
        fig_top = px.bar(
            df_top,
            x='valor_bruto',
            y='tipo_ativo',
            orientation='h',
            title="Top 10 Ativos por Valor",
            color='tipo_relatorio',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_top, use_container_width=True)
    
    # TAB 2: Dados Detalhados
    with tab2:
        st.subheader("Dados Detalhados dos Relatórios")
        
        tipo_selecionado = st.selectbox(
            "Selecione o tipo de relatório",
            list(st.session_state.dados_processados.keys())
        )
        
        df_tipo = st.session_state.dados_processados[tipo_selecionado]
        
        st.dataframe(df_tipo, use_container_width=True, height=500)
        
        # Download CSV
        csv = df_tipo.to_csv(index=False)
        st.download_button(
            label="📥 Baixar como CSV",
            data=csv,
            file_name=f"{tipo_selecionado}.csv",
            mime="text/csv"
        )
    
    # TAB 3: Alertas de Vencimento
    with tab3:
        st.subheader("⚠️ Alertas de Vencimento")
        
        # Filtrar ativos com vencimento próximo
        if 'dias_para_vencer' in df_consolidado.columns:
            df_vencimento = df_consolidado[df_consolidado['dias_para_vencer'] <= 30].copy()
            
            if df_vencimento.empty:
                st.success("✅ Nenhum ativo com vencimento próximo!")
            else:
                # Ordenar por dias para vencer
                df_vencimento = df_vencimento.sort_values('dias_para_vencer')
                
                # Exibir alertas
                for idx, row in df_vencimento.iterrows():
                    dias = row['dias_para_vencer']
                    
                    if dias <= 0:
                        css_class = "alert-critical"
                        status = "🔴 VENCIDO"
                    else:
                        css_class = "alert-warning"
                        status = "🟡 CRÍTICO"
                    
                    alerta_html = f"""
                    <div class="{css_class}">
                        <strong>{status}</strong> - {row['tipo_ativo']}<br>
                        Cliente: {row['cliente_nome']} | Assessor: {row['assessor']}<br>
                        Valor: R$ {row['valor_bruto']:,.2f} | Dias para vencer: {dias}
                    </div>
                    """
                    st.markdown(alerta_html, unsafe_allow_html=True)
        else:
            st.info("Nenhum ativo com data de vencimento neste conjunto de dados")
    
    # TAB 4: Análises
    with tab4:
        st.subheader("📈 Análises Avançadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Valor Médio por Ativo",
                f"R$ {df_consolidado['valor_bruto'].mean():,.2f}"
            )
            st.metric(
                "Valor Máximo",
                f"R$ {df_consolidado['valor_bruto'].max():,.2f}"
            )
        
        with col2:
            st.metric(
                "Valor Mínimo",
                f"R$ {df_consolidado['valor_bruto'].min():,.2f}"
            )
            st.metric(
                "Desvio Padrão",
                f"R$ {df_consolidado['valor_bruto'].std():,.2f}"
            )
        
        st.markdown("---")
        
        # Distribuição por Cliente
        st.subheader("Distribuição por Cliente")
        df_cliente = df_consolidado.groupby('cliente_nome')['valor_bruto'].sum().reset_index()
        df_cliente = df_cliente.sort_values('valor_bruto', ascending=False)
        
        fig_cliente = px.bar(
            df_cliente,
            x='cliente_nome',
            y='valor_bruto',
            title="Valor Total por Cliente",
            labels={'cliente_nome': 'Cliente', 'valor_bruto': 'Valor (R$)'},
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_cliente, use_container_width=True)
    
    # TAB 5: Informações
    with tab5:
        st.subheader("ℹ️ Informações da Aplicação")
        
        st.markdown("""
        ### 📊 Carteira VOGA
        
        Aplicação profissional para análise de carteiras de investimentos.
        
        #### Funcionalidades:
        - ✅ Upload de 5 tipos de relatórios (Renda Fixa, Fundos, Previdência, COE, Renda Variável)
        - ✅ Análise consolidada de carteiras
        - ✅ Filtros por assessor e classe de ativo
        - ✅ Alertas de vencimento
        - ✅ Download de planilha Excel consolidada
        - ✅ Gráficos interativos
        
        #### Tipos de Relatórios Suportados:
        1. **Renda Fixa** - Títulos, CDB, Debêntures
        2. **Fundos** - Fundos de investimento
        3. **Previdência** - PGBL e VGBL
        4. **COE** - Certificados estruturados
        5. **Renda Variável** - Ações e FIIs
        
        #### Segurança:
        - Sem armazenamento de dados
        - Processamento local
        - Acesso aberto
        
        #### Desenvolvido com:
        - Python 3.11
        - Streamlit
        - Pandas
        - Plotly
        
        ---
        
        **Versão:** 1.0  
        **Última atualização:** """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        )

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666; font-size: 12px;'>Carteira VOGA © 2026 - Análise de Carteiras de Investimentos</p>", unsafe_allow_html=True)
