"""
Módulo de utilitários e funções auxiliares.
"""

import os
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GerenciadorArquivos:
    """Gerenciador de arquivos para upload e processamento."""
    
    EXTENSOES_PERMITIDAS = {'.xlsx', '.xls', '.csv'}
    TAMANHO_MAXIMO_MB = 50
    
    @staticmethod
    def validar_arquivo(caminho_arquivo: str) -> tuple[bool, str]:
        """
        Valida se o arquivo é permitido.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tupla (válido, mensagem)
        """
        if not os.path.exists(caminho_arquivo):
            return False, "Arquivo não encontrado"
        
        # Verificar extensão
        _, ext = os.path.splitext(caminho_arquivo)
        if ext.lower() not in GerenciadorArquivos.EXTENSOES_PERMITIDAS:
            return False, f"Extensão não permitida. Use: {', '.join(GerenciadorArquivos.EXTENSOES_PERMITIDAS)}"
        
        # Verificar tamanho
        tamanho_mb = os.path.getsize(caminho_arquivo) / (1024 * 1024)
        if tamanho_mb > GerenciadorArquivos.TAMANHO_MAXIMO_MB:
            return False, f"Arquivo muito grande. Máximo: {GerenciadorArquivos.TAMANHO_MAXIMO_MB}MB"
        
        return True, "Arquivo válido"
    
    @staticmethod
    def criar_diretorio_saida(nome_cliente: str) -> Optional[str]:
        """
        Cria diretório de saída para um cliente.
        
        Args:
            nome_cliente: Nome do cliente
            
        Returns:
            Caminho do diretório ou None
        """
        try:
            # Sanitizar nome do cliente
            nome_sanitizado = "".join(c for c in nome_cliente if c.isalnum() or c in (' ', '_', '-')).rstrip()
            
            # Criar diretório
            data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            diretorio = f"./relatorios/{nome_sanitizado}_{data_str}"
            
            os.makedirs(diretorio, exist_ok=True)
            logger.info(f"Diretório criado: {diretorio}")
            
            return diretorio
        except Exception as e:
            logger.error(f"Erro ao criar diretório: {str(e)}")
            return None


class FormatadorDados:
    """Formatador de dados para exibição."""
    
    @staticmethod
    def formatar_moeda(valor: float, simbolo: str = "R$") -> str:
        """
        Formata valor como moeda.
        
        Args:
            valor: Valor a formatar
            simbolo: Símbolo de moeda
            
        Returns:
            Valor formatado
        """
        return f"{simbolo} {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def formatar_percentual(valor: float, casas_decimais: int = 2) -> str:
        """
        Formata valor como percentual.
        
        Args:
            valor: Valor a formatar (0-100)
            casas_decimais: Número de casas decimais
            
        Returns:
            Valor formatado
        """
        return f"{valor:.{casas_decimais}f}%"
    
    @staticmethod
    def formatar_data(data, formato: str = "%d/%m/%Y") -> str:
        """
        Formata data.
        
        Args:
            data: Data a formatar
            formato: Formato desejado
            
        Returns:
            Data formatada
        """
        if data is None or pd.isna(data):
            return "N/A"
        return data.strftime(formato)
    
    @staticmethod
    def formatar_numero(valor: float, casas_decimais: int = 2) -> str:
        """
        Formata número com separadores.
        
        Args:
            valor: Valor a formatar
            casas_decimais: Número de casas decimais
            
        Returns:
            Número formatado
        """
        return f"{valor:,.{casas_decimais}f}".replace(',', 'X').replace('.', ',').replace('X', '.')


class GeradorRelatorios:
    """Gerador de relatórios em diferentes formatos."""
    
    @staticmethod
    def gerar_resumo_texto(dados: dict) -> str:
        """
        Gera resumo em formato texto.
        
        Args:
            dados: Dados do relatório
            
        Returns:
            Texto formatado
        """
        texto = "=" * 80 + "\n"
        texto += "RELATÓRIO DE ANÁLISE DE CARTEIRA\n"
        texto += "=" * 80 + "\n\n"
        
        if 'data_processamento' in dados:
            texto += f"Data de Processamento: {dados['data_processamento']}\n\n"
        
        texto += "RESUMO EXECUTIVO\n"
        texto += "-" * 80 + "\n"
        
        if 'estatisticas' in dados:
            stats = dados['estatisticas']
            texto += f"Total de Ativos: {stats.get('total_ativos', 0)}\n"
            texto += f"Valor Total: {FormatadorDados.formatar_moeda(stats.get('valor_total', 0))}\n"
            texto += f"Valor Médio: {FormatadorDados.formatar_moeda(stats.get('valor_medio', 0))}\n"
            texto += f"Categorias: {stats.get('categorias', 0)}\n\n"
        
        if 'diversificacao' in dados:
            div = dados['diversificacao']
            texto += "DIVERSIFICAÇÃO\n"
            texto += "-" * 80 + "\n"
            texto += f"Score de Diversificação: {div.get('diversificacao_score', 0)}/100\n"
            texto += f"Classificação: {div.get('classificacao_concentracao', 'N/A')}\n"
            texto += f"Número de Ativos: {div.get('numero_ativos', 0)}\n"
            texto += f"Maior Posição: {FormatadorDados.formatar_percentual(div.get('maior_posicao_percentual', 0))}\n"
            texto += f"Top 5: {FormatadorDados.formatar_percentual(div.get('top_5_percentual', 0))}\n\n"
        
        if 'risco' in dados:
            risco = dados['risco']
            texto += "ANÁLISE DE RISCO\n"
            texto += "-" * 80 + "\n"
            texto += f"Nível de Risco Geral: {risco.get('nivel_risco_geral', 'N/A')}\n"
            texto += f"Risco Crítico: {FormatadorDados.formatar_percentual(risco.get('risco_critico_percentual', 0))}\n"
            texto += f"Risco Moderado: {FormatadorDados.formatar_percentual(risco.get('risco_moderado_percentual', 0))}\n"
            texto += f"Risco Baixo: {FormatadorDados.formatar_percentual(risco.get('risco_baixo_percentual', 0))}\n\n"
        
        texto += "=" * 80 + "\n"
        
        return texto


# Importar pandas para uso em FormatadorDados
import pandas as pd
