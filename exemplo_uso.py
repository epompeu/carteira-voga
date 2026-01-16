#!/usr/bin/env python3
"""
Exemplo de uso do Carteira Analyzer com dados fictícios.
Demonstra como usar a biblioteca programaticamente.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from core import ProcessadorCarteira, AnalisadorAvancado, GerenciadorArquivos
from core.gerador_relatorios import GeradorGraficos, GeradorRelatorioHTML


def criar_dados_exemplo():
    """Cria dados de exemplo para demonstração."""
    
    print("📊 Criando dados de exemplo...")
    
    # Dados de Renda Fixa
    rf_data = {
        'Ativo': ['LTN 01/01/2024', 'LTN 01/04/2024', 'NTN-B 15/08/2024', 'CDB Banco X', 'Debênture Y'],
        'Valor Bruto - Opção Cliente': [10000, 15000, 20000, 8000, 12000],
        'Data Vencimento': [
            datetime.now() + timedelta(days=30),
            datetime.now() + timedelta(days=90),
            datetime.now() + timedelta(days=180),
            datetime.now() + timedelta(days=365),
            datetime.now() + timedelta(days=730)
        ],
        'Sub Mercado': ['Tesouro Direto', 'Tesouro Direto', 'Tesouro Direto', 'Renda Fixa', 'Renda Fixa']
    }
    
    # Dados de COE
    coe_data = {
        'Ativo': ['COE Ação PETR4', 'COE Índice IBOV', 'COE Moeda USD'],
        'Valor Bruto - Opção Cliente': [5000, 7000, 3000],
        'Data Vencimento': [
            datetime.now() + timedelta(days=180),
            datetime.now() + timedelta(days=365),
            datetime.now() + timedelta(days=90)
        ],
        'Tipo': ['Ação', 'Índice', 'Moeda']
    }
    
    # Dados de Renda Variável
    rv_data = {
        'Ativo': ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'Fundo Imobiliário ABC'],
        'Valor Atual': [25000, 18000, 12000, 15000, 8000],
        'Tipo': ['Ação', 'Ação', 'Ação', 'Ação', 'Fundo Imobiliário']
    }
    
    # Dados de Derivativos
    der_data = {
        'Ativo': ['Opção PETR4 Call', 'Futuro IBOV', 'Swap USD/BRL'],
        'Valor': [2000, 5000, 3000],
        'Data Vencimento': [
            datetime.now() + timedelta(days=15),
            datetime.now() + timedelta(days=30),
            datetime.now() + timedelta(days=60)
        ],
        'Tipo': ['Opção', 'Futuro', 'Swap']
    }
    
    # Criar DataFrames
    df_rf = pd.DataFrame(rf_data)
    df_coe = pd.DataFrame(coe_data)
    df_rv = pd.DataFrame(rv_data)
    df_der = pd.DataFrame(der_data)
    
    # Salvar em arquivos temporários
    temp_dir = Path('/tmp/carteira_exemplo')
    temp_dir.mkdir(exist_ok=True)
    
    rf_file = temp_dir / 'renda_fixa.xlsx'
    coe_file = temp_dir / 'coe.xlsx'
    rv_file = temp_dir / 'renda_variavel.xlsx'
    der_file = temp_dir / 'derivativos.xlsx'
    
    df_rf.to_excel(rf_file, index=False)
    df_coe.to_excel(coe_file, index=False)
    df_rv.to_excel(rv_file, index=False)
    df_der.to_excel(der_file, index=False)
    
    print(f"✅ Dados criados em {temp_dir}")
    
    return rf_file, coe_file, rv_file, der_file


def exemplo_basico():
    """Exemplo básico de uso."""
    
    print("\n" + "="*80)
    print("EXEMPLO 1: USO BÁSICO".center(80))
    print("="*80)
    
    # Criar dados
    rf_file, coe_file, rv_file, der_file = criar_dados_exemplo()
    
    # Criar processador
    processador = ProcessadorCarteira()
    
    # Carregar dados
    print("\n📂 Carregando dados...")
    processador.carregar_renda_fixa(str(rf_file))
    processador.carregar_coe(str(coe_file))
    processador.carregar_renda_variavel(str(rv_file))
    processador.carregar_derivativos(str(der_file))
    
    # Consolidar
    print("\n🔄 Consolidando carteira...")
    carteira = processador.consolidar_carteira()
    print(f"✅ Carteira consolidada com {len(carteira)} ativos")
    
    # Obter resumo
    print("\n📊 RESUMO DA CARTEIRA")
    print("-" * 80)
    
    stats = processador.obter_estatisticas()
    print(f"Total de Ativos: {stats['total_ativos']}")
    print(f"Valor Total: R$ {stats['valor_total']:,.2f}")
    print(f"Valor Médio: R$ {stats['valor_medio']:,.2f}")
    print(f"Categorias: {stats['categorias']}")
    
    # Alocação
    print("\n💼 ALOCAÇÃO POR CATEGORIA")
    print("-" * 80)
    
    alocacao, total = processador.obter_resumo_alocacao()
    for _, row in alocacao.iterrows():
        print(f"{row['Categoria']:20} | R$ {row['Valor Total']:12,.2f} | {row['Percentual']:6.2f}%")
    
    # Alertas
    print("\n⚠️  ALERTAS DE VENCIMENTO")
    print("-" * 80)
    
    alertas = processador.obter_alertas_vencimento()
    if alertas is not None and not alertas.empty:
        for _, row in alertas.iterrows():
            dias = int(row['Dias para Vencer']) if pd.notna(row['Dias para Vencer']) else 0
            print(f"{row['Ativo']:30} | {dias:3} dias | {row['Status Vencimento']}")
    else:
        print("Nenhum alerta de vencimento")
    
    return processador, carteira


def exemplo_analises_avancadas(processador, carteira):
    """Exemplo de análises avançadas."""
    
    print("\n" + "="*80)
    print("EXEMPLO 2: ANÁLISES AVANÇADAS".center(80))
    print("="*80)
    
    # Criar analisador
    analisador = AnalisadorAvancado(carteira)
    
    # Diversificação
    print("\n🎯 ANÁLISE DE DIVERSIFICAÇÃO")
    print("-" * 80)
    
    diversificacao = analisador.analisar_diversificacao()
    print(f"Score de Diversificação: {diversificacao['diversificacao_score']}/100")
    print(f"Classificação: {diversificacao['classificacao_concentracao']}")
    print(f"Número de Ativos: {diversificacao['numero_ativos']}")
    print(f"Número de Classes: {diversificacao['numero_classes']}")
    print(f"Maior Posição: {diversificacao['maior_posicao_percentual']:.2f}%")
    print(f"Top 5: {diversificacao['top_5_percentual']:.2f}%")
    print(f"HHI: {diversificacao['hhi']:.2f}")
    
    # Vencimentos
    print("\n📅 ANÁLISE DE VENCIMENTOS")
    print("-" * 80)
    
    vencimentos = analisador.analisar_vencimentos()
    print(f"Próximos 30 dias: R$ {vencimentos['valor_proximo_30_dias']:,.2f} ({vencimentos['percentual_proximo_30_dias']:.2f}%)")
    print(f"Próximos 60 dias: R$ {vencimentos['valor_proximo_60_dias']:,.2f} ({vencimentos['percentual_proximo_60_dias']:.2f}%)")
    print(f"Próximos 90 dias: R$ {vencimentos['valor_proximo_90_dias']:,.2f} ({vencimentos['percentual_proximo_90_dias']:.2f}%)")
    print(f"Vencido: R$ {vencimentos['valor_vencido']:,.2f} ({vencimentos['percentual_vencido']:.2f}%)")
    
    # Risco
    print("\n⚠️  ANÁLISE DE RISCO")
    print("-" * 80)
    
    risco = analisador.analisar_risco_vencimento()
    print(f"Nível de Risco Geral: {risco['nivel_risco_geral']}")
    print(f"Risco Crítico: R$ {risco['risco_critico_valor']:,.2f} ({risco['risco_critico_percentual']:.2f}%)")
    print(f"Risco Moderado: R$ {risco['risco_moderado_valor']:,.2f} ({risco['risco_moderado_percentual']:.2f}%)")
    print(f"Risco Baixo: R$ {risco['risco_baixo_valor']:,.2f} ({risco['risco_baixo_percentual']:.2f}%)")
    
    # Top Ativos
    print("\n⭐ TOP 10 ATIVOS")
    print("-" * 80)
    
    top_ativos = analisador.obter_top_ativos(10)
    for _, row in top_ativos.iterrows():
        print(f"{row['Ativo']:30} | R$ {row['Valor']:12,.2f} | {row['Percentual']:6.2f}%")
    
    return diversificacao, vencimentos, risco, top_ativos


def exemplo_graficos_e_relatorios(processador, carteira, diversificacao, vencimentos, risco, top_ativos):
    """Exemplo de geração de gráficos e relatórios."""
    
    print("\n" + "="*80)
    print("EXEMPLO 3: GRÁFICOS E RELATÓRIOS".center(80))
    print("="*80)
    
    # Obter dados
    alocacao, total = processador.obter_resumo_alocacao()
    stats = processador.obter_estatisticas()
    
    # Gerar gráficos
    print("\n📈 Gerando gráficos...")
    
    caminhos_graficos = {}
    
    sucesso, caminho = GeradorGraficos.criar_grafico_pizza_alocacao(alocacao)
    if sucesso:
        caminhos_graficos['pizza_alocacao'] = caminho
        print(f"   ✅ Pizza de alocação: {caminho}")
    
    sucesso, caminho = GeradorGraficos.criar_grafico_barras_alocacao(alocacao)
    if sucesso:
        caminhos_graficos['barras_alocacao'] = caminho
        print(f"   ✅ Barras de alocação: {caminho}")
    
    sucesso, caminho = GeradorGraficos.criar_grafico_vencimentos(vencimentos)
    if sucesso:
        caminhos_graficos['vencimentos'] = caminho
        print(f"   ✅ Vencimentos: {caminho}")
    
    sucesso, caminho = GeradorGraficos.criar_grafico_risco(risco)
    if sucesso:
        caminhos_graficos['risco'] = caminho
        print(f"   ✅ Risco: {caminho}")
    
    sucesso, caminho = GeradorGraficos.criar_grafico_top_ativos(top_ativos)
    if sucesso:
        caminhos_graficos['top_ativos'] = caminho
        print(f"   ✅ Top ativos: {caminho}")
    
    # Gerar relatório HTML
    print("\n🌐 Gerando relatório HTML...")
    
    sucesso, html = GeradorRelatorioHTML.gerar_relatorio_html(
        nome_cliente="Cliente Exemplo",
        data_relatorio=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        estatisticas=stats,
        alocacao=alocacao,
        diversificacao=diversificacao,
        vencimentos=vencimentos,
        risco=risco,
        top_ativos=top_ativos,
        caminhos_graficos=caminhos_graficos
    )
    
    if sucesso:
        caminho_html = '/tmp/relatorio_exemplo.html'
        with open(caminho_html, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✅ Relatório HTML: {caminho_html}")
    
    # Exportar Excel
    print("\n📊 Exportando para Excel...")
    
    caminho_excel = '/tmp/relatorio_exemplo.xlsx'
    sucesso, msg = processador.exportar_para_excel(caminho_excel)
    if sucesso:
        print(f"   ✅ Relatório Excel: {caminho_excel}")
    else:
        print(f"   ❌ {msg}")


def main():
    """Função principal."""
    
    print("\n" + "="*80)
    print("CARTEIRA ANALYZER - EXEMPLOS DE USO".center(80))
    print("="*80)
    
    try:
        # Exemplo 1: Básico
        processador, carteira = exemplo_basico()
        
        # Exemplo 2: Análises Avançadas
        diversificacao, vencimentos, risco, top_ativos = exemplo_analises_avancadas(processador, carteira)
        
        # Exemplo 3: Gráficos e Relatórios
        exemplo_graficos_e_relatorios(processador, carteira, diversificacao, vencimentos, risco, top_ativos)
        
        print("\n" + "="*80)
        print("✅ EXEMPLOS CONCLUÍDOS COM SUCESSO".center(80))
        print("="*80)
        print("\nArquivos gerados:")
        print("  - /tmp/relatorio_exemplo.html")
        print("  - /tmp/relatorio_exemplo.xlsx")
        print("  - /tmp/grafico_*.png")
        print("\nAbra o arquivo HTML em um navegador para ver o relatório completo!\n")
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
