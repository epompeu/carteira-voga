"""
Módulo principal para processamento e análise de carteiras de investimentos.
Suporta múltiplas categorias: Renda Fixa, COE, Renda Variável e Derivativos.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
from enum import Enum
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CategoriaInvestimento(Enum):
    """Categorias de investimento suportadas."""
    RENDA_FIXA = "Renda Fixa"
    COE = "COE"
    RENDA_VARIAVEL = "Renda Variável"
    DERIVATIVOS = "Derivativos"


class ConfiguracaoCategoria:
    """Configuração de processamento para cada categoria de investimento."""
    
    CONFIGURACOES = {
        CategoriaInvestimento.RENDA_FIXA: {
            'coluna_valor': 'Valor Bruto - Opção Cliente',
            'coluna_classe': 'Sub Mercado',
            'tem_vencimento': True,
            'coluna_ativo': 'Ativo'
        },
        CategoriaInvestimento.COE: {
            'coluna_valor': 'Valor Bruto - Opção Cliente',
            'coluna_classe': 'Tipo',
            'tem_vencimento': True,
            'coluna_ativo': 'Ativo'
        },
        CategoriaInvestimento.RENDA_VARIAVEL: {
            'coluna_valor': 'Valor Atual',
            'coluna_classe': 'Tipo',
            'tem_vencimento': False,
            'coluna_ativo': 'Ativo'
        },
        CategoriaInvestimento.DERIVATIVOS: {
            'coluna_valor': 'Valor',
            'coluna_classe': 'Tipo',
            'tem_vencimento': True,
            'coluna_ativo': 'Ativo'
        }
    }
    
    @classmethod
    def obter_config(cls, categoria: CategoriaInvestimento) -> Dict:
        """Obtém configuração para uma categoria."""
        return cls.CONFIGURACOES.get(categoria, {})


class ValidadorDados:
    """Classe responsável pela validação de dados de entrada."""
    
    @staticmethod
    def validar_dataframe(df: pd.DataFrame, coluna_ativo: str = 'Ativo') -> Tuple[bool, str]:
        """
        Valida se o dataframe possui estrutura mínima necessária.
        
        Args:
            df: DataFrame a validar
            coluna_ativo: Nome da coluna de ativo
            
        Returns:
            Tupla (válido, mensagem)
        """
        if df is None or df.empty:
            return False, "Arquivo vazio ou inválido"
        
        if coluna_ativo not in df.columns:
            return False, f"Coluna '{coluna_ativo}' não encontrada no arquivo"
        
        # Verificar se há dados após remover NaN
        df_limpo = df.dropna(subset=[coluna_ativo])
        if df_limpo.empty:
            return False, f"Nenhum ativo válido encontrado após limpeza"
        
        return True, "Validação bem-sucedida"
    
    @staticmethod
    def validar_coluna_valor(df: pd.DataFrame, coluna_valor: str) -> Tuple[bool, str]:
        """
        Valida se a coluna de valor existe e contém dados numéricos válidos.
        
        Args:
            df: DataFrame a validar
            coluna_valor: Nome da coluna de valor
            
        Returns:
            Tupla (válido, mensagem)
        """
        if coluna_valor not in df.columns:
            return False, f"Coluna de valor '{coluna_valor}' não encontrada"
        
        # Tentar converter para numérico
        valores_numericos = pd.to_numeric(df[coluna_valor], errors='coerce')
        taxa_validos = valores_numericos.notna().sum() / len(df)
        
        if taxa_validos < 0.5:
            return False, f"Menos de 50% dos valores são numéricos válidos"
        
        return True, "Coluna de valor validada"


class ProcessadorCarteira:
    """Classe principal para processar relatórios de investimentos."""
    
    def __init__(self):
        """Inicializa o processador de carteira."""
        self.dados_processados: Dict[str, pd.DataFrame] = {}
        self.carteira_consolidada: Optional[pd.DataFrame] = None
        self.validador = ValidadorDados()
        self.data_processamento = datetime.now()
    
    def carregar_categoria(self, arquivo, categoria: CategoriaInvestimento) -> Tuple[bool, str]:
        """
        Carrega e processa arquivo de uma categoria de investimento.
        
        Args:
            arquivo: Caminho ou objeto do arquivo Excel
            categoria: Categoria de investimento
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Ler arquivo
            df = pd.read_excel(arquivo)
            
            # Obter configuração
            config = ConfiguracaoCategoria.obter_config(categoria)
            coluna_ativo = config.get('coluna_ativo', 'Ativo')
            
            # Validar dados básicos
            valido, msg = self.validador.validar_dataframe(df, coluna_ativo)
            if not valido:
                return False, f"Erro ao processar {categoria.value}: {msg}"
            
            # Limpar dados
            df = df.dropna(subset=[coluna_ativo])
            
            # Processar coluna de valor
            coluna_valor = config.get('coluna_valor', 'Valor')
            if coluna_valor not in df.columns:
                # Tentar alternativas
                colunas_alternativas = [col for col in df.columns if 'valor' in col.lower()]
                if colunas_alternativas:
                    coluna_valor = colunas_alternativas[0]
                else:
                    coluna_valor = 'Valor'
            
            df['Valor'] = pd.to_numeric(df.get(coluna_valor, 0), errors='coerce').fillna(0)
            
            # Processar vencimento
            if config.get('tem_vencimento', False):
                if 'Data Vencimento' in df.columns:
                    df['Data Vencimento'] = pd.to_datetime(df['Data Vencimento'], errors='coerce')
                else:
                    df['Data Vencimento'] = pd.NaT
            else:
                df['Data Vencimento'] = pd.NaT
            
            # Adicionar metadados
            df['Categoria'] = categoria.value
            coluna_classe = config.get('coluna_classe', 'Tipo')
            df['Classe'] = df.get(coluna_classe, categoria.value)
            
            # Armazenar dados processados
            self.dados_processados[categoria.value] = df
            logger.info(f"{categoria.value} carregado com sucesso. Total: {len(df)} registros")
            
            return True, f"{categoria.value} carregado com sucesso ({len(df)} registros)"
        
        except Exception as e:
            logger.error(f"Erro ao processar {categoria.value}: {str(e)}")
            return False, f"Erro ao processar {categoria.value}: {str(e)}"
    
    def carregar_renda_fixa(self, arquivo) -> Tuple[bool, str]:
        """Carrega arquivo de Renda Fixa."""
        return self.carregar_categoria(arquivo, CategoriaInvestimento.RENDA_FIXA)
    
    def carregar_coe(self, arquivo) -> Tuple[bool, str]:
        """Carrega arquivo de COE."""
        return self.carregar_categoria(arquivo, CategoriaInvestimento.COE)
    
    def carregar_renda_variavel(self, arquivo) -> Tuple[bool, str]:
        """Carrega arquivo de Renda Variável."""
        return self.carregar_categoria(arquivo, CategoriaInvestimento.RENDA_VARIAVEL)
    
    def carregar_derivativos(self, arquivo) -> Tuple[bool, str]:
        """Carrega arquivo de Derivativos."""
        return self.carregar_categoria(arquivo, CategoriaInvestimento.DERIVATIVOS)
    
    def processar_vencimentos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona informações de vencimento ao dataframe.
        
        Args:
            df: DataFrame a processar
            
        Returns:
            DataFrame com colunas de vencimento adicionadas
        """
        df = df.copy()
        hoje = datetime.now()
        
        if 'Data Vencimento' in df.columns:
            # Calcular dias para vencer
            df['Dias para Vencer'] = (df['Data Vencimento'] - hoje).dt.days
            
            # Definir status de vencimento
            def definir_status(dias):
                if pd.isna(dias):
                    return "Sem Vencimento"
                elif dias < 0:
                    return "VENCIDO"
                elif dias <= 30:
                    return "CRÍTICO (≤ 30 dias)"
                elif dias <= 60:
                    return "ALERTA (31-60 dias)"
                else:
                    return "OK"
            
            df['Status Vencimento'] = df['Dias para Vencer'].apply(definir_status)
        else:
            df['Dias para Vencer'] = np.nan
            df['Status Vencimento'] = "Sem Vencimento"
        
        return df
    
    def consolidar_carteira(self) -> Optional[pd.DataFrame]:
        """
        Consolida todos os dados processados em uma única carteira.
        
        Returns:
            DataFrame consolidado ou None se vazio
        """
        if not self.dados_processados:
            logger.warning("Nenhum dado processado para consolidar")
            return None
        
        dfs = []
        for categoria, df in self.dados_processados.items():
            df_proc = self.processar_vencimentos(df.copy())
            dfs.append(df_proc)
        
        self.carteira_consolidada = pd.concat(dfs, ignore_index=True)
        logger.info(f"Carteira consolidada com {len(self.carteira_consolidada)} registros")
        
        return self.carteira_consolidada
    
    def obter_resumo_alocacao(self) -> Optional[Tuple[pd.DataFrame, float]]:
        """
        Retorna resumo de alocação por categoria.
        
        Returns:
            Tupla (DataFrame de alocação, valor total) ou None
        """
        if self.carteira_consolidada is None:
            logger.warning("Carteira não consolidada")
            return None
        
        alocacao = self.carteira_consolidada.groupby('Categoria')['Valor'].agg([
            ('Valor Total', 'sum'),
            ('Quantidade', 'count')
        ]).reset_index()
        
        total = alocacao['Valor Total'].sum()
        alocacao['Percentual'] = (alocacao['Valor Total'] / total * 100).round(2)
        alocacao = alocacao.sort_values('Percentual', ascending=False)
        
        return alocacao, total
    
    def obter_resumo_por_classe(self) -> Optional[pd.DataFrame]:
        """
        Retorna resumo de alocação por classe dentro de cada categoria.
        
        Returns:
            DataFrame com resumo por classe ou None
        """
        if self.carteira_consolidada is None:
            return None
        
        resumo = self.carteira_consolidada.groupby(['Categoria', 'Classe'])['Valor'].agg([
            ('Valor Total', 'sum'),
            ('Quantidade', 'count')
        ]).reset_index()
        
        total = resumo['Valor Total'].sum()
        resumo['Percentual'] = (resumo['Valor Total'] / total * 100).round(2)
        resumo = resumo.sort_values(['Categoria', 'Percentual'], ascending=[True, False])
        
        return resumo
    
    def obter_alertas_vencimento(self, dias_alerta: int = 60) -> Optional[pd.DataFrame]:
        """
        Retorna ativos com vencimento próximo.
        
        Args:
            dias_alerta: Número de dias para considerar como alerta
            
        Returns:
            DataFrame com alertas ou None
        """
        if self.carteira_consolidada is None:
            return None
        
        alertas = self.carteira_consolidada[
            (self.carteira_consolidada['Dias para Vencer'] <= dias_alerta) & 
            (self.carteira_consolidada['Dias para Vencer'] >= 0)
        ].sort_values('Dias para Vencer')
        
        return alertas if not alertas.empty else None
    
    def obter_ativos_vencidos(self) -> Optional[pd.DataFrame]:
        """
        Retorna ativos vencidos.
        
        Returns:
            DataFrame com ativos vencidos ou None
        """
        if self.carteira_consolidada is None:
            return None
        
        vencidos = self.carteira_consolidada[
            self.carteira_consolidada['Dias para Vencer'] < 0
        ].sort_values('Dias para Vencer')
        
        return vencidos if not vencidos.empty else None
    
    def obter_carteira_detalhada(self) -> Optional[pd.DataFrame]:
        """
        Retorna a carteira consolidada com informações detalhadas.
        
        Returns:
            DataFrame com carteira detalhada ou None
        """
        if self.carteira_consolidada is None:
            return None
        
        colunas_exibicao = [
            'Ativo', 'Categoria', 'Classe', 'Valor', 
            'Data Vencimento', 'Dias para Vencer', 'Status Vencimento'
        ]
        
        # Manter apenas colunas que existem
        colunas_exibicao = [col for col in colunas_exibicao if col in self.carteira_consolidada.columns]
        
        df_exibicao = self.carteira_consolidada[colunas_exibicao].copy()
        df_exibicao = df_exibicao.sort_values('Dias para Vencer', na_position='last')
        
        return df_exibicao
    
    def obter_estatisticas(self) -> Optional[Dict]:
        """
        Retorna estatísticas gerais da carteira.
        
        Returns:
            Dicionário com estatísticas ou None
        """
        if self.carteira_consolidada is None:
            return None
        
        return {
            'total_ativos': len(self.carteira_consolidada),
            'valor_total': self.carteira_consolidada['Valor'].sum(),
            'valor_medio': self.carteira_consolidada['Valor'].mean(),
            'valor_maximo': self.carteira_consolidada['Valor'].max(),
            'valor_minimo': self.carteira_consolidada['Valor'].min(),
            'categorias': self.carteira_consolidada['Categoria'].nunique(),
            'data_processamento': self.data_processamento
        }
    
    def exportar_para_excel(self, caminho_saida: str) -> Tuple[bool, str]:
        """
        Exporta todos os dados para um arquivo Excel com múltiplas abas.
        
        Args:
            caminho_saida: Caminho para salvar o arquivo
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        if self.carteira_consolidada is None:
            return False, "Carteira não consolidada. Processe os dados primeiro."
        
        try:
            with pd.ExcelWriter(caminho_saida, engine='openpyxl') as writer:
                # Aba 1: Resumo de Alocação
                alocacao, total = self.obter_resumo_alocacao()
                if alocacao is not None:
                    alocacao.to_excel(writer, sheet_name='Resumo Alocação', index=False)
                
                # Aba 2: Resumo por Classe
                resumo_classe = self.obter_resumo_por_classe()
                if resumo_classe is not None:
                    resumo_classe.to_excel(writer, sheet_name='Resumo por Classe', index=False)
                
                # Aba 3: Carteira Detalhada
                carteira_det = self.obter_carteira_detalhada()
                if carteira_det is not None:
                    carteira_det.to_excel(writer, sheet_name='Carteira Detalhada', index=False)
                
                # Aba 4: Alertas de Vencimento
                alertas = self.obter_alertas_vencimento()
                if alertas is not None:
                    alertas.to_excel(writer, sheet_name='Alertas Vencimento', index=False)
                
                # Aba 5: Ativos Vencidos
                vencidos = self.obter_ativos_vencidos()
                if vencidos is not None:
                    vencidos.to_excel(writer, sheet_name='Ativos Vencidos', index=False)
                
                # Aba 6: Estatísticas
                stats = self.obter_estatisticas()
                if stats:
                    stats_df = pd.DataFrame([stats])
                    stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
            
            logger.info(f"Arquivo exportado com sucesso: {caminho_saida}")
            return True, f"Arquivo exportado com sucesso: {caminho_saida}"
        
        except Exception as e:
            logger.error(f"Erro ao exportar: {str(e)}")
            return False, f"Erro ao exportar: {str(e)}"
    
    def limpar_dados(self):
        """Limpa todos os dados processados."""
        self.dados_processados = {}
        self.carteira_consolidada = None
        logger.info("Dados limpos")
