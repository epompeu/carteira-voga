#!/usr/bin/env python3
"""
Módulo de análises para relatórios consolidados
Gera gráficos, filtros e análises dos dados
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnalisadorRelatorios:
    """Analisador de relatórios consolidados"""
    
    def __init__(self, dados_consolidados: pd.DataFrame):
        """
        Inicializa o analisador
        
        Args:
            dados_consolidados: DataFrame com todos os relatórios consolidados
        """
        self.dados = dados_consolidados.copy() if dados_consolidados is not None else None
    
    def obter_assessores(self) -> List[str]:
        """Obtém lista de assessores únicos"""
        if self.dados is None or self.dados.empty:
            return []
        
        assessores = self.dados['assessor'].unique().tolist()
        return sorted([a for a in assessores if pd.notna(a)])
    
    def obter_clientes(self, assessor: Optional[str] = None) -> List[str]:
        """
        Obtém lista de clientes
        
        Args:
            assessor: Filtrar por assessor (opcional)
            
        Returns:
            Lista de clientes
        """
        if self.dados is None or self.dados.empty:
            return []
        
        df = self.dados
        
        if assessor and assessor != 'Todos os Assessores':
            df = df[df['assessor'] == assessor]
        
        clientes = df['cliente_nome'].unique().tolist()
        return sorted([c for c in clientes if pd.notna(c)])
    
    def obter_classes_ativas(self) -> List[str]:
        """Obtém lista de classes de ativos"""
        if self.dados is None or self.dados.empty:
            return []
        
        classes = self.dados['classe_ativo'].unique().tolist()
        return sorted([c for c in classes if pd.notna(c)])
    
    def filtrar_dados(self, assessor: Optional[str] = None, 
                     cliente: Optional[str] = None,
                     classe: Optional[str] = None) -> pd.DataFrame:
        """
        Filtra dados conforme critérios
        
        Args:
            assessor: Filtrar por assessor
            cliente: Filtrar por cliente
            classe: Filtrar por classe de ativo
            
        Returns:
            DataFrame filtrado
        """
        if self.dados is None or self.dados.empty:
            return pd.DataFrame()
        
        df = self.dados.copy()
        
        if assessor and assessor != 'Todos os Assessores':
            df = df[df['assessor'] == assessor]
        
        if cliente and cliente != 'Todos os Clientes':
            df = df[df['cliente_nome'] == cliente]
        
        if classe and classe != 'Todas as Classes':
            df = df[df['classe_ativo'] == classe]
        
        return df
    
    def obter_alocacao_por_classe(self, assessor: Optional[str] = None,
                                  cliente: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém alocação de ativos por classe
        
        Args:
            assessor: Filtrar por assessor
            cliente: Filtrar por cliente
            
        Returns:
            DataFrame com alocação
        """
        df = self.filtrar_dados(assessor=assessor, cliente=cliente)
        
        if df.empty:
            return pd.DataFrame()
        
        alocacao = df.groupby('classe_ativo').agg({
            'valor_bruto': ['sum', 'count'],
            'cliente_nome': 'nunique'
        }).round(2)
        
        alocacao.columns = ['Valor Total', 'Quantidade', 'Clientes']
        alocacao = alocacao.reset_index()
        alocacao.columns = ['Classe de Ativo', 'Valor Total', 'Quantidade', 'Clientes']
        
        # Calcular percentual
        total = alocacao['Valor Total'].sum()
        alocacao['Percentual'] = (alocacao['Valor Total'] / total * 100).round(2)
        
        # Ordenar por valor
        alocacao = alocacao.sort_values('Valor Total', ascending=False)
        
        return alocacao
    
    def obter_alocacao_por_tipo_relatorio(self, assessor: Optional[str] = None,
                                          cliente: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém alocação por tipo de relatório (Fundos, Previdência, RF, etc)
        
        Args:
            assessor: Filtrar por assessor
            cliente: Filtrar por cliente
            
        Returns:
            DataFrame com alocação
        """
        df = self.filtrar_dados(assessor=assessor, cliente=cliente)
        
        if df.empty:
            return pd.DataFrame()
        
        alocacao = df.groupby('tipo_relatorio').agg({
            'valor_bruto': ['sum', 'count'],
            'cliente_nome': 'nunique'
        }).round(2)
        
        alocacao.columns = ['Valor Total', 'Quantidade', 'Clientes']
        alocacao = alocacao.reset_index()
        alocacao.columns = ['Tipo de Relatório', 'Valor Total', 'Quantidade', 'Clientes']
        
        # Calcular percentual
        total = alocacao['Valor Total'].sum()
        alocacao['Percentual'] = (alocacao['Valor Total'] / total * 100).round(2)
        
        # Ordenar por valor
        alocacao = alocacao.sort_values('Valor Total', ascending=False)
        
        return alocacao
    
    def obter_alertas_vencimento(self, assessor: Optional[str] = None,
                                 dias_limite: int = 30) -> pd.DataFrame:
        """
        Obtém alertas de vencimento
        
        Args:
            assessor: Filtrar por assessor
            dias_limite: Dias para considerar como alerta
            
        Returns:
            DataFrame com alertas
        """
        df = self.filtrar_dados(assessor=assessor)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filtrar apenas vencimentos próximos
        df = df[df['dias_para_vencer'] <= dias_limite]
        df = df[df['dias_para_vencer'] >= 0]  # Excluir vencidos
        
        # Ordenar por dias para vencer
        df = df.sort_values('dias_para_vencer')
        
        # Selecionar colunas relevantes
        colunas = ['cliente_nome', 'assessor', 'tipo_ativo', 'codigo_ativo',
                   'data_vencimento', 'dias_para_vencer', 'valor_bruto', 'status_vencimento']
        
        colunas_disponiveis = [c for c in colunas if c in df.columns]
        
        return df[colunas_disponiveis]
    
    def obter_resumo_executivo(self, assessor: Optional[str] = None,
                               cliente: Optional[str] = None) -> Dict:
        """
        Gera resumo executivo
        
        Args:
            assessor: Filtrar por assessor
            cliente: Filtrar por cliente
            
        Returns:
            Dicionário com resumo
        """
        df = self.filtrar_dados(assessor=assessor, cliente=cliente)
        
        if df.empty:
            return {
                'total_clientes': 0,
                'valor_total': 0,
                'valor_medio': 0,
                'total_ativos': 0,
                'classes_ativas': 0,
                'vencimentos_criticos': 0
            }
        
        return {
            'total_clientes': df['cliente_nome'].nunique(),
            'valor_total': df['valor_bruto'].sum(),
            'valor_medio': df['valor_bruto'].mean(),
            'total_ativos': len(df),
            'classes_ativas': df['classe_ativo'].nunique(),
            'vencimentos_criticos': len(df[df['status_vencimento'] == 'Crítico (≤ 30 dias)'])
        }
    
    def obter_top_ativos(self, n: int = 10, assessor: Optional[str] = None,
                        cliente: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém top N ativos por valor
        
        Args:
            n: Número de ativos
            assessor: Filtrar por assessor
            cliente: Filtrar por cliente
            
        Returns:
            DataFrame com top ativos
        """
        df = self.filtrar_dados(assessor=assessor, cliente=cliente)
        
        if df.empty:
            return pd.DataFrame()
        
        top = df.nlargest(n, 'valor_bruto')[
            ['cliente_nome', 'tipo_ativo', 'classe_ativo', 'valor_bruto', 'data_vencimento']
        ].copy()
        
        top.columns = ['Cliente', 'Tipo de Ativo', 'Classe', 'Valor', 'Vencimento']
        
        return top
    
    def obter_distribuicao_por_cliente(self, assessor: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém distribuição de valores por cliente
        
        Args:
            assessor: Filtrar por assessor
            
        Returns:
            DataFrame com distribuição
        """
        df = self.filtrar_dados(assessor=assessor)
        
        if df.empty:
            return pd.DataFrame()
        
        distribuicao = df.groupby('cliente_nome').agg({
            'valor_bruto': 'sum',
            'tipo_relatorio': 'nunique'
        }).round(2)
        
        distribuicao.columns = ['Valor Total', 'Tipos de Investimento']
        distribuicao = distribuicao.reset_index()
        distribuicao.columns = ['Cliente', 'Valor Total', 'Tipos de Investimento']
        
        # Ordenar por valor
        distribuicao = distribuicao.sort_values('Valor Total', ascending=False)
        
        return distribuicao
    
    def obter_estatisticas_gerais(self) -> Dict:
        """Obtém estatísticas gerais de todos os dados"""
        if self.dados is None or self.dados.empty:
            return {}
        
        return {
            'total_registros': len(self.dados),
            'total_clientes': self.dados['cliente_nome'].nunique(),
            'total_assessores': self.dados['assessor'].nunique(),
            'valor_total': self.dados['valor_bruto'].sum(),
            'valor_medio_por_cliente': self.dados.groupby('cliente_nome')['valor_bruto'].sum().mean(),
            'classes_ativas': self.dados['classe_ativo'].nunique(),
            'tipos_relatorio': self.dados['tipo_relatorio'].nunique(),
            'vencimentos_criticos': len(self.dados[self.dados['status_vencimento'] == 'Crítico (≤ 30 dias)']),
            'vencimentos_alerta': len(self.dados[self.dados['status_vencimento'] == 'Alerta (31-60 dias)'])
        }
