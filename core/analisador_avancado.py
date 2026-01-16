"""
Módulo de análises avançadas para carteiras de investimentos.
Inclui análises de diversificação, concentração, rentabilidade e risco.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class AnalisadorAvancado:
    """Classe para análises avançadas de carteiras."""
    
    def __init__(self, carteira_consolidada: pd.DataFrame):
        """
        Inicializa o analisador.
        
        Args:
            carteira_consolidada: DataFrame consolidado da carteira
        """
        self.carteira = carteira_consolidada.copy() if carteira_consolidada is not None else None
    
    def calcular_indice_herfindahl(self) -> Optional[float]:
        """
        Calcula o Índice de Herfindahl-Hirschman (HHI) para medir concentração.
        HHI = Σ(peso%)²
        Valores: 0-1500 (baixa), 1500-2500 (moderada), >2500 (alta)
        
        Returns:
            Valor do HHI ou None
        """
        if self.carteira is None or self.carteira.empty:
            return None
        
        total = self.carteira['Valor'].sum()
        if total == 0:
            return None
        
        pesos = (self.carteira['Valor'] / total) * 100
        hhi = (pesos ** 2).sum()
        
        return round(hhi, 2)
    
    def classificar_concentracao(self, hhi: float) -> str:
        """
        Classifica o nível de concentração baseado no HHI.
        
        Args:
            hhi: Índice de Herfindahl
            
        Returns:
            Classificação de concentração
        """
        if hhi < 1500:
            return "Baixa concentração (Bem diversificada)"
        elif hhi < 2500:
            return "Concentração moderada"
        else:
            return "Alta concentração (Pouco diversificada)"
    
    def analisar_diversificacao(self) -> Optional[Dict]:
        """
        Análise completa de diversificação da carteira.
        
        Returns:
            Dicionário com métricas de diversificação
        """
        if self.carteira is None or self.carteira.empty:
            return None
        
        total = self.carteira['Valor'].sum()
        if total == 0:
            return None
        
        # Análise por categoria
        por_categoria = self.carteira.groupby('Categoria')['Valor'].sum()
        num_categorias = len(por_categoria)
        
        # Análise por classe
        por_classe = self.carteira.groupby('Classe')['Valor'].sum()
        num_classes = len(por_classe)
        
        # Análise por ativo
        por_ativo = self.carteira.groupby('Ativo')['Valor'].sum()
        num_ativos = len(por_ativo)
        
        # Calcular HHI
        hhi = self.calcular_indice_herfindahl()
        
        # Maior posição
        maior_posicao = por_ativo.max() / total * 100
        
        # Concentração top 5
        top_5_valor = por_ativo.nlargest(5).sum()
        top_5_percentual = (top_5_valor / total) * 100
        
        return {
            'numero_categorias': num_categorias,
            'numero_classes': num_classes,
            'numero_ativos': num_ativos,
            'hhi': hhi,
            'classificacao_concentracao': self.classificar_concentracao(hhi),
            'maior_posicao_percentual': round(maior_posicao, 2),
            'top_5_percentual': round(top_5_percentual, 2),
            'diversificacao_score': self._calcular_score_diversificacao(num_ativos, hhi)
        }
    
    def _calcular_score_diversificacao(self, num_ativos: int, hhi: float) -> float:
        """
        Calcula um score de diversificação de 0 a 100.
        
        Args:
            num_ativos: Número de ativos
            hhi: Índice de Herfindahl
            
        Returns:
            Score de diversificação
        """
        # Score baseado em número de ativos (0-50 pontos)
        score_ativos = min(num_ativos / 2, 50)
        
        # Score baseado em HHI (0-50 pontos)
        score_hhi = max(0, 50 - (hhi / 50))
        
        return round(score_ativos + score_hhi, 2)
    
    def analisar_vencimentos(self) -> Optional[Dict]:
        """
        Análise de vencimentos da carteira.
        
        Returns:
            Dicionário com análise de vencimentos
        """
        if self.carteira is None or self.carteira.empty:
            return None
        
        total = self.carteira['Valor'].sum()
        
        # Contar por status
        status_counts = self.carteira['Status Vencimento'].value_counts()
        
        # Valor por status
        status_valores = self.carteira.groupby('Status Vencimento')['Valor'].sum()
        
        # Análise por período
        hoje = pd.Timestamp.now()
        
        # Próximos 30 dias
        proximo_30 = self.carteira[
            (self.carteira['Dias para Vencer'] > 0) & 
            (self.carteira['Dias para Vencer'] <= 30)
        ]['Valor'].sum()
        
        # Próximos 60 dias
        proximo_60 = self.carteira[
            (self.carteira['Dias para Vencer'] > 0) & 
            (self.carteira['Dias para Vencer'] <= 60)
        ]['Valor'].sum()
        
        # Próximos 90 dias
        proximo_90 = self.carteira[
            (self.carteira['Dias para Vencer'] > 0) & 
            (self.carteira['Dias para Vencer'] <= 90)
        ]['Valor'].sum()
        
        # Vencidos
        vencidos = self.carteira[
            self.carteira['Dias para Vencer'] < 0
        ]['Valor'].sum()
        
        # Sem vencimento
        sem_vencimento = self.carteira[
            self.carteira['Status Vencimento'] == 'Sem Vencimento'
        ]['Valor'].sum()
        
        return {
            'valor_total': total,
            'valor_proximo_30_dias': round(proximo_30, 2),
            'percentual_proximo_30_dias': round((proximo_30 / total * 100) if total > 0 else 0, 2),
            'valor_proximo_60_dias': round(proximo_60, 2),
            'percentual_proximo_60_dias': round((proximo_60 / total * 100) if total > 0 else 0, 2),
            'valor_proximo_90_dias': round(proximo_90, 2),
            'percentual_proximo_90_dias': round((proximo_90 / total * 100) if total > 0 else 0, 2),
            'valor_vencido': round(vencidos, 2),
            'percentual_vencido': round((vencidos / total * 100) if total > 0 else 0, 2),
            'valor_sem_vencimento': round(sem_vencimento, 2),
            'percentual_sem_vencimento': round((sem_vencimento / total * 100) if total > 0 else 0, 2),
            'status_counts': status_counts.to_dict(),
            'status_valores': status_valores.to_dict()
        }
    
    def obter_top_ativos(self, n: int = 10) -> Optional[pd.DataFrame]:
        """
        Retorna os N ativos com maior valor.
        
        Args:
            n: Número de ativos a retornar
            
        Returns:
            DataFrame com top ativos
        """
        if self.carteira is None or self.carteira.empty:
            return None
        
        total = self.carteira['Valor'].sum()
        
        top = self.carteira.groupby('Ativo').agg({
            'Valor': 'sum',
            'Categoria': 'first',
            'Classe': 'first'
        }).reset_index()
        
        top['Percentual'] = (top['Valor'] / total * 100).round(2)
        top = top.sort_values('Valor', ascending=False).head(n)
        
        return top
    
    def obter_top_classes(self, n: int = 10) -> Optional[pd.DataFrame]:
        """
        Retorna as N classes com maior valor.
        
        Args:
            n: Número de classes a retornar
            
        Returns:
            DataFrame com top classes
        """
        if self.carteira is None or self.carteira.empty:
            return None
        
        total = self.carteira['Valor'].sum()
        
        top = self.carteira.groupby('Classe').agg({
            'Valor': 'sum',
            'Categoria': 'first',
            'Ativo': 'count'
        }).reset_index()
        
        top.columns = ['Classe', 'Valor', 'Categoria', 'Quantidade']
        top['Percentual'] = (top['Valor'] / total * 100).round(2)
        top = top.sort_values('Valor', ascending=False).head(n)
        
        return top
    
    def analisar_risco_vencimento(self) -> Optional[Dict]:
        """
        Análise de risco relacionado a vencimentos.
        
        Returns:
            Dicionário com análise de risco
        """
        if self.carteira is None or self.carteira.empty:
            return None
        
        total = self.carteira['Valor'].sum()
        
        # Risco crítico: vencidos + próximos 30 dias
        risco_critico = self.carteira[
            (self.carteira['Dias para Vencer'] < 0) |
            ((self.carteira['Dias para Vencer'] > 0) & (self.carteira['Dias para Vencer'] <= 30))
        ]['Valor'].sum()
        
        # Risco moderado: 31-90 dias
        risco_moderado = self.carteira[
            (self.carteira['Dias para Vencer'] > 30) & 
            (self.carteira['Dias para Vencer'] <= 90)
        ]['Valor'].sum()
        
        # Risco baixo: > 90 dias ou sem vencimento
        risco_baixo = total - risco_critico - risco_moderado
        
        return {
            'valor_total': total,
            'risco_critico_valor': round(risco_critico, 2),
            'risco_critico_percentual': round((risco_critico / total * 100) if total > 0 else 0, 2),
            'risco_moderado_valor': round(risco_moderado, 2),
            'risco_moderado_percentual': round((risco_moderado / total * 100) if total > 0 else 0, 2),
            'risco_baixo_valor': round(risco_baixo, 2),
            'risco_baixo_percentual': round((risco_baixo / total * 100) if total > 0 else 0, 2),
            'nivel_risco_geral': self._classificar_risco_geral(risco_critico / total if total > 0 else 0)
        }
    
    def _classificar_risco_geral(self, percentual_critico: float) -> str:
        """
        Classifica o nível de risco geral.
        
        Args:
            percentual_critico: Percentual de valor em risco crítico
            
        Returns:
            Classificação de risco
        """
        if percentual_critico < 0.05:
            return "Baixo"
        elif percentual_critico < 0.15:
            return "Moderado"
        elif percentual_critico < 0.30:
            return "Alto"
        else:
            return "Crítico"
    
    def gerar_relatorio_completo(self) -> Optional[Dict]:
        """
        Gera um relatório completo com todas as análises.
        
        Returns:
            Dicionário com relatório completo
        """
        if self.carteira is None or self.carteira.empty:
            return None
        
        return {
            'diversificacao': self.analisar_diversificacao(),
            'vencimentos': self.analisar_vencimentos(),
            'risco': self.analisar_risco_vencimento(),
            'top_ativos': self.obter_top_ativos(10),
            'top_classes': self.obter_top_classes(10)
        }
