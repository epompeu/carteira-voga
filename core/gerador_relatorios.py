"""
Módulo para geração de relatórios avançados com gráficos e visualizações.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import seaborn as sns
from typing import Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Configurar matplotlib para português
rcParams['font.sans-serif'] = ['DejaVu Sans']
rcParams['axes.unicode_minus'] = False


class GeradorGraficos:
    """Gerador de gráficos para análise de carteira."""
    
    CORES_CATEGORIAS = {
        'Renda Fixa': '#1f77b4',
        'COE': '#ff7f0e',
        'Renda Variável': '#2ca02c',
        'Derivativos': '#d62728'
    }
    
    @staticmethod
    def criar_grafico_pizza_alocacao(alocacao: pd.DataFrame, titulo: str = "Alocação por Categoria") -> Tuple[bool, str]:
        """
        Cria gráfico de pizza com alocação.
        
        Args:
            alocacao: DataFrame com alocação
            titulo: Título do gráfico
            
        Returns:
            Tupla (sucesso, caminho do arquivo)
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            cores = [GeradorGraficos.CORES_CATEGORIAS.get(cat, '#999999') for cat in alocacao['Categoria']]
            
            wedges, texts, autotexts = ax.pie(
                alocacao['Valor Total'],
                labels=alocacao['Categoria'],
                autopct='%1.1f%%',
                colors=cores,
                startangle=90
            )
            
            # Melhorar aparência
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            for text in texts:
                text.set_fontsize(11)
            
            ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            caminho = '/tmp/grafico_pizza_alocacao.png'
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de pizza criado: {caminho}")
            return True, caminho
        
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de pizza: {str(e)}")
            return False, ""
    
    @staticmethod
    def criar_grafico_barras_alocacao(alocacao: pd.DataFrame, titulo: str = "Alocação por Categoria") -> Tuple[bool, str]:
        """
        Cria gráfico de barras com alocação.
        
        Args:
            alocacao: DataFrame com alocação
            titulo: Título do gráfico
            
        Returns:
            Tupla (sucesso, caminho do arquivo)
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            cores = [GeradorGraficos.CORES_CATEGORIAS.get(cat, '#999999') for cat in alocacao['Categoria']]
            
            barras = ax.bar(alocacao['Categoria'], alocacao['Valor Total'], color=cores, edgecolor='black', linewidth=1.5)
            
            # Adicionar valores nas barras
            for barra in barras:
                altura = barra.get_height()
                ax.text(barra.get_x() + barra.get_width()/2., altura,
                       f'R$ {altura:,.0f}',
                       ha='center', va='bottom', fontweight='bold')
            
            ax.set_ylabel('Valor (R$)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Categoria', fontsize=12, fontweight='bold')
            ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
            
            # Formatar eixo Y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1e6:.1f}M' if x >= 1e6 else f'R$ {x/1e3:.0f}K'))
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            caminho = '/tmp/grafico_barras_alocacao.png'
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de barras criado: {caminho}")
            return True, caminho
        
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de barras: {str(e)}")
            return False, ""
    
    @staticmethod
    def criar_grafico_vencimentos(analise_vencimentos: Dict, titulo: str = "Análise de Vencimentos") -> Tuple[bool, str]:
        """
        Cria gráfico com análise de vencimentos.
        
        Args:
            analise_vencimentos: Dicionário com análise de vencimentos
            titulo: Título do gráfico
            
        Returns:
            Tupla (sucesso, caminho do arquivo)
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Gráfico 1: Valor por período
            periodos = ['Próx. 30d', 'Próx. 60d', 'Próx. 90d', 'Vencido', 'Sem Vencimento']
            valores = [
                analise_vencimentos['valor_proximo_30_dias'],
                analise_vencimentos['valor_proximo_60_dias'],
                analise_vencimentos['valor_proximo_90_dias'],
                analise_vencimentos['valor_vencido'],
                analise_vencimentos['valor_sem_vencimento']
            ]
            
            cores_venc = ['#d62728', '#ff7f0e', '#2ca02c', '#8b0000', '#1f77b4']
            barras1 = ax1.bar(periodos, valores, color=cores_venc, edgecolor='black', linewidth=1.5)
            
            for barra in barras1:
                altura = barra.get_height()
                ax1.text(barra.get_x() + barra.get_width()/2., altura,
                        f'R$ {altura:,.0f}',
                        ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            ax1.set_ylabel('Valor (R$)', fontsize=11, fontweight='bold')
            ax1.set_title('Valor por Período de Vencimento', fontsize=12, fontweight='bold')
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1e6:.1f}M' if x >= 1e6 else f'R$ {x/1e3:.0f}K'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Gráfico 2: Percentual por período
            percentuais = [
                analise_vencimentos['percentual_proximo_30_dias'],
                analise_vencimentos['percentual_proximo_60_dias'],
                analise_vencimentos['percentual_proximo_90_dias'],
                analise_vencimentos['percentual_vencido'],
                analise_vencimentos['percentual_sem_vencimento']
            ]
            
            wedges, texts, autotexts = ax2.pie(
                percentuais,
                labels=periodos,
                autopct='%1.1f%%',
                colors=cores_venc,
                startangle=90
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            ax2.set_title('Percentual por Período', fontsize=12, fontweight='bold')
            
            fig.suptitle(titulo, fontsize=14, fontweight='bold', y=1.00)
            plt.tight_layout()
            
            caminho = '/tmp/grafico_vencimentos.png'
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de vencimentos criado: {caminho}")
            return True, caminho
        
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de vencimentos: {str(e)}")
            return False, ""
    
    @staticmethod
    def criar_grafico_risco(analise_risco: Dict, titulo: str = "Análise de Risco") -> Tuple[bool, str]:
        """
        Cria gráfico com análise de risco.
        
        Args:
            analise_risco: Dicionário com análise de risco
            titulo: Título do gráfico
            
        Returns:
            Tupla (sucesso, caminho do arquivo)
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Gráfico 1: Valor por nível de risco
            niveis = ['Crítico', 'Moderado', 'Baixo']
            valores = [
                analise_risco['risco_critico_valor'],
                analise_risco['risco_moderado_valor'],
                analise_risco['risco_baixo_valor']
            ]
            
            cores_risco = ['#d62728', '#ff7f0e', '#2ca02c']
            barras1 = ax1.bar(niveis, valores, color=cores_risco, edgecolor='black', linewidth=1.5)
            
            for barra in barras1:
                altura = barra.get_height()
                ax1.text(barra.get_x() + barra.get_width()/2., altura,
                        f'R$ {altura:,.0f}',
                        ha='center', va='bottom', fontweight='bold')
            
            ax1.set_ylabel('Valor (R$)', fontsize=11, fontweight='bold')
            ax1.set_title('Valor por Nível de Risco', fontsize=12, fontweight='bold')
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1e6:.1f}M' if x >= 1e6 else f'R$ {x/1e3:.0f}K'))
            
            # Gráfico 2: Percentual por nível de risco
            percentuais = [
                analise_risco['risco_critico_percentual'],
                analise_risco['risco_moderado_percentual'],
                analise_risco['risco_baixo_percentual']
            ]
            
            wedges, texts, autotexts = ax2.pie(
                percentuais,
                labels=niveis,
                autopct='%1.1f%%',
                colors=cores_risco,
                startangle=90
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            ax2.set_title('Percentual por Nível de Risco', fontsize=12, fontweight='bold')
            
            fig.suptitle(titulo, fontsize=14, fontweight='bold', y=1.00)
            plt.tight_layout()
            
            caminho = '/tmp/grafico_risco.png'
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de risco criado: {caminho}")
            return True, caminho
        
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de risco: {str(e)}")
            return False, ""
    
    @staticmethod
    def criar_grafico_top_ativos(top_ativos: pd.DataFrame, titulo: str = "Top 10 Ativos") -> Tuple[bool, str]:
        """
        Cria gráfico com top ativos.
        
        Args:
            top_ativos: DataFrame com top ativos
            titulo: Título do gráfico
            
        Returns:
            Tupla (sucesso, caminho do arquivo)
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Ordenar em ordem crescente para melhor visualização
            top_ativos_sorted = top_ativos.sort_values('Valor', ascending=True)
            
            # Cores por categoria
            cores = [GeradorGraficos.CORES_CATEGORIAS.get(cat, '#999999') for cat in top_ativos_sorted['Categoria']]
            
            barras = ax.barh(top_ativos_sorted['Ativo'], top_ativos_sorted['Valor'], color=cores, edgecolor='black', linewidth=1.5)
            
            # Adicionar valores nas barras
            for i, barra in enumerate(barras):
                largura = barra.get_width()
                ax.text(largura, barra.get_y() + barra.get_height()/2.,
                       f' R$ {largura:,.0f}',
                       ha='left', va='center', fontweight='bold', fontsize=9)
            
            ax.set_xlabel('Valor (R$)', fontsize=12, fontweight='bold')
            ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1e6:.1f}M' if x >= 1e6 else f'R$ {x/1e3:.0f}K'))
            
            # Adicionar legenda
            categorias_unicas = top_ativos_sorted['Categoria'].unique()
            patches = [mpatches.Patch(color=GeradorGraficos.CORES_CATEGORIAS.get(cat, '#999999'), label=cat) 
                      for cat in categorias_unicas]
            ax.legend(handles=patches, loc='lower right')
            
            plt.tight_layout()
            
            caminho = '/tmp/grafico_top_ativos.png'
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de top ativos criado: {caminho}")
            return True, caminho
        
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de top ativos: {str(e)}")
            return False, ""


class GeradorRelatorioHTML:
    """Gerador de relatórios em formato HTML."""
    
    @staticmethod
    def gerar_relatorio_html(
        nome_cliente: str,
        data_relatorio: str,
        estatisticas: Dict,
        alocacao: pd.DataFrame,
        diversificacao: Dict,
        vencimentos: Dict,
        risco: Dict,
        top_ativos: pd.DataFrame,
        caminhos_graficos: Dict[str, str]
    ) -> Tuple[bool, str]:
        """
        Gera relatório completo em HTML.
        
        Args:
            nome_cliente: Nome do cliente
            data_relatorio: Data do relatório
            estatisticas: Dicionário com estatísticas
            alocacao: DataFrame com alocação
            diversificacao: Dicionário com análise de diversificação
            vencimentos: Dicionário com análise de vencimentos
            risco: Dicionário com análise de risco
            top_ativos: DataFrame com top ativos
            caminhos_graficos: Dicionário com caminhos dos gráficos
            
        Returns:
            Tupla (sucesso, conteúdo HTML)
        """
        try:
            html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Carteira - {nome_cliente}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #1f77b4;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        
        .cliente-info {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        
        .cliente-info div {{
            flex: 1;
        }}
        
        .cliente-info label {{
            font-weight: bold;
            color: #1f77b4;
            display: block;
            margin-bottom: 5px;
        }}
        
        .section {{
            margin-bottom: 40px;
            page-break-inside: avoid;
        }}
        
        .section h2 {{
            color: #1f77b4;
            font-size: 20px;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .section h3 {{
            color: #333;
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card.alt1 {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .stat-card.alt2 {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .stat-card.alt3 {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }}
        
        .stat-card label {{
            display: block;
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        table thead {{
            background-color: #1f77b4;
            color: white;
        }}
        
        table th {{
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        table tbody tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .grafico {{
            text-align: center;
            margin: 30px 0;
            page-break-inside: avoid;
        }}
        
        .grafico img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        
        .alerta {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        
        .alerta.critico {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .alerta.sucesso {{
            background-color: #d4edda;
            border-left-color: #28a745;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #999;
            font-size: 12px;
        }}
        
        @media print {{
            body {{
                background-color: white;
            }}
            .container {{
                box-shadow: none;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Relatório de Análise de Carteira</h1>
            <p>Análise Completa de Investimentos</p>
        </div>
        
        <div class="cliente-info">
            <div>
                <label>Cliente:</label>
                <span>{nome_cliente}</span>
            </div>
            <div>
                <label>Data do Relatório:</label>
                <span>{data_relatorio}</span>
            </div>
        </div>
        
        <!-- RESUMO EXECUTIVO -->
        <div class="section">
            <h2>📈 Resumo Executivo</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <label>Valor Total da Carteira</label>
                    <div class="value">R$ {estatisticas.get('valor_total', 0):,.0f}</div>
                </div>
                <div class="stat-card alt1">
                    <label>Total de Ativos</label>
                    <div class="value">{estatisticas.get('total_ativos', 0)}</div>
                </div>
                <div class="stat-card alt2">
                    <label>Valor Médio por Ativo</label>
                    <div class="value">R$ {estatisticas.get('valor_medio', 0):,.0f}</div>
                </div>
                <div class="stat-card alt3">
                    <label>Categorias</label>
                    <div class="value">{estatisticas.get('categorias', 0)}</div>
                </div>
            </div>
        </div>
        
        <!-- ALOCAÇÃO -->
        <div class="section">
            <h2>💼 Alocação por Categoria</h2>
            <div class="grafico">
                <img src="{caminhos_graficos.get('pizza_alocacao', '')}" alt="Alocação por Categoria">
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Categoria</th>
                        <th>Valor Total</th>
                        <th>Percentual</th>
                        <th>Quantidade</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            # Adicionar linhas da tabela de alocação
            if alocacao is not None:
                for _, row in alocacao.iterrows():
                    html += f"""
                    <tr>
                        <td>{row['Categoria']}</td>
                        <td>R$ {row['Valor Total']:,.2f}</td>
                        <td>{row['Percentual']:.2f}%</td>
                        <td>{row['Quantidade']}</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
        </div>
        
        <!-- DIVERSIFICAÇÃO -->
        <div class="section">
            <h2>🎯 Análise de Diversificação</h2>
"""
            
            if diversificacao:
                score = diversificacao.get('diversificacao_score', 0)
                classe = diversificacao.get('classificacao_concentracao', 'N/A')
                
                if score >= 70:
                    alerta_class = "alerta sucesso"
                    msg = "✓ Carteira bem diversificada"
                elif score >= 50:
                    alerta_class = "alerta"
                    msg = "⚠ Diversificação moderada"
                else:
                    alerta_class = "alerta critico"
                    msg = "✗ Carteira pouco diversificada"
                
                html += f"""
            <div class="{alerta_class}">
                <strong>{msg}</strong> - Score: {score}/100
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <label>Score de Diversificação</label>
                    <div class="value">{score:.0f}/100</div>
                </div>
                <div class="stat-card alt1">
                    <label>Número de Ativos</label>
                    <div class="value">{diversificacao.get('numero_ativos', 0)}</div>
                </div>
                <div class="stat-card alt2">
                    <label>Maior Posição</label>
                    <div class="value">{diversificacao.get('maior_posicao_percentual', 0):.1f}%</div>
                </div>
                <div class="stat-card alt3">
                    <label>Top 5</label>
                    <div class="value">{diversificacao.get('top_5_percentual', 0):.1f}%</div>
                </div>
            </div>
            
            <h3>Classificação: {classe}</h3>
            <p>Índice de Herfindahl: {diversificacao.get('hhi', 0):.2f}</p>
"""
            
            html += """
        </div>
        
        <!-- VENCIMENTOS -->
        <div class="section">
            <h2>📅 Análise de Vencimentos</h2>
            <div class="grafico">
                <img src="{}" alt="Análise de Vencimentos">
            </div>
""".format(caminhos_graficos.get('vencimentos', ''))
            
            if vencimentos:
                html += f"""
            <div class="stats-grid">
                <div class="stat-card">
                    <label>Próximos 30 dias</label>
                    <div class="value">{vencimentos.get('percentual_proximo_30_dias', 0):.1f}%</div>
                </div>
                <div class="stat-card alt1">
                    <label>Próximos 60 dias</label>
                    <div class="value">{vencimentos.get('percentual_proximo_60_dias', 0):.1f}%</div>
                </div>
                <div class="stat-card alt2">
                    <label>Próximos 90 dias</label>
                    <div class="value">{vencimentos.get('percentual_proximo_90_dias', 0):.1f}%</div>
                </div>
                <div class="stat-card alt3">
                    <label>Vencido</label>
                    <div class="value">{vencimentos.get('percentual_vencido', 0):.1f}%</div>
                </div>
            </div>
"""
            
            html += """
        </div>
        
        <!-- RISCO -->
        <div class="section">
            <h2>⚠️ Análise de Risco</h2>
            <div class="grafico">
                <img src="{}" alt="Análise de Risco">
            </div>
""".format(caminhos_graficos.get('risco', ''))
            
            if risco:
                nivel = risco.get('nivel_risco_geral', 'Desconhecido')
                if nivel == 'Crítico':
                    alerta_class = "alerta critico"
                elif nivel == 'Alto':
                    alerta_class = "alerta"
                else:
                    alerta_class = "alerta sucesso"
                
                html += f"""
            <div class="{alerta_class}">
                <strong>Nível de Risco Geral: {nivel}</strong>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <label>Risco Crítico</label>
                    <div class="value">{risco.get('risco_critico_percentual', 0):.1f}%</div>
                </div>
                <div class="stat-card alt1">
                    <label>Risco Moderado</label>
                    <div class="value">{risco.get('risco_moderado_percentual', 0):.1f}%</div>
                </div>
                <div class="stat-card alt2">
                    <label>Risco Baixo</label>
                    <div class="value">{risco.get('risco_baixo_percentual', 0):.1f}%</div>
                </div>
            </div>
"""
            
            html += """
        </div>
        
        <!-- TOP ATIVOS -->
        <div class="section">
            <h2>⭐ Top 10 Ativos</h2>
            <div class="grafico">
                <img src="{}" alt="Top 10 Ativos">
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Ativo</th>
                        <th>Categoria</th>
                        <th>Valor</th>
                        <th>Percentual</th>
                    </tr>
                </thead>
                <tbody>
""".format(caminhos_graficos.get('top_ativos', ''))
            
            if top_ativos is not None:
                for _, row in top_ativos.iterrows():
                    html += f"""
                    <tr>
                        <td>{row['Ativo']}</td>
                        <td>{row['Categoria']}</td>
                        <td>R$ {row['Valor']:,.2f}</td>
                        <td>{row['Percentual']:.2f}%</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Relatório gerado automaticamente pelo Carteira Analyzer</p>
            <p>Este documento contém informações confidenciais e é destinado apenas ao cliente.</p>
        </div>
    </div>
</body>
</html>
"""
            
            return True, html
        
        except Exception as e:
            logger.error(f"Erro ao gerar relatório HTML: {str(e)}")
            return False, ""
