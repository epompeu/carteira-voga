"""
Módulo para processamento robusto de planilhas.
Suporta detecção automática de formato, limpeza de dados e mapeamento de colunas.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class DetectorColunas:
    """Detecta automaticamente colunas importantes em uma planilha."""
    
    # Padrões de busca para diferentes tipos de colunas
    PADROES_ATIVO = [
        r'(?i)^ativo$', r'(?i)^ticker$', r'(?i)^código$', 
        r'(?i)^isin$', r'(?i)^nome$', r'(?i)^título$'
    ]
    
    PADROES_VALOR = [
        r'(?i)valor.*bruto', r'(?i)valor.*atual', r'(?i)valor$',
        r'(?i)preço', r'(?i)montante', r'(?i)quantidade.*valor'
    ]
    
    PADROES_VENCIMENTO = [
        r'(?i)data.*vencimento', r'(?i)vencimento$', r'(?i)data.*resgate',
        r'(?i)data.*vencida', r'(?i)maturity'
    ]
    
    PADROES_CLASSE = [
        r'(?i)classe$', r'(?i)tipo$', r'(?i)categoria$',
        r'(?i)sub.*mercado', r'(?i)segmento$'
    ]
    
    @staticmethod
    def encontrar_coluna(df: pd.DataFrame, padroes: List[str]) -> Optional[str]:
        """
        Encontra uma coluna que corresponde a um dos padrões.
        
        Args:
            df: DataFrame para buscar
            padroes: Lista de padrões regex
            
        Returns:
            Nome da coluna encontrada ou None
        """
        for coluna in df.columns:
            for padrao in padroes:
                if re.match(padrao, coluna):
                    return coluna
        return None
    
    @staticmethod
    def detectar_colunas(df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """
        Detecta automaticamente as colunas importantes.
        
        Args:
            df: DataFrame para analisar
            
        Returns:
            Dicionário com colunas detectadas
        """
        return {
            'ativo': DetectorColunas.encontrar_coluna(df, DetectorColunas.PADROES_ATIVO),
            'valor': DetectorColunas.encontrar_coluna(df, DetectorColunas.PADROES_VALOR),
            'vencimento': DetectorColunas.encontrar_coluna(df, DetectorColunas.PADROES_VENCIMENTO),
            'classe': DetectorColunas.encontrar_coluna(df, DetectorColunas.PADROES_CLASSE)
        }


class LimpadorDados:
    """Responsável pela limpeza e normalização de dados."""
    
    @staticmethod
    def remover_linhas_vazias(df: pd.DataFrame) -> pd.DataFrame:
        """Remove linhas completamente vazias."""
        return df.dropna(how='all')
    
    @staticmethod
    def remover_colunas_vazias(df: pd.DataFrame) -> pd.DataFrame:
        """Remove colunas completamente vazias."""
        return df.dropna(axis=1, how='all')
    
    @staticmethod
    def normalizar_nomes_colunas(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza nomes de colunas.
        Remove espaços extras, converte para minúsculas, etc.
        """
        df.columns = df.columns.str.strip().str.lower()
        return df
    
    @staticmethod
    def remover_linhas_duplicadas(df: pd.DataFrame, coluna_chave: str = 'Ativo') -> pd.DataFrame:
        """Remove linhas duplicadas baseado em coluna chave."""
        if coluna_chave in df.columns:
            return df.drop_duplicates(subset=[coluna_chave], keep='first')
        return df
    
    @staticmethod
    def converter_valores_numericos(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
        """
        Converte coluna para numérico, tratando diferentes formatos.
        
        Args:
            df: DataFrame
            coluna: Nome da coluna
            
        Returns:
            DataFrame com coluna convertida
        """
        if coluna not in df.columns:
            return df
        
        df = df.copy()
        
        # Remover símbolos de moeda e separadores
        if df[coluna].dtype == 'object':
            df[coluna] = df[coluna].astype(str)
            df[coluna] = df[coluna].str.replace('R$', '', regex=False)
            df[coluna] = df[coluna].str.replace('$', '', regex=False)
            df[coluna] = df[coluna].str.replace('.', '', regex=False)
            df[coluna] = df[coluna].str.replace(',', '.', regex=False)
        
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
        
        return df
    
    @staticmethod
    def converter_datas(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
        """
        Converte coluna para datetime, tentando diferentes formatos.
        
        Args:
            df: DataFrame
            coluna: Nome da coluna
            
        Returns:
            DataFrame com coluna convertida
        """
        if coluna not in df.columns:
            return df
        
        df = df.copy()
        
        # Tentar diferentes formatos
        formatos = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S'
        ]
        
        for formato in formatos:
            try:
                df[coluna] = pd.to_datetime(df[coluna], format=formato, errors='coerce')
                if df[coluna].notna().sum() > 0:
                    return df
            except:
                continue
        
        # Se nenhum formato funcionou, tentar inferência automática
        df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
        
        return df
    
    @staticmethod
    def preencher_valores_ausentes(df: pd.DataFrame, coluna: str, valor_padrao: str = 'N/A') -> pd.DataFrame:
        """Preenche valores ausentes em uma coluna."""
        df = df.copy()
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna(valor_padrao)
        return df


class ProcessadorPlanilhas:
    """Processador robusto de planilhas com detecção automática."""
    
    def __init__(self):
        """Inicializa o processador."""
        self.detector = DetectorColunas()
        self.limpador = LimpadorDados()
        self.colunas_detectadas: Dict[str, Optional[str]] = {}
    
    def carregar_planilha(self, caminho_arquivo: str, nome_aba: Optional[str] = None) -> Tuple[bool, pd.DataFrame, str]:
        """
        Carrega uma planilha com tratamento de erros.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            nome_aba: Nome da aba (se None, carrega primeira aba)
            
        Returns:
            Tupla (sucesso, DataFrame, mensagem)
        """
        try:
            # Verificar se arquivo existe
            if not Path(caminho_arquivo).exists():
                return False, None, f"Arquivo não encontrado: {caminho_arquivo}"
            
            # Tentar carregar
            if nome_aba:
                df = pd.read_excel(caminho_arquivo, sheet_name=nome_aba)
            else:
                df = pd.read_excel(caminho_arquivo)
            
            logger.info(f"Planilha carregada: {caminho_arquivo}")
            return True, df, "Planilha carregada com sucesso"
        
        except Exception as e:
            logger.error(f"Erro ao carregar planilha: {str(e)}")
            return False, None, f"Erro ao carregar: {str(e)}"
    
    def processar_planilha(self, df: pd.DataFrame, detectar_automaticamente: bool = True) -> Tuple[bool, pd.DataFrame, str]:
        """
        Processa uma planilha com limpeza e normalização.
        
        Args:
            df: DataFrame a processar
            detectar_automaticamente: Se True, detecta colunas automaticamente
            
        Returns:
            Tupla (sucesso, DataFrame processado, mensagem)
        """
        try:
            if df is None or df.empty:
                return False, None, "DataFrame vazio"
            
            # Limpeza básica
            df = self.limpador.remover_linhas_vazias(df)
            df = self.limpador.remover_colunas_vazias(df)
            
            # Detectar colunas se solicitado
            if detectar_automaticamente:
                self.colunas_detectadas = self.detector.detectar_colunas(df)
                logger.info(f"Colunas detectadas: {self.colunas_detectadas}")
            
            # Processar colunas detectadas
            if self.colunas_detectadas.get('valor'):
                df = self.limpador.converter_valores_numericos(df, self.colunas_detectadas['valor'])
            
            if self.colunas_detectadas.get('vencimento'):
                df = self.limpador.converter_datas(df, self.colunas_detectadas['vencimento'])
            
            # Remover duplicatas
            if self.colunas_detectadas.get('ativo'):
                df = self.limpador.remover_linhas_duplicadas(df, self.colunas_detectadas['ativo'])
            
            logger.info(f"Planilha processada: {len(df)} linhas")
            return True, df, f"Planilha processada com sucesso ({len(df)} registros)"
        
        except Exception as e:
            logger.error(f"Erro ao processar planilha: {str(e)}")
            return False, None, f"Erro ao processar: {str(e)}"
    
    def mapear_colunas_customizadas(self, df: pd.DataFrame, mapeamento: Dict[str, str]) -> pd.DataFrame:
        """
        Mapeia colunas customizadas para nomes padrão.
        
        Args:
            df: DataFrame
            mapeamento: Dicionário {coluna_original: coluna_padrao}
            
        Returns:
            DataFrame com colunas renomeadas
        """
        df = df.copy()
        
        # Filtrar apenas colunas que existem
        mapeamento_valido = {k: v for k, v in mapeamento.items() if k in df.columns}
        
        df = df.rename(columns=mapeamento_valido)
        logger.info(f"Colunas mapeadas: {mapeamento_valido}")
        
        return df
    
    def validar_planilha_processada(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida se a planilha foi processada corretamente.
        
        Args:
            df: DataFrame processado
            
        Returns:
            Tupla (válido, lista de avisos)
        """
        avisos = []
        
        if df is None or df.empty:
            return False, ["DataFrame vazio"]
        
        # Verificar colunas essenciais
        colunas_essenciais = ['Ativo', 'Valor', 'Categoria']
        colunas_faltantes = [col for col in colunas_essenciais if col not in df.columns]
        
        if colunas_faltantes:
            avisos.append(f"Colunas faltantes: {', '.join(colunas_faltantes)}")
        
        # Verificar valores numéricos
        if 'Valor' in df.columns:
            valores_invalidos = df['Valor'].isna().sum()
            if valores_invalidos > 0:
                avisos.append(f"{valores_invalidos} valores inválidos na coluna Valor")
        
        # Verificar datas
        if 'Data Vencimento' in df.columns:
            datas_invalidas = df['Data Vencimento'].isna().sum()
            if datas_invalidas > len(df) * 0.5:
                avisos.append(f"Mais de 50% das datas são inválidas")
        
        return len(avisos) == 0, avisos
    
    def obter_relatorio_processamento(self) -> Dict:
        """
        Retorna relatório do processamento realizado.
        
        Returns:
            Dicionário com informações do processamento
        """
        return {
            'colunas_detectadas': self.colunas_detectadas,
            'timestamp': pd.Timestamp.now().isoformat()
        }


class ProcessadorMultiplasAbas:
    """Processador para planilhas com múltiplas abas."""
    
    def __init__(self):
        """Inicializa o processador."""
        self.processador = ProcessadorPlanilhas()
        self.abas_processadas: Dict[str, pd.DataFrame] = {}
    
    def listar_abas(self, caminho_arquivo: str) -> Tuple[bool, List[str], str]:
        """
        Lista as abas disponíveis em um arquivo.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tupla (sucesso, lista de abas, mensagem)
        """
        try:
            abas = pd.ExcelFile(caminho_arquivo).sheet_names
            return True, abas, f"Encontradas {len(abas)} abas"
        except Exception as e:
            logger.error(f"Erro ao listar abas: {str(e)}")
            return False, [], f"Erro: {str(e)}"
    
    def processar_todas_abas(self, caminho_arquivo: str) -> Tuple[bool, Dict[str, pd.DataFrame], str]:
        """
        Processa todas as abas de um arquivo.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tupla (sucesso, dicionário de abas processadas, mensagem)
        """
        try:
            # Listar abas
            sucesso, abas, msg = self.listar_abas(caminho_arquivo)
            if not sucesso:
                return False, {}, msg
            
            # Processar cada aba
            for aba in abas:
                sucesso, df, msg = self.processador.carregar_planilha(caminho_arquivo, aba)
                if sucesso:
                    sucesso, df_proc, msg = self.processador.processar_planilha(df)
                    if sucesso:
                        self.abas_processadas[aba] = df_proc
                        logger.info(f"Aba '{aba}' processada com sucesso")
            
            return True, self.abas_processadas, f"Processadas {len(self.abas_processadas)} abas"
        
        except Exception as e:
            logger.error(f"Erro ao processar abas: {str(e)}")
            return False, {}, f"Erro: {str(e)}"
