#!/usr/bin/env python3
"""
Módulo de Parsers para diferentes tipos de relatórios
Cada relatório tem uma estrutura diferente e requer um parser específico
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class ParserRendaFixa:
    """Parser para relatórios de Renda Fixa"""
    
    COLUNAS_ESPERADAS = [
        'Conta', 'Nome', 'Emissor', 'Produto', 'Sub Mercado',
        'Ativo', 'Indexador', 'Quantidade', 'Valor Custo',
        'Data Compra', 'Data Vencimento', 'Valor Bruto - Opção Cliente',
        'IR - Opção Cliente', 'IOF - Opção Cliente', 'Valor Líquido - Opção Cliente'
    ]
    
    @staticmethod
    def validar_estrutura(df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Valida se o DataFrame tem a estrutura esperada de Renda Fixa
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Tupla (válido, mensagem)
        """
        if df is None or df.empty:
            return False, "DataFrame vazio"
        
        # Verificar colunas essenciais
        colunas_essenciais = ['Conta', 'Nome', 'Produto', 'Data Vencimento', 'Valor Bruto - Opção Cliente']
        colunas_faltantes = [col for col in colunas_essenciais if col not in df.columns]
        
        if colunas_faltantes:
            return False, f"Colunas faltantes: {', '.join(colunas_faltantes)}"
        
        return True, "Estrutura válida"
    
    @staticmethod
    def processar(df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa um DataFrame de Renda Fixa
        
        Args:
            df: DataFrame bruto
            
        Returns:
            DataFrame processado
        """
        df = df.copy()
        
        # Renomear colunas para padronização
        df = df.rename(columns={
            'Conta': 'cliente_id',
            'Nome': 'cliente_nome',
            'Produto': 'tipo_ativo',
            'Sub Mercado': 'classe_ativo',
            'Ativo': 'codigo_ativo',
            'Indexador': 'indexador',
            'Quantidade': 'quantidade',
            'Data Vencimento': 'data_vencimento',
            'Valor Bruto - Opção Cliente': 'valor_bruto',
            'Valor Líquido - Opção Cliente': 'valor_liquido'
        })
        
        # Converter datas
        df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
        
        # Converter valores para float
        for col in ['valor_bruto', 'valor_liquido', 'quantidade']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Adicionar informações de vencimento
        hoje = pd.Timestamp.now()
        df['dias_para_vencer'] = (df['data_vencimento'] - hoje).dt.days
        
        # Classificar status de vencimento
        def classificar_vencimento(dias):
            if pd.isna(dias):
                return 'Sem data'
            elif dias < 0:
                return 'Vencido'
            elif dias <= 30:
                return 'Crítico (≤ 30 dias)'
            elif dias <= 60:
                return 'Alerta (31-60 dias)'
            elif dias <= 90:
                return 'Atenção (61-90 dias)'
            else:
                return 'Normal (> 90 dias)'
        
        df['status_vencimento'] = df['dias_para_vencer'].apply(classificar_vencimento)
        
        # Adicionar tipo de relatório
        df['tipo_relatorio'] = 'Renda Fixa'
        
        # Adicionar assessor (será preenchido depois se disponível)
        df['assessor'] = 'Não informado'
        
        # Remover linhas com valores nulos críticos
        df = df.dropna(subset=['cliente_id', 'cliente_nome', 'valor_bruto'])
        
        logger.info(f"Renda Fixa processado: {len(df)} registros")
        
        return df
    
    @staticmethod
    def obter_resumo(df: pd.DataFrame) -> Dict:
        """
        Gera resumo dos dados de Renda Fixa
        
        Args:
            df: DataFrame processado
            
        Returns:
            Dicionário com resumo
        """
        return {
            'total_registros': len(df),
            'total_clientes': df['cliente_nome'].nunique(),
            'valor_total': df['valor_bruto'].sum(),
            'valor_medio': df['valor_bruto'].mean(),
            'classes_ativas': df['classe_ativo'].unique().tolist(),
            'produtos': df['tipo_ativo'].unique().tolist(),
            'vencimentos_criticos': len(df[df['status_vencimento'] == 'Crítico (≤ 30 dias)']),
            'vencimentos_alerta': len(df[df['status_vencimento'] == 'Alerta (31-60 dias)'])
        }


class ParserFundos:
    """Parser para relatórios de Fundos"""
    
    COLUNAS_ESPERADAS = [
        'Conta', 'Nome', 'Produto', 'CNPJ', 'Administrador',
        'Gestor', 'Categoria', 'Subcategoria', 'Resgate (D+)',
        'Quantidade', 'Valor Bruto', 'IR', 'IOF', 'Valor Líquido'
    ]
    
    @staticmethod
    def validar_estrutura(df: pd.DataFrame) -> Tuple[bool, str]:
        """Valida se o DataFrame tem a estrutura esperada de Fundos"""
        if df is None or df.empty:
            return False, "DataFrame vazio"
        
        # Verificar colunas essenciais
        colunas_essenciais = ['Conta', 'Nome', 'Produto', 'Categoria', 'Valor Bruto']
        colunas_faltantes = [col for col in colunas_essenciais if col not in df.columns]
        
        if colunas_faltantes:
            return False, f"Colunas faltantes: {', '.join(colunas_faltantes)}"
        
        return True, "Estrutura válida"
    
    @staticmethod
    def processar(df: pd.DataFrame) -> pd.DataFrame:
        """Processa um DataFrame de Fundos"""
        df = df.copy()
        
        # Renomear colunas para padronização
        df = df.rename(columns={
            'Conta': 'cliente_id',
            'Nome': 'cliente_nome',
            'Produto': 'tipo_ativo',
            'Categoria': 'classe_ativo',
            'Subcategoria': 'subclasse_ativo',
            'Gestor': 'gestor',
            'Quantidade': 'quantidade',
            'Resgate (D+)': 'dias_resgate',
            'Valor Bruto': 'valor_bruto',
            'Valor Líquido': 'valor_liquido'
        })
        
        # Converter valores para float
        for col in ['valor_bruto', 'valor_liquido', 'quantidade', 'dias_resgate']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Adicionar informações de vencimento (fundos não têm vencimento, usar dias de resgate)
        df['dias_para_vencer'] = df['dias_resgate'].fillna(999)  # 999 = sem resgate
        
        # Classificar status (fundos não têm vencimento como RF)
        def classificar_status_fundo(dias):
            if pd.isna(dias) or dias >= 999:
                return 'Sem restrição'
            elif dias == 0:
                return 'Resgate D+0'
            elif dias == 1:
                return 'Resgate D+1'
            else:
                return f'Resgate D+{int(dias)}'
        
        df['status_vencimento'] = df['dias_resgate'].apply(classificar_status_fundo)
        
        # Adicionar tipo de relatório
        df['tipo_relatorio'] = 'Fundos'
        
        # Adicionar assessor (será preenchido depois se disponível)
        df['assessor'] = 'Não informado'
        
        # Remover linhas com valores nulos críticos
        df = df.dropna(subset=['cliente_id', 'cliente_nome', 'valor_bruto'])
        
        logger.info(f"Fundos processado: {len(df)} registros")
        
        return df
    
    @staticmethod
    def obter_resumo(df: pd.DataFrame) -> Dict:
        """Gera resumo dos dados de Fundos"""
        return {
            'total_registros': len(df),
            'total_clientes': df['cliente_nome'].nunique(),
            'valor_total': df['valor_bruto'].sum(),
            'valor_medio': df['valor_bruto'].mean(),
            'categorias': df['classe_ativo'].unique().tolist(),
            'gestores': df['gestor'].unique().tolist() if 'gestor' in df.columns else [],
            'subcategorias': df['subclasse_ativo'].unique().tolist() if 'subclasse_ativo' in df.columns else []
        }


class ParserPrevidencia:
    """Parser para relatorios de Previdencia"""
    
    COLUNAS_ESPERADAS = [
        'Conta', 'Nome', 'CNPJ', 'Produto', 'Ativo',
        'Tipo Previdencia', 'Situacao Retratabilidade',
        'Regime Tributario', 'Quantidade', 'Valor Bruto'
    ]
    
    @staticmethod
    def validar_estrutura(df: pd.DataFrame) -> Tuple[bool, str]:
        """Valida se o DataFrame tem a estrutura esperada de Previdencia"""
        if df is None or df.empty:
            return False, "DataFrame vazio"
        
        colunas_essenciais = ['Conta', 'Nome', 'Produto', 'Tipo Previdencia', 'Valor Bruto']
        colunas_faltantes = [col for col in colunas_essenciais if col not in df.columns]
        
        if colunas_faltantes:
            return False, f"Colunas faltantes: {', '.join(colunas_faltantes)}"
        
        return True, "Estrutura valida"
    
    @staticmethod
    def processar(df: pd.DataFrame) -> pd.DataFrame:
        """Processa um DataFrame de Previdencia"""
        df = df.copy()
        
        df = df.rename(columns={
            'Conta': 'cliente_id',
            'Nome': 'cliente_nome',
            'Produto': 'tipo_ativo',
            'Tipo Previdencia': 'classe_ativo',
            'Ativo': 'codigo_ativo',
            'Situacao Retratabilidade': 'retratabilidade',
            'Regime Tributario': 'regime_tributario',
            'Quantidade': 'quantidade',
            'Valor Bruto': 'valor_bruto'
        })
        
        for col in ['valor_bruto', 'quantidade']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['dias_para_vencer'] = 999
        
        def classificar_status_previdencia(retratabilidade):
            if pd.isna(retratabilidade):
                return 'Sem informacao'
            elif 'Irretratavel' in str(retratabilidade):
                return 'Irretratavel (Longo Prazo)'
            else:
                return 'Retratavel'
        
        df['status_vencimento'] = df['retratabilidade'].apply(classificar_status_previdencia)
        df['tipo_relatorio'] = 'Previdencia'
        df['assessor'] = 'Nao informado'
        
        df = df.dropna(subset=['cliente_id', 'cliente_nome', 'valor_bruto'])
        
        logger.info(f"Previdencia processado: {len(df)} registros")
        
        return df
    
    @staticmethod
    def obter_resumo(df: pd.DataFrame) -> Dict:
        """Gera resumo dos dados de Previdencia"""
        return {
            'total_registros': len(df),
            'total_clientes': df['cliente_nome'].nunique(),
            'valor_total': df['valor_bruto'].sum(),
            'valor_medio': df['valor_bruto'].mean(),
            'tipos': df['classe_ativo'].unique().tolist(),
            'retratabilidades': df['retratabilidade'].unique().tolist() if 'retratabilidade' in df.columns else [],
            'regimes': df['regime_tributario'].unique().tolist() if 'regime_tributario' in df.columns else []
        }

class ParserCOE:
    """Parser para relatorios de COE"""
    
    COLUNAS_ESPERADAS = [
        'Conta', 'Nome', 'Emissor', 'Produto', 'Ativo',
        'Ativo Subjacente', 'Tipo Opcao', 'Quantidade',
        'Data Emissao', 'Vencimento', 'Valor Bruto', 'Assessor'
    ]
    
    @staticmethod
    def validar_estrutura(df: pd.DataFrame) -> Tuple[bool, str]:
        """Valida se o DataFrame tem a estrutura esperada de COE"""
        if df is None or df.empty:
            return False, "DataFrame vazio"
        
        colunas_essenciais = ['Conta', 'Nome', 'Produto', 'Vencimento', 'Valor Bruto']
        colunas_faltantes = [col for col in colunas_essenciais if col not in df.columns]
        
        if colunas_faltantes:
            return False, f"Colunas faltantes: {', '.join(colunas_faltantes)}"
        
        return True, "Estrutura valida"
    
    @staticmethod
    def processar(df: pd.DataFrame) -> pd.DataFrame:
        """Processa um DataFrame de COE"""
        df = df.copy()
        
        df = df.rename(columns={
            'Conta': 'cliente_id',
            'Nome': 'cliente_nome',
            'Produto': 'tipo_ativo',
            'Ativo Subjacente': 'ativo_subjacente',
            'Tipo Opcao': 'classe_ativo',
            'Emissor': 'emissor',
            'Quantidade': 'quantidade',
            'Vencimento': 'data_vencimento',
            'Valor Bruto': 'valor_bruto',
            'Assessor': 'assessor'
        })
        
        for col in ['valor_bruto', 'quantidade']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
        
        hoje = pd.Timestamp.now()
        df['dias_para_vencer'] = (df['data_vencimento'] - hoje).dt.days
        
        def classificar_vencimento(dias):
            if pd.isna(dias):
                return 'Sem data'
            elif dias < 0:
                return 'Vencido'
            elif dias <= 30:
                return 'Critico (≤ 30 dias)'
            elif dias <= 60:
                return 'Alerta (31-60 dias)'
            elif dias <= 90:
                return 'Atencao (61-90 dias)'
            else:
                return 'Normal (> 90 dias)'
        
        df['status_vencimento'] = df['dias_para_vencer'].apply(classificar_vencimento)
        
        df['tipo_relatorio'] = 'COE'
        
        df['assessor'] = df['assessor'].fillna('Nao informado')
        
        df = df.dropna(subset=['cliente_id', 'cliente_nome', 'valor_bruto'])
        
        logger.info(f"COE processado: {len(df)} registros")
        
        return df
    
    @staticmethod
    def obter_resumo(df: pd.DataFrame) -> Dict:
        """Gera resumo dos dados de COE"""
        return {
            'total_registros': len(df),
            'total_clientes': df['cliente_nome'].nunique(),
            'valor_total': df['valor_bruto'].sum(),
            'valor_medio': df['valor_bruto'].mean(),
            'emissores': df['emissor'].unique().tolist() if 'emissor' in df.columns else [],
            'tipos_opcao': df['classe_ativo'].unique().tolist(),
            'vencimentos_criticos': len(df[df['status_vencimento'] == 'Critico (≤ 30 dias)'])
        }

class ParserRendaVariavel:
    """Parser para relatorios de Renda Variavel"""
    
    COLUNAS_ESPERADAS = [
        'Conta', 'Nome', 'Produto', 'Sub Mercado', 'Emissor',
        'Quantidade', 'Preco Mercado', 'Preco Medio',
        'Valor Bruto'
    ]
    
    @staticmethod
    def validar_estrutura(df: pd.DataFrame) -> Tuple[bool, str]:
        """Valida se o DataFrame tem a estrutura esperada de Renda Variavel"""
        if df is None or df.empty:
            return False, "DataFrame vazio"
        
        colunas_essenciais = ['Conta', 'Nome', 'Produto', 'Quantidade', 'Valor Bruto']
        colunas_faltantes = [col for col in colunas_essenciais if col not in df.columns]
        
        if colunas_faltantes:
            return False, f"Colunas faltantes: {', '.join(colunas_faltantes)}"
        
        return True, "Estrutura valida"
    
    @staticmethod
    def processar(df: pd.DataFrame) -> pd.DataFrame:
        """Processa um DataFrame de Renda Variavel"""
        df = df.copy()
        
        df = df.rename(columns={
            'Conta': 'cliente_id',
            'Nome': 'cliente_nome',
            'Produto': 'tipo_ativo',
            'Sub Mercado': 'classe_ativo',
            'Emissor': 'emissor',
            'Quantidade': 'quantidade',
            'Preco Mercado': 'preco_mercado',
            'Preco Medio': 'preco_medio',
            'Valor Bruto': 'valor_bruto'
        })
        
        for col in ['valor_bruto', 'quantidade', 'preco_mercado', 'preco_medio']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['dias_para_vencer'] = 999
        
        def classificar_status_rv(classe):
            if pd.isna(classe):
                return 'Sem classificacao'
            elif 'FII' in str(classe):
                return 'Fundo Imobiliario'
            elif 'ACAO' in str(classe):
                return 'Acao'
            else:
                return str(classe)
        
        df['status_vencimento'] = df['classe_ativo'].apply(classificar_status_rv)
        
        df['tipo_relatorio'] = 'Renda Variavel'
        
        df['assessor'] = 'Nao informado'
        
        df = df.dropna(subset=['cliente_id', 'cliente_nome', 'valor_bruto'])
        
        logger.info(f"Renda Variavel processado: {len(df)} registros")
        
        return df
    
    @staticmethod
    def obter_resumo(df: pd.DataFrame) -> Dict:
        """Gera resumo dos dados de Renda Variavel"""
        return {
            'total_registros': len(df),
            'total_clientes': df['cliente_nome'].nunique(),
            'valor_total': df['valor_bruto'].sum(),
            'valor_medio': df['valor_bruto'].mean(),
            'tipos_ativos': df['classe_ativo'].unique().tolist(),
            'quantidade_ativos': df['tipo_ativo'].nunique(),
            'valor_medio_por_ativo': df.groupby('tipo_ativo')['valor_bruto'].mean().mean()
        }

class GerenciadorParsers:
    """Gerenciador centralizado de parsers"""
    
    PARSERS = {
        'renda_fixa': ParserRendaFixa,
        'fundos': ParserFundos,
        'previdencia': ParserPrevidencia,
        'coe': ParserCOE,
        'renda_variavel': ParserRendaVariavel
    }
    
    @staticmethod
    def obter_parser(tipo: str):
        """
        Obtém o parser para um tipo de relatório
        
        Args:
            tipo: Tipo de relatório
            
        Returns:
            Classe do parser
        """
        tipo_lower = tipo.lower().replace(' ', '_')
        if tipo_lower not in GerenciadorParsers.PARSERS:
            raise ValueError(f"Parser não encontrado para tipo: {tipo}")
        return GerenciadorParsers.PARSERS[tipo_lower]
    
    @staticmethod
    def processar_relatorio(df: pd.DataFrame, tipo: str) -> Tuple[bool, pd.DataFrame, str]:
        """
        Processa um relatório com o parser apropriado
        
        Args:
            df: DataFrame bruto
            tipo: Tipo de relatório
            
        Returns:
            Tupla (sucesso, df_processado, mensagem)
        """
        try:
            parser = GerenciadorParsers.obter_parser(tipo)
            
            # Validar estrutura
            valido, msg = parser.validar_estrutura(df)
            if not valido:
                return False, None, f"Validação falhou: {msg}"
            
            # Processar
            df_processado = parser.processar(df)
            
            return True, df_processado, f"{tipo} processado com sucesso"
        
        except Exception as e:
            logger.error(f"Erro ao processar {tipo}: {str(e)}")
            return False, None, f"Erro: {str(e)}"
