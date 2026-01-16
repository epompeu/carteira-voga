#!/usr/bin/env python3
"""
Interface de linha de comando (CLI) para o Carteira Analyzer.
Permite processar carteiras de clientes através de comandos simples.
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import os

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from core import (
    ProcessadorCarteira,
    CategoriaInvestimento,
    AnalisadorAvancado,
    GerenciadorArquivos,
    FormatadorDados,
    GeradorRelatorios
)
from core.processador_planilhas import ProcessadorPlanilhas
from core.gerador_relatorios import GeradorGraficos, GeradorRelatorioHTML

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CarteiraCLI:
    """Interface de linha de comando para Carteira Analyzer."""
    
    def __init__(self):
        """Inicializa a CLI."""
        self.processador = ProcessadorCarteira()
        self.processador_planilhas = ProcessadorPlanilhas()
        self.diretorio_saida = None
    
    def processar_arquivo(self, caminho_arquivo: str, categoria: str) -> bool:
        """
        Processa um arquivo de carteira.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            categoria: Categoria do investimento
            
        Returns:
            True se bem-sucedido
        """
        print(f"\n📂 Processando arquivo: {caminho_arquivo}")
        
        # Validar arquivo
        valido, msg = GerenciadorArquivos.validar_arquivo(caminho_arquivo)
        if not valido:
            print(f"❌ {msg}")
            return False
        
        # Mapear categoria
        categoria_map = {
            'rf': CategoriaInvestimento.RENDA_FIXA,
            'coe': CategoriaInvestimento.COE,
            'rv': CategoriaInvestimento.RENDA_VARIAVEL,
            'der': CategoriaInvestimento.DERIVATIVOS
        }
        
        categoria_enum = categoria_map.get(categoria.lower())
        if not categoria_enum:
            print(f"❌ Categoria inválida: {categoria}")
            print(f"   Opções: {', '.join(categoria_map.keys())}")
            return False
        
        # Carregar e processar
        sucesso, msg = self.processador.carregar_categoria(caminho_arquivo, categoria_enum)
        if sucesso:
            print(f"✅ {msg}")
            return True
        else:
            print(f"❌ {msg}")
            return False
    
    def consolidar_e_analisar(self, nome_cliente: str) -> bool:
        """
        Consolida dados e realiza análises.
        
        Args:
            nome_cliente: Nome do cliente
            
        Returns:
            True se bem-sucedido
        """
        print(f"\n📊 Consolidando carteira para {nome_cliente}...")
        
        # Consolidar
        carteira = self.processador.consolidar_carteira()
        if carteira is None:
            print("❌ Erro ao consolidar carteira")
            return False
        
        print(f"✅ Carteira consolidada com {len(carteira)} ativos")
        
        # Criar diretório de saída
        self.diretorio_saida = GerenciadorArquivos.criar_diretorio_saida(nome_cliente)
        if not self.diretorio_saida:
            print("❌ Erro ao criar diretório de saída")
            return False
        
        print(f"📁 Diretório de saída: {self.diretorio_saida}")
        
        return True
    
    def gerar_relatorios(self, nome_cliente: str, gerar_html: bool = True, gerar_excel: bool = True) -> bool:
        """
        Gera relatórios em diferentes formatos.
        
        Args:
            nome_cliente: Nome do cliente
            gerar_html: Se deve gerar HTML
            gerar_excel: Se deve gerar Excel
            
        Returns:
            True se bem-sucedido
        """
        if self.diretorio_saida is None:
            print("❌ Diretório de saída não definido")
            return False
        
        print("\n📄 Gerando relatórios...")
        
        # Obter dados para análise
        alocacao, total = self.processador.obter_resumo_alocacao()
        analisador = AnalisadorAvancado(self.processador.carteira_consolidada)
        
        # Gerar gráficos
        print("📈 Gerando gráficos...")
        caminhos_graficos = {}
        
        sucesso, caminho = GeradorGraficos.criar_grafico_pizza_alocacao(alocacao)
        if sucesso:
            caminhos_graficos['pizza_alocacao'] = caminho
            print(f"   ✅ Gráfico de pizza criado")
        
        sucesso, caminho = GeradorGraficos.criar_grafico_barras_alocacao(alocacao)
        if sucesso:
            caminhos_graficos['barras_alocacao'] = caminho
            print(f"   ✅ Gráfico de barras criado")
        
        analise_vencimentos = analisador.analisar_vencimentos()
        if analise_vencimentos:
            sucesso, caminho = GeradorGraficos.criar_grafico_vencimentos(analise_vencimentos)
            if sucesso:
                caminhos_graficos['vencimentos'] = caminho
                print(f"   ✅ Gráfico de vencimentos criado")
        
        analise_risco = analisador.analisar_risco_vencimento()
        if analise_risco:
            sucesso, caminho = GeradorGraficos.criar_grafico_risco(analise_risco)
            if sucesso:
                caminhos_graficos['risco'] = caminho
                print(f"   ✅ Gráfico de risco criado")
        
        top_ativos = analisador.obter_top_ativos(10)
        if top_ativos is not None:
            sucesso, caminho = GeradorGraficos.criar_grafico_top_ativos(top_ativos)
            if sucesso:
                caminhos_graficos['top_ativos'] = caminho
                print(f"   ✅ Gráfico de top ativos criado")
        
        # Gerar HTML
        if gerar_html:
            print("🌐 Gerando relatório HTML...")
            
            stats = self.processador.obter_estatisticas()
            diversificacao = analisador.analisar_diversificacao()
            
            sucesso, html = GeradorRelatorioHTML.gerar_relatorio_html(
                nome_cliente=nome_cliente,
                data_relatorio=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                estatisticas=stats,
                alocacao=alocacao,
                diversificacao=diversificacao,
                vencimentos=analise_vencimentos,
                risco=analise_risco,
                top_ativos=top_ativos,
                caminhos_graficos=caminhos_graficos
            )
            
            if sucesso:
                caminho_html = os.path.join(self.diretorio_saida, 'relatorio_carteira.html')
                with open(caminho_html, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   ✅ Relatório HTML: {caminho_html}")
        
        # Gerar Excel
        if gerar_excel:
            print("📊 Gerando relatório Excel...")
            
            caminho_excel = os.path.join(self.diretorio_saida, 'relatorio_carteira.xlsx')
            sucesso, msg = self.processador.exportar_para_excel(caminho_excel)
            if sucesso:
                print(f"   ✅ Relatório Excel: {caminho_excel}")
            else:
                print(f"   ❌ {msg}")
        
        return True
    
    def exibir_resumo(self):
        """Exibe resumo da carteira."""
        if self.processador.carteira_consolidada is None:
            print("❌ Carteira não consolidada")
            return
        
        print("\n" + "="*80)
        print("RESUMO DA CARTEIRA".center(80))
        print("="*80)
        
        # Estatísticas
        stats = self.processador.obter_estatisticas()
        print(f"\nTotal de Ativos: {stats['total_ativos']}")
        print(f"Valor Total: {FormatadorDados.formatar_moeda(stats['valor_total'])}")
        print(f"Valor Médio: {FormatadorDados.formatar_moeda(stats['valor_medio'])}")
        print(f"Categorias: {stats['categorias']}")
        
        # Alocação
        print("\n" + "-"*80)
        print("ALOCAÇÃO POR CATEGORIA")
        print("-"*80)
        
        alocacao, total = self.processador.obter_resumo_alocacao()
        for _, row in alocacao.iterrows():
            print(f"{row['Categoria']:20} | {FormatadorDados.formatar_moeda(row['Valor Total']):20} | {row['Percentual']:6.2f}%")
        
        # Alertas
        alertas = self.processador.obter_alertas_vencimento()
        if alertas is not None and not alertas.empty:
            print("\n" + "-"*80)
            print("⚠️  ALERTAS DE VENCIMENTO (próximos 60 dias)")
            print("-"*80)
            
            for _, row in alertas.head(5).iterrows():
                dias = int(row['Dias para Vencer']) if pd.notna(row['Dias para Vencer']) else 0
                print(f"{row['Ativo']:20} | {dias:3} dias | {row['Status Vencimento']}")
        
        # Análise de diversificação
        analisador = AnalisadorAvancado(self.processador.carteira_consolidada)
        diversificacao = analisador.analisar_diversificacao()
        
        print("\n" + "-"*80)
        print("DIVERSIFICAÇÃO")
        print("-"*80)
        print(f"Score: {diversificacao['diversificacao_score']}/100")
        print(f"Classificação: {diversificacao['classificacao_concentracao']}")
        print(f"Número de Ativos: {diversificacao['numero_ativos']}")
        print(f"Maior Posição: {diversificacao['maior_posicao_percentual']:.2f}%")
        
        print("\n" + "="*80 + "\n")


def main():
    """Função principal da CLI."""
    parser = argparse.ArgumentParser(
        description='Carteira Analyzer - Análise de Carteiras de Investimentos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Processar arquivo de renda fixa
  python cli.py -c "João Silva" -rf carteira_rf.xlsx

  # Processar múltiplas categorias
  python cli.py -c "João Silva" -rf rf.xlsx -coe coe.xlsx -rv rv.xlsx

  # Processar e gerar apenas Excel
  python cli.py -c "João Silva" -rf rf.xlsx --no-html

  # Processar e exibir resumo
  python cli.py -c "João Silva" -rf rf.xlsx --resumo
        """
    )
    
    parser.add_argument('-c', '--cliente', required=True, help='Nome do cliente')
    parser.add_argument('-rf', '--renda-fixa', help='Arquivo de Renda Fixa')
    parser.add_argument('-coe', '--coe', help='Arquivo de COE')
    parser.add_argument('-rv', '--renda-variavel', help='Arquivo de Renda Variável')
    parser.add_argument('-der', '--derivativos', help='Arquivo de Derivativos')
    parser.add_argument('--no-html', action='store_true', help='Não gerar relatório HTML')
    parser.add_argument('--no-excel', action='store_true', help='Não gerar relatório Excel')
    parser.add_argument('--resumo', action='store_true', help='Exibir resumo no console')
    
    args = parser.parse_args()
    
    # Validar que pelo menos um arquivo foi fornecido
    arquivos = {
        'rf': args.renda_fixa,
        'coe': args.coe,
        'rv': args.renda_variavel,
        'der': args.derivativos
    }
    
    arquivos_fornecidos = {k: v for k, v in arquivos.items() if v}
    
    if not arquivos_fornecidos:
        print("❌ Erro: Nenhum arquivo fornecido")
        print("   Use -rf, -coe, -rv ou -der para especificar arquivos")
        parser.print_help()
        sys.exit(1)
    
    # Criar CLI
    cli = CarteiraCLI()
    
    print("\n" + "="*80)
    print("CARTEIRA ANALYZER - Análise de Carteiras de Investimentos".center(80))
    print("="*80)
    
    # Processar arquivos
    for categoria, arquivo in arquivos_fornecidos.items():
        if not cli.processar_arquivo(arquivo, categoria):
            sys.exit(1)
    
    # Consolidar e analisar
    if not cli.consolidar_e_analisar(args.cliente):
        sys.exit(1)
    
    # Gerar relatórios
    gerar_html = not args.no_html
    gerar_excel = not args.no_excel
    
    if not cli.gerar_relatorios(args.cliente, gerar_html, gerar_excel):
        sys.exit(1)
    
    # Exibir resumo se solicitado
    if args.resumo:
        cli.exibir_resumo()
    
    print("✅ Processamento concluído com sucesso!")
    print(f"📁 Relatórios salvos em: {cli.diretorio_saida}\n")


if __name__ == '__main__':
    import pandas as pd  # Importar aqui para evitar circular imports
    main()
