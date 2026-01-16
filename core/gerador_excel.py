"""
Módulo para geração de planilhas Excel consolidadas com dados dos relatórios.
"""

import pandas as pd
from io import BytesIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GeradorExcelConsolidado:
    """Gera planilhas Excel consolidadas com dados dos relatórios"""
    
    @staticmethod
    def criar_excel_consolidado(dados_relatorios: dict) -> BytesIO:
        """
        Cria um arquivo Excel com múltiplas abas contendo:
        - Resumo Executivo
        - Todos os Ativos
        - Ativos com Vencimento Próximo
        - Por Tipo de Relatório
        
        Args:
            dados_relatorios: Dicionário com dados de cada tipo de relatório
            
        Returns:
            BytesIO: Buffer com arquivo Excel
        """
        
        # Consolidar todos os dados
        todos_dados = []
        for tipo_relatorio, df in dados_relatorios.items():
            if df is not None and not df.empty:
                todos_dados.append(df)
        
        if not todos_dados:
            logger.warning("Nenhum dado para consolidar")
            return None
        
        df_consolidado = pd.concat(todos_dados, ignore_index=True)
        
        # Criar arquivo Excel com múltiplas abas
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba 1: Resumo Executivo
            GeradorExcelConsolidado._criar_aba_resumo(df_consolidado, writer)
            
            # Aba 2: Todos os Ativos
            GeradorExcelConsolidado._criar_aba_todos_ativos(df_consolidado, writer)
            
            # Aba 3: Ativos com Vencimento Próximo
            GeradorExcelConsolidado._criar_aba_vencimentos(df_consolidado, writer)
            
            # Aba 4: Por Tipo de Relatório
            GeradorExcelConsolidado._criar_aba_por_tipo(df_consolidado, writer)
            
            # Aba 5: Por Cliente
            GeradorExcelConsolidado._criar_aba_por_cliente(df_consolidado, writer)
            
            # Aba 6: Por Assessor
            GeradorExcelConsolidado._criar_aba_por_assessor(df_consolidado, writer)
        
        output.seek(0)
        return output
    
    @staticmethod
    def _criar_aba_resumo(df: pd.DataFrame, writer) -> None:
        """Cria aba de resumo executivo"""
        
        resumo_data = {
            'Métrica': [
                'Total de Ativos',
                'Valor Total Investido',
                'Valor Médio por Ativo',
                'Total de Clientes',
                'Total de Assessores',
                'Tipos de Relatório',
                'Ativos com Vencimento ≤ 30 dias',
                'Data de Geração'
            ],
            'Valor': [
                len(df),
                f"R$ {df['valor_bruto'].sum():,.2f}",
                f"R$ {df['valor_bruto'].mean():,.2f}",
                df['cliente_nome'].nunique(),
                df['assessor'].nunique() if 'assessor' in df.columns else 0,
                ', '.join(df['tipo_relatorio'].unique()),
                len(df[df['dias_para_vencer'] <= 30]) if 'dias_para_vencer' in df.columns else 0,
                datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            ]
        }
        
        df_resumo = pd.DataFrame(resumo_data)
        df_resumo.to_excel(writer, sheet_name='Resumo Executivo', index=False)
        
        logger.info("Aba Resumo Executivo criada")
    
    @staticmethod
    def _criar_aba_todos_ativos(df: pd.DataFrame, writer) -> None:
        """Cria aba com todos os ativos"""
        
        # Selecionar colunas relevantes
        colunas = [
            'cliente_nome', 'tipo_relatorio', 'tipo_ativo', 'classe_ativo',
            'quantidade', 'valor_bruto', 'assessor', 'status_vencimento'
        ]
        
        colunas_existentes = [col for col in colunas if col in df.columns]
        df_ativos = df[colunas_existentes].copy()
        
        # Ordenar por valor decrescente
        df_ativos = df_ativos.sort_values('valor_bruto', ascending=False)
        
        df_ativos.to_excel(writer, sheet_name='Todos os Ativos', index=False)
        
        logger.info("Aba Todos os Ativos criada")
    
    @staticmethod
    def _criar_aba_vencimentos(df: pd.DataFrame, writer) -> None:
        """Cria aba com ativos com vencimento próximo"""
        
        if 'dias_para_vencer' not in df.columns:
            return
        
        # Filtrar ativos com vencimento próximo
        df_vencimentos = df[df['dias_para_vencer'] <= 30].copy()
        
        if df_vencimentos.empty:
            # Criar aba vazia com mensagem
            df_vazio = pd.DataFrame({'Mensagem': ['Nenhum ativo com vencimento próximo']})
            df_vazio.to_excel(writer, sheet_name='Vencimentos Próximos', index=False)
        else:
            # Selecionar colunas relevantes
            colunas = [
                'cliente_nome', 'tipo_relatorio', 'tipo_ativo', 'valor_bruto',
                'dias_para_vencer', 'status_vencimento', 'assessor'
            ]
            
            colunas_existentes = [col for col in colunas if col in df_vencimentos.columns]
            df_venc = df_vencimentos[colunas_existentes].copy()
            
            # Ordenar por dias para vencer (crescente)
            if 'dias_para_vencer' in df_venc.columns:
                df_venc = df_venc.sort_values('dias_para_vencer')
            
            df_venc.to_excel(writer, sheet_name='Vencimentos Próximos', index=False)
        
        logger.info("Aba Vencimentos Próximos criada")
    
    @staticmethod
    def _criar_aba_por_tipo(df: pd.DataFrame, writer) -> None:
        """Cria aba com dados agrupados por tipo de relatório"""
        
        if 'tipo_relatorio' not in df.columns:
            return
        
        # Agrupar por tipo de relatório
        for tipo in df['tipo_relatorio'].unique():
            df_tipo = df[df['tipo_relatorio'] == tipo].copy()
            
            # Selecionar colunas
            colunas = [
                'cliente_nome', 'tipo_ativo', 'classe_ativo',
                'quantidade', 'valor_bruto', 'assessor'
            ]
            
            colunas_existentes = [col for col in colunas if col in df_tipo.columns]
            df_tipo_filtrado = df_tipo[colunas_existentes].copy()
            
            # Ordenar por valor
            df_tipo_filtrado = df_tipo_filtrado.sort_values('valor_bruto', ascending=False)
            
            # Nome da aba (máximo 31 caracteres)
            nome_aba = f"{tipo[:25]}"
            df_tipo_filtrado.to_excel(writer, sheet_name=nome_aba, index=False)
        
        logger.info("Abas por Tipo de Relatório criadas")
    
    @staticmethod
    def _criar_aba_por_cliente(df: pd.DataFrame, writer) -> None:
        """Cria aba com dados agrupados por cliente"""
        
        if 'cliente_nome' not in df.columns:
            return
        
        # Agrupar por cliente
        df_cliente = df.groupby('cliente_nome').agg({
            'valor_bruto': 'sum',
            'tipo_relatorio': lambda x: ', '.join(x.unique()),
            'tipo_ativo': 'count',
            'assessor': lambda x: x.iloc[0] if len(x) > 0 else 'N/A'
        }).reset_index()
        
        df_cliente.columns = ['Cliente', 'Valor Total', 'Tipos de Relatório', 'Quantidade de Ativos', 'Assessor']
        df_cliente = df_cliente.sort_values('Valor Total', ascending=False)
        
        df_cliente.to_excel(writer, sheet_name='Por Cliente', index=False)
        
        logger.info("Aba Por Cliente criada")
    
    @staticmethod
    def _criar_aba_por_assessor(df: pd.DataFrame, writer) -> None:
        """Cria aba com dados agrupados por assessor"""
        
        if 'assessor' not in df.columns:
            return
        
        # Agrupar por assessor
        df_assessor = df.groupby('assessor').agg({
            'valor_bruto': 'sum',
            'cliente_nome': 'nunique',
            'tipo_relatorio': lambda x: ', '.join(x.unique()),
            'tipo_ativo': 'count'
        }).reset_index()
        
        df_assessor.columns = ['Assessor', 'Valor Total', 'Quantidade de Clientes', 'Tipos de Relatório', 'Quantidade de Ativos']
        df_assessor = df_assessor.sort_values('Valor Total', ascending=False)
        
        df_assessor.to_excel(writer, sheet_name='Por Assessor', index=False)
        
        logger.info("Aba Por Assessor criada")


def gerar_excel_para_download(dados_relatorios: dict) -> tuple:
    """
    Gera Excel consolidado e retorna buffer e nome do arquivo
    
    Args:
        dados_relatorios: Dicionário com dados de cada tipo de relatório
        
    Returns:
        tuple: (buffer BytesIO, nome_arquivo string)
    """
    
    buffer = GeradorExcelConsolidado.criar_excel_consolidado(dados_relatorios)
    
    if buffer is None:
        return None, None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"Carteira_VOGA_{timestamp}.xlsx"
    
    return buffer, nome_arquivo
