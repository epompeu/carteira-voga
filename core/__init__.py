"""
Módulo core do Carteira Analyzer.
Contém as classes principais para processamento e análise de carteiras.
"""

from .processador_carteira import (
    ProcessadorCarteira,
    CategoriaInvestimento,
    ConfiguracaoCategoria,
    ValidadorDados
)
from .analisador_avancado import AnalisadorAvancado
from .utilitarios import GerenciadorArquivos, FormatadorDados, GeradorRelatorios

__all__ = [
    'ProcessadorCarteira',
    'CategoriaInvestimento',
    'ConfiguracaoCategoria',
    'ValidadorDados',
    'AnalisadorAvancado',
    'GerenciadorArquivos',
    'FormatadorDados',
    'GeradorRelatorios'
]
